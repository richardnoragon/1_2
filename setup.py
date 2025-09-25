#!/usr/bin/env python
"""
Setup script for Richard's File Utilities (RFU)

A comprehensive PyQt5-based file management suite with cross-platform
virtual environment support.
"""

import os
import sys
from pathlib import Path

from setuptools import find_packages, setup

# Ensure we're using the virtual environment if available
venv_path = Path(__file__).parent / "venv"
if venv_path.exists():
    # Add venv to path for development
    if sys.platform == "win32":
        venv_bin = venv_path / "Scripts"
    else:
        venv_bin = venv_path / "bin"
    
    if venv_bin.exists() and str(venv_bin) not in os.environ.get("PATH", ""):
        current_path = os.environ.get("PATH", "")
        os.environ["PATH"] = str(venv_bin) + os.pathsep + current_path

# Read long description from README
readme_path = Path(__file__).parent / "README.md"
if readme_path.exists():
    with open(readme_path, "r", encoding="utf-8") as fh:
        long_description = fh.read()
else:
    long_description = "A comprehensive PyQt5-based file management suite"

# Read requirements from requirements.txt
requirements_path = Path(__file__).parent / "requirements.txt"
install_requires = []
if requirements_path.exists():
    with open(requirements_path, "r", encoding="utf-8") as fh:
        install_requires = [
            line.strip()
            for line in fh
            if line.strip() and not line.startswith("#")
        ]

setup(
    name="richards-file-utilities",
    version="1.0.0",
    author="Richard Noragon",
    author_email="richardnoragon@example.com",
    description="A comprehensive PyQt5-based file management suite",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/richardnoragon/1_2",
    project_urls={
        "Bug Tracker": "https://github.com/richardnoragon/1_2/issues",
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Topic :: Desktop Environment :: File Managers",
        "Topic :: Utilities",
    ],
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    python_requires=">=3.9",
    install_requires=install_requires,
    extras_require={
        "dev": [
            "black",
            "flake8",
            "mypy",
            "pytest",
            "pytest-cov",
            "pytest-qt",
            "pytest-xvfb",
        ],
        "test": [
            "pytest",
            "pytest-asyncio",
            "pytest-cov",
            "pytest-qt",
            "pytest-randomly",
            "pytest-timeout",
            "pytest-xvfb",
            "coverage",
        ],
    },
    entry_points={
        "console_scripts": [
            "rfu=src.rfu.main:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)