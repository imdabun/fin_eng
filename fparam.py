"""
fparam.py

FParam Wrapper
Gan Yang ©2022
"""

class FParam:
    """Wrapper for parameter-determined functions."""

    def __init__(self, f, params):
        self._f = f
        self._params = params

    def add_dependents(self, dependent):
        """Any parameter dependent on this function is dependent on all its parameters/"""
        for p in self._params.values():
            p.add_dependent(dependent)

    def __getitem__(self, args):
        return self._f(*args, params=self._params)
