"""RFU Tool Launch Validation and Coverage Framework."""

from __future__ import annotations

import ast
import importlib
import inspect
import json
import logging
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import (
    Any,
    Dict,
    Iterable,
    List,
    Optional,
    Sequence,
    Tuple,
    Type,
    cast,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

HUB_FILE = SRC_ROOT / "tabbed_hub.py"
DEFAULT_LATENCY_BUDGET_MS = 1500
ISO_TIMESTAMP_FORMAT = "%Y-%m-%dT%H:%M:%SZ"
FILE_OPERATIONS_LABEL = "File Operations"
NO_STRATEGY_MSG = "No viable instantiation strategy found"

CATEGORY_KEYWORDS: Dict[str, str] = {
    "pdf": "PDF Tools",
    "duplicate": "Analysis",
    "analysis": "Analysis",
    "network": "Network",
    "bandwidth": "Network",
    "port": "Network",
    "encryption": "Security",
    "encrypt": "Security",
    "security": "Security",
    "hash": "Security",
    "password": "Security",
    "file": FILE_OPERATIONS_LABEL,
    "catalog": FILE_OPERATIONS_LABEL,
    "touch": FILE_OPERATIONS_LABEL,
    "split": FILE_OPERATIONS_LABEL,
    "compress": FILE_OPERATIONS_LABEL,
    "system": "System",
    "process": "System",
    "service": "System",
    "registry": "System",
    "clipboard": "System",
    "disk": "System",
    "metadata": "Metadata",
    "image": "Metadata",
    "office": "Metadata",
}


def _utc_timestamp() -> str:
    return time.strftime(ISO_TIMESTAMP_FORMAT, time.gmtime())


def _write_json(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    serialized = json.dumps(payload, indent=2)
    path.write_text(serialized, encoding="utf-8")


@dataclass
class ToolImportTarget:
    module: str
    name: Optional[str] = None
    optional: bool = False


@dataclass
class ToolLaunchRecord:
    tool_name: str
    method_name: str
    friendly_name: str
    category: str
    dispatch_key: str
    import_targets: List[ToolImportTarget] = field(default_factory=list)
    import_status: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    diagnostics: Dict[str, Any] = field(default_factory=dict)
    latency_budget_ms: int = DEFAULT_LATENCY_BUDGET_MS

    def add_error(self, message: str) -> None:
        if message not in self.errors:
            self.errors.append(message)

    def add_warning(self, message: str) -> None:
        if message not in self.warnings:
            self.warnings.append(message)

    @property
    def status(self) -> str:
        if self.errors:
            return "failed"
        if self.warnings:
            return "degraded"
        return "ok"


class TabbedHubInventory:
    def __init__(
        self,
        hub_path: Optional[Path] = None,
        logger: Optional[logging.Logger] = None,
    ) -> None:
        self.hub_path = hub_path or HUB_FILE
        self.logger = logger or logging.getLogger("TabbedHubInventory")
        self._tree: Optional[ast.Module] = None
        self._module_cache: Dict[str, Tuple[bool, Optional[str]]] = {}
        self._records_cache: Optional[List[ToolLaunchRecord]] = None

    def _load_tree(self) -> ast.Module:
        if self._tree is None:
            source = self.hub_path.read_text(encoding="utf-8")
            self._tree = ast.parse(source, filename=str(self.hub_path))
        return self._tree

    def _iter_tool_functions(self) -> Iterable[ast.FunctionDef]:
        tree = self._load_tree()
        for node in tree.body:
            if not isinstance(node, ast.FunctionDef):
                continue
            if not node.name.startswith("open_"):
                continue
            yield node

    def _method_to_tool_name(self, method_name: str) -> str:
        tool_key = method_name[len("open_") :]
        return tool_key.replace("_", " ").title()

    def _guess_category(self, tool_name: str) -> str:
        name_lower = tool_name.lower()
        for keyword, category in CATEGORY_KEYWORDS.items():
            if keyword in name_lower:
                return category
        return "General"

    def _dispatch_key(self, tool_name: str) -> str:
        return tool_name.lower().replace(" ", "_")

    def _resolve_relative(
        self,
        module: Optional[str],
        level: int,
    ) -> List[str]:
        base_parts = ["src", "tabbed_hub"]
        if level:
            base_parts = base_parts[:-level]
        base_module = ".".join(base_parts) if base_parts else ""
        module = module or ""
        candidates: List[str] = []
        pieces = [p for p in module.split(".") if p]
        if base_module:
            composed = ".".join(part for part in (base_module, *pieces) if part)
            if composed:
                candidates.append(composed)
        composed_alt = ".".join(part for part in ("src", *pieces) if part)
        if composed_alt and composed_alt not in candidates:
            candidates.append(composed_alt)
        if module and module not in candidates:
            candidates.append(module)
        return candidates or [module]

    def _collect_import_targets(
        self,
        func: ast.FunctionDef,
    ) -> List[ToolImportTarget]:
        targets: List[ToolImportTarget] = []
        for node in ast.walk(func):
            if isinstance(node, ast.ImportFrom):
                candidate_modules = self._resolve_relative(
                    node.module,
                    node.level,
                )
                for alias in node.names:
                    optional = alias.asname == "_" or alias.name.endswith("Optional")
                    for candidate in candidate_modules:
                        targets.append(
                            ToolImportTarget(
                                module=candidate,
                                name=alias.name,
                                optional=optional,
                            )
                        )
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    targets.append(
                        ToolImportTarget(
                            module=alias.name,
                            name=None,
                            optional=False,
                        )
                    )
        return targets

    def _attempt_import(self, module: str) -> Tuple[bool, Optional[str]]:
        if module in self._module_cache:
            return self._module_cache[module]
        try:
            importlib.import_module(module)
        except ImportError as exc:  # pragma: no cover
            self._module_cache[module] = (
                False,
                f"{type(exc).__name__}: {exc}",
            )
        else:
            self._module_cache[module] = (True, None)
        return self._module_cache[module]

    def _validate_import_targets(self, record: ToolLaunchRecord) -> None:
        for target in record.import_targets:
            self._validate_import_target(record, target)

    def _validate_import_target(
        self,
        record: ToolLaunchRecord,
        target: ToolImportTarget,
    ) -> None:
        ok, error = self._attempt_import(target.module)
        status = {
            "module": target.module,
            "name": target.name or "*",
            "optional": target.optional,
            "ok": ok,
        }
        if not ok:
            status["error"] = error or "unknown import error"
            self._handle_import_failure(record, target)
        else:
            if target.name:
                module_obj = sys.modules.get(target.module)
                if module_obj and not hasattr(module_obj, target.name):
                    status["ok"] = False
                    error_msg = self._missing_attribute_message(target)
                    status["error"] = error_msg
                    record.add_error(error_msg)
        record.import_status[target.module] = status

    def _handle_import_failure(
        self,
        record: ToolLaunchRecord,
        target: ToolImportTarget,
    ) -> None:
        if target.optional:
            record.add_warning(f"Optional dependency missing: {target.module}")
        else:
            record.add_error(f"Import failed: {target.module}")

    def _missing_attribute_message(self, target: ToolImportTarget) -> str:
        detail = f"Class {target.name}"
        return f"{detail} not exposed by {target.module}"

    def collect_records(self, refresh: bool = False) -> List[ToolLaunchRecord]:
        if self._records_cache is not None and not refresh:
            return list(self._records_cache)

        records: List[ToolLaunchRecord] = []
        for func in self._iter_tool_functions():
            method_name = func.name
            tool_name = self._method_to_tool_name(method_name)
            record = ToolLaunchRecord(
                tool_name=tool_name,
                method_name=method_name,
                friendly_name=tool_name,
                category=self._guess_category(tool_name),
                dispatch_key=self._dispatch_key(tool_name),
            )

            targets = self._collect_import_targets(func)
            if targets:
                record.import_targets.extend(targets)
                self._validate_import_targets(record)
            else:
                record.add_warning(
                    "Launcher does not import a tool class; likely tab toggle"
                )

            record.diagnostics["loc"] = getattr(func, "lineno", None)
            record.diagnostics["end_loc"] = getattr(func, "end_lineno", None)
            records.append(record)

        self._records_cache = records
        return list(records)

    def build_coverage_matrix(
        self,
        records: Optional[Sequence[ToolLaunchRecord]] = None,
    ) -> Dict[str, Any]:
        records = list(records or self.collect_records())
        summary = {
            "total_tools": len(records),
            "failed": sum(1 for rec in records if rec.status == "failed"),
            "degraded": sum(1 for rec in records if rec.status == "degraded"),
            "ok": sum(1 for rec in records if rec.status == "ok"),
        }
        categories: Dict[str, int] = {}
        for rec in records:
            categories.setdefault(rec.category, 0)
            categories[rec.category] += 1

        return {
            "generated_at": _utc_timestamp(),
            "summary": summary,
            "categories": categories,
            "records": [self._record_to_dict(rec) for rec in records],
        }

    def export_coverage_matrix(
        self,
        output_path: Path,
        matrix: Optional[Dict[str, Any]] = None,
        records: Optional[Sequence[ToolLaunchRecord]] = None,
    ) -> Dict[str, Any]:
        matrix = matrix or self.build_coverage_matrix(records=records)
        _write_json(output_path, matrix)
        return matrix

    def generate_accessibility_profile(
        self,
        output_path: Optional[Path] = None,
        records: Optional[Sequence[ToolLaunchRecord]] = None,
    ) -> Dict[str, Any]:
        records = list(records or self.collect_records())
        profile_records: List[Dict[str, Any]] = []
        score_total = 0
        for rec in records:
            base_score = 100
            penalty = 0
            if rec.warnings:
                penalty += 10
            if rec.errors:
                penalty += 25
            if not rec.import_targets:
                penalty += 5
            score = max(0, base_score - penalty)
            score_total += score
            profile_records.append(
                {
                    "tool_name": rec.tool_name,
                    "category": rec.category,
                    "score": score,
                    "warnings": rec.warnings,
                    "errors": rec.errors,
                }
            )

        average_score = score_total / max(1, len(profile_records))
        payload = {
            "generated_at": _utc_timestamp(),
            "average_score": round(average_score, 2),
            "records": profile_records,
        }

        if output_path:
            _write_json(output_path, payload)
        return payload

    def generate_ui_regression_manifest(
        self,
        output_path: Optional[Path] = None,
        records: Optional[Sequence[ToolLaunchRecord]] = None,
    ) -> Dict[str, Any]:
        records = list(records or self.collect_records())
        manifest: List[Dict[str, Any]] = []
        for rec in records:
            manifest.append(
                {
                    "tool_name": rec.tool_name,
                    "friendly_name": rec.friendly_name,
                    "category": rec.category,
                    "status": rec.status,
                    "latency_budget_ms": rec.latency_budget_ms,
                    "dispatch_key": rec.dispatch_key,
                    "needs_manual_review": bool(rec.errors),
                }
            )
        payload = {
            "generated_at": _utc_timestamp(),
            "entries": manifest,
        }
        if output_path:
            _write_json(output_path, payload)
        return payload

    def build_dashboard_payload(
        self,
        coverage: Dict[str, Any],
        accessibility: Dict[str, Any],
        ui_manifest: Dict[str, Any],
        output_path: Optional[Path] = None,
    ) -> Dict[str, Any]:
        payload = {
            "generated_at": _utc_timestamp(),
            "coverage": coverage,
            "accessibility": accessibility,
            "ui_manifest": ui_manifest,
            "recommendations": self._calculate_recommendations(
                coverage,
                accessibility,
            ),
        }
        if output_path:
            _write_json(output_path, payload)
        return payload

    def _calculate_recommendations(
        self,
        coverage: Dict[str, Any],
        accessibility: Dict[str, Any],
    ) -> List[str]:
        recommendations: List[str] = []
        failed = coverage["summary"].get("failed", 0)
        degraded = coverage["summary"].get("degraded", 0)
        avg_score = accessibility.get("average_score", 0)
        if failed:
            message = (
                f"{failed} launchers failed import validation – "
                "address dependencies."
            )
            recommendations.append(message)
        if degraded and not failed:
            message = (
                f"{degraded} launchers rely on optional dependencies – "
                "plan remediation."
            )
            recommendations.append(message)
        if avg_score < 85:
            recommendations.append(
                "Accessibility heuristics below target – escalate to UX QA."
            )
        if not recommendations:
            recommendations.append("All launchers passed automated validation checks.")
        return recommendations

    def _record_to_dict(self, record: ToolLaunchRecord) -> Dict[str, Any]:
        return {
            "tool_name": record.tool_name,
            "method_name": record.method_name,
            "friendly_name": record.friendly_name,
            "category": record.category,
            "dispatch_key": record.dispatch_key,
            "status": record.status,
            "warnings": record.warnings,
            "errors": record.errors,
            "imports": list(record.import_status.values()),
            "diagnostics": record.diagnostics,
            "latency_budget_ms": record.latency_budget_ms,
        }


class ToolLaunchValidator:
    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger or logging.getLogger("ToolLaunchValidator")
        self.validation_cache: Dict[str, Dict[str, Any]] = {}

    def validate_tool_launch(
        self,
        tool_class: Type,
        tool_name: str,
        parent_widget: Any = None,
    ) -> Dict[str, Any]:
        cache_key = f"{tool_class.__module__}.{tool_class.__name__}" f"::{tool_name}"
        if cache_key in self.validation_cache:
            return dict(self.validation_cache[cache_key])

        result: Dict[str, Any] = {
            "valid": False,
            "constructor": {},
            "strategy": None,
            "recommended_params": {},
            "errors": [],
            "warnings": [],
        }

        try:
            constructor = self._analyze_constructor(tool_class, tool_name)
            result["constructor"] = constructor
            strategy = self._select_strategy(constructor, parent_widget)
            if strategy is None:
                result["errors"].append(NO_STRATEGY_MSG)
            else:
                result["strategy"] = strategy
                result["recommended_params"] = strategy["params"]
                result["valid"] = True
        except (
            TypeError,
            ValueError,
            AttributeError,
        ) as exc:  # pragma: no cover
            message = f"Validation error for {tool_name}: {exc}"
            self.logger.exception(message)
            result["errors"].append(message)

        self.validation_cache[cache_key] = dict(result)
        return dict(result)

    def _analyze_constructor(
        self,
        tool_class: Type,
        tool_name: str,
    ) -> Dict[str, Any]:
        info: Dict[str, Any] = {
            "parameters": [],
            "accepts_parent": False,
            "accepts_title": False,
            "accepts_window_type": False,
            "required": [],
            "optional": [],
            "signature": "",
            "tool_name": tool_name,
        }
        signature = inspect.signature(tool_class.__init__)
        info["signature"] = str(signature)
        for name, param in signature.parameters.items():
            if name == "self":
                continue
            has_default = param.default is not inspect.Parameter.empty
            info["parameters"].append(
                {
                    "name": name,
                    "annotation": getattr(param, "annotation", None),
                    "has_default": has_default,
                }
            )
            if name == "parent":
                info["accepts_parent"] = True
            if name == "title":
                info["accepts_title"] = True
            if name == "window_type":
                info["accepts_window_type"] = True
            target_list = info["optional"] if has_default else info["required"]
            target_list.append(name)
        return info

    def _select_strategy(
        self,
        constructor: Dict[str, Any],
        parent_widget: Any,
    ) -> Optional[Dict[str, Any]]:
        strategies: List[Dict[str, Any]] = [
            {
                "id": "parent",
                "params": {"parent": parent_widget},
                "requirements": ["accepts_parent"],
            },
            {
                "id": "full",
                "params": {
                    "parent": parent_widget,
                    "title": f"{constructor['tool_name']} - RFU Explorer",
                    "window_type": "utility",
                },
                "requirements": ["accepts_parent"],
            },
            {
                "id": "title",
                "params": {
                    "title": f"{constructor['tool_name']} - RFU Explorer",
                },
                "requirements": ["accepts_title"],
            },
            {
                "id": "window_type",
                "params": {"window_type": "utility"},
                "requirements": ["accepts_window_type"],
            },
            {
                "id": "default",
                "params": {},
                "requirements": [],
            },
        ]
        for strategy in strategies:
            if not self._requirements_met(strategy, constructor):
                continue
            raw_params = cast(Dict[str, Any], strategy.get("params", {}))
            params = self._filter_params(dict(raw_params), constructor)
            if self._covers_required(params, constructor):
                prepared = dict(strategy)
                prepared["params"] = params
                return prepared
        return None

    def _requirements_met(
        self,
        strategy: Dict[str, Any],
        constructor: Dict[str, Any],
    ) -> bool:
        required_flags = (
            constructor.get(requirement, False)
            for requirement in strategy["requirements"]
        )
        return all(required_flags)

    def _filter_params(
        self,
        params: Dict[str, Any],
        constructor: Dict[str, Any],
    ) -> Dict[str, Any]:
        available = {entry["name"] for entry in constructor["parameters"]}
        return {key: value for key, value in params.items() if key in available}

    def _covers_required(
        self,
        params: Dict[str, Any],
        constructor: Dict[str, Any],
    ) -> bool:
        missing = set(constructor["required"]) - set(params.keys())
        return not missing

    def create_validated_instance(
        self,
        tool_class: Type,
        tool_name: str,
        parent_widget: Any = None,
    ) -> Any:
        validation = self.validate_tool_launch(
            tool_class,
            tool_name,
            parent_widget,
        )
        if not validation["valid"]:
            self.logger.error(
                "Validation failed for %s: %s",
                tool_name,
                "; ".join(validation["errors"]),
            )
            return None
        strategy = validation.get("strategy")
        params = validation.get("recommended_params", {}) if strategy else {}
        instance = tool_class(**params)
        self._post_configure(instance, tool_name, parent_widget)
        return instance

    def _post_configure(
        self,
        instance: Any,
        tool_name: str,
        parent_widget: Any,
    ) -> None:
        if parent_widget and hasattr(instance, "setParent"):
            try:
                instance.setParent(parent_widget)
            except (TypeError, RuntimeError):  # pragma: no cover
                self.logger.debug(
                    "Parent assignment skipped for %s",
                    tool_name,
                )
        if hasattr(instance, "setWindowTitle") and not instance.windowTitle():
            instance.setWindowTitle(f"{tool_name} - RFU Explorer")


def get_tool_validator() -> ToolLaunchValidator:
    instance = getattr(get_tool_validator, "_instance", None)
    if instance is None:
        instance = ToolLaunchValidator()
        setattr(get_tool_validator, "_instance", instance)
    return cast(ToolLaunchValidator, instance)
