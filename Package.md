AFC Python SDK
=========

Below steps are only needed until the pyafc package is published.

Create and install the package in the environment
------------

Clone the git repository
```bash
$ git clone git@github.hpe.com:GSE/ArubaAFC-python.git
```

Install the required python packages through pip
```bash
$ cd ArubaAFC-python/
$ pip install -r requirements.txt
```

Install build package and build the pyafc package
```bash
$ pip install build
$ python3 -m build
```

Install the pyafc package using whl file available under dist folder
```bash
$ pip install dist/pyafc-1.0.0-py3-none-any.whl
```
