import pygame
import random
import os
import numpy as np

# Path to assets folder relative to this file's location
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")

# Constants
WIDTH = 800
HEIGHT = 400
GROUND_Y = 320
GRAVITY = 0.8
JUMP_FORCE = -14
GAME_SPEED_START = 12

class Dino:
    def __init__(self, nn=None):
        self.x = 50
        self.y = GROUND_Y
        self.vel_y = 0
        self.base_width = 40
        self.base_height = 44
        self.duck_width = 50
        self.duck_height = 25
        
        self.width = self.base_width
        self.height = self.base_height
        
        self.is_alive = True
        self.is_ducking = False
        self.fitness = 0
        self.nn = nn  # NeuralNet instance
        
        try:
            raw_run = pygame.image.load(os.path.join(ASSETS_DIR, "dino.png")).convert_alpha()
            self.img_run = pygame.transform.scale(raw_run, (self.base_width, self.base_height))
            raw_duck = pygame.image.load(os.path.join(ASSETS_DIR, "dino_duck.png")).convert_alpha()
            self.img_duck = pygame.transform.scale(raw_duck, (self.duck_width, self.duck_height))
        except:
            self.img_run = pygame.Surface((self.base_width, self.base_height))
            self.img_run.fill((83, 83, 83))
            self.img_duck = pygame.Surface((self.duck_width, self.duck_height))
            self.img_duck.fill((83, 83, 83))
            
        self.image = self.img_run
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

    def jump(self):
        if self.y >= GROUND_Y and not self.is_ducking:
            self.vel_y = JUMP_FORCE

    def duck(self, is_ducking):
        if self.y >= GROUND_Y: # Only duck on ground
            self.is_ducking = is_ducking
            if is_ducking:
                self.width = self.duck_width
                self.height = self.duck_height
                self.y = GROUND_Y + (self.base_height - self.duck_height)
                self.image = self.img_duck
            else:
                self.width = self.base_width
                self.height = self.base_height
                self.y = GROUND_Y
                self.image = self.img_run
            self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

    def update(self):
        if not self.is_alive:
            return
            
        if not self.is_ducking:
            self.vel_y += GRAVITY
            self.y += self.vel_y
            
            if self.y >= GROUND_Y:
                self.y = GROUND_Y
                self.vel_y = 0
        
        self.rect.y = self.y
        self.fitness += 1

    def draw(self, screen):
        if self.is_alive:
            screen.blit(self.image, (self.rect.x, self.rect.y))

class Cactus:
    def __init__(self, speed):
        self.type = "cactus"
        self.count = random.choice([1, 2, 3]) # Single, Double, Triple
        self.single_width = 20
        self.width = self.single_width * self.count
        self.height = random.choice([35, 45, 55])
        self.x = WIDTH
        self.y = GROUND_Y + 44 - self.height
        
        try:
            base_img = pygame.image.load(os.path.join(ASSETS_DIR, "cactus.png")).convert_alpha()
            scaled_single = pygame.transform.scale(base_img, (self.single_width, self.height))
            
            # Create a combined surface for multiple cacti
            self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            for i in range(self.count):
                self.image.blit(scaled_single, (i * self.single_width, 0))
        except:
            self.image = pygame.Surface((self.width, self.height))
            self.image.fill((34, 139, 34))
            
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.speed = speed

    def update(self):
        self.x -= self.speed
        self.rect.x = self.x

    def draw(self, screen):
        screen.blit(self.image, (self.rect.x, self.rect.y))

class Bird:
    def __init__(self, speed):
        self.type = "bird"
        self.width = 40
        self.height = 30
        self.x = WIDTH
        # 3 possible heights: High (jump doesn't reach), Mid (must duck or jump), Low (must jump)
        # We'll use 2 for now to keep it simpler: High (duck) and Low (jump)
        self.y = random.choice([GROUND_Y - 20, GROUND_Y + 10]) 
        
        try:
            raw_bird = pygame.image.load(os.path.join(ASSETS_DIR, "bird.png")).convert_alpha()
            self.image = pygame.transform.scale(raw_bird, (self.width, self.height))
        except:
            self.image = pygame.Surface((self.width, self.height))
            self.image.fill((200, 100, 0))
            
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        self.speed = speed

    def update(self):
        self.x -= self.speed
        self.rect.x = self.x
        # Basic wing animation could go here

    def draw(self, screen):
        screen.blit(self.image, (self.rect.x, self.rect.y))

def get_state(dino, obstacles, speed):
    # State: [distance, obs_height, obs_y, game_speed, dino_y]
    if len(obstacles) == 0:
        return np.array([[1.0, 0.0, 1.0, speed/25.0, (GROUND_Y - dino.y)/100.0]])
        
    closest = None
    for obs in obstacles:
        if obs.x + obs.width > dino.x:
            if closest is None or obs.x < closest.x:
                closest = obs
                
    if closest is None:
        return np.array([[1.0, 0.0, 1.0, speed/25.0, (GROUND_Y - dino.y)/100.0]])
        
    d = (closest.x - dino.x) / WIDTH
    a = closest.height / 100.0
    oy = closest.y / HEIGHT
    v = speed / 25.0
    y_norm = (GROUND_Y - dino.y) / 100.0
    
    return np.array([[d, a, oy, v, y_norm]])
