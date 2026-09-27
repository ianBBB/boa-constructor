from __future__ import annotations

from pathlib import Path
from setuptools import find_packages, setup

ROOT = Path(__file__).parent.resolve()

# Install top-level modules (legacy Boa layout keeps many modules at repo root).
EXCLUDED_MODULES = {"setup"}
py_modules = sorted(
    p.stem
    for p in ROOT.glob("*.py")
    if p.stem not in EXCLUDED_MODULES
)

setup(
    packages=find_packages(exclude=("TestArea", "TestArea.*")),
    py_modules=py_modules,
    include_package_data=True,
    package_data={
        "": [
            "*.cfg",
            "*.rc.cfg",
            "*.txt",
            "*.htb",
            "*.jpg",
            "*.jpeg",
            "*.png",
            "*.gif",
            "*.ico",
            "*.xrc",
            "*.xml",
            "*.html",
            "*.css",
            "*.js",
            "*.po",
            "*.mo",
        ]
    },
    zip_safe=False,
)
