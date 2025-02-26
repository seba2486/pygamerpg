import engine
import pygame
import globals
import random


#Constants
SCREEN_SIZE = (800, 600)
DARK_GREY = (50,50,50)
MUSTARD = (209, 206, 25)

background ={ "1" : [('sprites/backgrounds/BackgroundForest4.png', 0.1),
            ('sprites/backgrounds/BackgroundForest3.png', 0.3),
            ('sprites/backgrounds/BackgroundForest2.png', 0.5),
            ('sprites/backgrounds/BackgroundForest1.png', 0.8)]
}

foreground ={ "1" : [('sprites/foregrounds/fore1.png', 1.5),
            ('sprites/foregrounds/fore2.png', 2.0)]
}

# Level 1
platform_tile_indices = {'0':0,"1":1,"2":2,"4":4,"5":5,"6":6,"50":50,'51':51,"52":52,"54":54,"56":56,"100":100,"101":101,"102":102,"104":104,"105":105,"106":106}

platform0 = pygame.image.load('sprites/platforms/level1/1.png')

def makeMovingPlatform(x, y, width, height, max_height, speed, type):
    movingPlatform = engine.MovingPlatform()
    movingPlatform.position = engine.Position(x, y, width, height)
    movingPlatform.start_y = y
    movingPlatform.start_x = x
    movingPlatform.max_height = max_height
    movingPlatform.speed = speed
    movingPlatform.dir = -1  # -1 para arriba, 1 para abajo
    entityMovingAnimation = engine.Animation([platform0])
    movingPlatform.animations.add('moving', entityMovingAnimation)
    movingPlatform.state = 'moving'
    movingPlatform.type = type
    movingPlatform.colide = True
    return movingPlatform

tree0 = pygame.image.load('sprites/trees/tree1.png')
tree1 = pygame.image.load('sprites/trees/tree2.png')
tree2 = pygame.image.load('sprites/trees/tree3.png')
tree3 = pygame.image.load('sprites/trees/tree4.png')



def makeTree(x, y):
    entity = engine.Entity()
    entity.position = engine.Position(x,y,32,64)
    entityIdleAnimation = engine.Animation([tree0])
    entityHitAnimation = engine.Animation([tree0,tree1,tree2,tree3])
    entity.animations.add('idle', entityIdleAnimation)
    entity.animations.add('hit', entityHitAnimation)
    entity.type = 'tree'
    return entity

door0 = pygame.image.load('sprites/doors/door.png')

def makeDoor(x, y):
    entity = engine.Entity()
    entity.position = engine.Position(x,y,48,48)
    entityIdleAnimation = engine.Animation([door0])
    entity.animations.add('idle', entityIdleAnimation)
    entity.type = 'door'
    return entity

spike0 = pygame.image.load('sprites/spikes/stonespikes.png')

def makeSpike(x, y):
    entity = engine.Entity()
    entity.position = engine.Position(x,y,32,32)
    entityAnimation = engine.Animation([spike0])
    entity.animations.add('idle', entityAnimation)
    entity.type = 'spike'
    entity.impact_power = enemies_power[entity.type]
    return entity

coin0 = pygame.image.load('sprites/coins/coin16_00.png')
coin1 = pygame.image.load('sprites/coins/coin16_01.png')
coin2 = pygame.image.load('sprites/coins/coin16_02.png')
coin3 = pygame.image.load('sprites/coins/coin16_03.png')
coin4 = pygame.image.load('sprites/coins/coin16_04.png')
coin5 = pygame.image.load('sprites/coins/coin16_05.png')


live_image = pygame.image.load('sprites/lives/heart.png')


def setHealth(entity):
    if entity.battle:
        entity.battle.energy = entity.battle.max_energy

def setInvisible(entity):
    if entity.animations:
        entity.animations.alpha = 50

def endInvisible(entity):
    if entity.animations:
        entity.animations.alpha = 255

def setCoin(entity):
    if entity.score is not None:
        coins_value = (5, 10, 20)
        entity.score.score += random.choice(coins_value)

def setKey(entity):
    if entity.key is not None:
        entity.key = 1

