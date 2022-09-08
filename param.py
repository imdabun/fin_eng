"""
param.py

Param Class Implementation
Gan Yang ©2022
"""

class Param:
    """A constant parameter node with no dependencies."""

    name = "Constant Param"

    def __init__(self, value):
        self._val = value
        self._dependents = []
        self._dirty = True

    def add_dependent(self, dependent):
        self._dependents.append(dependent)

    def make_dirty(self):
        self._dirty = True
        for dependent in self._dependents:
            dependent.make_dirty()

    def val(self):
        if self._dirty:
            self._dirty = False
        return self._val
