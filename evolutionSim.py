import pygame
from arena import Arena
from evolution import Evolution
from gameEvolution import GameEvolution


class Simulation(object):
	def __init__(self,width,height):
		self.width = width
		self.height = height
		self.escL = 5 # escape left
		self.escR = 60 # escape right
		self.escUp = 5 #escape Up
		self.escDown = 40 #escape down 

	def runSimulation(self):

		#pygame initialization
		pygame.init()
		screen = pygame.display.set_mode((self.width, self.height))
		self.screen = screen
		self.pygame = pygame

		#pygame time manager
		clock = pygame.time.Clock()

		#Game loop controller
		done = False

		#Font object for escape button
		self.escapeFont = pygame.font.SysFont('Arial', 20, True, True)

		#Splash screen initialization
		splashScreen = SplashScreen(self.width,self.height,pygame,screen)

		#Mode Initialization
		mode = Mode(self.width, self.height, pygame, screen)

		#info object initialization
		info = Info(pygame, screen, self.width, self.height)
              
		#game control loop
		while not done:
			#update command queue
			eventsList = pygame.event.get()

			#share these events with gameEvoltion for Simulation Player Mode control
			mode.gameMode.gameEvolution.eventsList = eventsList

			#dump + iterate event Queue
			for event in eventsList:
				if event.type == pygame.QUIT:
					done = True

				#quick escape to reset everything and return to splashscreen
				if(event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
					splashScreen.on = True
					mode.reset()

				#splash screen mode on
				if(splashScreen.on):
					#The button you press determined Mode to enter
					if event.type == pygame.MOUSEBUTTONDOWN:
						mode.modeName = splashScreen.processsClick(pygame.mouse.get_pos())
				#when splash screen not on check for escape button
				elif event.type == pygame.MOUSEBUTTONDOWN:
					x,y = pygame.mouse.get_pos()
					if(self.escapePassed(x,y)):
						splashScreen.on = True
						mode.reset()

				#Diplay evolution information
				if(event.type == pygame.KEYDOWN and event.key == pygame.K_i):
					info.on = not info.on

			#Clear screen
			screen.fill((50,50,50)) #gray fill
			#check if the splash screen is not on then run selected game mode
			if(not splashScreen.on):
				mode.updateCurrentMode()
				#info diplay and control
				if(info.on):
					mouseX, mouseY = pygame.mouse.get_pos()
					info.getInfo(mode, mouseX, mouseY)
					info.drawInfo()
				self.drawEscapeButton()
			else:
				splashScreen.drawSplashScreen()

			#game display and delay
			pygame.display.flip()
			clock.tick(80)

	#check if click is in bound of escape button
	def escapePassed(self, x, y):
		return (x>self.escL and x<self.escR and y > self.escUp and y < self.escDown)

	def drawEscapeButton(self):
		self.pygame.draw.rect(self.screen,(50,200,20),self.pygame.Rect(self.escL, self.escUp, 60, 35))
		self.screen.blit(self.escapeFont.render("Escape", True, (0,0,0)),(5, 5))


# controls the program mode to be set
class Mode(object):

	def __init__(self,width,height, pygame, screen):

		self.modeName = "OFFMODE"

		self.pygame = pygame
		self.screen = screen

		self.width = width
		self.height = height

		self.gameMode = GameMode(width, height, self.pygame, self.screen)
		self.simulationMode = SimulationMode(width, height, self.pygame, self.screen)
		self.helpMode = HelpMode(width, height, self.pygame, self.screen)

	def reset(self):

		self.modeName = ""
		self.gameMode = GameMode(self.width, self.height, self.pygame, self.screen)
		self.simulationMode = SimulationMode(self.width,self.height, self.pygame, self.screen)


	def updateCurrentMode(self):

		if(self.modeName == "GameMode"):
			self.gameMode.updateGame()
		elif(self.modeName == "SimulationMode"):
			self.simulationMode.updateSimulation()
		elif(self.modeName == "HelpMode"):
			self.helpMode.drawHelpMode()


class SimulationMode(object):

	def __init__(self, width, height, pygame, screen):

		self.pygame = pygame
		self.screen = screen

		self.width = width
		self.height = height

		arenaRadius = self.height*2/6
		arena = Arena(arenaRadius,self.width-200,self.height,pygame,screen)

		initialPopulationSize = 10
		self.evolutionEra = Evolution(arena,initialPopulationSize,pygame,screen)

	def updateSimulation(self):
		self.evolutionEra.updateEvolution()

class GameMode(object):

	def __init__(self, width, height, pygame, screen):

		self.pygame = pygame
		self.screen = screen

		self.width = width
		self.height = height

		arenaRadius = self.height*2/6
		arena = Arena(arenaRadius,self.width-200,self.height,pygame,screen)

		initialPopulationSize = 10
		self.gameEvolution = GameEvolution(arena, initialPopulationSize, pygame, screen)

	def updateGame(self):

		self.gameEvolution.update()

#controls the help screen
class HelpMode(object):

	def __init__(self,width, height, pygame, screen):
		self.pygame = pygame
		self.screen = screen
		self.width = width
		self.height = height

		self.titleFont = pygame.font.SysFont('Arial', 40, True, True)
		self.infoFont = pygame.font.SysFont('Arial', 15)


	def drawHelpMode(self):
		lineDiff = 20
		initialDiff = 70
		titleXLoc = self.width/2-200
		xLoc = self.width/2-250
		self.screen.blit(self.titleFont.render('Help and Simulation Info', True, (255,255,0)), (titleXLoc,10))
		self.screen.blit(self.infoFont.render('Escape = return to SplashScreen', True, (255,255,0)), (xLoc,initialDiff))
		self.screen.blit(self.infoFont.render('i = evolution information statistics', True, (255,255,0)), (xLoc,initialDiff+lineDiff))
		self.screen.blit(self.infoFont.render('hover mouse = see selected creature life information', True, (255,255,0)), (xLoc,initialDiff+lineDiff*2))
		self.screen.blit(self.infoFont.render('s = save (population to pickle object file)', True, (255,255,0)), (xLoc,initialDiff+lineDiff*3))
		self.screen.blit(self.infoFont.render('l = load (population from pickle object file)', True, (255,255,0)), (xLoc,initialDiff+lineDiff*4))
		self.screen.blit(self.infoFont.render('Mouse Click = kill a creature', True, (255,255,0)), (xLoc,initialDiff+lineDiff*5))
		self.screen.blit(self.infoFont.render('Space + Mouse Click = breed a creature', True, (255,255,0)), (xLoc,initialDiff+lineDiff*6))
		self.screen.blit(self.infoFont.render('f + Mouse Click = place food', True, (255,255,0)), (xLoc,initialDiff+lineDiff*7))
		self.screen.blit(self.infoFont.render('1 = Player Mode (breed your population as an evolution God)', True, (255,255,0)), (xLoc,initialDiff+lineDiff*8))
		self.screen.blit(self.infoFont.render('2 = Bot Mode (watch a random bot breed its own population)', True, (255,255,0)), (xLoc,initialDiff+lineDiff*9))
		self.screen.blit(self.infoFont.render('3 = Tournament Mode (Unleash your population against the bots)', True, (255,255,0)), (xLoc,initialDiff+lineDiff*10))
		self.screen.blit(self.infoFont.render('UP/ DOWN KEY = change mutation rate +/- .05', True, (255,255,0)), (xLoc,initialDiff+lineDiff*11))


#add picttures to splash screen here they wont slow down simulation but still look good
class SplashScreen(object):

	def __init__(self, width, height, pygame, screen):
		self.screen = screen
		self.pygame = pygame
		self.width = width
		self.height = height
		self.on = True
		self.titleFont = pygame.font.SysFont('Arial', 55, True, True)
		self.buttonFont = pygame.font.SysFont('Arial', 25)

		self.buttonWidth = width/2
		self.buttonHeight = height/6
		self.button1X = self.width/2-self.buttonWidth/2
		self.button1Y = self.height/4
		self.button2X = self.width/2-self.buttonWidth/2
		self.button2Y = self.height/4+100
		self.button3X = self.width/2-self.buttonWidth/2
		self.button3Y = self.height/4+200

		self.background = pygame.image.load("NeuralNet2.jpg")

	def drawSplashScreen(self):
		self.screen.fill((50,50,50))
		#button
		self.screen.blit(self.background, (0,0))
		self.screen.blit(self.titleFont.render('Neural Bots Simulator', True, (200,50,5)), (self.width/2-220, self.height/15))
		self.pygame.draw.rect(self.screen,(0,0,0),self.pygame.Rect(self.button1X, self.button1Y, self.buttonWidth, self.buttonHeight))
		self.screen.blit(self.buttonFont.render('Run Evolution Simulator', True, (255,0,0)), (self.width/2-self.buttonWidth/3,
			                                                                            self.button1Y+self.buttonHeight/2-10))
		self.pygame.draw.rect(self.screen,(0,0,0),self.pygame.Rect(self.button2X, self.button2Y, self.buttonWidth, self.buttonHeight))
		self.screen.blit(self.buttonFont.render('Play Evolution Game', True, (255,0,0)), (self.width/2-self.buttonWidth/3,
			                                                                            self.button2Y+self.buttonHeight/2-10))
		self.pygame.draw.rect(self.screen,(0,0,0),self.pygame.Rect(self.button3X, self.button3Y, self.buttonWidth, self.buttonHeight))
		self.screen.blit(self.buttonFont.render('Help', True, (255,0,0)), (self.width/2-20,
			                                                                            self.button3Y+self.buttonHeight/2-10))

	#Return the mode the program should enter if a button is clicked
	def processsClick(self,loc):

		if(loc[0]>self.button1X and loc[0]<(self.button1X+self.buttonWidth) and loc[1]>self.button1Y and loc[1]<(self.button1Y+self.buttonHeight)):
			self.on = False
			return "SimulationMode"
		if(loc[0]>self.button1X and loc[0]<(self.button2X+self.buttonWidth) and loc[1]>self.button1Y and loc[1]<(self.button2Y+self.buttonHeight)):
			self.on = False
			return "GameMode"
		if(loc[0]>self.button1X and loc[0]<(self.button2X+self.buttonWidth) and loc[1]>self.button1Y and loc[1]<(self.button3Y+self.buttonHeight)):
			self.on = False
			return "HelpMode"
		else:
			return "OFFMODE"

class Info(object):

	def __init__(self, pygame, screen, width, height):

		self.titleFont = pygame.font.SysFont('Arial', 30)
		self.screen = screen
		self.pygame = pygame
		self.width = width
		self.height = height

		self.title = "Evolution Information"
		self.infoFont = pygame.font.SysFont('Arial', 18)

		self.on = False
		self.generation = 0
		self.creaturesHealth = []
		self.creaturesSurvivalTime = []
		self.selectedCreature = ""

		self.mutationRate = 0

		#sets all current evolution data
	def getInfo(self, mode, mouseX, mouseY):
		self.creaturesHealth = []
		self.creaturesSurvivalTime = []
		if(mode.modeName == "SimulationMode"):
			evolutionEra = mode.simulationMode.evolutionEra
			self.generation = evolutionEra.generationCount
			for creature in evolutionEra.population:
				self.creaturesHealth.append(creature.health) #load health stats
				self.creaturesSurvivalTime.append(creature.survivalTime) #load survival time stats
				self.mutationRate = creature.mutationRate #load mutation rate
				creature.selected = False
				#look for mouse hovering over a creature for selected creature stats
				if(creature.intersects((mouseX,mouseY))):
					creature.selected = True
					self.selectedCreature = "Health: "+ str(creature.health) + " SurvivalTime: " + str(creature.survivalTime)

		elif(mode.modeName == "GameMode"):
			gameEvolution = mode.gameMode.gameEvolution
			modeIndex = gameEvolution.modeIndex
			self.generation = gameEvolution.generationCount[modeIndex]
			for creature in gameEvolution.populations[modeIndex]:
				self.creaturesHealth.append(creature.health)
				self.creaturesSurvivalTime.append(creature.survivalTime)
				self.mutationRate = creature.mutationRate
				creature.selected = False
				if(creature.intersects((mouseX,mouseY))):
					creature.selected = True
					self.selectedCreature = "Health: "+ str(creature.health) + " SurvivalTime: " + str(creature.survivalTime)

			if(gameEvolution.gameMode == "GameOver"):
				self.on = False
			

	def drawInfo(self):
		self.screen.blit(self.titleFont.render(self.title, True, (255,0,0)), (self.width-240, 40))
		self.screen.blit(self.infoFont.render("Generation: " + str(self.generation), True, (255,0,0)),
																(self.width-200-40, self.height/4))
		self.screen.blit(self.infoFont.render("Population Health", True, (255,0,0)),
																(self.width-200-40, self.height/4+20))
		self.screen.blit(self.infoFont.render(str(self.creaturesHealth), True, (255,0,0)),
																(self.width-200-40, self.height/4+40))
		self.screen.blit(self.infoFont.render("Population survivalTime", True, (255,0,0)),
																(self.width-200-40, self.height/4+60))
		self.screen.blit(self.infoFont.render(str(self.creaturesSurvivalTime), True, (255,0,0)),
																(self.width-200-40, self.height/4+80))
		self.screen.blit(self.infoFont.render("Selected: ", True, (255,0,0)),
																(self.width-200-40, self.height/4+100))
		self.screen.blit(self.infoFont.render(self.selectedCreature, True, (255,0,0)),
																(self.width-200-40, self.height/4+120))
		self.screen.blit(self.infoFont.render("mutationRate: "+str(self.mutationRate), True, (255,0,0)),
																(self.width-200-40, self.height/4+140))
		self.screen.blit(self.infoFont.render("Food: ", True, (255,0,0)),
																(self.width-200-40, self.height/4+180))
		self.pygame.draw.circle(self.screen, (0,255,0), (self.width-180, self.height/4+190), 10)



sim1 = Simulation(600,400)

sim1.runSimulation()