def setShield(entity):
    entityIdleAnimation = engine.Animation(player_animations['idleShield'])
    entityWalkingAnimation = engine.Animation(player_animations['walkingShield'])
    entityJumpAnimation = engine.Animation(player_animations['jumpShield'])
    entityAttackAnimation = engine.Animation(player_animations['attackShield'])
    entity.animations.add('idle', entityIdleAnimation)
    entity.animations.add('walking', entityWalkingAnimation)
    entity.animations.add('jump', entityJumpAnimation)
    entity.animations.add('attack', entityAttackAnimation)
    entity.shield = True

def setArmor(entity):
    entityIdleAnimation = engine.Animation(player_animations['idleArmor'])
    entityWalkingAnimation = engine.Animation(player_animations['walkingArmor'])
    entityJumpAnimation = engine.Animation(player_animations['jumpArmor'])
    entityAttackAnimation = engine.Animation(player_animations['attackArmor'])
    entity.animations.add('idle', entityIdleAnimation)
    entity.animations.add('walking', entityWalkingAnimation)
    entity.animations.add('jump', entityJumpAnimation)
    entity.animations.add('attack', entityAttackAnimation)
    entity.armor = True

powerups = ['health', 'invisible', 'coin', 'key', 'shield']

powerupImages = {
    'health' : [pygame.image.load('sprites/powerups/heart.png')],
    'invisible' : [pygame.image.load('sprites/powerups/invisible.png')],
    'coin' : [coin0,coin1,coin2,coin3,coin4,coin5],
    'key' : [pygame.image.load('sprites/powerups/levelkey.png')],
    'shield' : [pygame.image.load('sprites/powerups/shield.png')]
}

powerupSounds = {
    'health' : 'coin',
    'invisible' : 'coin',
    'coin' : 'coin',
    'key' : 'coin',
    'shield' : 'coin'
}

powerupApply = {
    'health' : setHealth,
    'invisible' : setInvisible,
    'coin' : setCoin,
    'key' : setKey,
    'shield' : setShield
}

powerupEnd = {
    'health' : None,
    'invisible' : endInvisible,
    'coin' : None,
    'key' : None,
    'shield' : None
}

powerupEffectTimer = {
    'health' : 0,
    'invisible' : 400,
    'coin' : 0,
    'key' : 0,
    'shield' : 0
}

def makePowerUp(type, x, y):
    entity = engine.Entity()
    entity.position = engine.Position(x,y,16,16)
    entityAnimation = engine.Animation(powerupImages[type])
    entity.animations.add('idle', entityAnimation)
    #entity.type = 'collectable'
    entity.effect = engine.Effect(powerupApply[type], powerupEffectTimer[type], powerupSounds[type], powerupEnd[type], type)
    entity.type = 'powerup'
    entity.speed = 1
    return entity    

def makeCoin(x, y):
    entity = engine.Entity()
    entity.position = engine.Position(x,y,23,23)
    entityAnimation = engine.Animation([coin0,coin1,coin2,coin3,coin4,coin5])
    entity.animations.add('idle', entityAnimation)
    entity.type = 'collectable'
    return entity

toad0 = pygame.image.load('sprites/enemies/toad1.png')
toad1 = pygame.image.load('sprites/enemies/toad2.png')
toad2 = pygame.image.load('sprites/enemies/toad3.png')
toad3 = pygame.image.load('sprites/enemies/toadhit1.png')
toad4 = pygame.image.load('sprites/enemies/toadhit2.png')


devil0 = pygame.image.load('sprites/enemies/devil1.png')
devil1 = pygame.image.load('sprites/enemies/devil2.png')
devil2 = pygame.image.load('sprites/enemies/devil3.png')
devil3 = pygame.image.load('sprites/enemies/devil4.png')

bat0 = pygame.image.load('sprites/enemies/bat1.png')
bat1 = pygame.image.load('sprites/enemies/bat2.png')
bat2 = pygame.image.load('sprites/enemies/bat3.png')
bat3 = pygame.image.load('sprites/enemies/bathit1.png')
bat4 = pygame.image.load('sprites/enemies/bathit2.png')

boss0 = pygame.image.load('sprites/enemies/boss1.png')
boss0 = pygame.transform.scale(boss0, (60,72))
boss1 = pygame.image.load('sprites/enemies/boss2.png')
boss1 = pygame.transform.scale(boss1, (60,72))
boss2 = pygame.image.load('sprites/enemies/boss3.png')
boss2 = pygame.transform.scale(boss2, (60,72))
boss3 = pygame.image.load('sprites/enemies/boss4.png')
boss3 = pygame.transform.scale(boss3, (60,72))

