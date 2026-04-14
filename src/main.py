"""
Richards File Utilities (RFU) - Main Entry Point.

This module serves as the central entry point for the RFU application,
handling initialization of logging, configuration, and the Qt application.
"""

import os
import sys
from pathlib import Path

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication

# Add the src directory to Python path for relative imports
script_dir = Path(__file__).parent
src_dir = script_dir.parent
sys.path.insert(0, str(src_dir))

IDENTITY_DB_FILENAME = "rfu_identity.sqlite3"

# Import with fallback for direct execution and capture diagnostics
_RFUHUB_IMPORT_SOURCE = "package"
_RFUHUB_IMPORT_ERRORS = []

try:
    from .tabbed_hub import RFUHub
except ImportError as primary_import_error:  # pragma: no cover - import guard
    _RFUHUB_IMPORT_ERRORS.append(("src.tabbed_hub", primary_import_error))
    _RFUHUB_IMPORT_SOURCE = "local"
    try:
        from tabbed_hub import RFUHub
    except (ImportError,) as secondary_import_error:  # pragma: no cover
        _RFUHUB_IMPORT_ERRORS.append(("tabbed_hub", secondary_import_error))
        raise


def _load_preference_manager(logger):
    """Best-effort import for PreferenceManager with graceful fallback."""

    try:
        from .core.preferences.manager import PreferenceManager

        return PreferenceManager
    except ImportError:
        try:
            from core.preferences.manager import PreferenceManager

            return PreferenceManager
        except ImportError as import_error:
            logger.debug(
                "PreferenceManager import failed; using default theme: %s",
                import_error,
            )

    return None


def _load_theme_manager(logger):
    """Best-effort import for ThemeManager with graceful fallback."""

    try:
        from .gui.themes import ThemeManager

        return ThemeManager
    except ImportError:
        try:
            from gui.themes import ThemeManager

            return ThemeManager
        except ImportError as import_error:
            logger.debug(
                "ThemeManager import failed; skipping theme bootstrap: %s",
                import_error,
            )

    return None


def _bootstrap_theme(logger):
    """Initialize theme based on saved preferences."""

    pref_manager_cls = _load_preference_manager(logger)
    theme_manager_cls = _load_theme_manager(logger)

    theme_name = None
    if pref_manager_cls:
        try:
            theme_name = pref_manager_cls().get_theme(default="light")
            logger.debug("Loaded saved theme preference: %s", theme_name)
        except Exception as pref_error:
            logger.warning(
                "Unable to read saved theme preference; " "fallback to default: %s",
                pref_error,
            )
            theme_name = None

    if theme_manager_cls and theme_name:
        try:
            theme_manager_cls.set_theme(theme_name)
            logger.info(
                "Activated theme '%s' from preferences",
                theme_name,
            )
        except Exception as theme_error:
            logger.warning(
                "Unable to apply saved theme '%s': %s",
                theme_name,
                theme_error,
            )

    return pref_manager_cls, theme_manager_cls


def _attach_theme_persistence(pref_manager_cls, theme_manager_cls, logger):
    """Persist theme changes through PreferenceManager callbacks."""

    if not pref_manager_cls or not theme_manager_cls:
        return

    if not hasattr(theme_manager_cls, "add_theme_changed_callback"):
        logger.debug("ThemeManager missing callback support; skipping sync")
        return

    def _persist_theme_change(theme_name):
        try:
            pref_manager_cls().set_theme(theme_name)
            logger.debug("Persisted theme preference: %s", theme_name)
        except Exception as error:
            logger.warning(
                "Unable to persist theme preference '%s': %s",
                theme_name,
                error,
            )

    try:
        theme_manager_cls.add_theme_changed_callback(_persist_theme_change)
    except Exception as callback_error:
        logger.warning(
            "Unable to register theme persistence callback: %s",
            callback_error,
        )


