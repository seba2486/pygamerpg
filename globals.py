import pygame

world = None

DARK_GREY = (50,50,50)
BLACK = (0,0,0)
WHITE = (255,255,255)
GREEN = (0,255,0)
MUSTARD = (209, 206, 25)
SCREEN_SIZE = (800,600)
WORLD_WIDTH = 2000
WORLD_HEIGHT = 800
TILE_SIZE = 16

player1 = None

soundManager = None

world_bounds = pygame.Rect(0, 0, WORLD_WIDTH, WORLD_HEIGHT)