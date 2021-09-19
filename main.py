import pygame
import os
import time
import random
pygame.font.init()

WIDTH, HEIGHT = 1280,720
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Shooter Tutorial")

# Loading images

RED_SPACE_SHIP = pygame.image.load(os.path.join("assets", "pixel_ship_red_small.png"))
# We could also use     - RED_SPACE_SHIP = pygame.image.load('assets/pixel_ship_red_small.png')
# Aanother way to do it - RED_SPACE_SHIP = pygame.image.load(r'C:\Users\User_Name\Desktop\PythonFileExample\file.png')
GREEN_SPACE_SHIP = pygame.image.load(os.path.join("assets","pixel_ship_green_small.png"))
BLUE_SPACE_SHIP = pygame.image.load(os.path.join("assets","pixel_ship_blue_small.png"))

# Main player
SPACESHIP = pygame.image.load(os.path.join("assets","spaceship.png"))

# Lasers
RED_LASER = pygame.image.load(os.path.join("assets","pixel_laser_red.png"))
GREEN_LASER = pygame.image.load(os.path.join("assets","pixel_laser_green.png"))
BLUE_LASER = pygame.image.load(os.path.join("assets","pixel_laser_blue.png"))
YELLOW_LASER = pygame.image.load(os.path.join("assets","pixel_laser_yellow.png"))

#Background
BG = pygame.transform.scale(pygame.image.load(os.path.join("assets","background.jpg")), (WIDTH, HEIGHT))

class Laser:
	def __init__(self, x, y, img):
		self.x = x
		self.y = y
		self.img = img
		self.mask = pygame.mask.from_surface(self.img)

	def draw(self, window):
		window.blit(self.img, (self.x, self.y))

	def move(self, vel):
		self.y += vel

	def off_screen(self, height):
		return not(self.y <= height and self.y >= 0)

	def collision(self,obj):
		return collide(self, obj)

class Ship:
	COOLDOWN = 15

	def __init__(self, x, y, health=100):
		self.x = x
		self.y = y
		self.health = health
		self.ship_img = None
		self.laser_img = None
		self.lasers = []
		self.cool_down_counter = 0

	def draw(self, window):
		window.blit(self.ship_img, (self.x, self.y))
		for laser in self.lasers:
			laser.draw(window)
	
	def move_lasers(self, vel, obj):
		self.cooldown()
		for laser in self.lasers:
			laser.move(vel)
			if laser.off_screen(HEIGHT):
				self.lasers.remove(laser)
			elif laser.collision(obj):
				obj.health -= 10
				self.lasers.remove(laser)

	def cooldown(self):
		if self.cool_down_counter >= self.COOLDOWN : #if there isn't cooldown the player can shoot the the cool_down_counter is beign reseted here
			self.cool_down_counter = 0
		elif self.cool_down_counter > 0: #if there is a cooldown the player can't shoot (30sec)
			self.cool_down_counter +=1

	def get_width(self):
		return self.ship_img.get_width()

	def get_height(self):
		return self.ship_img.get_height()

	def shoot(self):
		if self.cool_down_counter == 0:
			laser = Laser((int)(self.x-(self.get_width())/2), self.y-(self.get_height()), self.laser_img)
			self.lasers.append(laser)
			self.cool_down_counter = 1 #starting the count, for cooldown

class Player(Ship):
	def __init__(self, x, y, health=100):
		super().__init__(x, y, health) #override - in addition to the parent class attributes - x, y, health - add the following attributes
		self.ship_img = SPACESHIP
		self.laser_img = YELLOW_LASER
		self.mask = pygame.mask.from_surface(self.ship_img)
		self.max_health = health

	def move_lasers(self, vel, objs):
		self.cooldown()
		for laser in self.lasers:
			laser.move(vel)
			if laser.off_screen(HEIGHT):
				self.lasers.remove(laser)
			else:
				for obj in objs:
			 		if laser.collision(obj):
					   objs.remove(obj)
					   if laser in self.lasers:
					       self.lasers.remove(laser)

	def draw(self,window):
		super().draw(window) #override (write in addition to the parrent class method - draw)
		self.health_bar(window)

	def health_bar(self, window):			   #Location(x,y)									#Size(height,width)
		pygame.draw.rect(window, (255, 0, 0), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width(), 10)) #RED, width like the ship and height 10px
		pygame.draw.rect(window, (51, 204, 51), (self.x, self.y + self.ship_img.get_height() + 10, self.ship_img.get_width() * (self.health/self.max_health), 10)) #GREEN, width like the ship and height 10px


class Enemy(Ship):
	COLOR_MAP = {
				"red" : (RED_SPACE_SHIP, RED_LASER),
				"green" : (GREEN_SPACE_SHIP, GREEN_LASER),
				"blue" : (BLUE_SPACE_SHIP, BLUE_LASER)
	}

	def __init__(self, x, y, color, health=100): 
		super().__init__(x, y, health)
		(self.ship_img, self.laser_img) = self.COLOR_MAP[color]
		self.mask = pygame.mask.from_surface(self.ship_img)

	def move(self,vel):
		self.y+=vel

	def shoot(self):
		if self.cool_down_counter == 0:
			laser = Laser(self.x-20, self.y, self.laser_img)
			self.lasers.append(laser)
			self.cool_down_counter = 1 #starting the count, for cooldown

