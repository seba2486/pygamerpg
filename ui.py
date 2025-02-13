import utils
import globals

class ButtonUI:
    def __init__(self, keyCode, text, x, y):
        self.keycode = keyCode
        self.text = text
        self.x = x
        self.y = y
        self.on = False
        self.timer = 20
    
    def draw(self, screen):
        if self.on:
            colour = globals.GREEN
        else:
            colour = globals.WHITE
            
        utils.drawText(screen, self.text, self.x, self.y, colour, 255)
        
    def update(self, inputStream):
        self.pressed = inputStream.keyboard.isKeyPressed((self.keycode))
        if self.pressed:
            self.on = True
        if self.on:
            self.timer -= 1
            if self.timer <= 0:
                self.on = False
                self.timer = 20