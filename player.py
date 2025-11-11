from pico2d import load_image
import game_world
from state_machine import StateMachine

class Idle:
    pass

class Walk:
    pass

class Attack:
    pass

class Player:
    def __init__(self):
        self.x , self.y = 960, 100
        self.frame = 0
        self.face_dir = 1  # 1: right, -1: left
        self.image = {}
        self.image['Idle'] = [load_image('./resources/player/player_idle%d' %i +'.png') for i in range(1, 2 + 1)]
        self.image['Walk'] = [load_image('./resources/player/player_walk%d' %i +'.png') for i in range(1, 3 + 1)]
        self.image['Attack'] = [load_image('./resources/player/player_attack%d' %i +'.png') for i in range(1, 4 + 1)]

        self.IDLE = Idle(self)
        self.WALK = Walk(self)
        self.ATTACK = Attack(self)
        self.state_machine = StateMachine(self.IDLE, {
            self.IDLE: {},
            self.WALK: {},
            self.ATTACK: {}
        })

    def update(self):
        pass

    def handle_event(self, event):
        pass

    def draw(self):
        pass

    def get_bb(self):
        pass