from pico2d import load_image, get_time
from sdl2 import SDL_KEYDOWN, SDLK_LEFT, SDL_KEYUP, SDLK_RIGHT, SDLK_SPACE

import game_framework
import game_world
from state_machine import StateMachine

PIXEL_PER_METER = (10.0 / 0.2)  # 10 pixel 20 cm
RUN_SPEED_KMPH = 10.0
RUN_SPEED_MPM = (RUN_SPEED_KMPH * 1000.0 / 60.0)
RUN_SPEED_MPS = (RUN_SPEED_MPM / 60.0)
RUN_SPEED_PPS = (RUN_SPEED_MPS * PIXEL_PER_METER)

TIME_PER_ACTION = 0.5
ACTION_PER_TIME = 1.0 / TIME_PER_ACTION
FRAMES_PER_ACTION = {'Idle': 12, 'Run': 8}

pi = 3.141592

class Idle:
    def __init__(self, player):
        self.player = player

    def enter(self, event):
        self.player.dir = 0

    def exit(self, event):
        pass

    def do(self):
        self.player.frame = (self.player.frame + FRAMES_PER_ACTION['Idle'] * ACTION_PER_TIME * game_framework.frame_time) % FRAMES_PER_ACTION['Idle']

    def draw(self):
        if self.player.face_dir == 1: # 오른쪽
            self.player.image['Idle'].clip_draw(int(self.player.frame) * 64, 64, 64, 64, self.player.x, self.player.y, self.player.width, self.player.height)
        elif self.player.face_dir == -1: # 왼쪽
            self.player.image['Idle'].clip_draw(int(self.player.frame) * 64, 128, 64, 64, self.player.x, self.player.y, self.player.width, self.player.height)

class Run:
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
        self.player.frame = (self.player.frame + FRAMES_PER_ACTION['Run'] * ACTION_PER_TIME * game_framework.frame_time) % FRAMES_PER_ACTION['Run']
        self.player.x += self.player.dir * RUN_SPEED_PPS * game_framework.frame_time

    def draw(self):
        if self.player.face_dir == 1:  # 오른쪽
            self.player.image['Run'].clip_draw(int(self.player.frame) * 64, 64, 64, 64, self.player.x, self.player.y, self.player.width, self.player.height)
        elif self.player.face_dir == -1:  # 왼쪽
            self.player.image['Run'].clip_draw(int(self.player.frame) * 64, 128, 64, 64, self.player.x, self.player.y, self.player.width, self.player.height)

class Jump:
    def __init__(self, player):
        self.player = player
        self.jump_velocity = 0
        self.gravity = -800
        self.initial_jump_speed = 400
        self.ground_y = None
        self.prev_state = None  # 이전 상태 저장

    def enter(self, event):
        self.jump_velocity = self.initial_jump_speed
        self.ground_y = self.player.y
        # 현재 dir을 점프 방향으로 저장
        self.player.jumping_dir = self.player.dir
        # 점프 전 상태 저장 (IDLE인지 RUN인지)
        self.prev_state = self.player.state_machine.cur_state

    def exit(self, event):
        self.player.y = self.ground_y

    def do(self):
        self.player.frame = (self.player.frame + FRAMES_PER_ACTION['Run'] * ACTION_PER_TIME * game_framework.frame_time) % FRAMES_PER_ACTION['Run']

        # 수평 이동
        self.player.x += self.player.jumping_dir * RUN_SPEED_PPS * game_framework.frame_time

        # 수직 이동
        self.player.y += self.jump_velocity * game_framework.frame_time
        self.jump_velocity += self.gravity * game_framework.frame_time

        # 착지 체크
        if self.player.y <= self.ground_y:
            self.player.y = self.ground_y
            self.player.state_machine.handle_state_event(('JUMP_END', None))

    def draw(self):
        if self.player.face_dir == 1:
            self.player.image['Run'].clip_draw(int(self.player.frame) * 64, 64, 64, 64, self.player.x, self.player.y, self.player.width, self.player.height)
        elif self.player.face_dir == -1:
            self.player.image['Run'].clip_draw(int(self.player.frame) * 64, 128, 64, 64, self.player.x, self.player.y, self.player.width, self.player.height)

class Player:
    def __init__(self):
        self.x , self.y =  50, 150
        self.frame = 0
        self.face_dir = 1  # 1: right, -1: left
        self.dir = 0 # 0 정지 1 오른쪽 -1 왼쪽
        self.width = 300
        self.height = 300
        self.image = {}
        self.image['Idle'] = load_image('./resources/player/Player_IDLE.png')
        self.image['Run'] = load_image('./resources/player/Player_Run.png')
        self.IDLE = Idle(self)
        self.RUN = Run(self)
        self.JUMP = Jump(self)
        self.state_machine = StateMachine(self.IDLE, {
            self.IDLE: {left_down: self.RUN, right_down: self.RUN, space_down: self.JUMP},
            self.RUN: {left_down: self.IDLE, right_down: self.IDLE, left_up: self.IDLE, right_up: self.IDLE, space_down: self.JUMP},
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