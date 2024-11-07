import pygame
import csv

class Map:
    
    def __init__(self, csv_path, tile_size, spritesheet_path, platform_tile_indices):
        self.tile_size = tile_size
        self.platforms = []
        self.tiles = self.load_spritesheet(spritesheet_path, tile_size, tile_size)
        self.platform_tile_indices = platform_tile_indices
        self.load_map(csv_path)

    def load_map(self, csv_path):
        with open(csv_path, newline='') as file:
            reader = csv.reader(file)
            for y, row in enumerate(reader):
                for x, tile in enumerate(row):
                    if tile in self.platform_tile_indices:
                        rect = pygame.Rect(x * self.tile_size, y * self.tile_size, self.tile_size, self.tile_size)
                        collide = True 
                        self.platforms.append((rect, self.tiles[self.platform_tile_indices[tile]],collide))

    def load_spritesheet(self, filename, tile_width, tile_height):
        """Carga un spritesheet y divide los tiles individuales.
        
        Args:
            filename (str): La ruta del archivo del spritesheet.
            tile_width (int): Ancho de cada tile en píxeles.
            tile_height (int): Altura de cada tile en píxeles. 
        Returns:
            list: Una lista de superficies Pygame para cada tile.
        """
        spritesheet = pygame.image.load(filename).convert_alpha()
        sheet_width, sheet_height = spritesheet.get_size()
        tiles = []
    
        for y in range(0, sheet_height, tile_height):
            for x in range(0, sheet_width, tile_width):
                rect = pygame.Rect(x, y, tile_width, tile_height)
                image = pygame.Surface(rect.size, pygame.SRCALPHA).convert_alpha()
                image.blit(spritesheet, (0, 0), rect)
                tiles.append(image)
        
        return tiles

    def draw(self, screen, offset_x, offset_y):
        for rect, image in self.platforms:
            screen.blit(image, (rect.x + offset_x, rect.y + offset_y))
