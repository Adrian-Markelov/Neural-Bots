import cv2
import cv2.cv as cv
import numpy as np



class Vision(object):

	def __init__(self,pygame,screen,r,resolutionFactor):
		self.r = r
		self.pygame = pygame
		self.screen = screen
		self.viewImg = []
		self.grayImg = []
		self.resolutionFactor = resolutionFactor

	@staticmethod
	def RGB2GRAY(img):
		return np.dot(img[...,:3],[0.299, 0.587, 0.114])


	def getFieldImage(self):

		newSurface = self.screen.subsurface(self.pygame.Rect(0, 0, 400, 400))

		newSurface = self.pygame.transform.rotate(newSurface,90)
		newSurface = self.pygame.transform.flip(newSurface,False,True)

		#lowResSurface = self.pygame.transform.smoothscale(newSurface, (100, 100))

		arr = self.pygame.surfarray.array3d(newSurface)
		#print(arr)
		#grayimg = Vision.RGB2GRAY(arr)
		arr = cv2.cvtColor(arr, cv2.COLOR_BGR2RGB) #actually doing rever rgb-brg for ocv
		#cv2.imshow("simulation",arr)
		return arr

	#instead of cutting out field image it might be better to get area first
	def getIsolatedView(self,x,y):
		r = self.r
		arenaImg = self.getFieldImage()
		imgWidth = len(arenaImg[0])
		imgHeight = len(arenaImg)
		#open cv image different then pygame directions need to convert
		if((y-r)>0 and (y+r)<imgHeight and (x-r)>0 and (x+r)<imgWidth):
			self.viewImg = arenaImg[(y-r):(y+r),(x-r):(x+r)]

		#cv2.imshow("view",self.viewImg)

	def processView(self,x,y):

		self.getIsolatedView(x,y)
		smallImg = cv2.resize(self.viewImg, (0,0), fx=(1.0/self.resolutionFactor), fy=(1.0/self.resolutionFactor))
		grayImg = cv2.cvtColor(smallImg,cv2.COLOR_BGR2GRAY)
		rescale = cv2.resize(grayImg, (0,0), fx=(self.resolutionFactor), fy=(self.resolutionFactor))
		#cv2.imshow("grayImg",rescale)

		linearGrayImg = []

		for pixRow in range(0,len(grayImg)):
			for pixCol in range(0,len(grayImg[0])):
				linearGrayImg.append(grayImg[pixRow][pixCol])
		return linearGrayImg

