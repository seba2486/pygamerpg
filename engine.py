import pygame
import utils
import globals
import csv
from platform import platform
import random


class System():
    def __init__(self):
        pass
    
    def check(self, entity):
        return True
    
    def update(self, screen=None, inputStream = None):
        for entity in globals.world.entities:
            if self.check(entity):
                self.updateEntity(screen, inputStream, entity)

    def updateEntity(self, screen, inputStream, entity):
        pass

class PlayerAttackSystem(System):
    def check(self, entity):
        # Filtrar solo a los enemigos que pueden atacar
        return entity is not None and entity.intention is not None and entity.intention.attack

    def update(self, screen=None, inputStream=None):
        if self.check(globals.player1):
            self.updateEntity(screen, inputStream, globals.player1)

    def updateEntity(self, screen, inputStream, player):
        self.attack(player, inputStream)

    def attack(self, player, inputStream):
        current_time = pygame.time.get_ticks()
        if current_time - player.last_attack_time >= player.attack_weapon.cooldown:
            player.attack_weapon.attack(player)            
            # Actualizar el tiempo del último disparo
            player.last_attack_time = current_time

        if player.last_attack_time > 0:
            player.last_attack_time -= 1

class EnemyAttackSystem(System):
    def check(self, entity):
        # Filtrar solo a los enemigos que pueden atacar
        return entity is not None and entity.type == "devil"

    def update(self, screen=None, inputStream=None):
        # Iteramos sobre una copia de la lista para evitar modificarla durante el recorrido
        for enemy in list(globals.world.entities):
            if self.check(enemy):
                self.updateEntity(screen, inputStream, enemy)

    def updateEntity(self, screen, inputStream, enemy):
        # Si el enemigo está caminando, evaluamos si debe atacar
        if enemy.state == 'walking':
            # Con una probabilidad pequeña (por ejemplo, 1% por frame) decide atacar
            if random.random() < 0.01:
                enemy.state = 'idle'
                #enemy.speed = 0  # Detener su movimiento
                # Crear el proyectil
                projectile = utils.makeProjectile(
                    enemy.position.rect.x,
                    enemy.position.rect.y - 13,
                    enemy.direction,  # Puedes ajustar según la dirección del enemigo
                    speed=4,
                    damage=enemy.impact_power,
                    lifetime=120,  # Por ejemplo, 120 frames de vida
                    owner=enemy
                )
                globals.world.projectiles.append(projectile)
                # Establecer un temporizador de ataque para mantener el estado "idle"
                enemy.attack_cooldown = 60  # 60 frames (1 segundo a 60 fps)

        # Si el enemigo está en estado "idle", decrementamos el temporizador
        elif enemy.state == 'idle' and enemy.attack_cooldown > 0:
            enemy.attack_cooldown -= 1
            if enemy.attack_cooldown <= 0:
                enemy.state = 'walking'
                # Asigna aleatoriamente una dirección y restablece la velocidad
                enemy.direction = random.choice(["left", "right"])
                enemy.speed = utils.enemies_speed[enemy.type]

class BossAttackSystem(System):
    def check(self, entity):
        return isinstance(entity, BossEnemy) and entity.state == 'walking'

    def update(self, screen=None, inputStream = None):
        if self.check(globals.world.boss):
            self.updateEntity(screen, inputStream, globals.world.boss)
    
    #Agregar seleccion de ataque
    def updateEntity(self, screen, inputStream, entity):
        if entity.attack_weapon.cooldown > 0:
            entity.attack_weapon.cooldown -= 1
            if entity.attack_weapon.cooldown < 200:
                entity.state = 'walking'
                entity.intention.attack = False
        else:
            print('attack')
            if entity.is_player_within_aggro_distance(globals.player1):
                entity.intention.attack = True
                entity.state = 'attack'
                if entity.attack_weapon.cooldown == 0:
                    entity.attack_weapon = random.choice(entity.attack_weapons)
                    entity.attack_weapon.cooldown = utils.weaponsParams[entity.attack_weapon.name]['cooldown']              
                entity.attack_weapon.attack(entity)
                entity.attack_cooldown = entity.attack_weapon.cooldown




class TrackingEnemySystem(System):
    def check(self, entity):
        return isinstance(entity, TrackingEnemy)
    
    def update(self, screen=None, inputStream=None):
        for entity in globals.world.trackingEnemies:
            if self.check(entity):
                self.updateEntity(screen, inputStream, entity)

    def updateEntity(self, screen, inputStream, entity):
        player = globals.player1
        dist_x = abs(entity.position.rect.x - player.position.rect.x)
        dist_y = abs(entity.position.rect.y - player.position.rect.y - 10)

        if not entity.tracking_player and not entity.returning:
            if dist_x <= entity.tracking_distance and dist_y <= entity.tracking_distance:
                entity.tracking_player = True
        
        if entity.tracking_player:
            self.move_towards(entity, player.position.rect.x, player.position.rect.y)
            if entity.position.rect.colliderect(player.position.rect) or (dist_x > entity.tracking_distance) or (dist_y > entity.tracking_distance):
                entity.tracking_player = False
                entity.returning = True
                TrackingEnemySystem.hit(player, entity)

        if entity.returning:
            self.move_towards(entity, entity.start_x, entity.start_y)
            if entity.position.rect.x == entity.start_x and entity.position.rect.y == entity.start_y:
                entity.returning = False
    
    def hit(entity, otherEntity):
        threshold = 5  # Puedes ajustar este valor según sea necesario
        now = pygame.time.get_ticks()
        invisible = False
        shield = True
        if entity.effect != None:
            if entity.effect.type == 'invisible':
                invisible = True
        # Si colisiona, el player esta en idle y el shield esta en la direccion opuesta del enemy, el enemy rebota
        if shield and entity.state == 'idle' and entity.direction != otherEntity.direction:
            if entity.direction == "right":
                utils.enable_movement(otherEntity, otherEntity.position.rect.x + 40, otherEntity.position.rect.y - 15)
            else:
                utils.enable_movement(otherEntity, otherEntity.position.rect.x - 40, otherEntity.position.rect.y - 15)
        else:
            if now - entity.last_hit_time > entity.cooldown and not invisible:
                globals.soundManager.playSound('player_receive_damage')
                entity.battle.energy -= otherEntity.impact_power
                if entity.direction == "right":
                    utils.enable_movement(entity, entity.position.rect.x + 30, entity.position.rect.y - 15)
                else:
                    utils.enable_movement(entity, entity.position.rect.x - 30, entity.position.rect.y - 15)
                entity.speed = 2
                entity.last_hit_time = now
                if entity.animations:
                    entity.animations.alpha = 50
                #entity.last_hit_time = now

    def move_towards(self, entity, target_x, target_y):
        if entity.position.rect.x < target_x:
            entity.position.rect.x += entity.speed
        elif entity.position.rect.x > target_x:
            entity.position.rect.x -= entity.speed
        
        if entity.position.rect.y < target_y:
            entity.position.rect.y += entity.speed
        elif entity.position.rect.y > target_y:
            entity.position.rect.y -= entity.speed

