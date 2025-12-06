from pico2d import load_image, get_time, draw_rectangle

import random

import game_framework

PIXEL_PER_METER = (10.0 / 0.2)  # 10 pixel 20 cm
RUN_SPEED_KMPH = 10.0
RUN_SPEED_MPM = (RUN_SPEED_KMPH * 1000.0 / 60.0)
RUN_SPEED_MPS = (RUN_SPEED_MPM / 60.0)
RUN_SPEED_PPS = (RUN_SPEED_MPS * PIXEL_PER_METER)

TIME_PER_ACTION = 1.0
ACTION_PER_TIME = 1.0 / TIME_PER_ACTION
FRAMES_PER_ACTION = {'drink': 10, 'weapon': 8, 'Lute' : 6}

class TraderDrink:
    def __init__(self):
        self.image = load_image('./resources/npc/Trader_drink.png')

        self.x , self.y =  950, 135
        self.frame = random.randint(0, 10)
        self.face_dir = 1  # 1: right, -1: left
        self.size = 128
        self.category = 'drink'

    def update(self):
        self.frame = (self.frame + FRAMES_PER_ACTION[self.category] * ACTION_PER_TIME * game_framework.frame_time) % FRAMES_PER_ACTION[self.category]

    def draw(self):
        self.image.clip_draw(int(self.frame) * 32, 0, 32, 32, self.x, self.y, self.size, self.size)

        draw_rectangle(*self.get_bb())

    def get_bb(self):
        return self.x - 45, self.y - 55, self.x + 45, self.y + 65

    def handle_event(self, event):
        pass

    def handle_collision(self, group, other):
        pass

class TraderWeapon:
    def __init__(self):
        self.image = load_image('./resources/npc/Trader_weapon.png')

        self.x , self.y =  1200, 128
        self.frame = random.randint(0, 10)
        self.face_dir = 1  # 1: right, -1: left
        self.size = 128
        self.category = 'weapon'

    def update(self):
        self.frame = (self.frame + FRAMES_PER_ACTION[self.category] * ACTION_PER_TIME * game_framework.frame_time) % FRAMES_PER_ACTION[self.category]

    def draw(self):
        self.image.clip_draw(int(self.frame) * 32, 0, 32, 32, self.x, self.y, self.size, self.size)

        draw_rectangle(*self.get_bb())

    def get_bb(self):
        return self.x - 65, self.y - 45, self.x + 45, self.y + 65

    def handle_event(self, event):
        pass

    def handle_collision(self, group, other):
        pass