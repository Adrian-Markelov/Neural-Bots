from __future__ import print_function
from creature import Creature


import pygame
import random as ran
import copy

	#--Cycle--
	#Get initial population
	#Run simulation
	#	As creatures die turn into food 
	#	At time interval 
	#		-Evolution: evaluate species: give rankings 
	#		-Evolution: select species (gaus distribution)
	#		-Creature: breed species
	#		-Creature: mutate species


class Evolution(object):

	def __init__(self, arena,initialPopulationSize,pygame,screen):
		self.pygame = pygame
		self.screen = screen
		self.arena = arena
		#self.population = [Creature(arena,pygame,screen)]*initialPopulationSize
		self.population = []
		for c in range(initialPopulationSize):
			self.population.append(Creature(arena,pygame,screen))
		#print("population: ", self.population)
		self.sortedPopIndexes = []

		#time
		self.selectionCycleTime = 2000
		self.lastEvoTime = pygame.time.get_ticks()

		self.generationCount = 0

		self.maxPopulation = 12
		self.minPopulation = 6


	def updateEvolution(self):
		self.arena.updateArena()
		self.arena.drawArena()
		for creature in self.population:
			#creature.drawCreature() # put drawing here before update to let creatures see each other/self
			creature.updateCreature()
			if(not creature.alive):
				self.population.remove(creature)
		for creature in self.population:
			creature.drawCreature()

		#ready for evalutation cycle
		currentEvoTime = self.pygame.time.get_ticks()
		if((currentEvoTime-self.lastEvoTime)>=self.selectionCycleTime):
			print("population size: ",len(self.population))
			self.generationCount += 1
			print("Generation: ", self.generationCount)
			self.evaluate()
			self.evolutionarySelection()
			for creature in self.population:
				creature.evolutionaryUpdate()
			self.lastEvoTime = currentEvoTime
		#DONT DIE OUT
		if (len(self.population)<self.minPopulation):
			newCopyCreature = Creature(self.arena,self.pygame,self.screen)
			newCopyCreature.genome = copy.deepcopy(self.population[0].genome)
			self.population.append(newCopyCreature)
			#print("COPY CREATURE ADDED added")




	#originally written but inspired by CMU 15-112 merge sort
	def sortPopulation(self):
		def merge(left,right):
			sL = []
			lenLeft = len(left)
			lenRight = len(right)
			lI = 0 #left index
			rI = 0 #right index
			while((lI<lenLeft) or (rI<lenRight)):

				#sorted by survival time or health + HEALTH
				if((rI==lenRight) or (lI<lenLeft) and 
						((left[lI].survivalTime + left[lI].health) >= (right[rI].survivalTime + right[rI].health))):
					sL.append((left[lI]))
					lI += 1
				else:
					sL.append((right[rI]))
					rI += 1
			return sL

		def mergeSort(L):

			if(len(L)<2):
				return L
			else:
				middle = len(L)/2
				left = mergeSort(L[:middle])
				right = mergeSort(L[middle:])
				return merge(left,right)

		self.population = mergeSort(self.population)

	def evaluate(self):
		self.sortPopulation()
		for e in self.population:
			print(e.survivalTime + e.health,",", end="")
		print("\n")



	def evolutionarySelection(self):
		probalilityConstant = .6
		mutationProb = .7
		for i in range(len(self.population)):
			#mutation of all creatures
			if(ran.random() < mutationProb):
				self.population[i].genome.mutate()

			if(len(self.population) >self.maxPopulation):
				self.population.pop()

			probability =  probalilityConstant*((1-probalilityConstant)**(i)) #P = k(1-k)^rank 
			if(ran.random() < probability):
				#breeding
				if((i+1)<len(self.population)):
					childCreatureGenome = copy.deepcopy(self.population[i].genome.crossOver(self.population[i+1]))
					#print("childCreature", childCreatureGenome)
					childCreature = Creature(self.arena,self.pygame,self.screen)
					childCreature.genome = childCreatureGenome
					self.population.append(childCreature)
					#print("child Creature added")

		#select distributed best species for breeding
		#death does not occur here
		#but selection should be limited to max carrying capacity


#evolution = Evolution()