class MovingPlatformSystem(System):
    def check(self, entity):
        return entity is not None

    def update(self, screen=None, inputStream = None):
        for movingPlatform in globals.world.movingPlatforms:
            if self.check(movingPlatform):
                self.updateEntity(screen, inputStream, movingPlatform)

    def updateEntity(self, screen, inputStream, entity):
        # Vertical starts from bottom
        # Lateral starts from right
        if entity.type == 'vertical':
            entity.position.rect.y += entity.speed * entity.dir
            if entity.position.rect.y <= entity.max_height:
                entity.dir = 1  # Cambiar dirección a abajo
            elif entity.position.rect.y >= entity.start_y:
                entity.dir = -1  # Cambiar dirección a arriba
        else:
            entity.position.rect.x += entity.speed * entity.dir
            if entity.position.rect.x <= entity.max_height:
                entity.dir = 1  # Cambiar dirección a derecha
            elif entity.position.rect.x >= entity.start_x:
                entity.dir = -1  # Cambiar dirección a izquierda

class PowerUpSystem(System):
    def __init__(self):
        System.__init__(self)
        self.timer = 0
    
    def check(self, entity):
        return entity.effect is not None
    
    def update(self, screen=None, inputStream=None):
        System.update(self, screen=screen, inputStream=inputStream)
        # Count number of powerups in world
        # count = 0
        # for entity in globals.world.entities:
        #     if entity.type != 'player':
        #         if entity.effect:
        #             count += 1
        #
        # # If none start timer to create
        # if count == 0 and self.timer == 0:
        #     self.timer = 500
        # # Create one if its time
        # if self.timer > 0:
        #     # Decrement timer
        #     self.timer -= 1
        #     if self.timer <= 0:
        #         # spawn powerup
        #         if globals.world.powerupSpawnPoints is not None:
        #             if len(globals.world.powerupSpawnPoints) > 0:
        #                 spawnPos = random.choice(globals.world.powerupSpawnPoints)
        #                 globals.world.entities.append(
        #                     utils.makePowerUp(random.choice(utils.powerups), spawnPos[0], spawnPos[1])
        #                 )
                        
    def updateEntity(self, screen, inputStream, entity):
        # Collect PowerUp
        for otherEntity in globals.world.entities:
            if otherEntity is not entity and entity.type == 'powerup' and otherEntity.type == 'player':
                if entity.position.rect.colliderect(otherEntity.position.rect):
                    #give effect component to player
                    otherEntity.effect = entity.effect
                    globals.soundManager.playSound(entity.effect.sound)
                    #remove the collected powerup
                    globals.world.entities.remove(entity)
        
        # Apply powerUP
        if entity.type == 'player' and entity.effect is not None:
            entity.effect.apply(entity)
            entity.effect.timer -=1
            # If the effect runs out            
            if entity.effect.timer <= 0:
                # Reset entity if appropiate
                if entity.effect.end:
                    entity.effect.end(entity)
                # Destroy the Effect
                entity.effect = None        

class AnimationSystem(System):
    def check(self, entity):
        return entity is not None and entity.animations is not True
    
    def update(self, screen=None, inputStream = None):
        for entity in globals.world.entities:
            if self.check(entity):
                self.updateEntity(screen, inputStream, entity)

        for entity in globals.world.trackingEnemies:
            if self.check(entity):
                self.updateEntity(screen, inputStream, entity)
        
        if self.check(globals.world.boss):
            self.updateEntity(screen, inputStream, globals.world.boss)

    def updateEntity(self, screen, inputStream, entity):
        entity.animations.animationList[entity.state].update()

class PhysicsSystem(System):
    def check(self, entity):
        return entity.position is not None

    def updateEntity(self, screen, inputStream, entity):
        new_x = entity.position.rect.x
        new_y = entity.position.rect.y
        
        if entity.intention is not None and entity.type not in utils.enemies_types:
            if entity.intention.moveLeft:
                new_x -= 2
                entity.direction = 'left'
                if entity.on_ground:
                    entity.state = 'walking'
            if entity.intention.moveRight:
                new_x += 2
                entity.direction = 'right'
                if entity.on_ground:
                    entity.state = 'walking'
            if not entity.intention.moveLeft and not entity.intention.moveRight and entity.on_ground:
                entity.state = 'idle'
            if entity.intention.jump and entity.on_ground:
                globals.soundManager.playSound('jump')
                entity.state = 'jump'
                entity.speed = -5
            if entity.intention.attack and entity.attack_weapon.cooldown == 300:
                globals.soundManager.playSound('sword_swoosh')
                entity.state = 'attack'
        
        # Horizontal movement
        new_x_rect = pygame.Rect(int(new_x), int(entity.position.rect.y), entity.position.rect.width, entity.position.rect.height)
        x_collision = False

        if entity.position.rect.left < 0:
            entity.position.rect.left = 0
        elif entity.position.rect.right > globals.WORLD_WIDTH:
            entity.position.rect.right = globals.WORLD_WIDTH


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
                #entity.speed = 2
                # Adjust to the top of the platform when falling
                if platform_rect.top > new_y:
                    entity.position.rect.y = platform_rect.top - entity.position.rect.height
                    entity.on_ground = True
                if platform.type == 'lateral':
                    entity.position.rect.x += platform.speed * platform.dir
                break


        if not y_collision:
            entity.position.rect.y = int(new_y)

        if entity.position.rect.top < 0:
            entity.position.rect.top = 0
        elif entity.position.rect.bottom > globals.WORLD_HEIGHT:
            entity.position.rect.bottom = globals.WORLD_HEIGHT


        # Manejo de movimiento aleatorio para entidades enemies
        if entity.type in utils.enemies_types and entity.state=='walking': 
            self.random_move(entity, x_collision, y_collision)
            
   
    def random_move(self, entity, x_collision, y_collision):
        
        entity.speed = utils.enemies_speed[entity.type]
        if not x_collision: 
            self.direction = random.choice(["left", "right"])  # Elegir una nueva dirección aleatoria
            # Mover el enemigo en la dirección actual
            if entity.direction == "left":
                entity.position.rect.x -= entity.speed
            elif entity.direction == "right":
                entity.position.rect.x += entity.speed
            
            # Mantener al enemigo dentro de los límites de la pantalla
            if entity.position.rect.right > globals.WORLD_WIDTH or entity.position.rect.left < 0:
                entity.position.rect.x = max(0, min(entity.position.rect.x, globals.WORLD_WIDTH - entity.position.rect.width))
                entity.direction = "left" if entity.direction == "right" else "right"  # Cambiar de dirección si toca un borde horizontal
        else:
            if entity.direction == "left":
                entity.direction = "right"
                entity.position.rect.x += entity.speed
            elif entity.direction == "right":
                entity.direction = "left"
                entity.position.rect.x -= entity.speed
           
