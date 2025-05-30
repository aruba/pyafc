from setuptools import setup
from setuptools import find_packages

from os import path

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="pyafc",
    version="1.0.1",
    description="AFC Python Modules",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/aruba/pyafc",
    author="Aruba Automation",
    author_email="aruba-automation@hpe.com",
    license="Apache 2.0",
    python_requires=">=3.6",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: System Administrators",
        "Topic :: System :: Networking",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3 :: Only",
    ],
    keywords="networking aruba fabric composer rest api python",
    packages=find_packages(exclude=["docs"]),
    install_requires=[
        "requests",
        "PyYAML",
        "netaddr",
        "requests_toolbelt",
        "wheel",
        "pydantic==1.10.12",
        "httpx"
    ],
    zip_safe=False,
)
