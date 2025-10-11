"""Organize tools for the file management suite.

This package exposes the OrganizeWindow GUI and related helper
structures that power the rule-based organizer workflow.
"""

from .organize import OrganizeRule, OrganizeWindow

__all__ = ["OrganizeWindow", "OrganizeRule"]
