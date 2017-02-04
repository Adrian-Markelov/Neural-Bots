from __future__ import print_function
from creature import Creature


import pygame
import random as ran
import copy
import pickle


class GameEvolution(object):

	def __init__(self, arena,initialPopulationSize,pygame,screen):

		#game setup elements
		self.pygame = pygame
		self.screen = screen
		self.arena = arena
		self.modeFont = self.pygame.font.SysFont('Arial', 20)

		#game over
		self.gameOverFont = self.pygame.font.SysFont('Arial', 45, True)
		self.winner = ""

		self.eventsList = []

		#Mode control
		self.gameMode = "PlayerMode"

		self.savedBotsPath = 'SuperBots.pkl'
		self.genomeList = []

		#mutation Difference: for simulated Annealing
		self.mutationDiff = 0

		#initial Given population
		self.playerPopulation = []
		self.botPopulation = []
		self.populations = [self.playerPopulation, self.botPopulation]
		self.superBotsPopulation = []

		self.PLAYER = 0
		self.BOT = 1
		self.modeIndex = self.PLAYER

		for c in range(initialPopulationSize):
			#ADD COLOR CODER TO EACH CREATURE RED AND YELLOW
			self.populations[self.PLAYER].append(Creature(arena,pygame,screen, creatureType = self.PLAYER))
			self.populations[self.BOT].append(Creature(arena,pygame,screen, creatureType = self.BOT))

		#container for population evaluation
		self.sortedPopIndexes = []

		#Evolution time characteristics
		self.selectionCycleTime = 2000
		self.lastEvoTime = pygame.time.get_ticks()
		self.playerGenCount = 0
		self.botGenCount = 0
		self.generationCount = [self.playerGenCount, self.botGenCount]
		self.lastBotUpdateTime = pygame.time.get_ticks()

		#Evolution and Population characteristics
		self.maxPopulation = 12
		self.minPopulation = 6

		#images
		self.gameOverImg = pygame.image.load("bacteria.jpg")


