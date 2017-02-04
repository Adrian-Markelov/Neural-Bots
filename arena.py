
import random as ran


class Arena(object):
	def __init__(self,radius,width,height, pygame,screen):

		self.radius = radius
		self.width = width
		self.height = height
		self.cx = width/2
		self.cy = height/2
		self.color = (255,255,255)
		self.foodList = []
		self.poisonList = []

		self.screen = screen
		self.pygame = pygame

		self.spawnTime = 2500

		#time
		self.time = pygame.time
		self.lastTime = pygame.time.get_ticks()


	def itemSpawner(self, time):

		currentTime = time.get_ticks()
		spawnTime = self.spawnTime

		if((currentTime-self.lastTime) > spawnTime):
			self.lastTime = currentTime
			amountFood = len(self.foodList)
            #food rots 
            # 10 % chance food rots (random piece of food)
			if(amountFood != 0 and ran.randint(1,3) == 1): 
				self.foodList.pop(ran.randint(0,amountFood-1)) # fuck you randint for having upper inclusive
			else:
				x = ran.randint(self.width/2-self.radius/2,self.width/2+self.radius/2)
				y = ran.randint(self.height/2-self.radius/2,self.height/2+self.radius/2)
				newFood = Food(x,y)
				self.foodList.append(newFood)


			amountPoison = len(self.poisonList)
            #food rots 
            # 10 % chance poison rots (random piece of poison)
			if(amountPoison != 0 and ran.randint(1,3) == 1): 
				self.poisonList.pop(ran.randint(0,amountPoison-1))
			else:
				x = ran.randint(self.width/2-self.radius,self.width/2+self.radius)
				y = ran.randint(self.height/2-self.radius,self.height/2+self.radius)
				newPoison = Poison(x,y)
				self.poisonList.append(newPoison)
	def addFood(self, pos):
		newFood = Food(pos[0],pos[1])
		self.foodList.append(newFood)

	def updateArena(self):
		self.itemSpawner(self.time)
		maxFoodSize = 50
		if(len(self.foodList)>maxFoodSize):
			self.foodList.pop()



	def drawArena(self):
		self.pygame.draw.circle(self.screen, self.color,(self.cx,self.cy),self.radius)
		for f in self.foodList:
			f.drawFood(self.pygame,self.screen)
		# for p in self.poisonList:
		# 	p.drawPoison(self.pygame,self.screen)

class Food(object):

	def __init__(self,x,y):
		self.radius = 10
		self.color = (40,255,40)
		self.x  = x
		self.y = y

	def drawFood(self,pygame,screen):
		pygame.draw.circle(screen, self.color,(self.x,self.y),self.radius)


class Poison(object):

	def __init__(self,x,y):
		self.radius = 10
		self.color = (75,0,130)
		self.x  = x
		self.y = y

	def drawPoison(self,pygame,screen):
		pygame.draw.circle(screen, self.color,(self.x,self.y),self.radius)
