
import random as ran 
import math
import copy

class Genome(object):

	def __init__(self,numChromosomes):
		self.chromosomes = [None]*numChromosomes
		pass




class CreatureGenome(Genome):

	def __init__(self,mutationRate,NNWeightsList, NNBiasWeightsList):
		super(CreatureGenome,self).__init__(3) 

		#Neural network weights matric [W1,W2,W3, ...]
		self.chromosomes[0] = NNWeightsList

		self.chromosomes[2] = NNBiasWeightsList

		#Arsenal: [(weaponLen,direction),(...),(...)]
		self.chromosomes[1] = [(20,math.pi/2)]

		self.mutationRate = mutationRate

	def mutateArsenal(self):
		ranNum = ran.randint(1,10)

		numWeapons = len(self.chromosomes[1])
		# add (random) / delete weapon
		if(ranNum < 8): ## 20% chance add/pop
			if(ran.randint(0,2)==1):
				if(numWeapons != 0):	
					self.chromosomes[1].pop(ran.randint(0,numWeapons-1))
			else:
				ranWeaponLen = ran.randint(1,100)
				ranAngle = ran.random()*2*math.pi
				self.chromosomes[1].append((ranWeaponLen,ranAngle))

		#change old weapon
		numWeapons = len(self.chromosomes[1])
		if(ranNum < 4): # 40% chance
			#change this so only goes to some random indexes not all
			for i in range(numWeapons):
				ranNum = ran.randint(1,10)
				if(ranNum<5):
					sign = ran.choice([-1, 1])
					((self.chromosomes[1])[i]) = ((((self.chromosomes[1])[i])[0]*(1+sign*self.mutationRate)), 
						                          ((self.chromosomes[1])[i])[1])
					((self.chromosomes[1])[i]) =  (((self.chromosomes[1])[i])[0]*(1+sign*self.mutationRate),
						                          ((self.chromosomes[1])[i])[1])
	#destrucively mutate neural network weightslist
	def mutateNeuralNetwork(self):

		#each weight matrix in weightsList 
		for w in range(len(self.chromosomes[0])):
			wRows,wCols = len(self.chromosomes[0][w]), len(self.chromosomes[0][w][0])
			maxRows,maxCols = ran.randint(0,wRows-1), ran.randint(0,wCols-1)
			for wRow in range(maxRows): #rows in matrix w
				for wCol in range(maxCols): #cols in matrix w
					sign = ran.choice([-1, 1])
					ranRow = ran.randint(0,wRows-1)
					ranCol = ran.randint(0,wCols-1)
					weightVal = (self.chromosomes[0][w][ranRow][ranCol])
					self.chromosomes[0][w][ranRow][ranCol] = weightVal + sign*self.mutationRate
				sign = ran.choice([-1, 1])
				ranRow = ran.randint(0,wRows-1) 
				biasWeightVal = self.chromosomes[2][w][wRow]
				self.chromosomes[2][w][ranRow] = biasWeightVal + sign*self.mutationRate

	def mutate(self):
		#self.mutateArsenal()
		self.mutateNeuralNetwork()


		
	def crossOverArsenal(self,otherCreature):
		shortestLen = min(len(self.chromosomes[1]),len(otherCreature.genome.chromosomes[1])) 
		childGenome = CreatureGenome(self.mutationRate,self.chromosomes[0],self.chromosomes[2])
		for i in range(shortestLen):
			#50% change to get genes from one parent of the other
			if(bool(ran.getrandbits(1))):
				(childGenome.chromosomes[1]).append((self.chromosomes[1])[i])
			else:
				(childGenome.chromosomes[1]).append((otherCreature.genome.chromosomes[1])[i])
		longestGenome = self if (len(self.chromosomes[1])>len(otherCreature.genome.chromosomes[1])) else otherCreature.genome
		(childGenome.chromosomes[1]).extend((longestGenome.chromosomes[1])[shortestLen:])
		return childGenome.chromosomes[1]

	def crossOverNeuralNetwork(self,otherCreature):
		numLayers = len(self.chromosomes[0])
		childGenome = copy.deepcopy(self)
		w = 0 #weight List index
		for weights in self.chromosomes[0]:
			wRows,wCols = len(weights), len(weights[0])
			maxRows,maxCols = ran.randint(0,wRows-1), ran.randint(0,wCols-1)
			for wRow in range(maxRows):
				for wCol in range(maxCols):
					ranRow = ran.randint(0,wRows-1)
					ranCol = ran.randint(0,wCols-1)
					childGenome.chromosomes[0][w][ranRow][ranCol] = otherCreature.genome.chromosomes[0][w][ranRow][ranCol]
			w += 1
		return childGenome




	def crossOver(self,otherCreature):
		childGenome = self.crossOverNeuralNetwork(otherCreature)
		#childGenome.chromosomes[1] = self.crossOverArsenal(otherCreature)
		return childGenome



# genome = CreatureGenome(.2)

# for t in range(10):

# 	genome.mutateArsenal()
# 	print(genome.chromosomes[1])












#Extra
# Future add color as gene: camo into enviornment 