def collide(obj1, obj2):
	offset_x = obj2.x - obj1.x
	offset_y = obj2.y - obj1.y
	return obj1.mask.overlap(obj2.mask, (offset_x,offset_y)) != None

def main():
	#General Vars
	run = True
	FPS = 60
	level = 0
	lives = 5
	main_font = pygame.font.SysFont("comicsans", 50)
	lost_font = pygame.font.SysFont("comicsans", 60)
	lvlup_font = pygame.font.SysFont("comicsans", 70, bold=True)
	lvlup = False
	lvlup_cnt = 0

	#Enemies Vars
	enemies = []
	wave_length = 0
	enemy_vel = 1
	laser_vel = 6

	#Player
	player_vel = 7
	player = Player(300, 600)

	clock = pygame.time.Clock()
	lost = False
	lost_count = 0

	def redraw_window():
		WIN.blit(BG,(0,0))

		#draw txt
		lives_label = main_font.render(f"Lives: {lives}", 1, (255,255,255))
		level_label = main_font.render(f"level: {level}", 1, (255,255,255))
		lvlup_label = main_font.render("Level UP!", 1, (255,255,255))
		WIN.blit(lives_label, (10, 10))
		WIN.blit(level_label, (WIDTH - level_label.get_width() - 10 , 10))
		if lvlup:
			WIN.blit(lvlup_label, (WIDTH/2 - lvlup_label.get_width()/2, 350))

		for enemy in enemies:
			enemy.draw(WIN)
		
		player.draw(WIN)

		if lost:
			lost_label = lost_font.render("GAME OVER!", 1, (255, 255, 255))
			WIN.blit(lost_label, (WIDTH/2 - lost_label.get_width()/2, 350))

		pygame.display.update() #make the surface and the draws to be shown on the screen

	while run:
		clock.tick(FPS)
		redraw_window()
		if lvlup_cnt > 0 and lvlup_cnt < FPS * 2:
			lvlup_cnt += 1
		elif lvlup_cnt == (FPS * 2):
			lvlup = False
			lvlup_cnt = 0
		

		if lives <= 0 or player.health <= 0:
			lost = True
			lost_count +=1 #means how much time you are on 'lost' status,
						   #everytime the while loop runs the lost_count will increament (60 times per second)

		if lost:
			if lost_count > FPS * 5: #Hold the game for 5 sec
				run = False #END the game
			else:
				continue #go back to the start of the while loop

		if len(enemies) == 0:
			level += 1
			wave_length += 5
			player.health = 100
			if level > 1:
				lvlup = True
				lvlup_cnt = 1
			for i in range(wave_length):
				enemy = Enemy(random.randrange(50, WIDTH-100), random.randrange(-1500,-100), random.choice(["red","blue","green"]))
				enemies.append(enemy)

		#Movement keys setup
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				run = False
		keys = pygame.key.get_pressed()
		if keys[pygame.K_a] and player.x - player_vel >= 0: #left
			player.x -= player_vel
		if keys[pygame.K_d] and player.x + player_vel + player.get_width() <= WIDTH: #right
			player.x += player_vel
		if keys[pygame.K_w] and player.y - player_vel >= 0: #top
			player.y -= player_vel
		if keys[pygame.K_s] and player.y + player_vel + player.get_height() + 30 <= HEIGHT: #down, the '+30' is so the health bar will be shown and won't be off the screen
			player.y += player_vel
		if keys[pygame.K_SPACE]:
			player.shoot()

		for enemy in enemies[:]:
			enemy.move(enemy_vel)
			enemy.move_lasers(laser_vel, player)

			if random.randrange(0,2*60) == 1: #in that case we have a chance of 1 to 120 (in 120 frames, 2 seconds) that the enemy will shoot, in the worst case
				enemy.shoot()

			if collide(enemy, player):
				player.health -= 10
				enemies.remove(enemy)

			elif enemy.y + enemy.get_height() > HEIGHT: #delete the enemy when it's object is no longer on the screen
				lives -= 1
				enemies.remove(enemy)



		player.move_lasers(-laser_vel, enemies)

def main_menu():
	title_font = pygame.font.SysFont("comicsans", 70)
	run = True
	while run:
		WIN.blit(BG, (0,0))
		title_label = title_font.render("Press the mouse to begin...", 1, (255,255,255))
		WIN.blit(title_label, (WIDTH/2 - title_label.get_width()/2, 350))
		pygame.display.update()
		for event in pygame.event.get():
			if event.type == pygame.QUIT: #pygame.QUIT ->>> if we click on 'x' to close the windows
				run = False
			if event.type == pygame.MOUSEBUTTONDOWN:
				main()
	pygame.quit()

main_menu()