class BossPhysicsSystem():
    def check(self, entity):
        return entity is not None and entity.position is not None
    
    def update(self, screen=None, inputStream=None):
        if self.check(globals.world.boss):
            self.updateEntity(globals.world.boss)

    def updateEntity(self, entity):

        player = globals.player1

        new_x = entity.position.rect.x
        new_y = entity.position.rect.y

        if entity.state=='walking' and entity.is_player_within_aggro_distance(player):
            
            if entity.position.rect.x < player.position.rect.x:
                new_x = entity.position.rect.x + entity.speed
                entity.direction = 'right'
            elif entity.position.rect.x > player.position.rect.x:
                new_x = entity.position.rect.x - entity.speed
                entity.direction = 'left'
            
            if entity.position.rect.y < player.position.rect.y:
                new_y = entity.position.rect.y + entity.speed
            elif entity.position.rect.y > player.position.rect.y:
                new_y = entity.position.rect.y - entity.speed
#        elif entity.state=='walking':
#            dir = random.choice([1,-1])
#            if dir == 1: 
#                entity.direction = 'right' 
#            else: 
#                entity.direction = 'left'
#            new_x = entity.position.rect.x + (entity.speed * dir)

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

        if entity.position.rect.left < 0:
            entity.position.rect.left = 0
        elif entity.position.rect.right > globals.WORLD_WIDTH:
            entity.position.rect.right = globals.WORLD_WIDTH

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
                entity.speed = utils.enemies_speed['boss']
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
                entity.speed = utils.enemies_speed['boss']
                # Adjust to the top of the platform when falling
                if platform_rect.top > new_y:
                    entity.position.rect.y = platform_rect.top - entity.position.rect.height
                    entity.on_ground = True
                if platform.type == 'lateral':
                    entity.position.rect.x += platform.speed * platform.dir
                break


        if not y_collision:
            entity.position.rect.y = int(new_y)

        if entity.position.rect.top < 0:
            entity.position.rect.top = 0
        elif entity.position.rect.bottom > globals.WORLD_HEIGHT:
            entity.position.rect.bottom = globals.WORLD_HEIGHT

class InputSystem(System):
    def check(self, entity):
        return entity.input is not None and entity.intention is not None
    
    def updateEntity(self, screen, inputStream, entity):
        if inputStream.keyboard.isKeyDown(entity.input.up):
            entity.intention.jump = True
        else:
            entity.intention.jump = False

        if inputStream.keyboard.isKeyDown(entity.input.down):
            entity.intention.down = True
        else:
            entity.intention.down = False

        if inputStream.keyboard.isKeyDown(entity.input.left):
            entity.intention.moveLeft = True
        else:
            entity.intention.moveLeft = False

        if inputStream.keyboard.isKeyDown(entity.input.right):
            entity.intention.moveRight = True
        else:
            entity.intention.moveRight = False

        if inputStream.keyboard.isKeyDown(entity.input.b1):
            entity.intention.zoomOut = True
        else:
            entity.intention.zoomOut = False

        if inputStream.keyboard.isKeyDown(entity.input.b2):
            entity.intention.zoomIn = True
        else:
            entity.intention.zoomIn = False

        if inputStream.keyboard.isKeyDown(entity.input.attack):
            entity.intention.attack = True
        else:
            entity.intention.attack = False

class CollectionSystem (System):
    def check(self, entity):
        return entity.type == 'player' and entity.score is not None
 
    def updateEntity(self, screen, inputStream, entity):
        for otherEntity in globals.world.entities:
            if self.check(entity):
                if otherEntity is not entity and otherEntity.type == 'collectable':
                    #entity.collectable.onCollide(entity, otherEntity)
                    if entity.position.rect.colliderect(otherEntity.position.rect):
                        globals.soundManager.playSound('coin')
                        globals.world.entities.remove(otherEntity)
                        coins_value = (5, 10, 20)
                        entity.score.score += random.choice(coins_value)

