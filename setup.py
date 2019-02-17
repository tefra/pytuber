import os

from setuptools import find_packages, setup

here = os.path.abspath(os.path.dirname(__file__))

meta = dict()  # type: dict
with open(os.path.join(here, "pytuber", "version.py"), encoding="utf-8") as f:
    exec(f.read(), meta)

if __name__ == "__main__":
    setup(
        packages=find_packages(),
        version=meta["version"],
        install_requires=[
            "lxml == 4.3.1",
            "click == 7.0",
            "click_completion == 0.5.0",
            "pydrag == 18.1",
            "attrs == 18.2.0",
            "tabulate[widechars] == 0.8.3",
            "yaspin == 0.14.1",
            "google-api-python-client == 1.7.8",
            "google-auth == 1.6.2",
            "google-auth-oauthlib == 0.2.0",
        ],
        extras_require={
            "dev": [
                "pre-commit",
                "pytest",
                "pytest-cov",
                "codecov",
                "tox",
                "Pygments",
                "check-manifest",
            ],
            "docs": [
                "sphinx",
                "sphinx-rtd-theme",
                "sphinxcontrib-programoutput",
            ],
        },
        entry_points={"console_scripts": ["pytuber=pytuber:cli"]},
    )
