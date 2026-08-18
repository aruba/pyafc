# (C) Copyright 2020-2025 Hewlett Packard Enterprise Development LP.
# Apache License 2.0

from functools import wraps

from pyafc.common import exceptions


class Internal:
    @staticmethod
    def afc_connected(function):
        @wraps(function)
        def backend_exec(self, *args, **kwargs):
            if not self.client:
                msg = "Not connected to AFC"
                raise exceptions.AuthenticationIssue(msg)
            return function(self, *args, **kwargs)

        return backend_exec
