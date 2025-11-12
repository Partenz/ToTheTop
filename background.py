from pico2d import load_image
import play_mode


class Background:
    def __init__(self):
        self.image = {}
        self.image['stage1'] = load_image('./resources/background/start_bg.png')

    def update(self):
        pass

    def draw(self):
        self.image[play_mode.stage].draw(1920 // 2, 720 // 2, 1920, 720)