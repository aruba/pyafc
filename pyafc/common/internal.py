# (C) Copyright 2020-2025 Hewlett Packard Enterprise Development LP.
# Apache License 2.0

import sys
from functools import wraps


class Internal:
    def afc_connected(function):
        @wraps(function)
        def backend_exec(self, *args, **kwargs):
            if self.client:
                function(*args, **kwargs)
            else:
                sys.exit(0)

        return backend_exec
