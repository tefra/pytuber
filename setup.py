import os

from setuptools import find_packages, setup

here = os.path.abspath(os.path.dirname(__file__))

meta = dict()  # type: dict
with open(os.path.join(here, "pytubefm", "version.py"), encoding="utf-8") as f:
    exec(f.read(), meta)

if __name__ == "__main__":
    setup(
        packages=find_packages(),
        version=meta["version"],
        install_requires=[
            "click == 7.0",
            "pydrag == 18.1",
            "attrs == 18.2.0",
            "tabulate == 0.8.2",
            "yaspin == 0.14.0",
            "google-api-python-client == 1.7.7",
            "google-auth == 1.6.2",
            "google-auth-oauthlib == 0.2.0",
        ],
        extras_require={
            "dev": ["pre-commit", "pytest", "pytest-cov", "codecov", "tox"],
            "docs": ["sphinx", "sphinx-rtd-theme", "sphinx-autodoc-typehints"],
        },
        entry_points={"console_scripts": ["pytubefm=pytubefm:cli"]},
    )
