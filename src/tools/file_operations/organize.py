"""Compatibility wrapper for legacy organize tool imports."""

from src.tools.file_management import organizer

__all__ = ["OrganizeWindow", "OrganizeRule", "OrganizeGUI"]

OrganizeWindow = organizer.OrganizeWindow
OrganizeRule = organizer.OrganizeRule

# Maintain historical alias used by older tooling.
OrganizeGUI = OrganizeWindow