# Enemies parameters
enemies_energy = {'toad': 30,'devil': 40, 'bat': 30, 'boss' : 100}
enemies_speed = {'toad': 1,'devil': 3, 'bat': 2, 'boss' : 1}
enemies_power = {'toad': 10,'devil': 10, 'bat': 10, 'boss' : 20, 'spike' : 20}
enemies_types = ['toad', 'devil','bat', 'boss']
enemies_size = {'toad':[20,20],'devil':[25,23], 'bat':[26,26], 'boss' : [60,72]}
enemies_animations = {'toad' : {
                                'idle' : [toad0],
                                'walking' : [toad0,toad1,toad2],
                                'hit' : [toad3,toad4,toad3,toad4,toad3,toad4]
                                },
                      'devil': {
                                'idle' : [devil0],
                                'walking' : [devil0,devil1,devil2],
                                'hit' : [devil3]
                                },
                      'bat' : {
                                'idle' : [bat0],
                                'walking' : [bat0,bat1,bat2],
                                'hit' : [bat3,bat4,bat3,bat4,bat3,bat4]
                                }, 
                      'boss' : {
                                'idle' : [boss0],
                                'walking' : [boss0,boss1],
                                'hit' : [boss2],
                                'attack' : [boss3]
                                }, 
}

def makeEnemy(x, y, type):
    entity = engine.Entity()
    w = enemies_size[type][0]
    h = enemies_size[type][1]
    entity.position = engine.Position(x,y,w,h)
    enemyIddleAnimation = engine.Animation(enemies_animations[type]['idle'])
    enemyWalkingAnimation = engine.Animation(enemies_animations[type]['walking'])
    enemyHitAnimation = engine.Animation(enemies_animations[type]['hit'])
    entity.animations.add('idle', enemyIddleAnimation)
    entity.animations.add('walking', enemyWalkingAnimation)
    entity.animations.add('hit', enemyHitAnimation)
    entity.intention = None
    entity.type = type
    entity.speed = enemies_speed[type]
    entity.direction = 'right'
    entity.state = 'walking'
    entity.battle = engine.Battle(enemies_energy[type], enemies_energy[type])
    entity.impact_power = enemies_power[type]
    entity.cooldown = 50
    entity.attack_cooldown = 0  # Inicialmente sin temporizador
    return entity

def makeTrackingEnemy(x, y, tracking_d, type):
    entity = engine.TrackingEnemy()
    w = enemies_size[type][0]
    h = enemies_size[type][1]
    entity.position = engine.Position(x,y,w,h)
    enemyIddleAnimation = engine.Animation(enemies_animations[type]['idle'])
    enemyWalkingAnimation = engine.Animation(enemies_animations[type]['walking'])
    enemyHitAnimation = engine.Animation(enemies_animations[type]['hit'])
    entity.animations.add('idle', enemyIddleAnimation)
    entity.animations.add('walking', enemyWalkingAnimation)
    entity.animations.add('hit', enemyHitAnimation)
    entity.intention = None
    entity.type = type
    entity.speed = enemies_speed[type]
    entity.direction = 'right'
    entity.state = 'walking'
    entity.battle = engine.Battle(enemies_energy[type], enemies_energy[type])
    entity.start_x = x
    entity.start_y = y
    entity.tracking_distance = tracking_d
    entity.tracking_player = False
    entity.returning = False
    entity.impact_power = enemies_power[type]    
    return entity

