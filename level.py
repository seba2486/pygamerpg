import globals
import utils
from map import Map

class Level:
    def __init__(self, csv_path=None, entities = None, winFunc=None, loseFunc=None, tile_image_path=None, 
                 background = None, foreground = None, powerupSpawnPoints = None, movingPlatforms = None, trackingEnemies = None, boss = None, npc = None):
        self.map = Map(csv_path, globals.TILE_SIZE, tile_image_path, utils.platform_tile_indices)
        self.platforms = self.map.platforms
        self.entities = entities
        self.winFunc = winFunc
        self.loseFunc = loseFunc
        self.background = background
        self.foreground = foreground
        self.powerupSpawnPoints = powerupSpawnPoints
        self.movingPlatforms = movingPlatforms
        self.trackingEnemies = trackingEnemies
        self.boss = boss
        self.npc = npc

    def isWon(self):
        if self.winFunc is None:
            return False
        return self.winFunc(self)
    
    def isLost(self):
        if self.loseFunc is None:
            return False
        return self.loseFunc(self)
    
def lostLevel(level):
    #level isn't lost if any player has lives
    for entity in level.entities:
        if entity.type == 'player':
            if entity.battle is not None:
                if entity.battle.energy > 0:
                    return False
    #level lost
    return True

#win if no more coins
def wonLevel(level):

    for entity in level.entities:
        if entity.type == 'door':
           if entity.position.rect.colliderect(globals.player1.position.rect) and globals.player1.key==1 and globals.player1.intention.down:
            return True
    #Corregir siempre retorna falso, cambiar logica de WIN
    return False

def loadLevel(levelNumber):
    csv_path = f'maps/level{levelNumber}.csv'
    tile_image_path = f'sprites/levels/level{levelNumber}.png'
    if levelNumber == 1:
        globals.world = Level(
            csv_path=csv_path,
            tile_image_path=tile_image_path,
            background = utils.background[f"{levelNumber}"],
            foreground = utils.foreground[f"{levelNumber}"],
            entities=[
                # utils.makeCoin(100, 600),
                # utils.makeCoin(1800, 600),
                utils.makeDoor(5*globals.TILE_SIZE, 2*globals.TILE_SIZE),
                utils.makeSpike(37*globals.TILE_SIZE, 46*globals.TILE_SIZE),
                utils.makeSpike(39*globals.TILE_SIZE, 46*globals.TILE_SIZE),
                utils.makeSpike(41*globals.TILE_SIZE, 46*globals.TILE_SIZE),
                utils.makeSpike(43*globals.TILE_SIZE, 46*globals.TILE_SIZE),
                utils.makeSpike(45*globals.TILE_SIZE, 46*globals.TILE_SIZE),
                utils.makeSpike(47*globals.TILE_SIZE, 46*globals.TILE_SIZE),
                utils.makeSpike(49*globals.TILE_SIZE, 46*globals.TILE_SIZE),
                utils.makeSpike(62*globals.TILE_SIZE, 27*globals.TILE_SIZE),
                utils.makeSpike(64*globals.TILE_SIZE, 27*globals.TILE_SIZE),
                utils.makeSpike(66*globals.TILE_SIZE, 27*globals.TILE_SIZE),
                utils.makeSpike(68*globals.TILE_SIZE, 27*globals.TILE_SIZE),
                utils.makeSpike(70*globals.TILE_SIZE, 27*globals.TILE_SIZE),
                utils.makeSpike(72*globals.TILE_SIZE, 27*globals.TILE_SIZE),
                utils.makeEnemy(384, 700, 'toad'),
                utils.makeEnemy(55*globals.TILE_SIZE, 44*globals.TILE_SIZE, 'toad'),
                utils.makeEnemy(71*globals.TILE_SIZE, 16*globals.TILE_SIZE, 'toad'),
                utils.makeEnemy(93*globals.TILE_SIZE, 14*globals.TILE_SIZE, 'toad'),
                utils.makeEnemy(103*globals.TILE_SIZE, 44*globals.TILE_SIZE, 'devil'),
                utils.makeEnemy(19*globals.TILE_SIZE, 23*globals.TILE_SIZE, 'devil'),
                utils.makeEnemy(47*globals.TILE_SIZE, 26*globals.TILE_SIZE, 'devil'),
                utils.makeEnemy(114*globals.TILE_SIZE, 14*globals.TILE_SIZE, 'devil'),
                utils.makePowerUp('coin', 34*globals.TILE_SIZE, 41*globals.TILE_SIZE),
                globals.player1
            ],
            winFunc=wonLevel,
            loseFunc=lostLevel,
            powerupSpawnPoints = [(34*globals.TILE_SIZE, 41*globals.TILE_SIZE),(38*globals.TILE_SIZE, 41*globals.TILE_SIZE)],
            movingPlatforms=[
                utils.makeMovingPlatform(65*globals.TILE_SIZE, 27*globals.TILE_SIZE, globals.TILE_SIZE, globals.TILE_SIZE, 24*globals.TILE_SIZE, 1, 'vertical'),
                utils.makeMovingPlatform(70*globals.TILE_SIZE, 27*globals.TILE_SIZE, globals.TILE_SIZE, globals.TILE_SIZE, 24*globals.TILE_SIZE, 1, 'vertical'),
                utils.makeMovingPlatform(99*globals.TILE_SIZE, 31*globals.TILE_SIZE, globals.TILE_SIZE, globals.TILE_SIZE, 22*globals.TILE_SIZE, 1, 'vertical'),
                utils.makeMovingPlatform(113*globals.TILE_SIZE, 33*globals.TILE_SIZE, globals.TILE_SIZE, globals.TILE_SIZE, 24*globals.TILE_SIZE, 1, 'vertical'),
                utils.makeMovingPlatform(50*globals.TILE_SIZE, 43*globals.TILE_SIZE, globals.TILE_SIZE, globals.TILE_SIZE, 39*globals.TILE_SIZE, 2, 'lateral'),
                utils.makeMovingPlatform(118*globals.TILE_SIZE, 14*globals.TILE_SIZE, globals.TILE_SIZE, globals.TILE_SIZE, 8*globals.TILE_SIZE, 1, 'vertical')
            ],
            trackingEnemies = [
                utils.makeTrackingEnemy(25*globals.TILE_SIZE, 36*globals.TILE_SIZE, 200, 'bat'),
                utils.makeTrackingEnemy(98*globals.TILE_SIZE, 20*globals.TILE_SIZE, 200, 'bat'),
                utils.makeTrackingEnemy(113*globals.TILE_SIZE, 20*globals.TILE_SIZE, 200, 'bat')
            ],
            boss = utils.makeBossEnemy(24*globals.TILE_SIZE, 4*globals.TILE_SIZE, 'boss'),
            npc = utils.makeNpc(54*globals.TILE_SIZE, 15*globals.TILE_SIZE+5, 'smith')
        )
    elif levelNumber == 2:
        globals.world = Level(
            csv_path=csv_path,
            tile_image_path=tile_image_path,
            background = utils.background[f"{levelNumber}"],
            entities=[
                utils.makeCoin(100, 200),
                globals.player1
            ],
            winFunc=wonLevel,
            loseFunc=lostLevel
        )
        
    #Reset Players
    for entity in globals.world.entities:
            entity.reset(entity)
    for entity in globals.world.trackingEnemies:
            entity.reset(entity)