class BattleSystem(System):
    def check(self, entity):
        return entity.type == 'player' and entity.battle is not None

    def power_up_drop(entity, pu_pos_x, pu_pos_y):
        if entity.type != 'boss':    
            utils.powerups.remove('key')
            utils.powerups.remove('shield')
            globals.world.entities.append(utils.makePowerUp(random.choice(utils.powerups), pu_pos_x , pu_pos_y))
            utils.powerups.append('key')
            utils.powerups.append('shield')
        else:
            globals.world.entities.append(utils.makePowerUp('key', pu_pos_x , pu_pos_y))

    def updateEntity(self, screen, inputStream, entity):

        # Enemies Regular
        for otherEntity in globals.world.entities:
            # Player colisiona con Enemy
            if otherEntity is not entity and otherEntity.type in utils.enemies_types:
                threshold = 5  # Puedes ajustar este valor según sea necesario
                now = pygame.time.get_ticks()
                if utils.center_collide(entity.position.rect, otherEntity.position.rect, threshold):
                #if entity.position.rect.colliderect(otherEntity.position.rect):                    
                    invisible = False
                    if entity.effect != None:
                        if entity.effect.type == 'invisible':
                            invisible = True
                    # Si colisiona, el player esta en idle y el shield esta en la direccion opuesta del enemy, el enemy rebota
                    if entity.shield and entity.state == 'idle' and entity.direction != otherEntity.direction:

                        if entity.direction == "right":
                            utils.enable_movement(otherEntity, otherEntity.position.rect.x + 40, otherEntity.position.rect.y - 15)
                        else:
                            utils.enable_movement(otherEntity, otherEntity.position.rect.x - 40, otherEntity.position.rect.y - 15)

                    else:
                        if now - entity.last_hit_time > entity.cooldown and not invisible:
                            globals.soundManager.playSound('player_receive_damage')
                            entity.battle.energy -= otherEntity.impact_power

                            if entity.direction == "right":
                                utils.enable_movement(entity, entity.position.rect.x + 30, entity.position.rect.y - 15)
                            else:
                                utils.enable_movement(entity, entity.position.rect.x - 30, entity.position.rect.y - 15)

                            entity.speed = 2
                            entity.last_hit_time = now

                            if entity.animations:
                                entity.animations.alpha = 50
                            entity.last_hit_time = now
                
                # Si el enemigo esta en estado 'hit' y su cooldown es mayor a 0, decrementar el cooldown vuelve a caminar si no acaba de disparar
                if otherEntity.state == 'hit' and otherEntity.cooldown > 0:
                    otherEntity.cooldown -= 1
                else:
                    if otherEntity.cooldown <= 0:    
                        otherEntity.state = 'walking'
                        otherEntity.cooldown = 50

                if entity.intention.attack and utils.center_collide(entity.hitbox, otherEntity.position.rect, threshold):
                #if entity.hitbox.colliderect(otherEntity.position.rect):
                    globals.soundManager.playSound('enemy_takes_damage')
                    otherEntity.state = 'hit'
                    entity.hitbox = pygame.Rect(0, 0, 0, 0)
                    otherEntity.battle.energy -= entity.impact_power

                    if otherEntity.battle.energy == 0:
                        otherEntity.active = False
                        if entity.direction == 'left':   
                            pu_pos_x = otherEntity.position.rect.x
                        else:
                            pu_pos_x = otherEntity.position.rect.x + 15
                        pu_pos_y = otherEntity.position.rect.y - 15
                        BattleSystem.power_up_drop (otherEntity, pu_pos_x, pu_pos_y)
                        globals.world.entities.remove(otherEntity)
                    else:
                        if entity.direction == "right":
                            utils.enable_movement(otherEntity, otherEntity.position.rect.x + 40, otherEntity.position.rect.y - 15)
                        else:
                            utils.enable_movement(otherEntity, otherEntity.position.rect.x - 40, otherEntity.position.rect.y - 15)
            
            
            # Player es impactado por projectile enemigo
            self.projectile_impact_player(entity)

            # Player impacta enemigo estandar con projectile
            self.projectile_impact(otherEntity, entity, globals.world.entities)

            #Player colisiona con Spike            
            if otherEntity is not entity and otherEntity.type == 'spike':
                now = pygame.time.get_ticks()
                invisible = False
                if entity.effect != None:
                    if entity.effect.type == 'invisible':
                        invisible = True
                if otherEntity.position.rect.colliderect(entity.position.rect) and not invisible:
                    if now - entity.last_hit_time > entity.cooldown:
                        globals.soundManager.playSound('player_receive_damage')
                        entity.battle.energy -= otherEntity.impact_power
                        entity.speed = 2
                        if entity.direction == "right":
                            utils.enable_movement(entity, entity.position.rect.x + 10, entity.position.rect.y - 32)
                        else:
                            utils.enable_movement(entity, entity.position.rect.x - 10, entity.position.rect.y - 32)

                        entity.last_hit_time = now
                        #entity.effect = Effect(utils.setInvisible, 300, None , utils.endInvisible)
                        #entity.cooldown = 300
                        if entity.animations:
                            entity.animations.alpha = 50
                        entity.last_hit_time = now

        # Enemies Tracking
        for otherEntity in globals.world.trackingEnemies:
            # Player colisiona con Enemy
            if otherEntity is not entity:
                threshold = 5  # Puedes ajustar este valor según sea necesario
                now = pygame.time.get_ticks()
                #if utils.center_collide(entity.position.rect, otherEntity.position.rect, threshold):
                if entity.position.rect.colliderect(otherEntity.position.rect):
                    invisible = False
                    if entity.effect != None:
                        if entity.effect.type == 'invisible':
                            invisible = True
                    if now - entity.last_hit_time > entity.cooldown and not invisible:
                        globals.soundManager.playSound('player_receive_damage')
                        entity.battle.energy -= otherEntity.impact_power
                        print('hit')
                        if entity.direction == "right":
                            utils.enable_movement(entity, entity.position.rect.x + 30, entity.position.rect.y - 15)
                        else:
                            utils.enable_movement(entity, entity.position.rect.x - 30, entity.position.rect.y - 15)

                        entity.speed = 2
                        entity.last_hit_time = now
                        #entity.effect = Effect(utils.setInvisible, 300, None , utils.endInvisible)
                        #entity.cooldown = 300
                        if entity.animations:
                            entity.animations.alpha = 50
                        entity.last_hit_time = now
                
                if otherEntity.state == 'hit' and otherEntity.cooldown > 0:
                    otherEntity.cooldown -= 1
                else:
                    otherEntity.state = 'walking'
                    otherEntity.cooldown = 50

                #if entity.intention.attack and utils.center_collide(entity.hitbox, otherEntity.position.rect, threshold):
                if entity.intention.attack and otherEntity.position.rect.colliderect(entity.hitbox):
                    globals.soundManager.playSound('enemy_takes_damage')
                    otherEntity.state = 'hit'
                    entity.hitbox = pygame.Rect(0, 0, 0, 0)
                    otherEntity.battle.energy -= entity.impact_power
                    if otherEntity.battle.energy == 0:
                        otherEntity.active = False
                        if entity.direction == 'left':   
                            pu_pos_x = otherEntity.position.rect.x
                        else:
                            pu_pos_x = otherEntity.position.rect.x + 15
                        pu_pos_y = otherEntity.position.rect.y - 15
                        BattleSystem.power_up_drop(otherEntity, pu_pos_x, pu_pos_y)
                        globals.world.trackingEnemies.remove(otherEntity)
                    else:
                        if entity.direction == "right":
                            utils.enable_movement(otherEntity, otherEntity.position.rect.x + 40, otherEntity.position.rect.y - 15)
                        else:
                            utils.enable_movement(otherEntity, otherEntity.position.rect.x - 40, otherEntity.position.rect.y - 15)
                    otherEntity.state = 'hit'

            # Player impacta enemigo tracking con projectile
            self.projectile_impact(otherEntity, entity, globals.world.trackingEnemies)

            if now - entity.last_hit_time > entity.cooldown:
                if entity.animations:
                    entity.animations.alpha = 255

    # Impacto de proyectiles en enemigos
    def projectile_impact(self, otherEntity, entity, impactedList):
        # Impactos de projectiles en enemigos estandar
        for projectile in globals.world.projectiles:
            if otherEntity.type in utils.enemies_types:
                if projectile.position.rect.colliderect(otherEntity.position.rect) and projectile.owner != otherEntity:
                    globals.soundManager.playSound('enemy_takes_damage')
                    otherEntity.state = 'hit'
                    entity.hitbox = pygame.Rect(0, 0, 0, 0)
                    otherEntity.battle.energy -= entity.impact_power

                    if otherEntity.battle.energy == 0:
                        otherEntity.active = False
                        if entity.direction == 'left':   
                            pu_pos_x = otherEntity.position.rect.x
                        else:
                            pu_pos_x = otherEntity.position.rect.x + 15
                        pu_pos_y = otherEntity.position.rect.y - 15
                        BattleSystem.power_up_drop (otherEntity, pu_pos_x, pu_pos_y)
                        impactedList.remove(otherEntity)
                    else:
                        if entity.direction == "right":
                            utils.enable_movement(otherEntity, otherEntity.position.rect.x + 40, otherEntity.position.rect.y - 15)
                        else:
                            utils.enable_movement(otherEntity, otherEntity.position.rect.x - 40, otherEntity.position.rect.y - 15)
                    # Remover el proyectil una vez que impacta
                    if projectile in globals.world.projectiles:
                        globals.world.projectiles.remove(projectile)

    # Impacto de proyectiles de enemigos en player
    def projectile_impact_player(self, entity):
        # Impactos de projectiles en enemigos estandar
        for projectile in globals.world.projectiles:
            now = pygame.time.get_ticks()
            if projectile.position.rect.colliderect(entity.position.rect) and projectile.owner != entity:
                invisible = False
                if entity.effect != None:
                    if entity.effect.type == 'invisible':
                        invisible = True
                # Si colisiona, el player esta en idle y el shield esta en la direccion opuesta del enemy, el enemy rebota
                if entity.shield and entity.state == 'idle' and entity.direction != projectile.direction:

                    if entity.direction == "right":
                        utils.enable_movement(projectile, entity.position.rect.x + 40, entity.position.rect.y - 15)
                    else:
                        utils.enable_movement(projectile, entity.position.rect.x - 40, entity.position.rect.y - 15)

                else:
                    if now - entity.last_hit_time > entity.cooldown and not invisible:
                        globals.soundManager.playSound('player_receive_damage')
                        entity.battle.energy -= projectile.damage

                        if entity.direction == "right":
                            utils.enable_movement(entity, entity.position.rect.x + 30, entity.position.rect.y - 15)
                        else:
                            utils.enable_movement(entity, entity.position.rect.x - 30, entity.position.rect.y - 15)

                        entity.speed = 2
                        entity.last_hit_time = now

                        if entity.animations:
                            entity.animations.alpha = 50
                        entity.last_hit_time = now

                # Remover el proyectil una vez que impacta
                if projectile in globals.world.projectiles:
                    globals.world.projectiles.remove(projectile)

