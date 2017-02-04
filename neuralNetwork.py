
#code is mine all originally built but I learned about Neural networks from here
#https://www.youtube.com/watch?v=aVId8KMsdUU&list=PL29C61214F2146796
#https://www.youtube.com/watch?v=Oe-qmOYr8cY&list=PLRyu4ecIE9ti5wsokn1j_ZJU7a7N5hREf
#https://www.youtube.com/watch?v=Ku7D-F6xOUM&list=PLRyu4ecIE9tibdzuhJr94uQeKnOFkkbq6#t=149.473191


#code is mine all originally built but I learned about Genetics algorithms from here
#https://blog.abhranil.net/2015/03/03/training-neural-networks-with-genetic-algorithms/
#https://visualstudiomagazine.com/articles/2014/03/01/code-an-evolutionary-optimization-solution.aspx


import numpy as np
import math
import random as ran
import copy

class NeuralNetwork(object):
	def __init__(self,networkShape):

		self.networkShape = networkShape
		self.networkLen = len(networkShape)


		self.weightsList = [None]*(self.networkLen-1)
		self.biasWeightsList = [None]*(self.networkLen-1)
	
	def buildNetwork(self):

		for i in range(1, self.networkLen):# start at 1 b/c input has no connections
			weightsMatrix = []
			for j in range(self.networkShape[i]):# each neuron in current layer
				sign = ran.choice([-1, 1])
				weightsMatrix.append([sign*ran.random()/20]*self.networkShape[i-1]) # append connections to prev layer
			self.weightsList[i-1] = copy.deepcopy(weightsMatrix)
		for i in range(self.networkLen-1):
			biasWeightVector = []
			for j in range(self.networkShape[i]):
				sign = ran.choice([-1, 1])
				biasWeightVector.append(sign*ran.random()/10)
			self.biasWeightsList[i] = copy.deepcopy(biasWeightVector)

	@staticmethod
	def sigmoid(x):
		return 1 / (1 + math.exp(-x))

	def propagate(self,inputLayer):

		output = inputLayer
		#traverse all layers of neural network
		layerIndex = 0
		for weights in self.weightsList:
			output = np.dot(weights,output)
			for e in range(len(output)):
				#add bias weight
				output[e] = output[e] + self.biasWeightsList[layerIndex][e]
				output[e] = math.tanh(output[e]) 
			layerIndex += 1
		#Use this for boolean control
		# for o in range(len(output)):
		# 	output[o] = (output[o] >= 0)
		return output
