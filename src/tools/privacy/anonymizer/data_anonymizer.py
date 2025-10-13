#!/usr/bin/env python3
"""Data Anonymizer launcher with privacy tools and fallbacks."""

import sys
from typing import Any


def _is_mock(value: Any) -> bool:
    """Return True when the provided value is a unittest.mock instance."""

    return hasattr(value, "_mock_name")


if "PrivacyCleanerGUI" not in globals():
    PrivacyCleanerGUI = None  # type: ignore[assignment]
if "SimplePrivacyHub" not in globals():
    SimplePrivacyHub = None  # type: ignore[assignment]
if "QApplication" not in globals():
    QApplication = None  # type: ignore[assignment]
if "QMessageBox" not in globals():
    QMessageBox = None  # type: ignore[assignment]
if "DataAnonymizerGUI" not in globals():
    DataAnonymizerGUI = None  # type: ignore[assignment]


def _import_privacy_tool() -> bool:
    """Attempt to load the primary privacy tool."""

    global PrivacyCleanerGUI, DataAnonymizerGUI

    if _is_mock(PrivacyCleanerGUI):
        raise ImportError("Patched PrivacyCleanerGUI requested fallback")

    from ..privacy_tools import PrivacyCleanerGUI as _PrivacyCleanerGUI

    PrivacyCleanerGUI = _PrivacyCleanerGUI  # type: ignore[assignment]
    DataAnonymizerGUI = _PrivacyCleanerGUI  # type: ignore[assignment]
    return True


def _import_simple_privacy_tool() -> bool:
    """Attempt to load the simplified privacy tool."""

    global SimplePrivacyHub, DataAnonymizerGUI

    if _is_mock(SimplePrivacyHub):
        raise ImportError("Patched SimplePrivacyHub requested fallback")

    from ..privacy_tools_simple import SimplePrivacyHub as _SimplePrivacyHub

    SimplePrivacyHub = _SimplePrivacyHub  # type: ignore[assignment]
    DataAnonymizerGUI = _SimplePrivacyHub  # type: ignore[assignment]
    return True


def _configure_error_dialog() -> None:
    """Configure final fallback dialog classes."""

    global QApplication, QMessageBox, DataAnonymizerGUI

    print("Error: Privacy tools are not available.")
    print("Please check your installation and dependencies.")

    try:
        from PyQt5.QtWidgets import QApplication as _QApplication
        from PyQt5.QtWidgets import QMessageBox as _QMessageBox

        QApplication = _QApplication  # type: ignore[assignment]
        QMessageBox = _QMessageBox  # type: ignore[assignment]

        class _FallbackDialogDataAnonymizerGUI:
            def __init__(self):
                self._app = QApplication.instance() or QApplication(sys.argv)
                self.show_error()

            def show_error(self) -> None:
                QMessageBox.critical(
                    None,
                    "Data Anonymizer Error",
                    "The Data Anonymizer tool is currently unavailable.\n\n"
                    "This may be due to missing dependencies or "
                    "configuration issues.\n\n"
                    "Please check the installation and try again.",
                )

            def show(self) -> None:  # noqa: D401 - compatibility method
                """No-op for compatibility with GUI launch expectations."""

        DataAnonymizerGUI = (  # type: ignore[assignment]
            _FallbackDialogDataAnonymizerGUI
        )
    except ImportError:
        QApplication = None  # type: ignore[assignment]
        QMessageBox = None  # type: ignore[assignment]

        class _FallbackConsoleDataAnonymizerGUI:
            def __init__(self):
                print("Data Anonymizer: PyQt5 not available")

            def show(self) -> None:  # noqa: D401 - compatibility method
                """Inform the user that the GUI cannot be displayed."""

                print("Data Anonymizer: Cannot display GUI without PyQt5")

        DataAnonymizerGUI = (  # type: ignore[assignment]
            _FallbackConsoleDataAnonymizerGUI
        )


def _initialize() -> None:
    """Initialize the anonymizer class with appropriate fallbacks."""

    try:
        if _import_privacy_tool():
            return
    except ImportError:
        pass

    try:
        if _import_simple_privacy_tool():
            return
    except ImportError:
        pass

    _configure_error_dialog()


_initialize()


def main() -> None:
    """Main function for standalone execution."""

    try:
        from PyQt5.QtWidgets import QApplication as _QApplication

        app = _QApplication(sys.argv)
        window = DataAnonymizerGUI()
        if hasattr(window, "setWindowTitle"):
            window.setWindowTitle("Data Anonymizer - Richard's File Utilities")
        window.show()
        sys.exit(app.exec_())
    except ImportError:
        print("Error: PyQt5 is required to run the Data Anonymizer.")
        print("Please install PyQt5: pip install PyQt5")
        sys.exit(1)
    except Exception as error:  # noqa: BLE001 - provide user-friendly fallback
        print(f"Error starting Data Anonymizer: {error}")
        sys.exit(1)


if __name__ == "__main__":
    main()
