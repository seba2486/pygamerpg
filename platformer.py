#Imports
import pygame
import globals
import utils
import engine
import scene
import inputstream
import soundmanager   



#Constants
SCREEN_SIZE = (800,600) 
DARK_GREY = (50,50,50)
MUSTARD = (209, 206, 25)

#*****************************Init**********************************
pygame.init()
#screen = pygame.display.set_mode(SCREEN_SIZE, pygame.FULLSCREEN)
screen = pygame.display.set_mode(SCREEN_SIZE)
clock = pygame.time.Clock()
player_on_ground = True


globals.soundManager = soundmanager.SoundManager()

#Create Player
globals.player1 = utils.makePlayer(100, 600)
globals.player1.camera = engine.Camera(0,800,800,600,2000,800)
globals.player1.camera.entityToTrack = globals.player1
globals.player1.input = engine.Input(pygame.K_w,pygame.K_s,pygame.K_a,pygame.K_d,pygame.K_q,pygame.K_e, pygame.K_SPACE)

sceneManager = scene.SceneManager()
mainMenu = scene.MainMenuScene()
sceneManager.push(mainMenu)

inputStream = inputstream.InputStream()

running = True

#************************** Game Loop *****************************
while running:
    
    inputStream.processInput()
    globals.soundManager.update()
    
    #Check for Quit
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    if sceneManager.isEmpty():
        running = False
    sceneManager.input(inputStream)
    sceneManager.update(inputStream)
    sceneManager.draw(screen)
    
    
    clock.tick(60)
    
#Quit
pygame.quit()