def _log_identity_db_candidates(logger, config):
    """Emit debug-level diagnostics for identity DB resolution."""

    def _log_identity_candidate(label: str, candidate_path: Path) -> None:
        try:
            expanded = candidate_path.expanduser()
        except Exception:
            expanded = candidate_path

        exists = expanded.exists()
        detail = ""
        if exists:
            try:
                detail = f", size={expanded.stat().st_size} bytes"
            except OSError as stat_error:
                detail = f", stat_error={stat_error}"
        logger.debug(
            "Identity DB candidate (%s): %s (exists=%s%s)",
            label,
            expanded,
            exists,
            detail,
        )

    configured_identity = (
        config.get_setting("identity", "database_path", "") or ""
    ).strip()
    env_identity = (os.getenv("RFU_IDENTITY_DB_PATH") or "").strip()
    if configured_identity:
        _log_identity_candidate("config", Path(configured_identity))
    if env_identity:
        _log_identity_candidate("env", Path(env_identity))

    project_default = Path(__file__).resolve().parent / "data" / IDENTITY_DB_FILENAME
    _log_identity_candidate("project-default", project_default)
    cwd_default = Path.cwd() / "data" / IDENTITY_DB_FILENAME
    _log_identity_candidate("cwd-default", cwd_default)


def main():
    """
    Initialize and run the Richards File Utilities application.

    Returns:
        int: Exit code (0 for success, 1 for failure)
    """
    # Initialize logging first
    try:
        from .log_manager import get_log_manager
    except ImportError:
        from log_manager import get_log_manager

    logger = get_log_manager().get_logger("Main")
    logger.info("Starting Richards Files Utilities")

    if _RFUHUB_IMPORT_ERRORS:
        for attempt_source, attempt_error in _RFUHUB_IMPORT_ERRORS:
            logger.warning(
                "RFUHub import attempt '%s' failed: %s",
                attempt_source,
                attempt_error,
            )

    logger.debug(
        "RFUHub imported from %s (sys.path[0]=%s)",
        _RFUHUB_IMPORT_SOURCE,
        sys.path[0],
    )

    try:
        # Initialize configuration
        try:
            from .config_manager import get_config_manager
        except ImportError:
            from config_manager import get_config_manager

        config = get_config_manager()
        logging_level = config.get_setting("general", "logging_level", "INFO")
        debug_enabled = config.get_setting(
            "general",
            "enable_debug_logging",
            False,
        )
        _log_identity_db_candidates(logger, config)

        # Initialize network connectivity configuration
        # try:
        #     from network_connectivity.config import (
        #         get_network_config_manager)
        #     network_config = get_network_config_manager()
        #     logger.info('Network connectivity configuration initialized')
        # except Exception as e:
        #     logger.warning('Failed to initialize network connectivity '
        #                    'config: %s', e)

        # Set logging level based on configuration
        if debug_enabled:
            get_log_manager().set_level("DEBUG")
        else:
            get_log_manager().set_level(logging_level)

        # Create Qt application with proper cleanup
        # Enable HiDPI scaling (A11Y-5) — must be set before QApplication.
        if hasattr(Qt, "AA_EnableHighDpiScaling"):
            QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
        if hasattr(Qt, "AA_UseHighDpiPixmaps"):
            QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
        app = QApplication(sys.argv)
        logger.info("Qt Application initialized")

        pref_manager_cls, theme_manager_cls = _bootstrap_theme(logger)
        _attach_theme_persistence(pref_manager_cls, theme_manager_cls, logger)

        # Create and show main window
        window = RFUHub()

        if theme_manager_cls:
            try:
                theme_manager_cls.apply_main_window_theme(window)
            except Exception as theme_apply_error:
                logger.warning(
                    "Unable to apply theme styling to main window: %s",
                    theme_apply_error,
                )

        window.show()
        logger.info("Main window displayed")

        # Start event loop
        return_code = app.exec_()
        logger.info("Application shutting down")

        # Ensure proper cleanup
        try:
            if hasattr(window, "gui_hub") and window.gui_hub:
                window.gui_hub.close()
            app.quit()
            app.deleteLater()
        except Exception as e:
            logger.error("Error during final cleanup: %s", e)

        return return_code

    except Exception as e:
        logger.critical("Critical error in main: %s", str(e), exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
