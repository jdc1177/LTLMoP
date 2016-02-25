#!/usr/bin/env python

import numpy as np

class SystemDynamics():
	"""
	Specifies dynamics-depedent methods for a specific system
	"""

	def __init__(self, dimConfigSpace, dimStateSpace, dimInputSpace):
		
        self.numConfig = dimConfigSpace
        self.numState = dimStateSpace
        self.numState = dimInputSpace

        self.uLim = np.array([np.inf] * dimInputSpace)

    def state2SEconfig(self, x):
    	"""
    	Transforms a state vector to an SE(2) configuration (x,y translations plus rotation)
    	"""

        y = np.identity(self.numConfig+1)*x[:self.numConfig+1]

        return y

    def SEconfig2state(self, y):
    	"""
    	Transforms SE(2) configuration vector to a state vector
    	"""

        x = np.array([0]*self.numState)
        x[:self.numConfig+1] = np.identity(self.numConfig+1)*y

        return x

class Holonomic(SystemDynamics):
	"""
	Specifies dynamics-depedent methods for a holonomic-drive robot
	"""
	def __init__(self):
		SystemDynamics.__init__(self,2,2,2)

    def state2SEconfig(self, x):
    	"""
    	Transforms a state vector to an SE(2) configuration (x,y translations plus rotation)
    	"""
    	
    	y = SystemDynamics.state2SEconfig(self,x)
    	y[2] = 0

        return y

    def SEconfig2state(self, y):
    	"""
    	Transforms SE(2) configuration vector to a state vector
    	"""

        x = SystemDynamics.SEconfig2state(self, y)
        
        return x

    def command2robotInput(self, x, u):

    	z = state2SEconfig(x)

        u_local = u*[
        	[np.cos(-z[2]), -np.sin(-z[2])],
        	[np.sin(-z[2]), np.cos(-z[2])]]
        vx = u_local[0]
        vy = u_local[1]
        w = u[2]

    	return vx, vy, w

class Unicycle(SystemDynamics):
	"""
	Specifies dynamics-depedent methods for a unicycle
	"""
	def __init__(self):
		SystemDynamics.__init__(self,2,3,2)

		# The following sets the +/- limits for the input command
		self.uLim = np.array([np.inf, 10])

    def state2SEconfig(self, x):
    	"""
    	Transforms a state vector to an SE(2) configuration (x,y translations plus rotation)
    	"""

        y = SystemDynamics.state2SEconfig(self,x)

        return y

    def SEconfig2state(self, y):
    	"""
    	Transforms SE(2) configuration vector to a state vector
    	"""

        x = SystemDynamics.SEconfig2state(self, y)

        return x

    def command2robotInput(self, x, u):

    	vx = u[0]
    	vy = 0.
    	w = max(min([u[1]], self.uLim[1]), -self.uLim[1])

    	return vx, vy, w

if __name__ == "__main__":
	# cmd-line argument checking, etc.
	SystemDynamics()