# Actualizar el sistema de batalla del jefe para que funcione con el nuevo sistema de batalla
class BossBattleSystem():
    def check(self, entity):
        return entity is not None and entity.battle is not None

    def power_up_drop(entity, pu_pos_x, pu_pos_y):
        globals.world.entities.append(utils.makePowerUp('key', pu_pos_x , pu_pos_y))

    def update(self):
        if self.check(globals.world.boss):
            self.updateEntity(globals.world.boss)

    def updateEntity(self, entity):

        player = globals.player1
        boss = globals.world.boss
        #boss_attack = False

        if boss.last_hit_time <= 0:
            boss.invulnerable = False
            boss.state = 'walking'
        else:
            if boss.last_hit_time > 0:
                boss.last_hit_time -= 1
                boss.state = 'hit'
                boss.invulnerable = True

        # Player colisiona con Boss
        threshold = 5  # Ajustar este valor según sea necesario
        now = pygame.time.get_ticks()
        

        #Refrescar el tipo de arma para ver si es distancia o melee
        if boss.state == 'attack':

            if  boss.attack_weapon.hitbox.colliderect(player.position.rect) and boss.attack_weapon.cooldown == 300:
                print("Boss melee attack hit the player!")
                invisible = False
                if player.effect != None:
                    if player.effect.type == 'invisible':
                        invisible = True

                if now - player.last_hit_time > player.cooldown and not invisible:
                    globals.soundManager.playSound('player_receive_damage')
                    player.battle.energy -= boss.impact_power
                    if boss.direction == "right":
                        utils.enable_movement(player, player.position.rect.x + 30, player.position.rect.y - 15)
                    else:
                        utils.enable_movement(player, player.position.rect.x - 30, player.position.rect.y - 15)
                    player.speed = 2
                    player.last_hit_time = now
                    if player.animations:
                        player.animations.alpha = 50

 
        if utils.center_collide(player.position.rect, boss.position.rect, threshold):
        #if player.position.rect.colliderect(boss.position.rect):                    
            invisible = False
            if player.effect != None:
                if player.effect.type == 'invisible':
                    invisible = True

            # Si colisiona, el player esta en idle y el shield esta en la direccion opuesta del boss, el boss rebota
            if player.shield and player.state == 'idle' and player.direction != boss.direction:
                if player.direction == "right":
                    utils.enable_movement(boss, boss.position.rect.x + 40, boss.position.rect.y - 15)
                else:
                    utils.enable_movement(boss, boss.position.rect.x - 40, boss.position.rect.y - 15)
            else:
                if now - player.last_hit_time > player.cooldown and not invisible:
                    globals.soundManager.playSound('player_receive_damage')
                    player.battle.energy -= boss.impact_power
                    if boss.direction == "right":
                        utils.enable_movement(player, player.position.rect.x + 30, player.position.rect.y - 15)
                    else:
                        utils.enable_movement(player, player.position.rect.x - 30, player.position.rect.y - 15)
                    player.speed = 2
                    player.last_hit_time = now
                    if player.animations:
                        player.animations.alpha = 50
        
        if boss.invulnerable == False:     
            # Player impacta boss       
            if boss.invulnerable == False and player.intention.attack and utils.center_collide(player.attack_weapon.hitbox, boss.position.rect, threshold):
            #if entity.hitbox.colliderect(otherEntity.position.rect):
                globals.soundManager.playSound('enemy_takes_damage')
                player.hitbox = pygame.Rect(0, 0, 0, 0)
                boss.take_damage(player.attack_weapon.power)
                print('sword power', player.attack_weapon.power)

                print('boss ener', boss.battle.energy)

                if boss.battle.energy == 0:
                    boss.active = False
                    if player.direction == 'left':   
                        pu_pos_x = boss.position.rect.x
                    else:
                        pu_pos_x = boss.position.rect.x + 15
                    pu_pos_y = boss.position.rect.y - 15
                    BattleSystem.power_up_drop (boss, pu_pos_x, pu_pos_y)
                    globals.world.boss = None
                else:
                    boss.last_hit_time = 100
                    boss.state = 'hit'
                    if player.direction == "right":
                        utils.enable_movement(boss, boss.position.rect.x + 40, boss.position.rect.y - 15)
                    else:
                        utils.enable_movement(boss, boss.position.rect.x - 40, boss.position.rect.y - 15)
                    
            # Player impacta boss con projectile
            for projectile in globals.world.projectiles:
                if projectile.owner != boss and projectile.position.rect.colliderect(boss.position.rect):
                    globals.soundManager.playSound('enemy_takes_damage')
                    player.hitbox = pygame.Rect(0, 0, 0, 0)
                    boss.take_damage(player.attack_weapon.power)

                    if boss.battle.energy == 0:
                        boss.active = False
                        if player.direction == 'left':   
                            pu_pos_x = boss.position.rect.x
                        else:
                            pu_pos_x = boss.position.rect.x + 15
                        pu_pos_y = boss.position.rect.y - 15
                        BattleSystem.power_up_drop (boss, pu_pos_x, pu_pos_y)
                        globals.world.boss = None
                    else:
                        boss.last_hit_time = 100
                        boss.state = 'hit'
                        if player.direction == "right":
                            utils.enable_movement(boss, boss.position.rect.x + 40, boss.position.rect.y - 15)
                        else:
                            utils.enable_movement(boss, boss.position.rect.x - 40, boss.position.rect.y - 15)

                    # Remover el proyectil una vez que impacta
                    if projectile in globals.world.projectiles:
                        globals.world.projectiles.remove(projectile)
        
        
        if now - player.last_hit_time > player.cooldown:
            if player.animations:
                player.animations.alpha = 255

