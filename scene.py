import pygame
import utils
import engine
import globals
import ui
import level


class Scene():
    def __init__(self):
        pass
    
    def onEnter(self):
        pass
    
    def onExit(self):
        pass
    
    def input(self, sm, inputStream):
        pass
    
    def update(self, sm, inputStream):
        pass
    
    def draw(self, sm, screen):
        pass
    
class MainMenuScene(Scene):
    def __init__(self):
        self.enter = ui.ButtonUI(pygame.K_RETURN, '[Enter=Next]', 50, 200)
        self.escape = ui.ButtonUI(pygame.K_ESCAPE, '[Escape=Quit]', 50, 250)
    
    def onEnter(self):
        globals.soundManager.playMusicFade('solace')
    
    def input(self, sm, inputStream):
        if inputStream.keyboard.isKeyPressed(pygame.K_RETURN):
            sm.push(FadeTransitionScene([self],[LevelSelectScene()]))
        if inputStream.keyboard.isKeyPressed(pygame.K_ESCAPE):
                sm.pop()
    
    def update(self, sm, inputStream):
        self.enter.update(inputStream)
        self.escape.update(inputStream)
    
    def draw(self, sm, screen):
        screen.fill(globals.DARK_GREY)
        utils.drawText(screen, 'Main Menu', 10, 10, globals.WHITE, 255)
        self.enter.draw(screen)
        self.escape.draw(screen)

class LevelSelectScene(Scene):
    def __init__(self):
        self.b1 = ui.ButtonUI(pygame.K_1, '[1 = Level 1]', 50, 200)
        self.b2 = ui.ButtonUI(pygame.K_2, '[2 = Level 2]', 50, 250)
        self.escape = ui.ButtonUI(pygame.K_2, '[Escape = Main Menu]', 50, 300)

    def onEnter(self):
        globals.soundManager.playMusicFade('solace')

    def update(self, sm, inputStream):
        self.b1.update(inputStream)
        self.b2.update(inputStream)
        self.escape.update(inputStream)
        
    def input(self, sm, inputStream):
        if inputStream.keyboard.isKeyPressed(pygame.K_1):
            level.loadLevel(1)
            sm.push(FadeTransitionScene([self], [GameScene()]))
        if inputStream.keyboard.isKeyPressed(pygame.K_2):
            level.loadLevel(2)
            sm.push(FadeTransitionScene([self], [GameScene()]))
        if inputStream.keyboard.isKeyPressed(pygame.K_ESCAPE):
            sm.pop()
            sm.push(FadeTransitionScene([self], []))
    
    def draw(self, sm, screen):
        screen.fill(globals.DARK_GREY)
        utils.drawText(screen, 'Level Select', 10, 10, globals.WHITE, 255)
        self.b1.draw(screen)
        self.b2.draw(screen)
        self.escape.draw(screen)

