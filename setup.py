from pathlib import Path

from setuptools import setup, find_packages

readme = Path("README.md").read_text(encoding="utf-8")
version = Path("morpher/_version.py").read_text(encoding="utf-8")
about = {}
exec(version, about)

setup(
    name="morpher",
    version=about["__version__"],
    description="Transform your JSON (or any other dict) using simple DSL",
    long_description=readme,
    long_description_content_type="text/markdown",
    url="https://github.com/cheyuriy/morpher",
    author="cheyuriy",
    author_email="crsmithdev@gmail.com",
    license="Apache 2.0",
    packages=find_packages(),
    zip_safe=False,
    python_requires=">=3.6",
    install_requires=[
        "jsonpath-ng",
        "arrow"
    ],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    keywords="json transform dict"
)