class CameraSystem(System):
    def check(self, entity):
        return entity.input is not None and entity.camera is not None

    def updateEntity(self, screen, inputStream, entity):
        if entity.camera:
            entity.camera.update()  # Asegura que la posición de la cámara está actualizada

            offsetX = -entity.camera.rect.x
            offsetY = -entity.camera.rect.y
            
            #Render Shop
            screen.blit(pygame.image.load('sprites/shops/shop.png'), ((54*globals.TILE_SIZE) + 10 + offsetX,(14*globals.TILE_SIZE) + 30 + offsetY))

            #Render Npc
            if globals.world.npc:
                e = globals.world.npc
                s = e.state
                a = e.animations.animationList[s]
                a.draw(screen, 
                        (e.position.rect.x) + offsetX, 
                        (e.position.rect.y) + offsetY,
                        e.direction == 'left', 
                        False, 
                        entity.camera.zoomLevel,
                        e.animations.alpha
                )

            #Render Entities
            for e in globals.world.entities:
                if e.active:
                    s = e.state
                    a = e.animations.animationList[s]
                    a.draw(screen, 
                           (e.position.rect.x) + offsetX, 
                           (e.position.rect.y) + offsetY,
                           e.direction == 'left', 
                           False, 
                           entity.camera.zoomLevel,
                           e.animations.alpha
                    )

            #Render Tracking Entities
            for e in globals.world.trackingEnemies:
                if e.active:
                    s = e.state
                    a = e.animations.animationList[s]
                    a.draw(screen, 
                           (e.position.rect.x) + offsetX, 
                           (e.position.rect.y) + offsetY,
                           e.direction == 'left', 
                           False, 
                           entity.camera.zoomLevel,
                           e.animations.alpha
                    )

            #Render Boss
            if globals.world.boss:
                e = globals.world.boss
                s = e.state
                a = e.animations.animationList[s]
                a.draw(screen, 
                        (e.position.rect.x) + offsetX, 
                        (e.position.rect.y) + offsetY,
                        e.direction == 'left', 
                        False, 
                        entity.camera.zoomLevel,
                        e.animations.alpha
                )
                # Test Boss Sword
                # weapon_rect = pygame.Rect(e.attack_weapon.hitbox.x + offsetX, e.attack_weapon.hitbox.y + offsetY, e.attack_weapon.hitbox.width, e.attack_weapon.hitbox.height)
                # pygame.draw.rect(screen, (255, 0, 0), weapon_rect)


            #Render MovingPlatforms
            for e in globals.world.movingPlatforms:
                if e.active:
                    #e.update()
                    s = e.state
                    a = e.animations.animationList[s]
                    a.draw(screen, 
                           (e.position.rect.x) + offsetX, 
                           (e.position.rect.y) + offsetY,
                           False, 
                           False, 
                           entity.camera.zoomLevel,
                           e.animations.alpha
                    )

            # Similarmente, ajustar el dibujo de plataformas y otros elementos
            # Renderizar plataformas con sus imágenes
            for p, image, _ in globals.world.platforms:
                if image:  # Comprueba que la imagen esté cargada
                    #newPosRect = pygame.Rect(p.x + offsetX, p.y + offsetY, p.w * entity.camera.zoomLevel, p.h * entity.camera.zoomLevel)
                    newPosRect = pygame.Rect(p.x + offsetX, p.y + offsetY, p.w, p.h)
                    scaled_image = pygame.transform.scale(image, (newPosRect.width, newPosRect.height))
                    screen.blit(scaled_image, newPosRect.topleft)
                    #self.draw_collision_rect(screen, newPosRect, (255, 0, 0))  # Rojo para visibilidad     

             # --- DIBUJO DE LOS PROYECTILES ---
            for projectile in globals.world.projectiles:
                # Suponiendo que cada proyectil tiene una animación en el estado 'idle'
                anim = projectile.animations.animationList.get('idle')
                if anim:
                    anim.draw(screen,
                              projectile.position.rect.x + offsetX,
                              projectile.position.rect.y + 22 + offsetY,
                              False,  # flipX
                              False,  # flipY
                              entity.camera.zoomLevel,
                              projectile.animations.alpha)
                else:
                    # Si el proyectil tiene una imagen simple
                    screen.blit(projectile.image,
                                (projectile.position.rect.x + offsetX,
                                 projectile.position.rect.y + 22 + offsetY))
                
            # #TEST DIBUJO ARMA**********************************************************
            # if globals.player1.intention.attack and globals.player1.last_attack_time > 0:
            #     # Actualizar posición del arma según la dirección del jugador
            #     # Definición del arma (rectángulo rojo)
            #     weapon_rect = pygame.Rect(0, 0, 20, 3)
            #     # Offsets para posicionar el arma en función de la dirección del jugador
            #     weapon_offset = {
            #         "right": (globals.player1.position.rect.w - 20, 21),  # A la derecha del jugador
            #         "left": (2, 21)                  # A la izquierda del jugador
            #     }

            #     offset = weapon_offset[globals.player1.direction]
            #     weapon_rect.topleft = (globals.player1.position.rect.x + offset[0] + offsetX, globals.player1.position.rect.y + offset[1] + offsetY)

            #     # Dibujo
            #     pygame.draw.rect(screen, (255, 0, 0), weapon_rect)
            # else:
            #     # Actualizar posición del arma según la dirección del jugador
            #     # Definición del arma (rectángulo rojo)
            #     weapon_rect = pygame.Rect(0, 0, 3, 20)
            #     # Offsets para posicionar el arma en función de la dirección del jugador
            #     weapon_offset = {
            #         "right": (globals.player1.position.rect.w - 29, 5),  # A la derecha del jugador
            #         "left": (26, 5)                  # A la izquierda del jugador
            #     }

            #     offset = weapon_offset[globals.player1.direction]
            #     weapon_rect.topleft = (globals.player1.position.rect.x + offset[0] + offsetX, globals.player1.position.rect.y + offset[1] + offsetY)

            #     # Dibujo
            #     pygame.draw.rect(screen, (255, 0, 0), weapon_rect)

            # #**********************************************************************************
            
            #entity HUD - Coins
            if entity.score is not None:
                screen.blit(utils.coin0,(entity.camera.rect.x + 10 + offsetX,entity.camera.rect.y + 10 + offsetY))
                utils.drawText(screen, str(entity.score.score), entity.camera.rect.x + 40 + offsetX, entity.camera.rect.y + 10 + offsetY, globals.WHITE, 255)
            
            #entity HUD - Key
            if entity.key == 1:
                #display score
                screen.blit(pygame.image.load('sprites/powerups/levelkey.png'), (entity.camera.rect.x + 10 + offsetX,entity.camera.rect.y + 30 + offsetY))

            if entity.type == 'player' and entity.battle is not None:    
                #display energy
                CameraSystem.draw_energy_bar(screen, 120, 10, 200, 20, entity.battle.energy, entity.battle.max_energy)
                #for l in range(entity.battle.lives):
                screen.blit(utils.live_image,(entity.camera.rect.x + 90 + offsetX, entity.camera.rect.y + 10 + offsetY))
                
            if entity.type == 'player' and entity.direction == 'left':
                entity.hitbox = pygame.Rect(entity.position.rect.x - 10 , entity.position.rect.y + 10, 10, 20)
            else:    
                entity.hitbox = pygame.Rect(entity.position.rect.x + 40 , entity.position.rect.y + 10, 10, 20) 


    def draw_energy_bar(screen, x, y, width, height, current_energy, max_energy):
        # Calcular el ancho de la barra de energía basada en la energía actual
        ratio = current_energy / max_energy
        current_width = int(width * ratio)

        # Dibujar el fondo de la barra de energía (por ejemplo, en gris)
        pygame.draw.rect(screen, (100, 100, 100), (x, y, width, height))
        
        # Dibujar la barra de energía actual (por ejemplo, en verde)
        pygame.draw.rect(screen, (255, 0, 0), (x, y, current_width, height))

    def draw_collision_rect(self, screen, rect, color):
        """Dibuja un rectángulo de contorno para depuración de colisiones."""
        pygame.draw.rect(screen, color, rect, 2)  # El último argumento '2' es el grosor del borde

