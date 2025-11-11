from pico2d import load_image
from sdl2 import SDL_KEYDOWN, SDLK_LEFT, SDL_KEYUP, SDLK_RIGHT, SDLK_UP, SDLK_DOWN

import game_world
from state_machine import StateMachine

class Idle:
    def __init__(self, player):
        self.player = player

    def enter(self, event):
        pass

    def exit(self, event):
        pass

    def do(self):
        pass

    def draw(self):
        pass

class Walk:
    def __init__(self, player):
        self.player = player

    def enter(self, event):
        if right_down(event) or left_up(event):
            self.player.face_dir = self.player.dir = 1
        elif left_down(event) or right_up(event):
            self.player.face_dir = self.player.dir = -1

    def exit(self, event):
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

    def exit(self, event):
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
        self.dir = 0 # 0 정지 1 오른쪽 -1 왼쪽
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
        self.state_machine.update()

    def handle_event(self, event):
        self.state_machine.handle_state_event(('INPUT', event))

    def draw(self):
        self.state_machine.draw()

    def get_bb(self):
        pass

def left_down(self, event):
    return event[0] == 'INPUT' and event[1] == SDL_KEYDOWN and event[2] == SDLK_LEFT

def left_up(self, event):
    return event[0] == 'INPUT' and event[1] == SDL_KEYUP and event[2] == SDLK_LEFT

def right_down(self, event):
    return event[0] == 'INPUT' and event[1] == SDL_KEYDOWN and event[2] == SDLK_RIGHT

def right_up(self, event):
    return event[0] == 'INPUT' and event[1] == SDL_KEYUP and event[2] == SDLK_RIGHT

def up_down(self, event):
    return event[0] == 'INPUT' and event[1] == SDL_KEYDOWN and event[2] == SDLK_UP

def up_up(self, event):
    return event[0] == 'INPUT' and event[1] == SDL_KEYUP and event[2] == SDLK_UP

def down_down(self, event):
    return event[0] == 'INPUT' and event[1] == SDL_KEYDOWN and event[2] == SDLK_DOWN

def down_up(self, event):
    return event[0] == 'INPUT' and event[1] == SDL_KEYUP and event[2] == SDLK_DOWN