from pico2d import load_image

import game_world


class Background:
    def __init__(self):
        self.image = {}
        self.image['stage1'] = load_image('./resources/background/start_bg.png')
        self.image['stage2'] = load_image('./resources/background/stage2_bg.png')
        self.image['stage3'] = load_image('./resources/background/stage3_bg.png')
        self.image['stage4'] = load_image('./resources/background/stage4_bg.png')

    def update(self):
        pass

    def draw(self):
        self.image[game_world.stage].draw(1920 // 2, 720 // 2, 1920, 720)