class ProjectileSystem(System):
    def check(self, entity):
        # Solo procesamos entidades de tipo 'projectile'
        return entity is not None and getattr(entity, "type", None) == 'projectile'
    
    def update(self, screen=None, inputStream=None):
        # Suponiendo que tienes una lista dedicada para proyectiles en tu mundo:
        for projectile in list(globals.world.projectiles):
            if self.check(projectile):
                self.updateEntity(screen, inputStream, projectile)
    
    def updateEntity(self, screen, inputStream, projectile):
        # Actualizar posición según la dirección
        if projectile.direction == "right":
            projectile.position.rect.x += projectile.speed
        elif projectile.direction == "left":
            projectile.position.rect.x -= projectile.speed
        elif projectile.direction == "up":
            projectile.position.rect.y -= projectile.speed
        elif projectile.direction == "down":
            projectile.position.rect.y += projectile.speed
        # Si usas vectores de dirección, podrías hacer algo como:
        # projectile.position.rect.x += projectile.speed * projectile.direction[0]
        # projectile.position.rect.y += projectile.speed * projectile.direction[1]
        
        # Actualizar timer y remover el proyectil si se agota su vida útil
        projectile.timer -= 1
        if projectile.timer <= 0:
            globals.world.projectiles.remove(projectile)
            return

        # Verificar colisión con plataformas
        for platform in globals.world.platforms:
            platform_rect, image, collide = platform  # Suponiendo que la plataforma es una tupla
            if platform_rect.colliderect(projectile.position.rect):
                if projectile in globals.world.projectiles:
                    globals.world.projectiles.remove(projectile)
                return  # Salir ya que el proyectil ya fue eliminado

        # (Opcional) También puedes verificar si el proyectil sale de los límites del mundo
        if not globals.world_bounds.colliderect(projectile.position.rect):
            if projectile in globals.world.projectiles:
                globals.world.projectiles.remove(projectile)

class ShopSystem():
    def __init__(self):
        pass
    
    def check(self, npc):
        return npc.type is not None
    
    def update(self, npc, entity):
        if self.check(npc):
            self.updateEntity(npc, entity)
    
    def updateEntity(self, npc, entity):
        if utils.center_collide(npc.position.rect, entity.position.rect, 5):
            npc.state = "sign"
        else:
            npc.state = "idle"

class Camera:
    def __init__(self, x, y, w, h, world_width, world_height):
        self.rect = pygame.Rect(x, y, w, h)
        self.world_width = world_width
        self.world_height = world_height
        self.entityToTrack = None
        self.zoomLevel = 1.0

    def update(self):
        if self.entityToTrack:
            # Centrar la cámara en la entidad rastreada
            target_x = self.entityToTrack.position.rect.centerx - self.rect.width / 2
            target_y = self.entityToTrack.position.rect.centery - self.rect.height / 2

            # Ajustar los límites para evitar ver fuera del nivel
            self.rect.x = max(0, min(target_x, self.world_width - self.rect.width))
            self.rect.y = max(0, min(target_y, self.world_height - self.rect.height))
   
class Animation():
    
    def __init__(self, imageList):
        self.imageList = imageList
        self.imageIndex = 0
        self.animationTimer = 0
        self.AnimationSpeed = 10
    
    def update(self):
        self.animationTimer += 1
        if self.animationTimer >= self.AnimationSpeed:
            self.animationTimer = 0
            self.imageIndex += 1
            if self.imageIndex > len(self.imageList)-1:
                self.imageIndex = 0
    
    def draw(self, screen, x, y, flipX, flipY, zoomLevel, alpha):
        image = self.imageList[self.imageIndex]
        image.set_alpha(alpha)
        newWidht = int(image.get_rect().w * zoomLevel) 
        newHeight = int(image.get_rect().h * zoomLevel)
        image = pygame.transform.scale(pygame.transform.flip(image, flipX, flipY), (newWidht, newHeight))
        screen.blit(image, (x, y))

class Animations():
    def __init__(self):
        self.animationList = {}
        self.alpha = 255
    def add(self, state, animation):
        self.animationList[state] = animation

class Position():
    def __init__(self, x, y, w, h):
        self.rect = pygame.Rect(x, y, w, h)
        
class Score():
    def __init__(self):
        self.score = 0
    
class Battle():
    def __init__(self, energy, max_energy):
        self.energy = energy
        self.max_energy = max_energy

class Input():
    def __init__(self, up, down, left, right, b1, b2, attack):
        self.up = up
        self.down = down
        self.left = left
        self.right = right
        self.b1 = b1
        self.b2 = b2
        self.attack = attack

class Intention():
    def __init__(self):
        self.moveLeft = False
        self.moveRight = False
        self.jump = False
        self.zoomIn = False
        self.zoomOut = False
        self.attack = False
        self.down = False

class Effect():
    def __init__(self, apply, timer, sound, end, type):
        self.apply = apply
        self.timer = timer
        self.sound = sound
        self.end = end
        self.type = type

def resetEntity(entity):
    pass

class Entity():
    def __init__(self):
        self.state = 'idle'
        self.type = "normal"
        self.input = None
        self.position = None
        self.animations = Animations()
        self.direction = 'right'
        self.battle = None
        self.speed = 0
        self.intention = None
        self.on_ground = False
        self.acceleration = 0
        self.reset = resetEntity
        self.hitbox = pygame.Rect(0, 0, 0, 0)
        self.active = True
        self.cooldown = 3000
        self.phase = 1
        self.last_attack_time = 0
        self.attack_cooldown = 300
        self.impact_power = 0
        self.defense_power = 0 
        self.effect = None
        # Atributos para el disparo
        self.last_shot_time = 0           # Tiempo del último disparo (inicialmente 0)
        self.shoot_cooldown = 500         # 500 ms de cooldown entre disparos
        # Armamento de ataque
        self.attack_weapon = None
        # Armamento de defensa
        self.defense_weapon = None
      
class MovingPlatform():
    
    def __init__(self):
        self.dir = 1
        self.state = 'idle'
        self.type = "vertical"
        self.position = None
        self.animations = Animations()
        self.speed = 0
        self.input = None
        self.active = True
        self.start_x = 0
        self.start_y = 0

class TrackingEnemy(Entity):
    def __init__(self):
        super().__init__()
        self.position = None
        self.start_x = 0
        self.start_y = 0
        self.speed = 0
        self.tracking_distance = 0
        self.tracking_player = False
        self.returning = False

class ParallaxForeground:
    def __init__(self, layers, screen_size):
        """Inicializa el foreground Parallax con varias capas.
        Args:
            layers (list): Una lista de tuplas con (image_path, parallax_factor)
            screen_size (tuple): El tamaño de la pantalla (width, height)
        """
        self.layers = []
        self.screen_width, self.screen_height = screen_size
        for image_path, factor in layers:
            image = pygame.image.load(image_path).convert_alpha()
            image = pygame.transform.scale(image, (self.screen_width, self.screen_height))
            self.layers.append((image, factor))
            
        self.offsets = [0] * len(self.layers)

    def update(self, camera_x):
        """Actualiza los offsets de cada capa basados en la posición de la cámara.
        Args:
            camera_x (int): La posición x de la cámara en el mundo del juego.
        """
        for i, (layer, factor) in enumerate(self.layers):
            self.offsets[i] = -camera_x * factor % self.screen_width

    def draw(self, screen):
        """Dibuja las capas en la pantalla.
        Args:
            screen (pygame.Surface): La superficie de Pygame donde se dibuja el juego.
        """
        for (image, _), offset in zip(self.layers, self.offsets):
            screen.blit(image, (offset, 0))
            if offset > 0:
                screen.blit(image, (offset - self.screen_width, 0))
            elif offset < 0:
                screen.blit(image, (offset + self.screen_width, 0))

