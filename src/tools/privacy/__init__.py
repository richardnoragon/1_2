"""Richard's File Utilities - Privacy Tools."""

from .anonymizer.data_anonymizer import (
    DataAnonymizerGUI,
)
from .anonymizer.data_anonymizer import main as data_anonymizer_main
from .privacy_cleaner import (
    PRIVACY_CLEANER_TEXT,
    PrivacyCleanerGUI,
)
from .privacy_cleaner import main as privacy_cleaner_main

# Preserve existing import surface while exposing privacy cleaner entries.
main = data_anonymizer_main

__all__ = [
    "DataAnonymizerGUI",
    "PrivacyCleanerGUI",
    "PRIVACY_CLEANER_TEXT",
    "data_anonymizer_main",
    "privacy_cleaner_main",
    "main",
]
