import pygame
class SoundManager:
    def __init__(self):
        pygame.mixer.init()
        self.soundVolume = 0.4
        self.musicVolume = 0.1
        self.targetMusicVolume = 0.2
        self.nextMusic = None
        self.currentMusic = None
        self.sounds = {
            'jump' : pygame.mixer.Sound ('sounds/jump.wav'),
            'coin' : pygame.mixer.Sound ('sounds/coinPickup.ogg'),
            'sword_swoosh' : pygame.mixer.Sound ('sounds/sword_swoosh.wav'),
            'enemy_takes_damage' : pygame.mixer.Sound ('sounds/enemy_takes_damage.wav'),
            'player_receive_damage' : pygame.mixer.Sound ('sounds/player_receive_damage.wav'),
        }
        self.music = {
            'solace' : 'music/solace.ogg',
            'down' : 'music/btd.ogg'
        }
    
    def playSound(self, soundName):
        self.sounds[soundName].set_volume(self.soundVolume)
        self.sounds[soundName].play()
    
    def playMusic(self, musicName):
        if musicName != self.currentMusic:
            pygame.mixer.music.load(self.music[musicName])
            pygame.mixer.music.set_volume(self.musicVolume)
            pygame.mixer.music.play(-1)
            self.currentMusic = musicName
        
    def playMusicFade(self, musicName):
        if musicName != self.currentMusic:
            self.nextMusic = musicName
            self.fadeOut()
    
    def fadeOut(self):
        pygame.mixer.music.fadeout(500)
        
    def update(self):
        #raise volume if lower than target
        if self.musicVolume < self.targetMusicVolume:
            self.musicVolume = min(self.musicVolume + 0.005, self.targetMusicVolume)
            pygame.mixer.music.set_volume(self.musicVolume)
        #play next music if appropieate
        if self.nextMusic is not None:
            #if old music has finished fading out
            if not pygame.mixer.music.get_busy():
                self.currentMusic = None
                self.musicVolume = 0
                pygame.mixer.music.set_volume(self.musicVolume)
                self.playMusic(self.nextMusic)
                #remove from music quee
                self.nextMusic = None