class ParallaxBackground:
    def __init__(self, layers, screen_size):
        """Inicializa el fondo Parallax con varias capas.
        Args:
            layers (list): Una lista de tuplas con (image_path, parallax_factor)
            screen_size (tuple): El tamaño de la pantalla (width, height)
        """
        self.layers = []
        self.screen_width, self.screen_height = screen_size
        for image_path, factor in layers:
            image = pygame.image.load(image_path).convert_alpha()
            # Escalar la imagen al tamaño de la pantalla o según sea necesario
            #image = pygame.transform.scale(image, (self.screen_width, int(image.get_height() * self.screen_width / image.get_width())))
            image = pygame.transform.scale(image, (self.screen_width, self.screen_height))
            #print(f"Loaded {image_path} with size {image.get_size()}")
            self.layers.append((image, factor))
            
        self.offsets = [0] * len(self.layers)

    def update(self, camera_x):
        """Actualiza los offsets de cada capa basados en la posición de la cámara.
        Args:
            camera_x (int): La posición x de la cámara en el mundo del juego.
        """
        for i, (layer, factor) in enumerate(self.layers):
            # Calcula el offset para cada capa; las capas más distantes se mueven más lentamente
            self.offsets[i] = -camera_x * factor % self.screen_width

    def draw(self, screen):
        """Dibuja las capas en la pantalla.
        Args:
            screen (pygame.Surface): La superficie de Pygame donde se dibuja el juego.
        """
        for (image, _), offset in zip(self.layers, self.offsets):
            # Dibuja la imagen una vez y una segunda vez si es necesario para cubrir toda la pantalla
            screen.blit(image, (offset, 0))
            if offset > 0:
                screen.blit(image, (offset - self.screen_width, 0))
            elif offset < 0:
                screen.blit(image, (offset + self.screen_width, 0))

class BossEnemy(Entity):

    def __init__(self):
        super().__init__()
        self.attack_weapons = []
        
    def is_player_within_aggro_distance(self, player):
        distance = (abs(self.position.rect.x - player.position.rect.x) ** 2 + 
                    (self.position.rect.y - player.position.rect.y) ** 2) ** 0.5
        return distance <= self.aggro_distance

    def take_damage(self, amount):
        if not self.invulnerable:
            self.health -= amount
            self.battle.energy -= amount
            self.invulnerable = True
            self.last_hit_time = 50
            self.state = 'hit'
    
        if self.health <= self.max_health / 2 and self.phase == 1:
            self.phase = 2
            self.speed += 1  # Aumenta la velocidad en la fase 2

class ShopItem():
    def __init__(self):
        self.position = None
        self.image = None
        self.price = 0
        self.price_position = (0,0)

class AttackWeapon():
    def __init__(self):
        self.name = ''
        self.position = None
        self.power = 0
        self.price = 0
        self.cooldown = 0
        self.hitbox = pygame.Rect(0, 0, 0, 0)

    def attack(self, entity):
        pass

class AttackWeaponSword():
    def __init__(self, name='', position=None, power=0, price=0, cooldown=300):
        self.name = name
        self.position = position
        self.power = power
        self.price = price
        self.cooldown = cooldown
        self.hitbox = pygame.Rect(0, 0, 0, 0)

    def attack(self, entity):
        if entity.intention.attack:
            if entity.direction == 'left':
                entity.attack_weapon.hitbox = pygame.Rect(entity.position.rect.x - 10, entity.position.rect.y + 10, 10, 20)
            else:    
                entity.attack_weapon.hitbox = pygame.Rect(entity.position.rect.x + 40, entity.position.rect.y + 10, 10, 20) 
        else:
            entity.attack_weapon.hitbox = pygame.Rect(0, 0, 0, 0)

class AttackWeaponProjectile():
    def __init__(self, name='', position=None, power=0, price=0, cooldown=300):
        self.name = name
        self.position = position
        self.power = power
        self.price = price
        self.cooldown = cooldown
        self.hitbox = pygame.Rect(0, 0, 0, 0)

    def attack(self, entity):
        projectile = utils.makeProjectile(
            entity.position.rect.x, 
            entity.position.rect.y, 
            entity.direction,   # o según la dirección del jugador
            speed=5, 
            damage=10,
            lifetime=120
        )
        projectile.owner = entity
        globals.world.projectiles.append(projectile)

class DefenseWeapon():
    def __init__(self):
        self.position = None
        self.power = 0
        self.price = 0

class Player(Entity):
    def __init__(self):
        super().__init__()
        self.camera = None
        self.score = None
        self.key = 0
        self.shield = False
        self.armor = False

class Projectile(Entity):
    def __init__(self, x, y, width, height, direction, speed, damage, lifetime, image, owner):
        super().__init__()
        self.position = Position(x, y, width, height)
        self.direction = direction  # Por ejemplo, "right", "left", "up", "down" o incluso un vector (dx, dy)
        self.speed = speed
        self.damage = damage
        self.lifetime = lifetime  # En frames o milisegundos
        self.timer = lifetime
        self.type = 'projectile'
        self.state = 'flying'
        self.image = image
        self.owner = owner
        # Aquí puedes asignar una animación o imagen, por ejemplo:
        # self.animations.add('idle', Animation([tu_imagen_del_proyectil]))

class AttackWeaponBossSword():
    def __init__(self, name='', position=None, power=0, price=0, cooldown=300):
        self.name = name
        self.position = position
        self.power = power
        self.price = price
        self.cooldown = cooldown
        self.hitbox = pygame.Rect(0, 0, 0, 0)

    def attack(self, entity):
        if entity.intention.attack:
            if entity.direction == 'left':
                entity.attack_weapon.hitbox = pygame.Rect(entity.position.rect.x + 10, entity.position.rect.y + 35, 20, 10)
            else:    
                entity.attack_weapon.hitbox = pygame.Rect(entity.position.rect.x + 50, entity.position.rect.y + 35, 20, 10)

        else:
            entity.attack_weapon.hitbox = pygame.Rect(0, 0, 0, 0)

class AttackWeaponBossProjectile():
    def __init__(self, name='', position=None, power=0, price=0, cooldown=300):
        self.name = name
        self.position = position
        self.power = power
        self.price = price
        self.cooldown = cooldown
        self.hitbox = pygame.Rect(0, 0, 0, 0)

    def attack(self, entity):
        
        if entity.direction == 'left':
            x = entity.position.rect.x - 20
        else:
            x = entity.position.rect.x + 60
        y = entity.position.rect.y + 22
        
        projectile = utils.makeProjectile(
            x, 
            y, 
            entity.direction,   # o según la dirección del jugador
            speed=5, 
            damage=10,
            lifetime=120
        )
        projectile.owner = entity
        globals.world.projectiles.append(projectile)
