
import math
import random as ran
from vision import Vision
from genome import CreatureGenome
from neuralNetwork import NeuralNetwork

#Creature:
	#Health
	#Eyes: Vision/ incoming image
	#Brain: neuralnetwork

class Creature(object):
	def __init__(self,arena,pygame,screen, mutationRate = .05, creatureType = 0):
		# initial location
		sign = ran.choice([-1,0])
		self.x = int(arena.cx + sign*ran.randint(0,80))
		self.y = int(arena.cy + sign*ran.randint(0,80))
		self.lastX = self.x
		self.lastY = self.y

		self.PLAYER = 0
		self.BOT = 1
		self.type = creatureType
		self.selected = False

		#characteristics
		self.radius = 10
		self.color = (22,250,20)
		self.maxHealth = 7
		self.health = self.maxHealth
		visionRadius = self.radius*6
		resolutionFactor = 20
		self.eyes = Vision(pygame,screen,visionRadius,resolutionFactor) #vision
		self.arsenal = Arsenal(pygame,screen)

		#Neural Network / brain
		#get brain weights from genetic algorithm or from self back prop
		networkShape = ((2*visionRadius/resolutionFactor)**2,(2*visionRadius/resolutionFactor), (visionRadius/resolutionFactor),2)
		self.neuralNetwork = NeuralNetwork(networkShape)
		self.neuralNetwork.buildNetwork()

		#genome
		self.mutationRate = mutationRate
		self.genome = CreatureGenome(mutationRate,self.neuralNetwork.weightsList, self.neuralNetwork.biasWeightsList)
		#print("GENOME TYPE: ", self.genome)

		#State
		self.alive = True
		self.attacking = False

		#Survival time tracking
		self.initialTime = pygame.time.get_ticks()
		self.survivalTime = 0

		#game features
		self.time = pygame.time
		self.lastHealthTime = pygame.time.get_ticks()
		self.pygame = pygame
		self.screen = screen

		self.lastExhaustionTime = pygame.time.get_ticks()
		self.exhaustionTimerAcumulator = 0
		self.exhaustionTimerOn = False

		#enviornment to interact with
		self.arena = arena

		#Creature Img
		self.botImg = pygame.image.load("orangeFaceScaled.jpg").convert_alpha()
		self.creatureImg = pygame.image.load("blueFaceScaled.jpg").convert_alpha()

	def move(self,dx,dy):
		if(self.arenaCollision()):
			self.x = self.lastX
			self.y = self.lastY
			self.health -= 2
		else:
			self.lastX = self.x
			self.lastY = self.y
			self.x += dx
			self.y += dy


	def arenaCollision(self):
		#distance formula
		innerRoot = (self.x-self.arena.cx)**2+(self.y-self.arena.cy)**2
		d = math.sqrt(innerRoot)
		#collision has occured
		return((d+self.radius) >= self.arena.radius)


	def foodCheck(self):
		x = self.x
		y = self.y
		for f in self.arena.foodList:
			fX = f.x #food x
			fY = f.y #food y
			d = math.sqrt((x-fX)**2 + (y-fY)**2)
			if(d <= self.radius + f.radius):
				self.health += 2
				self.arena.foodList.remove(f)

				#print("HEALTH: ",self.health)

	def poisonCheck(self):
		x = self.x
		y = self.y
		for p in self.arena.poisonList:
			pX = p.x #food x
			pY = p.y #food y
			d = math.sqrt((x-pX)**2 + (y-pY)**2)
			if(d <= self.radius + p.radius):
				self.health -= 1
				self.arena.poisonList.remove(p)

				#print("HEALTH: ",self.health)

	def intersects(self,pos):
		distance = ((self.x-pos[0])**2+(self.y-pos[1])**2)**.5
		return distance < self.radius

	def updateHealth(self,time):
		currentTime = self.time.get_ticks()

		self.survivalTime = (currentTime - self.initialTime)/1000

		starveTime = 2000
		if((currentTime-self.lastHealthTime) > starveTime):
			self.lastHealthTime = currentTime
			self.health -= 2

		# #fighting exaustion: every .5 second of fighting reduces health 
		# exhaustionTime = 5000
		# if(self.attacking == True):
		# 	if(self.exhaustionTimerOn):
		# 		addedExhaustTime = currentTime - self.lastExhaustionTime
		# 		self.exhaustionTimerAcumulator += addedExhaustTime
		# 		self.lastExhaustionTime = currentTime
		# 	else:
		# 		self.exhaustionTimerOn = True
		# else:
		# 	self.exhaustionTimerOn = False
		# if(self.exhaustionTimerAcumulator>=exhaustionTime):
		# 	self.health -= 1
		# 	self.exhaustionTimerAcumulator = 0

		if(self.health <= 0):
			self.health = 0
			self.alive = False #should be false debuging
		#print(self.health)
		colorFactor = self.health if self.health<=self.maxHealth else self.maxHealth

		if(self.type == self.PLAYER): 
			self.color = (int(255*(colorFactor/float(self.maxHealth))), 20, 20)
		else:
			self.color = (int(255*(colorFactor/float(self.maxHealth))), int(255*(colorFactor/float(self.maxHealth))), 20)


	#called by evolution class
	def evolutionaryUpdate(self):
		#if evolution cycle time update arsenal
		#self.arsenal.arsenalList = self.genome.chromosomes[1]

		self.neuralNetwork.weightsList = self.genome.chromosomes[0]
		self.neuralNetwork.biasWeightsList = self.genome.chromosomes[2]

	def updateControl(self):
		pygame = self.pygame

		# movement
		diff = 10
		dx = 0
		dy = 0
		pressed = pygame.key.get_pressed()
		if pressed[pygame.K_UP]: dy = -diff
		if pressed[pygame.K_DOWN]: dy = diff
		if pressed[pygame.K_LEFT]: dx = -diff
		if pressed[pygame.K_RIGHT]: dx = diff

		#fighting
		if pressed[pygame.K_f]:
			self.attacking = True
		else:
			self.attacking = False

		return (dx,dy)

	def updateNeuralNetworkControl(self):
		# movement
		diff = 20
		dx = 0
		dy = 0
		linearInputView = self.eyes.processView(self.x,self.y)
		#print("linearInputVision: ", linearInputView)
		decisionArr = self.neuralNetwork.propagate(linearInputView)

		#decimal control
		dx = int(decisionArr[0]*diff)
		dy = int(decisionArr[1]*diff)

		return (dx,dy)


	def updateCreature(self):
		if(self.alive):
			#dx,dy = self.updateControl()
			dx,dy = self.updateNeuralNetworkControl()
			self.foodCheck()
			#self.poisonCheck()
			self.updateHealth(self.time)
			self.move(dx,dy)
		else:
			self.color = (0,0,0)

    #----------------------------------------------------------------------------------------
	#-----------------------------------------VIEW-------------------------------------------
    #----------------------------------------------------------------------------------------
	def drawHealthBar(self):
		self.pygame.draw.rect(self.screen,(255,0,0),self.pygame.Rect(self.x-self.health*self.radius/2, 
			                        self.y+self.radius, self.health*self.radius, 2*self.radius))

	def drawCreature(self):
		#self.drawHealthBar()
		#print(self.color)
		if(self.selected):
			self.pygame.draw.circle(self.screen, (50,70,255), (self.x, self.y), self.radius)
		else:
			self.pygame.draw.circle(self.screen, self.color, (self.x, self.y), self.radius+5)
			if(self.type == self.PLAYER):
				self.screen.blit(self.creatureImg, (self.x-self.radius,self.y-self.radius))
			else:
				self.screen.blit(self.botImg, (self.x-self.radius,self.y-self.radius))
		# if(self.attacking):
		# 	self.arsenal.drawArsenal(self.x,self.y,self.radius)



class Arsenal(object):
	def __init__(self,pygame,screen):
		self.pygame = pygame
		self.screen = screen
		#pistons
		self.arsenalList = []#[(40,math.pi/3),(20,math.pi),(40,math.pi*2/3)] #list of tuples weapon (length, angle from East)
		self.color = (255,0,0) # red
			
	def drawArsenal(self,x,y,creatureRadius):
		for weapon in self.arsenalList:
			weaponLen = weapon[0]
			angle = weapon[1]
			startX = x + creatureRadius*math.cos(angle)
			startY = y - creatureRadius*math.sin(angle) #graphics yaxis opposite
			endX = startX + weaponLen*math.cos(angle)
			endY = startY - weaponLen*math.sin(angle)
			self.pygame.draw.line(self.screen,self.color,(startX,startY),(endX,endY),5)
