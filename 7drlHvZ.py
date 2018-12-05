import libtcodpy as libtcod
import random
import time
import _thread
import threading
import math
SCREEN_WIDTH = 91
SCREEN_HEIGHT = 61
MAP_WIDTH = 261
MAP_HEIGHT = 261
MMX = 81
MMY = 1
MAX_ROOMS = 20
ROOM_MIN_SIZE = 5
ROOM_MAX_SIZE = 20
PRETTY = False
left = [0, 2, 3, 6, 1, 0, 9, 4, 7, 8]
right = [0, 4, 1, 2, 7, 0, 3, 8, 9, 6]
forward = [(0,0,0),(-1,1,71),(0,1,50),(1,1,71),(-1,0,50),(0,0,0),(1,0,50),(-1,-1,71),(0,-1,50),(1,-1,71)]
reverse = [[7, 4, 1], [8, 5, 2], [9, 6, 3]]
global player, goal, winCount

color_cement = libtcod.Color(204, 204, 204)
color_grass = libtcod.Color(30, 150, 0)
color_brick = libtcod.Color(154, 51, 0)
color_stone = libtcod.Color(132, 132, 132)
color_asphalt = libtcod.Color(20, 20, 20)
color_floor = libtcod.Color(204, 204, 255)
color_traffic = libtcod.Color(200, 200, 0)

class Tile:
	#a tile of the map and its properties
	def __init__(self, color, visionBlock, moveChange, fallDanger, blocked):
		self.color = color
		self.visionBlock = visionBlock
		self.moveChange = moveChange
		self.fallDanger = fallDanger
		self.blocked = blocked

	def changeTile(self, color, visionBlock, moveChange, fallDanger, blocked):
		self.color = color
		self.visionBlock = visionBlock
		self.moveChange = moveChange
		self.fallDanger = fallDanger
		self.blocked = blocked

	def getDanger(self):
		return self.fallDanger

