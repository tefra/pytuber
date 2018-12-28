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
            "tinydb == 3.12.2",
            "appdirs == 1.4.3",
            "pydrag == 18.1",
            "attrs == 18.2.0",
            "tabulate == 0.8.2",
            "google-api-python-client == 1.7.6",
            "google-auth == 1.6.1",
            "google-auth-httplib2 == 0.0.3",
            "google-auth-oauthlib == 0.2.0",
        ],
        extras_require={
            "dev": ["pre-commit", "pytest", "pytest-cov", "codecov", "tox"],
            "docs": ["sphinx", "sphinx-rtd-theme", "sphinx-autodoc-typehints"],
        },
        entry_points={"console_scripts": ["pytubefm=pytubefm:cli"]},
    )