class GameScene(Scene):
    def __init__(self):
        self.cameraSystem = engine.CameraSystem()
        self.collectionSystem = engine.CollectionSystem()
        self.battleSystem = engine.BattleSystem()
        self.inputSystem = engine.InputSystem()
        self.physicsSystem = engine.PhysicsSystem()
        self.animationSystem = engine.AnimationSystem()
        self.powerUpSystem = engine.PowerUpSystem()
        self.movingPlatformSystem = engine.MovingPlatformSystem()
        self.trackingEnemySystem = engine.TrackingEnemySystem()
        self.bossAttackSystem = engine.BossAttackSystem()
        self.bossBattleSystem = engine.BossBattleSystem()
        self.bossPhysicsSystem = engine.BossPhysicsSystem()
        self.shopSystem = engine.ShopSystem()
        self.projectileSystem = engine.ProjectileSystem()
        self.enemyAttackSystem = engine.EnemyAttackSystem()
        self.playerAttackSystem = engine.PlayerAttackSystem()
        # Configura las capas con sus respectivas imágenes y factores de parallax
        self.background = engine.ParallaxBackground(globals.world.background, utils.SCREEN_SIZE)
        self.foreground = engine.ParallaxForeground(globals.world.foreground, utils.SCREEN_SIZE)
        self.player = globals.player1
        self.npc = globals.world.npc
        

    def onEnter(self):
        globals.soundManager.playMusicFade('down')
    
    def input(self, sm, inputStream):
        if inputStream.keyboard.isKeyPressed(pygame.K_ESCAPE):
            sm.pop()
            sm.push(FadeTransitionScene([self], []))

        if inputStream.keyboard.isKeyPressed(pygame.K_i):
            if utils.center_collide(self.npc.position.rect, self.player.position.rect, 5):
                sm.push(FadeTransitionScene([self], [ShopMenuScene()]))

        if globals.world.isWon():
            sm.push(WinScene())
        if globals.world.isLost():                
            sm.push(LoseScene())
    
    def get_camera_x_position(self):
        # Retorna la posición X del jugador para efectos de cálculo de parallax
        return self.player.position.rect.x if self.player and self.player.position else 0

    def update(self, sm, inputStream):
        # Aquí, deberías actualizar la posición de la cámara basada en el jugador o la lógica del juego
        camera_x = self.get_camera_x_position()
        self.background.update(camera_x)
        self.movingPlatformSystem.update()
        self.trackingEnemySystem.update()
        self.collectionSystem.update()
        self.foreground.update(camera_x)
        self.battleSystem.update()
        self.bossBattleSystem.update()
        self.inputSystem.update(inputStream=inputStream)
        self.bossAttackSystem.update()
        self.physicsSystem.update()
        self.bossPhysicsSystem.update()
        self.animationSystem.update()
        self.powerUpSystem.update()
        self.shopSystem.update(self.npc, self.player)
        self.projectileSystem.update()
        self.enemyAttackSystem.update()
        self.playerAttackSystem.update()

        
    def draw(self, sm, screen):
        self.background.draw(screen)
        #screen.fill(globals.DARK_GREY)
        self.cameraSystem.update(screen)
        self.foreground.draw(screen)

class WinScene(Scene):
    def __init__(self):
        self.alpha = 0
    
    def update(self, sm, inputStream):
        self.alpha = min(255, self.alpha + 10) 
        
    def input(self, sm, inputStream):
        if inputStream.keyboard.isKeyPressed(pygame.K_ESCAPE):
            sm.set([FadeTransitionScene([GameScene(),self], [MainMenuScene(),LevelSelectScene()])])
            
    def draw(self, sm, screen):
        if len(sm.scenes) > 1:
            sm.scenes[-2].draw(sm, screen)
        bgSurf = pygame.Surface(utils.SCREEN_SIZE)
        bgSurf.fill(globals.BLACK)
        utils.blit_alpha(screen, bgSurf, (0,0), self.alpha * 0.7)
        utils.drawText(screen, 'You Win!', 350, 200, globals.WHITE, self.alpha)

class LoseScene(Scene):
    def __init__(self):
        self.alpha = 0
    
    def update(self, sm, inputStream):
        self.alpha = min(255, self.alpha + 10) 

    def input(self, sm, inputStream):
        if inputStream.keyboard.isKeyPressed(pygame.K_ESCAPE):
            sm.set([FadeTransitionScene([GameScene(),self], [MainMenuScene(),LevelSelectScene()])])

    def draw(self, sm, screen):
        if len(sm.scenes) > 1:
            sm.scenes[-2].draw(sm, screen)
        bgSurf = pygame.Surface(utils.SCREEN_SIZE)
        bgSurf.fill(globals.BLACK)
        utils.blit_alpha(screen, bgSurf, (0,0), self.alpha * 0.7)
        utils.drawText(screen, 'You Lose!, press Escape', 350, 200, globals.WHITE, 255)

class TransitionScene(Scene):
    def __init__(self, fromScenes, toScenes):
        self.currentPercentage = 0
        self.fromScenes = fromScenes
        self.toScenes = toScenes
    
    def update(self, sm, inputStream):
        self.currentPercentage += 2
        if self.currentPercentage >= 100:
            sm.pop()
            for s in self.toScenes:
                sm.push(s)
        for scene in self.fromScenes:
            scene.update(sm, inputStream)
        if len(self.toScenes) > 0:
            for scene in self.toScenes:
                scene.update(sm, inputStream)
        else:
            if len(sm.scenes) > 1:
                sm.scenes[-2].update(sm, inputStream)
        