class Object:
	#A Thing
	#Its always represented by a character
	def __init__(self, x, y, char, color):
		self.x = x
		self.y = y
		self.char = char
		self.color = color
		self.init = 0
		self.facing = 3
		self.vision = 3
		self.velocity = 0
		self.runInit = 0

	def makeAlive(self, stamina, speed, acc, tech):
		self.stamina = stamina
		self.speed = speed
		self.acc = acc
		self.tech = tech
		self.endurance = stamina*200

	def move(self, dx, dy):
		#move by the given amount
		if (self.x + dx) < size and (self.y + dy) < size and (self.x + dx) >= 0 and (self.y + dy) >= 0:
			if not map[self.x + dx][self.y + dy].blocked:
				crash = False
				for object in zombies:
					if object.x == self.x + dx and object.y == self.y + dy:
						crash = True
						break
				if player.x == self.x + dx and player.y == self.y + dy:
					crash = True
				if not crash:
					self.x += dx
					self.y += dy
					return True
			return False
	def run(self):
		if self.move(forward[self.facing][0],forward[self.facing][1]):
			self.runInit = (forward[self.facing][2]*5)//(self.velocity*self.speed)
			self.endurance -= self.velocity-((self.stamina-1)//5)
			if self.endurance <= (self.velocity-1)*200:
				self.velocity -= 1
		else:
			self.velocity = 0
			self.endurance -= 50
			self.runInit = 1
	def draw(self, x, y):
		#set the color and then draw the character that represents the object at its location
		libtcod.console_set_default_foreground(con, self.color)
		libtcod.console_put_char(con, x, y, self.char, libtcod.BKGND_NONE)
	def clear(self, x, y):
		#erase the character that represents this object
		libtcod.console_put_char(con, x, y, ' ', libtcod.BKGND_NONE)
	def decrement(self):
		self.init -= 1
	def recharge(self):
		self.endurance = self.stamina*150

class Zombie(Object):
	def __init__(self, x, y, char, color):
		self.x = x
		self.y = y
		self.char = char
		self.color = color
		self.init = 0
		self.facing = 3
		self.vision = 3
		self.spawnTime = 0
		self.velocity = 0
		self.runInit = 0

	def decrement(self):
		self.init -= 1
		if self.spawnTime > 0:
			self.spawnTime -= 1
			if self.spawnTime == 0:
				self.char = 'Z'
				self.color = libtcod.orange
	def stun(self):
		self.char = 'z'
		self.color = libtcod.blue
		self.spawnTime = 15000

	def recharge(self):
		self.endurance = self.stamina*150
		self.char = 'Z'
		self.color = libtcod.orange
		self.spawnTime = 0

class Rect:
    #a rectangle on the map. used to characterize a room or building
	def __init__(self, x, y, w, h):
		self.center_x = int((2*x+w) // 2)
		self.center_y = int((2*y+h) // 2)
		self.x1 = x
		self.y1 = y
		self.x2 = x + w
		self.y2 = y + h
	def center(self):
		center_x = int((self.x1 + self.x2) // 2)
		center_y = int((self.y1 + self.y2) // 2)
		return (center_x, center_y)
	def intersect(self, other):
		return (self.x1 <= other.x2 and self.x2 >= other.x1 and self.y1 <= other.y2 and self.y2 >= other.y1)

class Point:
	def __init__(self, x, y):
		self.x = x
		self.y = y

class Gun:
	def __init__(self):
		self.broken = False

	def fire(self, x, y):
		print("Cathunk")

	def load(self, ammo):
		print("Ammo Loaded")

	def cock(self, x, y):
		print("Gun Cocked")

class Maverik(Gun):
	def __init__(self):
		self.broken = False
		self.chamber = 0
		self.badChamber = [False, False, False, False, False, False]
		for x in range(len(self.badChamber)-1):
			if random.randint(0,6) == 0:
				self.badChamber[x] = True
		self.loaded = [Ammo(1, 1) for x in range(6)]
		self.cocked = False
		self.range = 3*player.acc

	def cock(self):
		self.cocked = True
		return 250//player.tech

	def fire(self, target):
		if self.cocked:
			if self.loaded[self.chamber].real():
				if(abs(target.x-player.x)*abs(target.x-player.x)+abs(target.y-player.y)*abs(target.y-player.y)<self.range*self.range):
					target.stun()
					objects.append(Object(target.x, target.y, '\'', self.loaded[self.chamber].color()))
				else:
					temp = sortedBresendam(player.x, player.y, target.x, target.y)
					closest = 0
					distance = 2000
					for object in range(len(temp)):
						cDistance = abs(abs(temp[object].x-player.x)*abs(temp[object].x-player.x)+abs(temp[object].y-player.y)*abs(temp[object].y-player.y)-self.range*self.range)
						if cDistance < distance:
							closest = object
							distance = cDistance
					objects.append(Object(temp[closest].x, temp[closest].y, '\'', self.loaded[self.chamber].color()))
				objects[len(objects)-1].init = self.loaded[self.chamber].condition
				self.cocked = False
				self.loaded[self.chamber] = Ammo(0, 0)
		self.chamber = (self.chamber+1)%6
		return 100//player.tech

	def fireS(self):
		if self.cocked:
			if self.loaded[self.chamber].real():
				temp = Object(player.x, player.y, '\'', self.loaded[self.chamber].color())
				temp.init = self.loaded[self.chamber].condition
				for i in range(self.range):
					if not temp.move(forward[player.facing][0], forward[player.facing][1]):
						break
				objects.append(temp)
				self.loaded[self.chamber] = Ammo(0, 0)
			self.cocked = False
		self.chamber = (self.chamber+1)%6
		return 100//player.tech

	def load(self, where, dart):
		if self.loaded[where].real():
			return (1000+500*gunHand)//player.tech
		else:
			self.loaded[where] = dart
			return (1500+1000*gunHand)//player.tech



class Ammo:
	def __init__(self, type, condition):
		self.type = type
		self.condition = condition
	def real(self):
		if self.type == 0:
			return False
		return True
	def color(self):
		if self.type == 2: #Elite
			return libtcod.blue
		elif self.type == 1: #Streamline
			return libtcod.orange
		elif self.type == 4:#Mega
			return libtcod.red
		elif self.type == 3: #Disk
			return libtcod.green
		elif self.type == 5: #Whistler
			return libtcod.black
		elif self.type == 0: #None
			return libtcod.white


def bresendam(x1, y1, x2, y2):
	points = []
	steep = abs(y2-y1) > abs(x2-x1)
	points.append(Point(x2, y2))
	if steep:
		x1,y1 = y1,x1
		x2,y2 = y2,x2
	if x1 > x2:
		x1,x2 = x2,x1
		y1,y2 = y2,y1
	deltaX = x2 - x1
	deltaY = abs(y2 - y1)
	error = deltaX//2
	yStep = 0
	y = y1
	if y1 < y2:
		yStep = 1
	else:
		yStep = -1
	for x in range(x1, x2):
		if steep:
			points.append(Point(y,x))
		else:
			points.append(Point(x,y))
		error = error - deltaY
		if error < 0:
			y = y+yStep
			error = error + deltaX

	return points

def sortedBresendam(x1, y1, x2, y2):
	temp = bresendam(x1,y1,x2,y2)
	temp.sort(key=lambda x:abs(x.x-x1)+abs(x.y-y1))
	return temp

def toGrid(points):
	grid = [[False
			for y in range(SCREEN_HEIGHT) ]
				for x in range(SCREEN_WIDTH-30) ]
	for point in points:
		if point.x+30 < SCREEN_WIDTH-30 and point.y+30 < SCREEN_HEIGHT and point.x+30 >= 0 and point.y+30 >= 0:
			grid[point.x+30][point.y+30]=True
	return grid

def visionTriangle(arc, dist):
	points = []
	rePoints = []
	for y in range(0, dist):
		for x in range(0,y+2):
			points.append(Point(x,y))
	if arc == 1:
		rePoints = points
	elif arc == 2:
		for point in points:
			rePoints.append(Point(point.y, point.x))
	elif arc == 3:
		for point in points:
			rePoints.append(Point(point.y, -1*point.x))
	elif arc == 4:
		for point in points:
			rePoints.append(Point(point.x, -1*point.y))
	elif arc == 5:
		for point in points:
			rePoints.append(Point(-1*point.x, -1*point.y))
	elif arc == 6:
		for point in points:
			rePoints.append(Point(-1*point.y, -1*point.x))
	elif arc == 7:
		for point in points:
			rePoints.append(Point(-1*point.y, point.x))
	elif arc == 8:
		for point in points:
			rePoints.append(Point(-1*point.x, point.y))
	else:
		print("Error, Arc must be between 1 and 8")
	return rePoints

def handle_end():
	global playerx, playery, player, map, goal, newGoal, locked, grab,feedLocation, goAgain
	key = libtcod.console_wait_for_keypress(True)
	if key.vk == libtcod.KEY_ENTER and key.lalt:
		#Alt+Enter: Toggle Fullscreen
		libtcod.console_set_fullscreen(not libtcod.console_is_fullscreen())
	elif key.vk == libtcod.KEY_ESCAPE:
		string = 'Are you sure you want to quit? (Y)(N)'
		wait = True
		for x in range(len(string)):
			libtcod.console_set_default_foreground(con, libtcod.white)
			libtcod.console_put_char(con, 15+x, 25, string[x], libtcod.BKGND_NONE)
			libtcod.console_set_char_background(con, 15+x, 25, libtcod.black, libtcod.BKGND_SET )
		libtcod.console_blit(con, 0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, 0, 0, 0)
		libtcod.console_flush()
		while wait:
			key1 = libtcod.console_wait_for_keypress(True)
			temp = chr(key1.c)
			if temp == 'Y' or temp == 'y':
				return True
			elif temp == 'N' or temp == 'n':
				for x in range(len(string)):
					libtcod.console_put_char(con, 15+x, 25, ' ', libtcod.BKGND_NONE)
				break
	else:
		key_char = chr(key.c)
		if key_char == 'r':
			goAgain = True
			return True
		elif key_char == '-':
			if feedLocation<len(feed)-1:
				feedLocation += 1
		elif key_char == '+':
			if feedLocation-23>0:
				feedLocation -= 1


def handle_keys():
	global playerx, playery, player, map, goal, newGoal, locked, grab,feedLocation, quit, gunHand
	key = libtcod.console_wait_for_keypress(True)
	if key.vk == libtcod.KEY_ENTER and key.lalt:
		#Alt+Enter: Toggle Fullscreen
		libtcod.console_set_fullscreen(not libtcod.console_is_fullscreen())
	elif key.vk == libtcod.KEY_ESCAPE:
		string = 'Are you sure you want to quit? (Y)(N)'
		wait = True
		for x in range(len(string)):
			libtcod.console_set_default_foreground(con, libtcod.white)
			libtcod.console_put_char(con, 15+x, 25, string[x], libtcod.BKGND_NONE)
			libtcod.console_set_char_background(con, 15+x, 25, libtcod.black, libtcod.BKGND_SET )
		libtcod.console_blit(con, 0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, 0, 0, 0)
		libtcod.console_flush()
		while wait:
			key1 = libtcod.console_wait_for_keypress(True)
			temp = chr(key1.c)
			if temp == 'Y' or temp == 'y':
				quit = True
				return True
			elif temp == 'N' or temp == 'n':
				for x in range(len(string)):
					libtcod.console_put_char(con, 15+x, 25, ' ', libtcod.BKGND_NONE)
				break
	#movement keys
	if libtcod.console_is_key_pressed(libtcod.KEY_UP):
		if player.velocity == 0:
			player.move(forward[player.facing][0],forward[player.facing][1])
			player.init = (forward[player.facing][2]*10)//player.speed
		else:
			if player.velocity < 3:
				player.velocity += 1
				player.init = 150//player.speed
	elif libtcod.console_is_key_pressed(libtcod.KEY_DOWN):
		if player.velocity == 0:
			player.move(forward[10-player.facing][0],forward[10-player.facing][1])
			player.init = 2*forward[player.facing][2]
		else:
			player.velocity -= 1
			player.init = 150//player.speed
	elif libtcod.console_is_key_pressed(libtcod.KEY_LEFT):
		player.facing = left[player.facing]
		if locked:
			player.vision = player.facing
		elif player.facing+player.vision == 10:
			player.vision = left[player.vision]
		player.init = 250//player.speed
	elif libtcod.console_is_key_pressed(libtcod.KEY_RIGHT):
		player.facing = right[player.facing]
		if locked:
			player.vision = player.facing
		elif player.facing+player.vision == 10:
			player.vision = right[player.vision]
		player.init = 250//player.speed
	else:
		key_char = chr(key.c)
		if key_char == 'm':
			if player.x == goal.x and player.y == goal.y:
				newGoal = True
				player.init = 1000
			else:
				player.init = 10
		elif key_char == 'p':
			for object in objects:
				if object.char == '\'' and object.x==player.x and object.y==player.y:
					putInPocket(Ammo(paintByNumber(object.color), object.init))
					del objects[objects.index(object)]
			player.init = 500//player.tech
		elif key_char == '8':
			if(player.facing != 2):
				player.vision = 8
				player.init = 30
		elif key_char == '9':
			if(player.facing != 1):
				player.vision = 9
				player.init = 30
		elif key_char == '7':
			if(player.facing != 3):
				player.vision = 7
				player.init = 30
		elif key_char == '6':
			if(player.facing != 4):
				player.vision = 6
				player.init = 30
		elif key_char == '4':
			if(player.facing != 6):
				player.vision = 4
				player.init = 30
		elif key_char == '3':
			if(player.facing != 7):
				player.vision = 3
				player.init = 30
		elif key_char == '2':
			if(player.facing != 8):
				player.vision = 2
				player.init = 30
		elif key_char == '1':
			if(player.facing != 9):
				player.vision = 1
				player.init = 30
		elif key_char == '5':
			player.vision = player.facing
			player.init = 10
		elif key_char == 'L':
			locked = not locked
		elif key_char == ']':
			if hasattr(player, 'target'):
				if targets.index(player.target)<len(targets)-1:
					player.target = targets[targets.index(player.target)+1]
				else:
					player.target = targets[0]
			player.init = 5
		elif key_char == '[':
			if hasattr(player, 'target'):
				if targets.index(player.target)>0:
					player.target = targets[targets.index(player.target)-1]
				else:
					player.target = targets[len(targets)-1]
			player.init = 5
		elif key_char == '}':
			if grab[gunHand] < len(pocket[gunHand])-1:
				grab[gunHand] += 1
			player.init = 250//player.tech
		elif key_char == '{':
			if grab[gunHand] > 0:
				grab[gunHand] -= 1
			player.init = 250//player.tech
		elif key_char == 'h':
			gunHand = (gunHand+1)%2
		elif key_char == ' ':
			player.endurance += player.stamina//2
			player.init = 50
		elif key_char == 'c':
			player.init = gun.cock()
			addToFeed('Cachunk!')
		elif key_char == 'l':
			for x in range(5):
				if(len(pocket[gunHand])>0):
					if(not gun.loaded[(x+gun.chamber+1)%6].real()):
						player.init = gun.load((x+gun.chamber+1)%6, pocket[gunHand][grab[gunHand]])
						del pocket[gunHand][grab[gunHand]]
						grab[gunHand] = 0
						break
		elif key_char == 'f':
			if hasattr(player, 'target'):
				gun.fire(player.target)
			else:
				gun.fireS()
			player.init = 20
		elif key_char == 'r':
			if player.velocity == 0:
				player.velocity = 1
		elif key_char == '-':
			if feedLocation<len(feed)-1:
				feedLocation += 1
		elif key_char == '+':
			if feedLocation-23>0:
				feedLocation -= 1
		elif key_char == '?':
			speal = []
			speal.append("Your goal is to make it to the 'C' square and take classes.")
			speal.append("The building the square is located in is shown on your minimap.")
			speal.append("Once you have finished all your classes you have to return to")
			speal.append("the upper right square in order to leave campus and win.")
			speal.append(" ")
			speal.append("Arrow keys control movement.  Left and right rotate you")
			speal.append("Forward moves you in the direction you are facing")
			speal.append("Back moves you in reverse.")
			speal.append("Num pad controls vision.  You cannot look straight behind you.")
			speal.append("m lets you go to class when you are standing on the 'C' square.")
			speal.append("l loads your gun")
			speal.append("c cocks your gun")
			speal.append("f fires your gun")
			speal.append("p picks up ammo on the ground")
			speal.append("+/- scrolls up and down in your messages")
			speal.append("[/] lets you change the zombie you are aiming at")
			speal.append("{/} lets you select the dart you load with l")
			speal.append("h switches between pockets")
			speal.append("esc exits the game")
			speal.append("? brings up this help menu")
			speal.append("r lets you start to run.  Running is explained in the README")
			speal.append("space lets you wait for a bit and regenerate some endurance")
			speal.append("(Press Enter to return to the game)")
			for y in range(len(speal)):
				for x in range(len(speal[y])):
					libtcod.console_set_default_foreground(con, libtcod.white)
					libtcod.console_put_char(con, 13+x, 8+2*y, speal[y][x], libtcod.BKGND_NONE)
			for y in range(47):
				for x in range(70):
					libtcod.console_set_char_background(con, 12+x, 7+y, libtcod.black, libtcod.BKGND_SET )
			libtcod.console_blit(con, 0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, 0, 0, 0)
			libtcod.console_flush()
			while True:
				key = libtcod.console_wait_for_keypress(True)
				if key.vk == libtcod.KEY_ENTER:
					for y in range(len(speal)):
						for x in range(len(speal[y])):
							libtcod.console_set_default_foreground(con, libtcod.white)
							libtcod.console_put_char(con, 13+x, 8+2*y, " ", libtcod.BKGND_NONE)
					libtcod.console_blit(con, 0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, 0, 0, 0)
					libtcod.console_flush()
					break
	if player.velocity>1:
		player.init += (500*(player.velocity-1))//player.speed

def putInPocket(ammo):
	if len(pocket[gunHand])<20:
		pocket[gunHand].append(ammo)
	elif len(pocket[(gunHand+1)%2])<20:
		pocket[(gunHand+1)%2].append(ammo)
	else:
		objects.append(Object(player.x,player.y,'\'',ammo.color()))

def spawnZom(number):
	global map, miniMap
	zombies = []
	for z in range(number):
		unPlaced = True
		while unPlaced:
			x = random.randint(31, size-32)
			y = random.randint(31, size-32)
			if(map[x][y].color == color_grass):
				unPlaced = False
		zed = Zombie(x,y,'Z',libtcod.orange)
		zed.makeAlive(5,5,5,5)
		zombies.append(zed)
	return zombies

def dartSpawn(number):
	global size
	total = size*size//number
	darts = []
	for n in range(total):
		x = random.randint(0, size-1)
		y = random.randint(0, size-1)
		z = random.randint(1,2)
		if z == 1:
			dart = Object(x,y,'\'',libtcod.orange)
		else:
			dart = Object(x,y,'\'',libtcod.blue)
		dart.init = 1
		darts.append(dart)
	return darts

def genMen():
	menu = []
	menu.append(Object(78, 1, 28 ,libtcod.blue))
	menu.append(Object(76, 1, 'F', libtcod.white))
	menu.append(Object(77, 1, ':', libtcod.white))
	menu.append(Object(78, 2, 28 ,libtcod.yellow))
	menu.append(Object(76, 2, 'V', libtcod.white))
	menu.append(Object(77, 2, ':', libtcod.white))
	menu.append(Object(78, 3, 'Y',libtcod.green))
	menu.append(Object(76, 3, 'L', libtcod.white))
	menu.append(Object(77, 3, ':', libtcod.white))
	menu.append(Object(62, 20, 'M', libtcod.white))
	menu.append(Object(63, 20, ':', libtcod.white))
	for x in range(6):
		menu.append(Object(64+x, 20, ' ', libtcod.white))
	menu.append(Object(64, 21, 24, libtcod.white))
	menu.append(Object(62, 30, 'P', libtcod.white))
	menu.append(Object(63, 30, ':', libtcod.white))
	for x in range(len(pocket[0])):
		menu.append(Object(64+x,30, '|', pocket[0][x].color()))
	for x in range(20-len(pocket[0])):
		menu.append(Object(64+x+len(pocket[0]),30, ' ', libtcod.black))
	menu.append(Object(70, 31, 24, libtcod.white))
	for y in range(35, 59):
		for x in range(64, 90):
			menu.append(Object(x, y, '+', libtcod.yellow))
	menu.append(Object(62, 35, 24, libtcod.gray))
	menu.append(Object(62, 58, 25, libtcod.gray))
	menu.append(Object(76, 4, 'C', libtcod.white))
	menu.append(Object(77, 4, ':', libtcod.white))
	menu.append(Object(78, 4, 48+winCount,libtcod.purple))
	menu.append(Object(76, 5, 'S', libtcod.white))
	menu.append(Object(77, 5, ':', libtcod.white))
	menu.append(Object(78, 5, 48+player.velocity,libtcod.sky))
	for x in range(20):
		menu.append(Object(71+x, 10, ' ', libtcod.black))
	for x in range(len(pocket[1])):
		menu.append(Object(64+x,32, '|', pocket[1][x].color()))
	for x in range(20-len(pocket[1])):
		menu.append(Object(64+x+len(pocket[1]),32, ' ', libtcod.black))
	for x in range(len(playerName)):
		menu.append(Object(62+x, 1, playerName[x], libtcod.white))
	status = []
	status.append('Stamina:  '+str(player.stamina))
	status.append('Speed:    '+str(player.speed))
	status.append('Accuracy: '+str(player.acc))
	status.append('Practice: '+str(player.tech))
	for y in range(len(status)):
		for x in range(len(status[y])):
			menu.append(Object(62+x, 2+y, status[y][x], libtcod.white))
	status = 'Endurance:'
	for x in range(len(status)):
		menu.append(Object(62+x, 10, status[x], libtcod.white))
	menu.append(Object(62, 32, 'P', libtcod.white))
	menu.append(Object(63, 32, ':', libtcod.white))
	return menu

def updateMenu(menu):
	global locked
	for y in range(35, 59):
		for x in range(64, 90):
			if feedLocation-y+35 < len(feed) and feedLocation-y+35 >= 0:
				if x-64 < len(feed[feedLocation-y+35]):
					menu[41+x-64+(y-35)*26] = Object(x,y,feed[feedLocation-y+35][x-64],libtcod.white)
				else:
					menu[41+x-64+(y-35)*26] = Object(x,y,' ',libtcod.yellow)
			else:
				menu[41+x-64+(y-35)*26] = Object(x,y,' ',libtcod.yellow)
	if(feedLocation < len(feed)-1):
		menu[39+90-64+24*25] = Object(62, 35, 24, libtcod.white)
	else:
		menu[39+90-64+24*25] = Object(62, 35, 24, libtcod.gray)
	if(feedLocation - 23 > 0):
		menu[40+90-64+24*25] = Object(62, 58, 25, libtcod.white)
	else:
		menu[40+90-64+24*25] = Object(62, 58, 25, libtcod.gray)
	menu[43+90-64+24*25] = Object(78, 4, 48+winCount,libtcod.purple)
	menu[46+90-64+24*25] = Object(78, 5, 48+player.velocity,libtcod.sky)
	for x in range(player.endurance//100):
		menu[47+90-64+24*25+x] = Object(71+x,10,'#',libtcod.Color(255-player.endurance//10,player.endurance//10,0))
	for x in range(20-player.endurance//100):
		menu[47+90-64+24*25+x+player.endurance//100] = Object(71+x+player.endurance//100,10,'#',libtcod.black)
	for x in range(len(pocket[1])):
		menu[67+90-64+24*25+x] = Object(64+x,32, '|', pocket[1][x].color())
	for x in range(20-len(pocket[1])):
		menu[67+90-64+24*25+len(pocket[1])+x] = Object(64+x+len(pocket[1]),32, ' ', libtcod.black)
	menu[17] = Object(64+gun.chamber, 21, 24, libtcod.white)
	for bullet in range(len(gun.loaded)):
		menu[11+bullet] = Object(64+bullet, 20, '|', gun.loaded[bullet].color())
	for x in range(len(pocket[0])):
		menu[20+x] = Object(64+x,30, '|', pocket[0][x].color())
	for x in range(20-len(pocket[0])):
		menu[20+len(pocket[0])+x] = Object(64+x+len(pocket[0]),30, ' ', libtcod.black)
	menu[40] = Object(64+grab[gunHand], 31+2*gunHand, 24, libtcod.white)
	if player.facing == 8:
		menu[0] = Object(78, 1, 24, libtcod.blue)
	elif player.facing == 2:
		menu[0] = Object(78, 1, 25 ,libtcod.blue)
	elif player.facing == 6:
		menu[0] = Object(78, 1, 26 ,libtcod.blue)
	elif player.facing == 4:
		menu[0] = Object(78, 1, 27 ,libtcod.blue)
	elif player.facing == 9:
		menu[0] = Object(78, 1, 187 ,libtcod.blue)
	elif player.facing == 3:
		menu[0] = Object(78, 1, 188 ,libtcod.blue)
	elif player.facing == 7:
		menu[0] = Object(78, 1, 201 ,libtcod.blue)
	elif player.facing == 1:
		menu[0] = Object(78, 1, 200 ,libtcod.blue)
	if player.vision == 8:
		menu[3] = Object(78, 2, 24, libtcod.yellow)
	elif player.vision == 2:
		menu[3] = Object(78, 2, 25 ,libtcod.yellow)
	elif player.vision == 6:
		menu[3] = Object(78, 2, 26 ,libtcod.yellow)
	elif player.vision == 4:
		menu[3] = Object(78, 2, 27 ,libtcod.yellow)
	elif player.vision == 9:
		menu[3] = Object(78, 2, 187 ,libtcod.yellow)
	elif player.vision == 3:
		menu[3] = Object(78, 2, 188 ,libtcod.yellow)
	elif player.vision == 7:
		menu[3] = Object(78, 2, 201 ,libtcod.yellow)
	elif player.vision == 1:
		menu[3] = Object(78, 2, 200 ,libtcod.yellow)
	if locked == True:
		menu[6] = Object(78, 3, 'Y',libtcod.green)
	else:
		menu[6] = Object(78, 3, 'N',libtcod.red)
	return menu

def findGoal():
	global map, miniMap
	unPlaced = True
	while unPlaced:
		x = random.randint(0, size-1)
		y = random.randint(0, size-1)
		if(map[x][y].color == color_floor):
			unPlaced = False
	return (x, y)

def make_map(size, buildingRate):
	global map, miniMap
	if(PRETTY):
		map = [[Tile(libtcod.Color(132+random.randint(-20,20), 204+random.randint(-20,20), 0+random.randint(0,30)), False, 1, 1, False)
			for y in range(size) ]
				for x in range(size) ]
	else:
		map = [[Tile(color_grass, False, 1, 1, False)
			for y in range(size) ]
				for x in range(size) ]
	for y in range (size):
		for x in range (size):
			if (x < 31 and x>=10) or (y < 31 and y>=10) or (x > size - 31 and x <= size - 10) or (y > size - 31 and y <= size - 10):
				if x == 21 or y == 21 or x == 19 or y == 19 or x == size-19 or x == size-21 or y == size - 19 or y == size - 21:
					map[x][y].changeTile(color_traffic, False, 0, 10, True)
				else:
					map[x][y].changeTile(color_asphalt, False, 0, 10, True)
	miniMap = [[Tile(color_grass, False, 1, 1, False)
		for y in range(int(size//100)) ]
			for x in range(int(size//100)) ]
	totalBuildings = 0
	while totalBuildings == 0:
		for y in range (int(size//100)):
			for x in range (int(size//100)):
				if(random.randint(0,buildingRate) == 0):
					totalBuildings += 1
					temp = make_building()
					miniMap[x][y].changeTile(temp[0][0].color, True, 0, 5, True)
					offsetY = random.randint(1, 10)
					offsetX = random.randint(1, 10)
					for yB in range (len(temp[0])):
						for xB in range (len(temp)):
							map[31+100*x+offsetX+xB][31+100*y+offsetY+yB] = temp[xB][yB]


def make_building():
	global map
	tRooms = []
	tRoomN = 0
	sizeX = 30+random.randint(0, 49)
	sizeY = 30+random.randint(0, 49)
	if random.randint(0,2) == 0:
		buildingMap = [[Tile(color_stone, True, 0, 5, True)
		for y in range(sizeY) ]
			for x in range(sizeX) ]
	else:
		buildingMap = [[Tile(color_brick, True, 0, 5, True)
			for y in range(sizeY) ]
				for x in range(sizeX) ]
	for r in range(MAX_ROOMS):
        #random width and height
		w = libtcod.random_get_int(0, ROOM_MIN_SIZE, ROOM_MAX_SIZE)
		h = libtcod.random_get_int(0, ROOM_MIN_SIZE, ROOM_MAX_SIZE)
		x = libtcod.random_get_int(0, 0, sizeX - w - 1)
		y = libtcod.random_get_int(0, 0, sizeY - h - 1)
		new_room = Rect(x, y, w, h)
		#run through the other rooms and see if they intersect with this one
		failed = False
		for other_room in tRooms:
			if new_room.intersect(other_room):
				failed = True
				break
		if not failed:
			for x in range(new_room.x1 + 1, new_room.x2):
				for y in range(new_room.y1 + 1, new_room.y2):
					buildingMap[x][y].changeTile(color_floor, False, 1, 3, False)
			new_x = int(new_room.center_x)
			new_y = int(new_room.center_y)
			if tRoomN == 0:
				tole = 7
			else:
				(prev_x, prev_y) = tRooms[tRoomN-1].center()
                #draw a coin (random number that is either 0 or 1)
				if libtcod.random_get_int(0, 0, 1) == 1:
					#first move horizontally, then vertically
					for x in range(min(prev_x, new_x), max(prev_x, new_x) + 1):
						buildingMap[x][prev_y].changeTile(color_floor, False, 1, 3, False)
					for y in range(min(prev_y, new_y), max(prev_y, new_y) + 1):
						buildingMap[new_x][y].changeTile(color_floor, False, 1, 3, False)
				else:
                    #first move vertically, then horizontally
					for y in range(min(prev_y, new_y), max(prev_y, new_y) + 1):
						buildingMap[prev_x][y].changeTile(color_floor, False, 1, 3, False)
					for x in range(min(prev_x, new_x), max(prev_x, new_x) + 1):
						buildingMap[x][new_y].changeTile(color_floor, False, 1, 3, False)


            #finally, append the new room to the list
			tRooms.append(new_room)
			tRoomN += 1
	#Make exits
	numExits = random.randint(1,6)
	for e in range(numExits):
		rRoom = tRooms[random.randint(0,tRoomN-1)]
		bSide = random.randint(1,4)
		if(bSide == 1):
			ry = random.randint(1, sizeY-2)
			rx = 0
			for x in range(min(rRoom.center_x, rx), max(rRoom.center_x, rx) + 1):
				buildingMap[x][ry].changeTile(color_floor, False, 1, 3, False)
			for y in range(min(rRoom.center_y, ry), max(rRoom.center_y, ry) + 1):
				buildingMap[rRoom.center_x][y].changeTile(color_floor, False, 1, 3, False)
		elif(bSide == 2):
			ry = 0
			rx = random.randint(1, sizeX-2)
			for y in range(min(rRoom.center_y, ry), max(rRoom.center_y, ry) + 1):
				buildingMap[rx][y].changeTile(color_floor, False, 1, 3, False)
			for x in range(min(rRoom.center_x, rx), max(rRoom.center_x, rx) + 1):
				buildingMap[x][rRoom.center_y].changeTile(color_floor, False, 1, 3, False)
		elif(bSide == 3):
			ry = random.randint(1, sizeY-2)
			rx = sizeX-1
			for x in range(min(rRoom.center_x, rx), max(rRoom.center_x, rx) + 1):
				buildingMap[x][ry].changeTile(color_floor, False, 1, 3, False)
			for y in range(min(rRoom.center_y, ry), max(rRoom.center_y, ry) + 1):
				buildingMap[rRoom.center_x][y].changeTile(color_floor, False, 1, 3, False)
		elif(bSide == 4):
			ry = sizeY-1
			rx = random.randint(1, sizeX-2)
			for y in range(min(rRoom.center_y, ry), max(rRoom.center_y, ry) + 1):
				buildingMap[rx][y].changeTile(color_floor, False, 1, 3, False)
			for x in range(min(rRoom.center_x, rx), max(rRoom.center_x, rx) + 1):
				buildingMap[x][rRoom.center_y].changeTile(color_floor, False, 1, 3, False)
	return buildingMap

def paintByNumber(color):
	if(color == libtcod.blue):
		return 2
	elif(color == libtcod.orange):
		return 1
	elif(color == libtcod.red):
		return 4
	elif(color == libtcod.green):
		return 3
	elif(color == libtcod.black):
		return 5

def endGame():
	global menu, newGoal, goal, winCount
	menu = updateMenu(menu)
	render_some()
	libtcod.console_flush()
	for thing in menu:
		thing.clear(thing.x, thing.y)
	for object in objects+zombies:
		if(object.x < player.x + 30 and object.x > player.x - 30 and object.y < player.y + 30 and object.y > player.y - 30):
			object.clear(object.x-player.x+30, object.y-player.y+30)
	player.clear((player.x-31)//100+MMX, (player.y-31)//100+MMY)
	goal.clear((goal.x-31)//100+MMX, (goal.y-31)//100+MMY)
	exit = handle_end()
	if exit:
		return True

def playerUpdate():
	global menu, newGoal, goal, winCount
	menu = updateMenu(menu)
	render_all()
	libtcod.console_flush()
	for thing in menu:
		thing.clear(thing.x, thing.y)
	for object in objects+zombies:
		if(object.x < player.x + 30 and object.x > player.x - 30 and object.y < player.y + 30 and object.y > player.y - 30):
			object.clear(object.x-player.x+30, object.y-player.y+30)
	player.clear((player.x-31)//100+MMX, (player.y-31)//100+MMY)
	goal.clear((goal.x-31)//100+MMX, (goal.y-31)//100+MMY)
	#handle keys and exit if needed
	exit = handle_keys()
	if newGoal:
		if winCount == 0:
			player.init = 0
			return True
		elif winCount == 1:
			winCount = 0
			goal = Object(31,31,'C', libtcod.yellow)
			goal.init = 2*goalTimer
			player.recharge()
			for object in zombies:
				object.recharge()
			objects[1] = goal
			newGoal = False
		else:
			winCount -= 1
			(gx, gy) = findGoal()
			goal = Object(gx, gy, 'C', libtcod.yellow)
			goal.init = goalTimer
			player.recharge()
			for object in zombies:
				object.recharge()
			objects[1] = goal
			newGoal = False
	if exit:
		return True

def zomMove(zed):
	global tagged
	if(abs(zed.x-player.x)+abs(zed.y-player.y)<=1 and zed.color!=libtcod.blue):
		tagged = True
		addToFeed("Tagged!")
		zed.init = 1

	elif (abs(zed.x-player.x)+abs(zed.y-player.y)<=29 and zed.color!=libtcod.blue and zed.endurance>200):
		move = sortedBresendam(zed.x, zed.y, player.x, player.y)
		if zed.velocity>0:
			if zed.facing == reverse[move[0].x-zed.x+1][move[0].y-zed.y+1]:
				if zed.velocity < 2:
					zed.velocity+=1
					zed.init = 150//zed.speed
				else:
					zed.init = 10
			elif left[zed.facing] == reverse[move[0].x-zed.x+1][move[0].y-zed.y+1]:
				zed.facing = left[zed.facing]
				zed.init = 250//zed.speed
			elif right[zed.facing] == reverse[move[0].x-zed.x+1][move[0].y-zed.y+1]:
				zed.facing = right[zed.facing]
				zed.init = 250//zed.speed
			else:
				zed.velocity-=1
				zed.init = 150//zed.speed
		else:
			zed.facing = reverse[move[0].x-zed.x+1][move[0].y-zed.y+1]
			zed.velocity = 1
			zed.init = 500//zed.speed
	elif(abs(zed.x-player.x)+abs(zed.y-player.y)<=10 and zed.color==libtcod.blue):
		move = sortedBresendam(zed.x, zed.y, player.x, player.y)
		zed.facing = reverse[zed.x-move[0].x+1][zed.y-move[0].y+1]
		zed.move(zed.x-move[0].x, zed.y-move[0].y)
		if abs(move[0].x-zed.x)+abs(move[0].y-zed.y)<2:
			zed.init = 250//zed.speed
		else:
			zed.init = 375//zed.speed
	elif(abs(zed.x-player.x)+abs(zed.y-player.y)<=10 and zed.color!=libtcod.blue):
		move = sortedBresendam(zed.x, zed.y, player.x, player.y)
		zed.facing = reverse[move[0].x-zed.x+1][move[0].y-zed.y+1]
		zed.move(move[0].x-zed.x, move[0].y-zed.y)
		if abs(move[0].x-zed.x)+abs(move[0].y-zed.y)<2:
			zed.init = 250//zed.speed
		else:
			zed.init = 375//zed.speed
	else:
		x = random.randint(-1,1)
		y = random.randint(-1,1)
		zed.move(x,y)
		zed.facing = reverse[x+1][y+1]
		zed.endurance += zed.stamina//2
		if abs(x)+abs(y)<2:
			zed.init = 250//zed.speed
		else:
			zed.init = 375//zed.speed
	if zed.velocity>1:
		zed.init += (500*(zed.velocity-1))//zed.speed
	return zed

def addToFeed(string):
	global feedLocation
	feed.append(string)
	feedLocation = len(feed)-1

def render_some():
	global targets, size
	for y in range(int(size//100)):
		for x in range(int(size//100)):
			libtcod.console_set_char_background(con, MMX+x, MMY+y, miniMap[x][y].color, libtcod.BKGND_SET )
	player.draw((player.x-31)//100+MMX, (player.y-31)//100+MMY)
	goal.draw((goal.x-31)//100+MMX, (goal.y-31)//100+MMY)
	for thing in menu:
		thing.draw(thing.x, thing.y)
	for object in objects+zombies:
		if(object.x < player.x + 30 and object.x > player.x - 30 and object.y < player.y + 30 and object.y > player.y - 30):
			object.draw(object.x-player.x+30, object.y-player.y+30)
	for y in range(SCREEN_HEIGHT):
		for x in range(SCREEN_WIDTH-30):
			libtcod.console_set_char_background(con, x, y, map[x+player.x-30][y+player.y-30].color, libtcod.BKGND_SET )
	libtcod.console_blit(con, 0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, 0, 0, 0)

def render_all():
	#draw all objects in the list
	global targets, size
	for y in range(int(size//100)):
		for x in range(int(size//100)):
			libtcod.console_set_char_background(con, MMX+x, MMY+y, miniMap[x][y].color, libtcod.BKGND_SET )
	player.draw((player.x-31)//100+MMX, (player.y-31)//100+MMY)
	goal.draw((goal.x-31)//100+MMX, (goal.y-31)//100+MMY)
	for thing in menu:
		thing.draw(thing.x, thing.y)
	inTriangle = preTriangle[player.vision]
	targets = []
	for object in objects+zombies:
		if(object.x < player.x + 30 and object.x > player.x - 30 and object.y < player.y + 30 and object.y > player.y - 30):
			if(map[player.x][player.y].color == color_floor):
				if object.char != 'Z' and object.char != 'z':
					object.draw(object.x-player.x+30, object.y-player.y+30)
			if(inTriangle[object.x-player.x+30][object.y-player.y+30]):
				blocked = False
				for point in bresendam(player.x, player.y, object.x, object.y):
					if map[point.x][point.y].visionBlock:
						blocked = True
						break
				if not blocked:
					object.draw(object.x-player.x+30, object.y-player.y+30)
					if object.char == 'Z':
						targets.append(object)
				elif object.velocity > 0:
					object.draw(object.x-player.x+30, object.y-player.y+30)
			else:
				if object.velocity > 0:
					object.draw(object.x-player.x+30, object.y-player.y+30)
	targets.sort(key=lambda x:abs(x.x-player.x)+abs(x.y-player.y))
	if len(targets) > 0:
		if not hasattr(player, 'target'):
			setattr(player, 'target', targets[0])
		if targets.count(player.target) == 0:
			setattr(player, 'target', targets[0])
	else:
		if hasattr(player, 'target'):
			delattr(player, 'target')

	for y in range(SCREEN_HEIGHT):
		for x in range(SCREEN_WIDTH-30):
			if inTriangle[x][y]:
				blocked = False
				for point in bresendam(player.x, player.y, player.x+x-30, player.y+y-30):
					if map[point.x][point.y].visionBlock:
						blocked = True
						break
				if blocked:
					libtcod.console_set_char_background(con, x, y, map[x+player.x-30][y+player.y-30].color-libtcod.Color(60, 60, 60), libtcod.BKGND_SET )
				else:
					libtcod.console_set_char_background(con, x, y, map[x+player.x-30][y+player.y-30].color-libtcod.Color(abs(x-30)+abs(y-30), abs(x-30)+abs(y-30), abs(x-30)+abs(y-30)), libtcod.BKGND_SET )
			else:
				libtcod.console_set_char_background(con, x, y, map[x+player.x-30][y+player.y-30].color-libtcod.Color(60, 60, 60), libtcod.BKGND_SET )
	if hasattr(player, 'target'):
		libtcod.console_set_char_background(con, player.target.x-player.x+30, player.target.y-player.y+30, libtcod.purple, libtcod.BKGND_SET )
	libtcod.console_blit(con, 0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, 0, 0, 0)


def setup():
	speal = []
	speal.append("Humans vs Zombies is a large scale tag like game played")
	speal.append("primarily on college campuses.  Zombies try to tag humans")
	speal.append("in order to convert them into zombies, while humans can")
	speal.append("defend themselves with nerf guns and socks.")
	speal.append(" ")
	speal.append("In this game you will be playing a human who is trying to not get")
	speal.append("killed by zombies while also making it to all of their classes.")
	speal.append(" ")
	speal.append("You will lose if you are tagged by a zombie or if you are late")
	speal.append("to one of your classes.  You win if you make it to every class")
	speal.append("and successfully return to your car and leave campus.")
	speal.append(" ")
	speal.append("Please read the README document for full controls.")
	speal.append("A limited set can be seen with ? once the game starts.")
	speal.append("(Press Enter to Continue)")
	for y in range(len(speal)):
		for x in range(len(speal[y])):
			libtcod.console_set_default_foreground(con, libtcod.white)
			libtcod.console_put_char(con, 15+x, 15+2*y, speal[y][x], libtcod.BKGND_NONE)
	libtcod.console_blit(con, 0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, 0, 0, 0)
	libtcod.console_flush()
	while True:
		key = libtcod.console_wait_for_keypress(True)
		if key.vk == libtcod.KEY_ENTER:
			break
	for y in range(len(speal)):
		for x in range(len(speal[y])):
			libtcod.console_set_default_foreground(con, libtcod.white)
			libtcod.console_put_char(con, 15+x, 15+2*y, " ", libtcod.BKGND_NONE)
	libtcod.console_blit(con, 0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, 0, 0, 0)
	libtcod.console_flush()
	string = "What is your name? (13 Character Max)"
	for x in range(len(string)):
		libtcod.console_set_default_foreground(con, libtcod.white)
		libtcod.console_put_char(con, 25+x, 25, string[x], libtcod.BKGND_NONE)
	libtcod.console_blit(con, 0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, 0, 0, 0)
	libtcod.console_flush()
	#time.sleep(1)
	name = ""
	x = 0
	while x < 14:
		key = libtcod.console_wait_for_keypress(True)
		if key.vk == libtcod.KEY_ENTER:
			break
		if key.vk == libtcod.KEY_BACKSPACE:
			if x>0:
				name = str(name[0:x-1])
				x-=1
				libtcod.console_set_default_foreground(con, libtcod.white)
				libtcod.console_put_char(con, 25+x, 27, ' ', libtcod.BKGND_NONE)
				libtcod.console_blit(con, 0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, 0, 0, 0)
				libtcod.console_flush()
				#time.sleep(.2)
		elif key.vk == libtcod.KEY_SHIFT:
			time.sleep(.001)
		else:
			input = chr(key.c)
			if input != '' and x < 13:
				name += input
				libtcod.console_set_default_foreground(con, libtcod.white)
				libtcod.console_put_char(con, 25+x, 27, input, libtcod.BKGND_NONE)
				libtcod.console_blit(con, 0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, 0, 0, 0)
				libtcod.console_flush()
				x+=1
				#time.sleep(.2)
		if x>13:
			x = 13
	for x in range(40):
		libtcod.console_put_char(con,25+x,27,' ',libtcod.BKGND_NONE)
		libtcod.console_put_char(con,25+x,25,' ',libtcod.BKGND_NONE)
	libtcod.console_blit(con, 0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, 0, 0, 0)
	libtcod.console_flush()
	options = []
	options.append("Map Options")
	options.append(" ")
	options.append("Map Size:       Tiny  Small Med   Large")
	options.append("Zombie Rate:    Rare  Few   Med   Many ")
	options.append("Ground Ammo:    None  Rare  Some  Much ")
	options.append("Tardy Bell:     5m    7m    10m   15m  ")
	options.append("Buildings:      Rare  Few   Lots  Max  ")
	options.append("Num Classes:    2     3     4     5    ")
	for y in range(len(options)):
		for x in range(len(options[y])):
			libtcod.console_set_default_foreground(con, libtcod.white)
			libtcod.console_put_char(con, 25+x, 20+2*y, options[y][x], libtcod.BKGND_NONE)
	libtcod.console_blit(con, 0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, 0, 0, 0)
	libtcod.console_flush()
	#time.sleep(.7)
	choices = [1,2,1,2,3,2]
	w = 0
	while True:
		for x in range(4):
			for y in range(6):
				for z in range(5):
					if choices[y]==x:
						if(y==w):
							libtcod.console_set_char_background(con, 41+6*x+z, 24+2*y, libtcod.red, libtcod.BKGND_SET )
						else:
							libtcod.console_set_char_background(con, 41+6*x+z, 24+2*y, libtcod.blue, libtcod.BKGND_SET )
					else:
						libtcod.console_set_char_background(con, 41+6*x+z, 24+2*y, libtcod.black, libtcod.BKGND_SET )
		libtcod.console_blit(con, 0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, 0, 0, 0)
		libtcod.console_flush()
		key = libtcod.console_wait_for_keypress(True)
		if key.vk == libtcod.KEY_ENTER:
			if w == 5:
				break
			else:
				w += 1
		elif key.vk == libtcod.KEY_UP:
			if w != 0:
				w -= 1
		elif key.vk == libtcod.KEY_DOWN:
			if w != 5:
				w += 1
		elif key.vk == libtcod.KEY_LEFT:
			choices[w] = (choices[w]-1)%4
		elif key.vk == libtcod.KEY_RIGHT:
			choices[w] = (choices[w]+1)%4
		#time.sleep(.3)

	for y in range(len(options)):
		for x in range(len(options[y])):
			libtcod.console_set_default_foreground(con, libtcod.white)
			libtcod.console_put_char(con, 25+x, 20+2*y, ' ', libtcod.BKGND_NONE)
			libtcod.console_set_char_background(con, 25+x, 20+2*y, libtcod.black, libtcod.BKGND_SET )

	lock = _thread.allocate_lock()
	_thread.start_new_thread(mapMaker, (choices[0],choices[1],choices[2],choices[3],choices[4],choices[5],lock))
	options = []
	options.append("Player Options")
	options.append(" ")
	options.append("Stamina:")
	options.append("Speed:")
	options.append("Accuracy:")
	options.append("Training:")
	options.append("Nerf Gun:  Maverick(0)  Alpha Trooper(3)  Stampede(5)  Pyragon (5)")
	options.append("Extra Darts:  None(0)   12 Streamline(1)   18 Elite(2)   30 Streamline(2)")
	options.append("Extra Clip:  None  6 Dart(1)  18 Dart(2)")
	options.append("Points Left:")
	stamina = 5
	speed = 5
	accuracy = 5
	training = 5
	nerf = 0
	darts = 0
	clip = 0
	points = 10
	at = 0
	#time.sleep(1)
	while True:
		for i in range(len(options)):
			for j in range(len(options[i])):
				if (i == 8) or (i == 6 and j>22):
					libtcod.console_set_default_foreground(con, libtcod.gray)
				else:
					libtcod.console_set_default_foreground(con, libtcod.white)
				libtcod.console_put_char(con, 15+j, 15+2*i, options[i][j], libtcod.BKGND_NONE)
				libtcod.console_set_char_background(con, 15+j, 15+2*i, libtcod.black, libtcod.BKGND_SET )
		libtcod.console_set_char_background(con, 15, 19+2*at, libtcod.red, libtcod.BKGND_SET )
		accumulator(stamina, 19)
		accumulator(speed, 21)
		accumulator(accuracy, 23)
		accumulator(training, 25)
		for x in range(11):
			libtcod.console_set_char_background(con, 26+x, 27, libtcod.orange, libtcod.BKGND_SET )
		temp = [(29,36),(39,55),(58,69),(72,88)]
		for x in range(16,90):
			if x >= temp[darts][0] and x < temp[darts][1]:
				libtcod.console_set_char_background(con, x, 29, libtcod.orange, libtcod.BKGND_SET )
			else:
				libtcod.console_set_char_background(con, x, 29, libtcod.black, libtcod.BKGND_SET )
		accumulator(points, 33)
		libtcod.console_blit(con, 0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, 0, 0, 0)
		libtcod.console_flush()
		key = libtcod.console_wait_for_keypress(True)
		if key.vk == libtcod.KEY_ENTER:
			if at == 5:
				break
			else:
				at+=1
		elif key.vk == libtcod.KEY_UP:
			if at > 0:
				at -= 1
		elif key.vk == libtcod.KEY_DOWN:
			if at != 5:
				at += 1
		elif key.vk == libtcod.KEY_RIGHT:
			if at == 0 and stamina < 10 and points > 0:
				stamina+=1
				points-=1
			elif at == 1 and speed < 10 and points > 0:
				speed+=1
				points-=1
			elif at == 2 and accuracy < 10 and points > 0:
				accuracy+=1
				points-=1
			elif at == 3 and training < 10 and points > 0:
				training+=1
				points-=1
			elif at == 5:
				if darts < 2 and points > 0:
					darts += 1
					points -= 1
				elif darts == 2:
					darts = 3
		elif key.vk == libtcod.KEY_LEFT:
			if at == 0 and stamina > 1:
				stamina-=1
				points+=1
			elif at == 1 and speed > 1:
				speed-=1
				points+=1
			elif at == 2 and accuracy > 1:
				accuracy-=1
				points+=1
			elif at == 3 and training > 1:
				training-=1
				points+=1
			elif at == 5:
				if darts < 3 and darts > 0:
					darts -= 1
					points += 1
				elif darts == 3:
					darts = 2
		#time.sleep(.3)
		if darts == 0:
			dartNum = 0
			dartType = 1
		elif darts == 1:
			dartNum = 12
			dartType = 1
		elif darts == 2:
			dartNum = 18
			dartType = 2
		elif darts == 3:
			dartNum = 30
			dartType = 1
	for x in range(SCREEN_WIDTH):
		for y in range(SCREEN_HEIGHT):
			libtcod.console_set_default_foreground(con, libtcod.black)
			libtcod.console_put_char(con, x, y, ' ', libtcod.BKGND_NONE)
			libtcod.console_set_char_background(con, x, y, libtcod.black, libtcod.BKGND_SET )
	#time.sleep(2)
	return (name, stamina, speed, accuracy, training, nerf, dartNum, dartType, lock)

def accumulator(stat, y):
	for n in range(stat):
		if stat <= 10:
			libtcod.console_set_default_foreground(con, libtcod.Color(255-25*n,25*n,0))
		else:
			libtcod.console_set_default_foreground(con, libtcod.Color(255-10*n,0,10*n))
		libtcod.console_put_char(con, 30+n, y, '#', libtcod.BKGND_NONE)
	for n in range(30-stat):
		libtcod.console_set_default_foreground(con, libtcod.black)
		libtcod.console_put_char(con, 30+n+stat, y, ' ', libtcod.BKGND_NONE)

def mapMaker(inSize, zombieRate, ammoRate, bellTime, buildingRate, numClasses, lock):
	global size, goal, newGoal, goalTimer, winCount, zombies, darts
	lock.acquire()
	size = 200*(1+inSize)+61
	sendBuilding = 3-buildingRate
	make_map(size, sendBuilding)
	winCount = numClasses+2
	timer = [30000, 42000, 60000, 90000]
	goalTimer = timer[bellTime]
	(gx, gy) = findGoal()
	goal = Object(gx, gy, 'C', libtcod.yellow)
	goal.init = goalTimer
	newGoal = False
	if ammoRate > 0:
		dartScale = 3000//(ammoRate*ammoRate)
		darts = dartSpawn(dartScale)
	else:
		darts = []
	zombieScale = 1000//(zombieRate+1)
	zombies = spawnZom(size*size//zombieScale)
	lock.release()

def play():
	global player, goal, winCount, pocket, objects, quit, grab, feed, feedLocation, menu, preTriangle, tagged, locked, gun, playerName, con, darts, gunHand
	con = libtcod.console_new(SCREEN_WIDTH, SCREEN_HEIGHT)
	(playerName, stamina, speed, accurate, technical, gunType, ammoNumber, ammoType, lock) = setup()
	quit = False
	player1 = Object(31, 31, '@', libtcod.red)
	player1.makeAlive(stamina, speed, accurate, technical)
	lock.acquire()
	objects = [player1, goal]
	lock.release()
	objects = objects + darts
	player = player1
	pocket1 = []
	pocket2 = []
	pocket = [pocket1, pocket2]
	gunHand = 0
	for x in range(ammoNumber):
		n = Ammo(ammoType,1)
		putInPocket(n)
	grab = [0,0]
	feed = []
	feed.append("")
	feed.append("Welcome to HvZ.")
	feedLocation = 1
	menu = genMen()
	preTriangle = [[],[],[],[],[],[],[],[],[],[]]
	preTriangle[2] = toGrid(visionTriangle(8,31)+visionTriangle(1,31))
	preTriangle[3] = toGrid(visionTriangle(1,31)+visionTriangle(2,31))
	preTriangle[1] = toGrid(visionTriangle(7,31)+visionTriangle(8,31))
	preTriangle[4] = toGrid(visionTriangle(6,31)+visionTriangle(7,31))
	preTriangle[6] = toGrid(visionTriangle(2,31)+visionTriangle(3,31))
	preTriangle[7] = toGrid(visionTriangle(6,31)+visionTriangle(5,31))
	preTriangle[8] = toGrid(visionTriangle(5,31)+visionTriangle(4,31))
	preTriangle[9] = toGrid(visionTriangle(4,31)+visionTriangle(3,31))
	tagged = False
	locked = True
	gun = Maverik()
	while not libtcod.console_is_window_closed():
		while True:
			while player.init == 0:
				if playerUpdate():
					break
			if player.velocity > 0:
				if player.runInit == 0:
					player.run()
				player.runInit -= 1
			if player.init == 0:
				addToFeed("You survived HvZ.")
				addToFeed("Congratulations!")
				break
			player.decrement()
			if goal.init == 0:
				addToFeed("Missed Class.")
				break
			elif goal.init == 6000:
				addToFeed("1 minute till Class")
			elif goal.init%6000 == 0:
				addToFeed(str(goal.init//6000)+" minutes till Class")
			goal.decrement()
			for z in range(len(zombies)-1):
				while zombies[z].init == 0:
					zombies[z] = zomMove(zombies[z])
				if zombies[z].velocity > 0:
					if zombies[z].runInit == 0:
						zombies[z].run()
					zombies[z].runInit -= 1
				zombies[z].decrement()
			if tagged:
				break
		if quit == True:
			break
		if tagged:
			addToFeed("Got Tagged!")
		addToFeed(" ")
		addToFeed("Press r to Restart")
		addToFeed("Press Esc to Quit")
		while True:
			if endGame():
				break
		break
libtcod.console_set_custom_font('arial10x10.png', libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_TCOD)
libtcod.console_init_root(SCREEN_WIDTH, SCREEN_HEIGHT, 'Humans vs Zombies', False)
goAgain = True
while goAgain == True:
	goAgain = False
	play()
