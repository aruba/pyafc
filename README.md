# pyafc
HPE Aruba Networking PyAFC Modules to work with HPE Aruba Networking Fabric Composer

See the [Release Notes](RELEASE-NOTES.md) for more information.

It is also important to note that the latest code commits on the main branch in Git are usually ahead of the official releases and tags, so please be aware of this when cloning the repo versus doing a `pip install pyafc`

## Structure
Detailed information about the structure and design can be found in the [Design document](pyafc/DESIGN.md).

* REST API call functions are found in the modules in /pyafc/*/.
* REST API call functions are combined into other functions that emulate low-level processes. These low-level process functions are also placed in files in /pyafc/*/.
* Functions from the /pyafc/* files (API functions and low-level functions) are combined to emulate larger network configuration processes (workflows). These workflow scripts stored in the /workflows folder.


## How to contribute

Please see the accompanying [CONTRIBUTING.md](CONTRIBUTING.md) file for guidelines on how to contribute to this repository.

### How to run this code
In order to run the workflow scripts, please complete the steps below:
1. install virtual env (refer https://docs.python.org/3/library/venv.html). Make sure python version 3 is installed in system.

    ```
    $ python3 -m venv py_env
    ```
2. Activate the virtual env
    ```
    $ source py_env/bin/activate
    in Windows:
    $ venv/Scripts/activate.bat
    ```
3. Install the pyafc package
    ```
    (py_env)$ pip install pyafc
    ```
4. Now you can run different workflows from pyafc/workflows (e.g. `create_fabric.py`)
5. Keep in mind that the workflows perform high-level configuration processes; they are highly dependent on the status of HPEANFC prior to running the workflows.

## Troubleshooting Issues
1. If you encounter module import errors, make sure that the package has been installed correctly.

Additionally, please read the RELEASE-NOTES.md file for the current release information and known issues.
