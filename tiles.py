from pico2d import load_image, draw_rectangle
import play_mode


class Tile:
    def __init__(self, x = 30, y = 60):
        self.image = {}
        self.x = x
        self.y = y
        self.image['stage1'] = load_image('./resources/tile/default_dirt_tile.png')

    def update(self):
        pass

    def draw(self):
        self.image[play_mode.stage].draw(self.x, self.y)
        draw_rectangle(*self.get_bb())

    def get_bb(self):
        return self.x - 32, self.y - 32, self.x + 32, self.y + 20