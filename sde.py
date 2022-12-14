"""
sde.py

SDE Simulation Classes
Gan Yang ©2022
"""

import math
import numpy as np
from param import Param

class EulerParam(Param):
    """A node of Euler's discretization of an SDE."""

    name = "Euler Param"

    def __init__(self, mu, v, S_t, t, dt, z):
        """
        mu      A lambda describing the diffusion term taking S_t and t
        v       A lambda describing vol term taking S_t and t
        S_t     An Euler param representing value at previous time step
        t       Time index
        dt      A constant param representing step size
        """
        self._mu  = mu
        mu.add_dependents(self)
        self._v   = v
        v.add_dependents(self)
        S_t.add_dependent(self)
        self._S_t = S_t
        self._t   = t
        dt.add_dependent(self)
        self._dt  = dt
        self._z   = z
        self._dependents = []
        self._dirty = True
        self._last = None

    @property
    def z(self):
        return self._z

    @z.setter
    def z(self, z_):
        self._z = z_
        super().make_dirty()

    def eval(self):
        # just return cached value if node is not dirty
        if not self._dirty:
            return self._last
        # if not, calculate using SDE
        S_t = self._S_t.eval()
        dt = self._dt.eval()
        self._last = S_t + self._mu[S_t, self._t] * dt + self._v[S_t, self._t] * math.sqrt(dt) * self._z
        self._dirty = False
        return self._last


class LogEulerParam(EulerParam):
    """A node of Non-negative Euler's discretization of an SDE."""

    name = "Log Euler Param"

    def eval(self):
        # just return cached value if node is not dirty
        if not self._dirty:
            return self._last
        # if not, calculate using SDE
        S_t = self._S_t.eval()
        dt = self._dt.eval()
        self._last = S_t * np.exp(self._mu[S_t, self._t] * dt + self._v[S_t, self._t] * math.sqrt(dt) * self._z)
        self._dirty = False
        return self._last


class StochVolParam(EulerParam):
    """A node of Euler's discretization of stochastic volatility process."""

    name = "Stoch Vol Param"

    def eval(self, cir):
        # just return cached value if node is not dirty
        if not self._dirty:
            return self._last
        # if not, calculate using SDE
        S_t = self._S_t.eval(cir)
        dt = self._dt.eval()
        self._last = S_t + self._mu[S_t, self._t] * dt + self._v[S_t, self._t, cir] * math.sqrt(dt) * self._z
        self._dirty = False
        return self._last


class EulerSimulation:
    """Wrapper for Euler's discretation Monte Carlo Simulation."""

    def __init__(self, mu, v, S_0, T, dt, n_sims, param=EulerParam):
        """
        mu      Lambda function input for Euler Param
        v       Lambda function input for Euler Param
        S_0     Constant param of Initial value
        T       Max time index
        dt      Constant param input for Euler Param
        n_sims  Number of simulations, >= 1
        """
        self._S_0 = S_0
        self._T = T
        self._n = n_sims
        last = S_0
        self.nodes = [last]
        self.Z = np.random.normal(size=[T, n_sims])
        for i in range(T):
            last = param(mu, v, last, i+1, dt, self.Z[i, 0])
            self.nodes.append(last)
        self.results = np.empty([T+1, n_sims])
        self.results[0, :] = S_0.eval()

    def run_all(self):
        for i in range(self._n):
            for j in range(self._T):
                self.nodes[j+1].z = self.Z[j, i]
                self.results[j+1, i] = self.nodes[j+1].eval()

    def run_new(self, n_sims):
        self._n = n_sims
        self.Z = np.random.normal(size=[self._T, n_sims])
        self.run_all()


class StochVolSimulation(EulerSimulation):
    """Wrapper for Euler's discretation Monte Carlo Simulation of a Stoch Vol Model."""

    def __init__(self, mu, v, S_0, cir, T, dt, n_sims, rho=None):
        """
        mu      Lambda function input for Euler Param
        v       Lambda function input for Euler Param
        S_0     Constant param of Initial value
        cir     EulerSimulation of the volatility process
        T       Max time index
        dt      Constant param input for Euler Param
        n_sims  Number of simulations, >= 1
        """
        super().__init__(mu, v, S_0, T, dt, n_sims, param=StochVolParam)
        self._cir = cir
        for i in range(T):
            cir.nodes[i].add_dependent(self.nodes[i+1])
        self.Z_corr = rho * cir.Z + math.sqrt(1 - rho ** 2) * self.Z

    def run_all(self):
        for i in range(self._n):
            for j in range(self._T):
                self.nodes[j+1].z = self.Z_corr[j, i]
                self.results[j+1, i] = self.nodes[j+1].eval(self._cir)

    def run_new(self, n_sims):
        self._n = n_sims
        self.Z = np.random.normal(size=[self._T, n_sims])
        self.run_all()
