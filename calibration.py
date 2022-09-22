"""
calibration.py

Parameter Calibration Class
Gan Yang ©2022S
"""

from param import Param
from sde import *
from fparam import *
import numpy as np
import math

class Calibration:
    """Calibration Simulation"""

    def __init__(self, params_range, simulation):