def makeBossEnemy(x, y, type):
    entity = engine.BossEnemy()
    w = enemies_size[type][0]
    h = enemies_size[type][1]
    entity.position = engine.Position(x,y,w,h)
    enemyIddleAnimation = engine.Animation(enemies_animations[type]['idle'])
    enemyWalkingAnimation = engine.Animation(enemies_animations[type]['walking'])
    enemyHitAnimation = engine.Animation(enemies_animations[type]['hit'])
    enemyAttackAnimation = engine.Animation(enemies_animations[type]['attack'])

    entity.animations.add('idle', enemyIddleAnimation)
    entity.animations.add('walking', enemyWalkingAnimation)
    entity.animations.add('hit', enemyHitAnimation)
    entity.animations.add('attack', enemyAttackAnimation)

    entity.acceleration = 0.2
    entity.intention = None
    entity.type = type
    entity.speed = enemies_speed[type]
    entity.direction = 'right'
    entity.state = 'walking'
    entity.battle = engine.Battle(enemies_energy[type], enemies_energy[type])
    entity.health = enemies_energy[type]
    entity.max_health = enemies_energy[type]
    entity.phase = 1
    entity.attack_cooldown = 300
    entity.invulnerable = False
    #entity.invulnerable_time = 100  # Milisegundos de invulnerabilidad
    entity.last_hit_time = 0
    entity.aggro_distance = 200  # Distancia a la que el boss detecta al jugador
    entity.impact_power = enemies_power[type]

    return entity

idle0 = pygame.image.load('sprites/player/wonderboywalk35px1.png')

idle0 = pygame.transform.scale(idle0, (40,39))

idleShield0 = pygame.image.load('sprites/player/wonderboywalkShield35px1.png')

idleShield0 = pygame.transform.scale(idleShield0, (40,39))

idleArmor0 = pygame.image.load('sprites/player/wonderboyidlearmor35px1.png')

idleArmor0 = pygame.transform.scale(idleArmor0, (40,39))

jump0 = pygame.image.load('sprites/player/wonderboyjump35px.png')

jump0 = pygame.transform.scale(jump0, (40,39))

jumpShield0 = pygame.image.load('sprites/player/wonderboyjumpshield35px.png')

jumpShield0 = pygame.transform.scale(jumpShield0, (40,39))

jumpArmor0 = pygame.image.load('sprites/player/wonderboyjumparmor35px.png')

jumpArmor0 = pygame.transform.scale(jumpArmor0, (40,39))

attack0 = pygame.image.load('sprites/player/wonderboyattack35px.png')

attack0 = pygame.transform.scale(attack0, (40,39))

attackShield0 = pygame.image.load('sprites/player/wonderboyattackshield35px.png')

attackShield0 = pygame.transform.scale(attackShield0, (40,39))

attackArmor0 = pygame.image.load('sprites/player/wonderboyattackArmor35px.png')

attackArmor0 = pygame.transform.scale(attackArmor0, (40,39))

walking0 = pygame.image.load('sprites/player/wonderboywalk35px1.png')
walking1 = pygame.image.load('sprites/player/wonderboywalk35px2.png')
walking2 = pygame.image.load('sprites/player/wonderboywalk35px3.png')
walking3 = pygame.image.load('sprites/player/wonderboywalk35px4.png')

walkingShield0 = pygame.image.load('sprites/player/wonderboywalkShield35px1.png')
walkingShield1 = pygame.image.load('sprites/player/wonderboywalkShield35px2.png')
walkingShield2 = pygame.image.load('sprites/player/wonderboywalkShield35px3.png')
walkingShield3 = pygame.image.load('sprites/player/wonderboywalkShield35px4.png')

walkingArmor0 = pygame.image.load('sprites/player/wonderboywalkArmor35px1.png')
walkingArmor1 = pygame.image.load('sprites/player/wonderboywalkArmor35px2.png')
walkingArmor2 = pygame.image.load('sprites/player/wonderboywalkArmor35px3.png')
walkingArmor3 = pygame.image.load('sprites/player/wonderboywalkArmor35px4.png')

walking0 = pygame.transform.scale(walking0, (40,39))
walking1 = pygame.transform.scale(walking1, (40,39))
walking2 = pygame.transform.scale(walking2, (40,39))
walking3 = pygame.transform.scale(walking3, (40,39))

walkingShield0 = pygame.transform.scale(walkingShield0, (40,39))
walkingShield1 = pygame.transform.scale(walkingShield1, (40,39))
walkingShield2 = pygame.transform.scale(walkingShield2, (40,39))
walkingShield3 = pygame.transform.scale(walkingShield3, (40,39))

walkingArmor0 = pygame.transform.scale(walkingArmor0, (40,39))
walkingArmor1 = pygame.transform.scale(walkingArmor1, (40,39))
walkingArmor2 = pygame.transform.scale(walkingArmor2, (40,39))
walkingArmor3 = pygame.transform.scale(walkingArmor3, (40,39))

