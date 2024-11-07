import pygame
class Keyboard:
    def __init__(self):
        self.currentKeyStates = None
        self.previusKeyStates = None
    
    def processInput(self):
        self.previusKeyStates = self.currentKeyStates
        self.currentKeyStates = pygame.key.get_pressed()
    
    def isKeyDown(self, keycode):
        return self.currentKeyStates[keycode] == True
    
    def isKeyPressed(self, keycode):
        if self.currentKeyStates is None or self.previusKeyStates is None:
            return False
    
        return self.currentKeyStates[keycode] == True and self.previusKeyStates[keycode] == False

    def isKeyReleased(self, keycode):
        if self.currentKeyStates is None or self.previusKeyStates is None:
            return False

        return self.currentKeyStates[keycode] == False and self.previusKeyStates[keycode] == True

class InputStream:
    def __init__(self):
        self.keyboard = Keyboard()
        
    def processInput(self):
        self.keyboard.processInput()