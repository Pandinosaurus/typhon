"""Minimal setup.py shim supplying the dynamic version to setuptools.

All package metadata lives in pyproject.toml. This file only computes the
version (mirroring typhon.__init__.py's VERSION-file read, with a
git-describe fallback for dev builds) and passes it to setup(), which
setuptools accepts because ``version`` is declared as dynamic.
"""
import logging
import subprocess
from codecs import open
from os.path import dirname, join

from setuptools import setup


version = open(join(dirname(__file__), "typhon", "VERSION")).read().strip()

if "dev" in version:
    try:
        cp = subprocess.run(
            ["git", "describe", "--tags"], stdout=subprocess.PIPE, check=True
        )
    except subprocess.CalledProcessError:
        logging.warning(
            "Warning: could not determine version from git, "
            "using version from source"
        )
    else:
        version = (
            cp.stdout.strip()
            .decode("ascii")
            .lstrip("v")
            .replace("-", "+dev", 1)
            .replace("-", ".")
        )

setup(version=version)
