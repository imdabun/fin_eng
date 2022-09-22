"""
param.py

Param Class
Gan Yang ©2022
"""

class Param:
    """A constant parameter node with no dependencies."""

    name = "Constant Param"

    def __init__(self, value):
        self._val = value
        self._dependents = []
        self._dirty = True

    @property
    def val(self):
        return self._val

    @val.setter
    def val(self, value):
        self._val = value
        self.make_dirty()

    def add_dependent(self, dependent):
        """Register downstream node that has this as a dependency."""
        self._dependents.append(dependent)

    def make_dirty(self):
        """Turn this node and all downstream nodes dirty."""
        if self._dirty: return
        self._dirty = True
        for dependent in self._dependents:
            dependent.make_dirty()

    def eval(self, *args):
        """Evaluate parameter."""
        self._dirty = False
        return self.val
