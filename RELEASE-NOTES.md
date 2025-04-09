# v1.0.0

### Overview
This release introduces significant updates, including new features, enhancements, and bug fixes to the Ansible collection `afc`. Below is a detailed summary of the changes.

---

### General Changes
- Updated copyright year across all files.

---

### Enhancements and Features

#### `pyafc/afc/afc.py`
- Added support for type annotations using `from __future__ import annotations`.
- Introduced `licenses.License` as a base class for `Afc`.
- Enhanced connection logic with improved timeout handling and response validation.
- Refactored `connect` and `connect_async` methods for better readability.
- Updated docstrings with detailed examples for better clarity.

#### `pyafc/afc/backups.py`
- Improved docstrings for `create_backup` and `create_scheduled_backup` methods with detailed examples.
- Enhanced validation and error handling for backup creation workflows.

#### `pyafc/afc/models.py`
- Added root validators to handle type conversions and ensure data consistency.
- Improved type hints for model attributes.

#### `pyafc/common/utils.py`
- Added utility methods for handling switch UUIDs and IP ranges.
- Enhanced `remove_null_from_dict` for better performance.
- Updated `response_ok` to include additional HTTP status codes (e.g., 207).

#### `pyafc/dss/dss.py`
- Improved type hints and docstrings for DSS-related methods.
- Enhanced error handling for invalid policy types and timeframes.

#### `pyafc/dss/endpoint_groups.py`
- Added detailed docstrings for `create_eg` and `delete_eg` methods.
- Improved validation for endpoint group creation workflows.

#### `pyafc/dss/policies.py`
- Enhanced `create_policy` and `delete_policy` methods with better validation and error handling.
- Improved support for enforcer and rule management.

#### `pyafc/dss/rules.py`
- Improved `create_rule` and `delete_rule` methods with better validation for endpoint groups, qualifiers, and applications.

#### `pyafc/fabric/fabric.py`
- Added support for managing multiple devices in a fabric with enhanced validation.
- Improved methods for creating and deleting fabrics with better error handling.
- Enhanced support for adding single and multiple devices to a fabric.

#### `pyafc/fabric/evpn.py`
- Improved EVPN creation and deletion workflows with better validation and error handling.
- Enhanced support for multisite EVPN configurations.

#### `pyafc/fabric/leaf_spine.py`
- Added support for creating and reapplying L3 Leaf-Spine configurations.
- Improved workflows for subleaf configurations.

---

### Bug Fixes
- Fixed issues with response validation in HTTP requests.
- Resolved inconsistencies in type hints and docstrings across modules.
- Addressed edge cases in switch and fabric management workflows.

---

### Breaking Changes
- Some methods now require stricter type annotations, which may affect backward compatibility.
- Updated method signatures for several classes to improve clarity and maintainability.

---

### Documentation
- Improved docstrings across all modules for better clarity and usage examples.
- Added detailed examples for key methods in the Ansible collection.

---

### Miscellaneous
- General code cleanup and refactoring for better readability and maintainability.
- Added `# noqa` comments to suppress specific linting warnings where necessary.

---

### Notes