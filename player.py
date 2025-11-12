from pico2d import load_image, get_time
from sdl2 import SDL_KEYDOWN, SDLK_LEFT, SDL_KEYUP, SDLK_RIGHT, SDLK_UP, SDLK_DOWN, SDLK_SPACE

import game_framework
import game_world
from state_machine import StateMachine

PIXEL_PER_METER = (10.0 / 0.2)  # 10 pixel 20 cm
WALK_SPEED_KMPH = 10.0
WALK_SPEED_MPM = (WALK_SPEED_KMPH * 1000.0 / 60.0)
WALK_SPEED_MPS = (WALK_SPEED_MPM / 60.0)
WALK_SPEED_PPS = (WALK_SPEED_MPS * PIXEL_PER_METER)

TIME_PER_ACTION = 0.5
ACTION_PER_TIME = 1.0 / TIME_PER_ACTION
FRAMES_PER_ACTION = {'Idle': 2, 'Walk': 3, 'Attack': 4}

pi = 3.141592

class Idle:
    def __init__(self, player):
        self.player = player

    def enter(self, event):
        pass

    def exit(self, event):
        pass

    def do(self):
        self.player.frame = (self.player.frame + FRAMES_PER_ACTION['Idle'] * ACTION_PER_TIME * game_framework.frame_time) % FRAMES_PER_ACTION['Idle']

    def draw(self):
        if self.player.face_dir == 1:
            self.player.image['Idle'][int(self.player.frame)].draw(self.player.x, self.player.y, self.player.width, self.player.height)
        else:
            self.player.image['Idle'][int(self.player.frame)].composite_draw(0, 'h', self.player.x, self.player.y, self.player.width, self.player.height)

class Walk:
    def __init__(self, player):
        self.player = player

    def enter(self, event):
        if left_down(event) or right_up(event):
            self.player.dir = -1
            self.player.face_dir = -1
        elif right_down(event) or left_up(event):
            self.player.dir = 1
            self.player.face_dir = 1

    def exit(self, event):
        pass

    def do(self):
        self.player.frame = (self.player.frame + FRAMES_PER_ACTION['Walk'] * ACTION_PER_TIME * game_framework.frame_time) % FRAMES_PER_ACTION['Walk']
        self.player.x += self.player.dir * WALK_SPEED_PPS * game_framework.frame_time

    def draw(self):
        if self.player.face_dir == 1:
            self.player.image['Walk'][int(self.player.frame)].draw(self.player.x, self.player.y, self.player.width, self.player.height)
        else:
            self.player.image['Walk'][int(self.player.frame)].composite_draw(0, 'h', self.player.x, self.player.y, self.player.width, self.player.height)

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

class Jump:
    def __init__(self, player):
        self.player = player

    def enter(self, event):
        self.player.jump_time = get_time()

    def exit(self, event):
        pass

    def do(self):
        if get_time() - self.player.jump_time < ACTION_PER_TIME / 2:
            self.player.y += WALK_SPEED_PPS * game_framework.frame_time
        elif ACTION_PER_TIME / 2 <= get_time() - self.player.jump_time < ACTION_PER_TIME:
            self.player.y -= WALK_SPEED_PPS * game_framework.frame_time

        if get_time() - self.player.jump_time > ACTION_PER_TIME:
            self.player.state_machine.handle_state_event(('JUMP_END', None))

        self.player.frame = (self.player.frame + FRAMES_PER_ACTION['Walk'] * ACTION_PER_TIME * game_framework.frame_time) % FRAMES_PER_ACTION['Walk']
        self.player.x += self.player.dir * WALK_SPEED_PPS * game_framework.frame_time

    def draw(self):
        if self.player.face_dir == 1:
            self.player.image['Walk'][int(self.player.frame)].draw(self.player.x, self.player.y, self.player.width, self.player.height)
        else:
            self.player.image['Walk'][int(self.player.frame)].composite_draw(0, 'h', self.player.x, self.player.y, self.player.width, self.player.height)

class Player:
    def __init__(self):
        self.x , self.y =  50, 50
        self.frame = 0
        self.face_dir = 1  # 1: right, -1: left
        self.dir = 0 # 0 정지 1 오른쪽 -1 왼쪽
        self.width = 100
        self.height = 100
        self.image = {}
        self.image['Idle'] = [load_image('./resources/player/player_idle%d' %i +'.png') for i in range(1, 2 + 1)]
        self.image['Walk'] = [load_image('./resources/player/player_walk%d' %i +'.png') for i in range(1, 3 + 1)]
        self.image['Attack'] = [load_image('./resources/player/player_attack%d' %i +'.png') for i in range(1, 4 + 1)]

        self.IDLE = Idle(self)
        self.WALK = Walk(self)
        self.ATTACK = Attack(self)
        self.JUMP = Jump(self)
        self.state_machine = StateMachine(self.IDLE, {
            self.IDLE: {left_down: self.WALK, right_down: self.WALK, left_up: self.WALK, right_up: self.WALK, space_down: self.JUMP},
            self.WALK: {left_down: self.IDLE, right_down: self.IDLE, left_up: self.IDLE, right_up: self.IDLE, space_down: self.JUMP},
            self.ATTACK: {},
            self.JUMP: {jump_end: self.IDLE}
        })

    def update(self):
        self.state_machine.update()

    def handle_event(self, event):
        self.state_machine.handle_state_event(('INPUT', event))

    def draw(self):
        self.state_machine.draw()

    def get_bb(self):
        pass

def left_down(event):
    return event[0] == 'INPUT' and event[1].type == SDL_KEYDOWN and event[1].key == SDLK_LEFT

def left_up(event):
    return event[0] == 'INPUT' and event[1].type == SDL_KEYUP and event[1].key == SDLK_LEFT

def right_down(event):
    return event[0] == 'INPUT' and event[1].type == SDL_KEYDOWN and event[1].key == SDLK_RIGHT

def right_up(event):
    return event[0] == 'INPUT' and event[1].type == SDL_KEYUP and event[1].key == SDLK_RIGHT

def space_down(event):
    return event[0] == 'INPUT' and event[1].type == SDL_KEYDOWN and event[1].key == SDLK_SPACE

def jump_end(event):
    return event[0] == 'JUMP_END'