#Mode selection
# press 1 for Player mode
# press 2 for bot mode
# press 3 for Tournament Mode

	def modeSelection(self):
		#print("event: ", self.pygame.event.get())
		for event in self.eventsList:
			if(event.type == self.pygame.KEYDOWN and event.key == self.pygame.K_1):
				self.gameMode = "PlayerMode"
			elif(event.type == self.pygame.KEYDOWN and event.key == self.pygame.K_2):
				self.gameMode = "BotMode"
			elif(event.type == self.pygame.KEYDOWN and event.key == self.pygame.K_3):
				for creature in self.populations[self.BOT]:
					creature.health = 5 #normalize health for fair play
				for i in range(abs(len(self.populations[self.BOT]) - len(self.populations[self.PLAYER]))):
					self.populations[self.BOT].pop()
				self.arena.spawnTime = 1000
				self.gameMode = "TournamentMode"
			

	#This is the main cycle control for the game which check what to do based on the current mode
	def update(self):
		self.modeSelection()
		if(self.gameMode != "GameOver"):
			if(self.gameMode == "PlayerMode"):
				self.updatePlayerInput()
				self.updateEvolution()

			elif(self.gameMode == "BotMode"):
				self.updateEvolution()
				self.updateBotInput()

			elif(self.gameMode == "TournamentMode"):
				#in this mode there is no evolution just survival
				self.runTournament()

			elif(self.gameMode == "SuperBots"):
				self.arena.spawnTime = 300
				self.runSuperBots()
			self.drawMode()
		else:
			self.drawGameOver()

	def updatePlayerInput(self):

		# go through pygame.events and make changes
		for event in self.eventsList:
			if event.type == pygame.MOUSEBUTTONDOWN:
				pos = pygame.mouse.get_pos()
				pressed = pygame.key.get_pressed()
				#place food on arena
				if(pressed[pygame.K_f]):
					self.arena.addFood(pos)
				for creature in self.populations[self.modeIndex]:
					#breed selected creature 
					if(creature.intersects(pos)):
						if (pressed[pygame.K_SPACE]):
							copyCreature = Creature(self.arena,self.pygame,self.screen, creatureType = self.modeIndex)
							copyCreature.genome.chromosomes = copy.deepcopy(creature.genome.chromosomes)
							self.populations[self.modeIndex].append(copyCreature)
						else:
							self.populations[self.modeIndex].remove(creature)
			#save current bots
			if(event.type == pygame.KEYDOWN and event.key == pygame.K_s):
				self.pickleSaveSuperBots()
			#SuperBots Game Mode
			if(event.type == pygame.KEYDOWN and event.key == pygame.K_l):
				self.gameMode = "SuperBots"
				self.pickleLoadSuperBots()
			#change mutation rate
			if(event.type == pygame.KEYDOWN and event.key == pygame.K_UP):
				self.mutationDiff += .05
				for creature in self.populations[self.modeIndex]:
					creature.mutationRate += self.mutationDiff
			if(event.type == pygame.KEYDOWN and event.key == pygame.K_DOWN):
				self.mutationDiff -= .05
				for creature in self.populations[self.modeIndex]:
					creature.mutationRate += self.mutationDiff
			self.eventsList.remove(event) #clear event queue

	#save a population to a file: note code insired by pickle docs
	def pickleSaveSuperBots(self):
		for creature in self.populations[self.PLAYER]:
			self.genomeList.append(creature.genome)
		with open(self.savedBotsPath, 'wb') as output:
			pickle.dump(self.genomeList, output, pickle.HIGHEST_PROTOCOL)

			#load population from a file: note code inpired from pickle docs
	def pickleLoadSuperBots(self):
		genomeList = []
		with open(self.savedBotsPath, 'rb') as input:
			genomeList = pickle.load(input)

		#load the saved genomes to newly creature creatures
		for genome in genomeList:
			creature = Creature(self.arena,self.pygame,self.screen, creatureType = self.modeIndex)
			creature.genome = genome
			creature.neuralNetwork.weightsList = genome.chromosomes[0]
			creature.neuralNetwork.biasWeightsList = genome.chromosomes[2]
			creature.health = 50 # set high health for a longer game
			self.superBotsPopulation.append(creature)

			#alternative save method for saving bots genome as string
	def convertPopulation2String(self, population):
		populationString = ""
		for creature in population:
			# print(creature.genome.chromosomes[0])
			populationString += ",".join(str(gene) for gene in creature.genome.chromosomes[0]) # weights
			populationString += ",b"
			populationString += ",".join(str(gene) for gene in creature.genome.chromosomes[2]) # Bias weights
			populationString += "\n"
		return populationString

			#alternative save method for saving bots genome as string
	def convertString2Population(self, populationString):
		population = []
		for line in populationString.splitlines():
			creature = Creature(self.arena,self.pygame,self.screen, creatureType = self.modeIndex)
			weightsList = []
			biasWeightsList = []
			for weight in line.split(","):
				if(weight == "b"):
					line = line[line.find('b')+1:]
					break
				else:
					weightsList.append(float(weight))
			for biasWeight in line.split(","):
				biasWeightsList.append(float(biasWeight))
			creature.genome.chromosomes[0] = copy.copy(weightsList)
			creature.genome.chromosomes[2] = copy.copy(biasWeightsList)
			population.append(creature)
		return population




	#runs demo of saved bots with no evolution 
	def runSuperBots(self):
		self.arena.updateArena()
		self.arena.drawArena()
		for creature in self.superBotsPopulation:
			creature.updateCreature()
			if(not creature.alive):
				self.superBotsPopulation.remove(creature)

				#seperate drawing from creature
		for creature in self.superBotsPopulation:
			creature.drawCreature()


	def updateBotInput(self):
		botCycleTime = 300
		currentTime = pygame.time.get_ticks()

		if((currentTime-self.lastBotUpdateTime)> botCycleTime):
			#randomly kill a creature
			#ranCreature = ran.randint(0, len(self.populations[self.modeIndex])-1)
			self.populations[self.modeIndex].pop(0)

			#randomly breed a creature
			ranCreature = ran.randint(0, len(self.populations[self.modeIndex])-1)
			copyCreature = Creature(self.arena,self.pygame,self.screen, creatureType = self.modeIndex)
			copyCreature.genome.chromosomes = copy.deepcopy(self.populations[self.modeIndex][ranCreature].genome.chromosomes)
			self.populations[self.modeIndex].append(copyCreature)

			#randomly add food
			x = ran.randint(self.arena.width/2-self.arena.radius/2,self.arena.width/2+self.arena.radius/2)
			y = ran.randint(self.arena.height/2-self.arena.radius/2,self.arena.height/2+self.arena.radius/2)
			self.arena.addFood((x,y))

			self.lastBotUpdateTime = currentTime



	def runTournament(self):
		self.arena.updateArena()
		self.arena.drawArena()
		for creature in self.populations[self.PLAYER]:
			creature.updateCreature()
			if(not creature.alive):
				self.populations[self.PLAYER].remove(creature)
		for creature in self.populations[self.BOT]:
			creature.updateCreature()
			if(not creature.alive):
				self.populations[self.BOT].remove(creature)

		#seperate drawing from creature
		for creature in self.populations[self.PLAYER]:
			creature.drawCreature()		
		for creature in self.populations[self.BOT]:
			creature.drawCreature()

		if(len(self.populations[self.PLAYER]) == 0):
			self.gameMode = "GameOver"
			self.winner = "BOT"
			# print("PLAYER LOST BOT WON")
		elif(len(self.populations[self.BOT]) == 0):
			self.gameMode = "GameOver"
			self.winner = "PLAYER"
			# print("BOT LOST PLAYER WON")

 	#Here the evolutionary cycle is managed
 		#doesnt let species die out
 		#updates creatures run cycle
 		#evaluates population
 		#calls breed and mutation routines

	def updateEvolution(self):

		if(self.gameMode == "PlayerMode"):
			self.modeIndex = self.PLAYER
		elif(self.gameMode == "BotMode"):
			self.modeIndex = self.BOT

		self.arena.updateArena()
		self.arena.drawArena()
		for creature in self.populations[self.modeIndex]:
			creature.updateCreature()
			if(not creature.alive):
				self.populations[self.modeIndex].remove(creature)
		for creature in self.populations[self.modeIndex]:
			creature.drawCreature()

		#ready for evalutation cycle
		currentEvoTime = self.pygame.time.get_ticks()
		if((currentEvoTime-self.lastEvoTime)>=self.selectionCycleTime):
			#print("population size: ",len(self.populations[self.modeIndex]))
			self.generationCount[self.modeIndex] += 1
			#print("Generation: ", self.generationCount)
			self.evaluate()
			self.evolutionarySelection()
			for creature in self.populations[self.modeIndex]:
				creature.evolutionaryUpdate()
			self.lastEvoTime = currentEvoTime

		#Dont let population die out by refilling with the strongest
		if (len(self.populations[self.modeIndex])<self.minPopulation):
			newCopyCreature = Creature(self.arena,self.pygame,self.screen, creatureType = self.modeIndex)
			newCopyCreature.genome = copy.deepcopy(self.populations[self.modeIndex][0].genome)
			self.populations[self.modeIndex].append(newCopyCreature)
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

				if((rI==lenRight) or (lI<lenLeft) and 
					((left[lI].survivalTime + left[lI].health) >= (right[rI].survivalTime + right[rI].health))):
					sL.append(left[lI])
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

		self.populations[self.modeIndex] = mergeSort(self.populations[self.modeIndex])

	def evaluate(self):
		self.sortPopulation()
		#for e in self.populations[self.modeIndex]:
			#print(e.survivalTime + e.health,",", end="")
		#print("\n")


