#!/usr/bin/env python
import numpy as npy
import matplotlib.pyplot as plt
import rospy
# from std_msgs.msg import String
# import roslib
import sys
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt 
import random
from scipy.stats import rankdata
from matplotlib.pyplot import *
from scipy import signal
import copy

basis_size = 3
discrete_size = 50

#Action size also determines number of convolutional filters. 
action_size = 8
# action_space = [[0,1],[1,0],[0,-1],[-1,0],[1,1],[1,-1],[-1,1],[-1,-1]]

action_space = [[-1,0],[1,0],[0,-1],[0,1],[-1,-1],[-1,1],[1,-1],[1,1]]
############# UP, DOWN, LEFT, RIGHT, UPLEFT, UPRIGHT, DOWNLEFT, DOWNRIGHT........

#Transition space size determines size of convolutional filters. 
transition_space = 3

#Static / instantaneous reward. 
reward_function = npy.loadtxt(str(sys.argv[1]))

time_limit = 50

value_functions = npy.zeros(shape=(time_limit,discrete_size,discrete_size))
value_function = npy.zeros(shape=(discrete_size,discrete_size))

optimal_policy = npy.zeros(shape=(discrete_size,discrete_size))

gamma = 0.95

trans_mat = npy.zeros(shape=(action_size,transition_space,transition_space))

def conv_transition_filters():
	trans_mat_1 = [[0.,0.7,0.],[0.1,0.1,0.1],[0.,0.,0.]]
	trans_mat_2 = [[0.7,0.1,0.],[0.1,0.1,0.],[0.,0.,0.]]
	
	trans_mat[0] = trans_mat_1
	trans_mat[1] = npy.rot90(trans_mat_1,2)
	trans_mat[2] = npy.rot90(trans_mat_1,1)
	trans_mat[3] = npy.rot90(trans_mat_1,3)

	trans_mat[4] = trans_mat_2
	trans_mat[5] = npy.rot90(trans_mat_2,3)	
	trans_mat[7] = npy.rot90(trans_mat_2,2)
	trans_mat[6] = npy.rot90(trans_mat_2,1)

conv_transition_filters()

def conv_layer(time):	
	global value_functions
	action_value_layers = npy.zeros(shape=(action_size,discrete_size,discrete_size))
	layer_value = npy.zeros(shape=(discrete_size,discrete_size))
	for act in range(0,action_size):		
		#Convolve with each transition matrix.
		action_value_layers[act]=signal.convolve2d(value_functions[time,:,:],trans_mat[act],'same','fill',0)
	
	#Max pooling over actions. 
	value_functions[time+1,:,:] = gamma*npy.amax(action_value_layers,axis=0)
	# layer_value = gamma*npy.amax(action_value_layers,axis=0)
	optimal_policy[:,:] = npy.argmax(action_value_layers,axis=0)
	# return layer_value

def reward_bias(time):
	global value_functions
	value_functions[time,:,:] = value_functions[time,:,:] + reward_function[:,:]

def recurrent_value_iteration():
	global value_functions
	t=0	
	while (t<time_limit-1):
		conv_layer(t)
		t+=1
		reward_bias(t)		
		print t
	
recurrent_value_iteration()

for i in range(0,discrete_size):
	print optimal_policy[i]

for i in range(0,discrete_size):
	print reward_function[i]

# policy_iteration()

# print "These are the value functions."
# for t in range(0,time_limit):
# 	print value_functions[t]

with file('output_policy.txt','w') as outfile: 
	outfile.write('#Policy.\n')
	npy.savetxt(outfile,optimal_policy,fmt='%-7.2f')

