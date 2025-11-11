from pico2d import load_image
import game_world
from state_machine import StateMachine

class Idle:
    def __init__(self, player):
        self.player = player

    def enter(self, event):
        pass

    def exot(self, event):
        pass

    def do(self):
        pass

    def draw(self):
        pass

class Walk:
    def __init__(self, player):
        self.player = player

    def enter(self, event):
        pass

    def exot(self, event):
        pass

    def do(self):
        pass

    def draw(self):
        pass

class Attack:
    def __init__(self, player):
        self.player = player

    def enter(self, event):
        pass

    def exot(self, event):
        pass

    def do(self):
        pass

    def draw(self):
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
            self.IDLE: {left_down: self.WALK, left_up:self.WALK, right_down:self.WALK, right_up:self.WALK, up_down:self.WALK, up_up:self.WALK, down_down:self.WALK, down_up:self.WALK, space_down:self.ATTACK},
            self.WALK: {left_down: self.IDLE, left_up:self.IDLE, right_down:self.IDLE, right_up:self.IDLE, up_down:self.IDLE, up_up:self.IDLE, down_down:self.IDLE, down_up:self.IDLE, space_down:self.ATTACK},
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