class FadeTransitionScene(TransitionScene):
    def draw(self, sm, screen):
        if self.currentPercentage < 50:
            for s in self.fromScenes:
                s.draw(sm, screen)
        else:
            if len(self.toScenes) == 0:
                if len(sm.scenes) > 1:
                    sm.scenes[-2].draw(sm,screen)
            else:
                for s in self.toScenes:
                    s.draw(sm, screen)
        #Fade overlay
        overlay = pygame.Surface(utils.SCREEN_SIZE)
        # 0 = transparent 255 = opaque
        # 0% = 0
        # 50% = 255
        # 100% = 0
        alpha = int(abs(255 - ((255/50)*self.currentPercentage)))
        overlay.set_alpha(255-alpha)
        overlay.fill(globals.BLACK)
        screen.blit(overlay, (0,0))

class SceneManager:
    def __init__(self):
        self.scenes = []
    
    def isEmpty(self):
        return len(self.scenes) == 0
    
    def enterScene(self):
        if len(self.scenes) > 0:
            self.scenes[-1].onEnter()
    
    def exitScene(self):
        if len(self.scenes) > 0:
            self.scenes[-1].onExit()
    
    def input(self, InputStream):
        if len(self.scenes) > 0:
            self.scenes[-1].input(self, InputStream)
    
    def update(self, inputStream):
        if len(self.scenes) > 0:
            self.scenes[-1].update(self, inputStream)
    
    def draw(self, screen):
        if len(self.scenes) > 0:
            self.scenes[-1].draw(self,screen)
        pygame.display.flip()    

    
    def push(self,scene):
        #Exit current scene
        self.exitScene()
        self.scenes.append(scene)
        #Enter current scene
        self.enterScene()
        
    def pop(self):
        self.exitScene()
        self.scenes.pop()
        self.enterScene()
    
    def set(self,scenes):
        #Pop all scenes
        while len(self.scenes) > 0:
            self.pop()
        for s in scenes:
            self.push(s)

class ShopMenuScene(Scene):
    def __init__(self):
        self.escape = ui.ButtonUI(pygame.K_ESCAPE, '[Escape=Quit]', 10, 250)
        self.highlight_item_rect_position = 1
        self.highlight_item_rect_line = 3
        self.highlight_item_rect_color = (255, 0, 0)
        #Items
        self.item1 = utils.makeShopItem(1, "shield")
        self.item2 = utils.makeShopItem(2, "armor")

    def onEnter(self):
        globals.soundManager.playMusicFade('solace')
    
    def input(self, sm, inputStream):
        if inputStream.keyboard.isKeyPressed(pygame.K_d):
            self.highlight_item_rect_position = 2    
        if inputStream.keyboard.isKeyPressed(pygame.K_a):
            self.highlight_item_rect_position = 1
        if inputStream.keyboard.isKeyPressed(pygame.K_RETURN):
                if self.highlight_item_rect_position == 1 and (globals.player1.score.score - self.item1.price) > 0 :
                    globals.player1.score.score -= self.item1.price
                    globals.player1.shield = True
                    utils.setShield(globals.player1)
                    sm.pop()
                elif (globals.player1.score.score - self.item2.price) > 0:
                    globals.player1.score.score -= self.item2.price
                    globals.player1.armor = True
                    globals.player1.battle.max_energy += 20
                    utils.setArmor(globals.player1)               
                    sm.pop()
        if inputStream.keyboard.isKeyPressed(pygame.K_ESCAPE):
                sm.pop()
    
    def update(self, sm, inputStream):
        self.escape.update(inputStream)
    
    def draw(self, sm, screen):
        screen.fill(globals.DARK_GREY)
        utils.drawText(screen, 'Shop Menu', 10, 10, globals.WHITE, 255)
        self.escape.draw(screen)
        
        
        #Items
        screen.blit(self.item1.image, (self.item1.position.rect.x, self.item1.position.rect.y))
        utils.drawText(screen, "$" + str(self.item1.price), self.item1.price_position[0], self.item1.price_position[1], globals.WHITE, 255)
        screen.blit(self.item2.image, (self.item2.position.rect.x, self.item2.position.rect.y))
        utils.drawText(screen, "$" + str(self.item2.price), self.item2.price_position[0], self.item2.price_position[1], globals.WHITE, 255)
        
        #Higlight
        if self.highlight_item_rect_position == 1:
            pygame.draw.rect(screen, self.highlight_item_rect_color, self.item1.position.rect, self.highlight_item_rect_line)
        else:
            pygame.draw.rect(screen, self.highlight_item_rect_color, self.item2.position.rect, self.highlight_item_rect_line)