# mutate and breed creatures through a distributed selection process
	def evolutionarySelection(self):
		probalilityConstant = .6
		mutationProb = .7
		for i in range(len(self.populations[self.modeIndex])):

			#mutation of all creatures
			if(ran.random() < mutationProb):
				self.populations[self.modeIndex][i].genome.mutate()

			#Population threshold execeeded weakest creatures die
			if(len(self.populations[self.modeIndex]) > self.maxPopulation):
				self.populations[self.modeIndex].pop() 

			# distributed selections and breeding for new generation of children creatures
			probability =  probalilityConstant*((1-probalilityConstant)**(i)) #P = k(1-k)^rank
			if(ran.random() < probability):
				#If there is an ajacent creature let them breed
				if((i+1)<len(self.populations[self.modeIndex])):
					childCreatureGenome = copy.deepcopy(self.populations[self.modeIndex][i].genome.crossOver(self.populations[self.modeIndex][i+1]))
					childCreature = Creature(self.arena,self.pygame,self.screen, creatureType = self.modeIndex)
					childCreature.genome = childCreatureGenome
					self.populations[self.modeIndex].append(childCreature)



	def drawMode(self):
		self.screen.blit(self.modeFont.render("Mode: " + self.gameMode, True, (255,0,0)), (10, 40))

	def drawGameOver(self):
		self.screen.blit(self.gameOverImg, (-25,-25))
		self.screen.blit(self.gameOverFont.render("GAME OVER", True, (200,20,0)), (self.arena.cx, self.arena.cy-140))
		self.screen.blit(self.gameOverFont.render("WINNER: " + self.winner, True, (200,20,0)), ((self.arena.cx, self.arena.cy-100)))
		self.screen.blit(self.gameOverFont.render("Press Escape", True, (200,20,0)), ((self.arena.cx, self.arena.cy-60)))

