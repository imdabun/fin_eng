"""
calibration.py

Parameter Calibration Class
Gan Yang ©2022
"""

from param import Param
from sde import EulerSimulation
from fparam import FParam

class Calibration:
    """Calibration Simulation"""

    def __init__(self, params_range, simulation):
