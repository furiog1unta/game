import pygame
import os

pygame.init()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
HIGH_SCORE_FILE = "high_score.json"

GRAVITY = 0.5
JUMP_SPEED = -15
MOVE_SPEED = 5
FRICTION = 0.5

PLAYER_WIDTH = 80
PLAYER_HEIGHT = 60
PLATFORM_WIDTH = 100
PLATFORM_HEIGHT = 20
ENEMY_WIDTH = 50
ENEMY_HEIGHT = 50


WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
ORANGE = (255, 165, 0)
RED = (255, 0, 0)
GRAY = (128, 128, 128)
GOLD = (255, 215, 0)


try:
    PLAYER_IMAGE = pygame.image.load(os.path.join("assets", "hero.png"))
    PLAYER_IMAGE = pygame.transform.scale(PLAYER_IMAGE, (PLAYER_WIDTH, PLAYER_HEIGHT))
except:
    PLAYER_IMAGE = None

try:
    BACKGROUND_IMAGE = pygame.image.load(os.path.join("assets", "background.jpg"))
    BACKGROUND_IMAGE = pygame.transform.scale(BACKGROUND_IMAGE, (SCREEN_WIDTH, SCREEN_HEIGHT))
except:
    BACKGROUND_IMAGE = None

try:
    ENEMY_IMAGE = pygame.image.load(os.path.join("assets", "enemy.png"))
    ENEMY_IMAGE = pygame.transform.scale(ENEMY_IMAGE, (ENEMY_WIDTH, ENEMY_HEIGHT))
except:
    ENEMY_IMAGE = None 