player_animations = {
    'idle' : [idle0],
    'idleShield' : [idleShield0],
    'idleArmor' : [idleArmor0],
    'walking' : [walking0,walking1,walking2,walking3],
    'walkingShield' : [walkingShield0,walkingShield1,walkingShield2,walkingShield3],
    'walkingArmor' : [walkingArmor0,walkingArmor1,walkingArmor2,walkingArmor3],
    'jump' : [jump0],
    'jumpShield' : [jumpShield0],
    'jumpArmor' : [jumpArmor0],
    'attack' : [attack0],
    'attackShield' : [attackShield0],
    'attackArmor' : [attackArmor0],
}

def resetPlayer(entity):
    entity.score.score = 0
    entity.battle = engine.Battle(100,100)
    entity.position.rect.x = 100
    entity.position.rect.y = 600
    entity.speed = 2
    entity.acceleration = 0.2
    #entity.camera.setWorldPos(300,0)
    entity.animations.alpha = 255
    entity.effect = None
    entity.cooldown = 3000
    entity.last_hit_time = 0
    entity.shield = False
    entity.armor = False
    entityIdleAnimation = engine.Animation(player_animations['idle'])
    entityWalkingAnimation = engine.Animation(player_animations['walking'])
    entityJumpAnimation = engine.Animation(player_animations['jump'])
    entityAttackAnimation = engine.Animation(player_animations['attack'])
    entity.animations.add('idle', entityIdleAnimation)
    entity.animations.add('walking', entityWalkingAnimation)
    entity.animations.add('jump', entityJumpAnimation)
    entity.animations.add('attack', entityAttackAnimation)

def makePlayer(x, y):
    entity = engine.Player()
    entity.position = engine.Position(x,y,40,39)
    entityIdleAnimation = engine.Animation(player_animations['idle'])
    entityWalkingAnimation = engine.Animation(player_animations['walking'])
    entityJumpAnimation = engine.Animation(player_animations['jump'])
    entityAttackAnimation = engine.Animation(player_animations['attack'])
    entity.animations.add('idle', entityIdleAnimation)
    entity.animations.add('walking', entityWalkingAnimation)
    entity.animations.add('jump', entityJumpAnimation)
    entity.animations.add('attack', entityAttackAnimation)
    entity.type = 'player'
    entity.score = engine.Score()
    entity.battle = engine.Battle(100, 100)
    entity.intention = engine.Intention()
    entity.acceleration = 0.2
    entity.reset = resetPlayer
    entity.impact_power = 10
    entity.shield = False
    entity.armor = False
    # Atributos para el disparo
    entity.last_shot_time = 0           # Tiempo del último disparo (inicialmente 0)
    entity.shoot_cooldown = 500         # 500 ms de cooldown entre disparos    
    return entity

pygame.font.init()
font = pygame.font.Font(pygame.font.get_default_font(),24)

def blit_alpha(target, source, location, opacity):
    x = location[0]
    y = location[1]
    temp = pygame.Surface((source.get_width(), source.get_height())).convert()
    temp.blit(target, (-x, -y))
    temp.blit(source, (0, 0))
    temp.set_alpha(opacity)
    target.blit(temp, location)

def drawText(screen, t, x, y, fg, alpha):
    text = font.render(t, True, fg)
    text_rectangle = text.get_rect()
    text_rectangle.topleft = (x,y)
    blit_alpha(screen, text, (x, y), alpha)
    
""" def center_collide(rect1, rect2, threshold):
    center1 = rect1.center
    center2 = rect2.center
    #distance = ((center1[0] - center2[0]) ** 2 + (center1[1] - center2[1]) ** 2) ** 0.5
    distance = ((center1[0] - center2[0]) ** 2) ** 0.5
    distance_y = False
    if abs(rect1.y - rect2.y) <= (rect1.h + rect2.h):
        distance_y = True
    return (distance < threshold) and distance_y
 """
def center_collide(rect1, rect2, threshold):
    collide = False
    if rect1.colliderect(rect2) and abs(rect1.x - rect2.x) >= threshold:
        collide = True
    return collide

def enable_movement(entity, new_pos_x, new_pos_y):
    new_x = new_pos_x
    new_y = new_pos_y
    print(new_x)
    # Horizontal movement
    new_x_rect = pygame.Rect(int(new_x), int(entity.position.rect.y), entity.position.rect.width, entity.position.rect.height)
    x_collision = False

    for platform in globals.world.platforms:
        platform_rect, _, collide = platform  # Unpack the tuple to get the rect
        if platform_rect.colliderect(new_x_rect) and collide:
            x_collision = True
            break
        
    if not x_collision:
        entity.position.rect.x = new_x

    # Vertical movement
    entity.speed += entity.acceleration
    new_y += entity.speed
    new_y_rect = pygame.Rect(int(entity.position.rect.x), int(new_y), entity.position.rect.width, entity.position.rect.height)
    y_collision = False
    entity.on_ground = False
    
    for platform in globals.world.platforms:
        platform_rect, _, collide = platform  # Unpack the tuple to get the rect
        if platform_rect.colliderect(new_y_rect) and collide:
            y_collision = True
            entity.speed = 0
            # Adjust to the top of the platform when falling
            if platform_rect.top > new_y:
                entity.position.rect.y = platform_rect.top - entity.position.rect.height
                entity.on_ground = True
            break

    # MovingPlatforms collitions
    for platform in globals.world.movingPlatforms:
        platform_rect = platform.position.rect  # Unpack the tuple to get the rect
        if platform_rect.colliderect(new_y_rect):
            y_collision = True
            entity.speed = 2
            # Adjust to the top of the platform when falling
            if platform_rect.top > new_y:
                entity.position.rect.y = platform_rect.top - entity.position.rect.height
                entity.on_ground = True
            if platform.type == 'lateral':
                entity.position.rect.x += platform.speed * platform.dir
            break

    if not y_collision:
        entity.position.rect.y = new_y

    #if x_collision or y_collision: 
    #    return False
    #else:
    #    return True


smith0 = pygame.image.load('sprites/npcs/smith.png')
smith1 = pygame.image.load('sprites/npcs/smith_sign.png')

npcs_types = ['smith']
npcs_size = {'smith':[30,60]}
npcs_animations = {'smith' : {
                                'idle' : [smith0],
                                'sign' : [smith1]
                                },
}

def makeNpc(x, y, type):
    entity = engine.Entity()
    w = npcs_size[type][0]
    h = npcs_size[type][1]
    entity.position = engine.Position(x,y,w,h)
    npcIddleAnimation = engine.Animation(npcs_animations[type]['idle'])
    npcSignAnimation = engine.Animation(npcs_animations[type]['sign'])
    entity.animations.add('idle', npcIddleAnimation)
    entity.animations.add('sign', npcSignAnimation)
    entity.intention = None
    entity.type = type
    entity.speed = 0
    entity.direction = 'right'
    entity.state = 'idle'
    entity.battle = None
    entity.impact_power = 0
    entity.cooldown = 50
    return entity

shop_items_images = {
    "shield" : pygame.image.load('sprites/shops/shield_shop.png'),
    "armor" : pygame.image.load('sprites/shops/armor_shop.png'),
    "boots" : pygame.image.load('sprites/shops/boots_shop.png'),
    "pants" : pygame.image.load('sprites/shops/pants_shop.png'),
}

shop_items_prices = {
    "shield" : 20,
    "armor" : 5,
    "boots" : 10,
    "pants" : 15,
}

def makeShopItem(place, type):
    item = engine.ShopItem()
    if place==1:
        item.position = engine.Position(10, 100, 64, 64)
        item.price_position = (25, 170)
    elif place==2:
        item.position = engine.Position(84, 100, 64, 64)
        item.price_position = (99, 170)
    else:
        item.position = engine.Position(158, 100, 64, 64)
        item.price_position = (173, 170)
    item.image = shop_items_images[type]
    item.price = shop_items_prices[type]
    return item

def makeProjectile(x, y, direction, speed, damage, lifetime=60, owner=None):
    # Supongamos que el tamaño del proyectil es de 8x8 píxeles.
    image = pygame.image.load('sprites/projectiles/projectile.png')
    projectile = engine.Projectile(x, y, 20, 20, direction, speed, damage, lifetime, image, owner)
    # Si tienes animaciones específicas para proyectiles, las puedes agregar aquí:
    # projectile.animations.add('idle', Animation([tu_imagen_del_proyectil]))
    return projectile