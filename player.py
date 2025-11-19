from pico2d import load_image, get_time, draw_rectangle
from sdl2 import SDL_KEYDOWN, SDLK_LEFT, SDL_KEYUP, SDLK_RIGHT, SDLK_SPACE, SDLK_a

import game_framework
import game_world
from state_machine import StateMachine

PIXEL_PER_METER = (10.0 / 0.2)  # 10 pixel 20 cm
RUN_SPEED_KMPH = 10.0
RUN_SPEED_MPM = (RUN_SPEED_KMPH * 1000.0 / 60.0)
RUN_SPEED_MPS = (RUN_SPEED_MPM / 60.0)
RUN_SPEED_PPS = (RUN_SPEED_MPS * PIXEL_PER_METER)

TIME_PER_ACTION = 1.0
ACTION_PER_TIME = 1.0 / TIME_PER_ACTION
FRAMES_PER_ACTION = {'Idle': 12, 'Run': 8, 'Attack' : 8, 'Hurt' : 5, 'Death' : 7}

GRAVITY = 9.8  # 중력 가속도 (m/s²)
GRAVITY_PPS = GRAVITY * PIXEL_PER_METER  # 중력을 픽셀 단위로 변환

JUMP_SPEED_KMPH = 30.0  # 점프 초기 속도 (m/s)
JUMP_SPEED_MPM = (JUMP_SPEED_KMPH * 1000.0 / 60.0)
JUMP_SPEED_MPS = (JUMP_SPEED_MPM / 60.0)
JUMP_SPEED_PPS = (JUMP_SPEED_MPS * PIXEL_PER_METER)  # 점프 속도를 픽셀 단위로 변환

class Idle:
    def __init__(self, player):
        self.player = player

    def enter(self, event):
        self.player.dir = 0
        self.player.frame = 0

    def exit(self, event):
        pass

    def do(self):
        self.player.frame = (self.player.frame + FRAMES_PER_ACTION['Idle'] * ACTION_PER_TIME * game_framework.frame_time) % FRAMES_PER_ACTION['Idle']

        # 타일 위에 있지 않으면 추락
        if not self.player.on_tile:
            self.player.y_velocity -= GRAVITY_PPS * game_framework.frame_time
            self.player.y += self.player.y_velocity * game_framework.frame_time

    def draw(self):
        if self.player.face_dir == 1:  # 오른쪽
            self.player.image['Idle'].clip_draw(int(self.player.frame) * 64, 64, 64, 64, self.player.x, self.player.y, self.player.width, self.player.height)
        elif self.player.face_dir == -1:  # 왼쪽
            self.player.image['Idle'].clip_draw(int(self.player.frame) * 64, 128, 64, 64, self.player.x, self.player.y, self.player.width, self.player.height)

class Run:
    def __init__(self, player):
        self.player = player

    def enter(self, event):
        self.player.frame = 0
        if left_down(event):
            self.player.dir = -1
            self.player.face_dir = -1
        elif right_down(event):
            self.player.dir = 1
            self.player.face_dir = 1
        elif left_up(event):
            self.player.dir = 1
            self.player.face_dir = 1
        elif right_up(event):
            self.player.dir = -1
            self.player.face_dir = -1

    def exit(self, event):
        pass

    def do(self):
        self.player.frame = (self.player.frame + FRAMES_PER_ACTION['Run'] * ACTION_PER_TIME * game_framework.frame_time) % FRAMES_PER_ACTION['Run']
        self.player.x += self.player.dir * RUN_SPEED_PPS * game_framework.frame_time

        # 타일 위에 있지 않으면 추락
        if not self.player.on_tile:
            self.player.y_velocity -= GRAVITY_PPS * game_framework.frame_time
            self.player.y += self.player.y_velocity * game_framework.frame_time

    def draw(self):
        if self.player.face_dir == 1:  # 오른쪽
            self.player.image['Run'].clip_draw(int(self.player.frame) * 64, 64, 64, 64, self.player.x, self.player.y, self.player.width, self.player.height)
        elif self.player.face_dir == -1:  # 왼쪽
            self.player.image['Run'].clip_draw(int(self.player.frame) * 64, 128, 64, 64, self.player.x, self.player.y, self.player.width, self.player.height)

class Attack:
    def __init__(self, player):
        self.player = player
        self.attack_start_time = None

    def enter(self, event):
        self.attack_start_time = get_time()
        self.player.is_attacking = True
        self.player.frame = 0

    def exit(self, event):
        pass

    def do(self):
        self.player.frame = (self.player.frame + FRAMES_PER_ACTION['Attack'] * ACTION_PER_TIME * game_framework.frame_time) % FRAMES_PER_ACTION['Attack']

        if get_time() - self.attack_start_time >= TIME_PER_ACTION:
            self.player.state_machine.handle_state_event(('TIME_OUT', None))
            self.player.is_attacking = False

    def draw(self):
        if self.player.face_dir == 1: # 오른쪽
            self.player.image['Attack'].clip_draw(int(self.player.frame) * 64, 64, 64, 64, self.player.x, self.player.y, self.player.width, self.player.height)
        elif self.player.face_dir == -1: # 왼쪽
            self.player.image['Attack'].clip_draw(int(self.player.frame) * 64, 128, 64, 64, self.player.x, self.player.y, self.player.width, self.player.height)

class Jump:
    def __init__(self, player):
        self.player = player
        self.jump_start_time = None

    def enter(self, event):
        self.jump_start_time = get_time()
        self.player.y_velocity = JUMP_SPEED_PPS

    def exit(self, event):
        pass

    def do(self):
        self.player.frame = (self.player.frame + FRAMES_PER_ACTION['Run'] * ACTION_PER_TIME * game_framework.frame_time) % FRAMES_PER_ACTION['Run']
        self.player.x += self.player.dir * RUN_SPEED_PPS * game_framework.frame_time

        self.player.y_velocity -= GRAVITY_PPS * game_framework.frame_time
        self.player.y += self.player.y_velocity * game_framework.frame_time

    def draw(self):
        if self.player.face_dir == 1:  # 오른쪽
            self.player.image['Run'].clip_draw(int(self.player.frame) * 64, 64, 64, 64, self.player.x, self.player.y, self.player.width, self.player.height)
        elif self.player.face_dir == -1:  # 왼쪽
            self.player.image['Run'].clip_draw(int(self.player.frame) * 64, 128, 64, 64, self.player.x, self.player.y, self.player.width, self.player.height)


class Hurt:
    def __init__(self, player):
        self.player = player

    def enter(self, event):
        self.player.frame = 0

    def exit(self, event):
        pass

    def do(self):
        self.player.frame = (self.player.frame + FRAMES_PER_ACTION['Hurt'] * ACTION_PER_TIME * game_framework.frame_time) % FRAMES_PER_ACTION['Hurt']

    def draw(self):
        if self.player.face_dir == 1:  # 오른쪽
            self.player.image['Hurt'].clip_draw(int(self.player.frame) * 64, 64, 64, 64, self.player.x, self.player.y, self.player.width, self.player.height)
        elif self.player.face_dir == -1:  # 왼쪽
            self.player.image['Hurt'].clip_draw(int(self.player.frame) * 64, 128, 64, 64, self.player.x, self.player.y, self.player.width, self.player.height)



class Death:
    def __init__(self, player):
        self.player = player

    def enter(self, event):
        self.player.frame = 0

    def exit(self, event):
        pass

    def do(self):
        self.player.frame = (self.player.frame + FRAMES_PER_ACTION['Death'] * ACTION_PER_TIME * game_framework.frame_time) % FRAMES_PER_ACTION['Death']

    def draw(self):
        if self.player.face_dir == 1:  # 오른쪽
            self.player.image['Death'].clip_draw(int(self.player.frame) * 64, 64, 64, 64, self.player.x, self.player.y, self.player.width, self.player.height)
        elif self.player.face_dir == -1:  # 왼쪽
            self.player.image['Death'].clip_draw(int(self.player.frame) * 64, 128, 64, 64, self.player.x, self.player.y, self.player.width, self.player.height)


class Player:
    def __init__(self, x = 50, y = 128, hp = 100):
        self.hp = hp

        self.x , self.y =  x, y
        self.frame = 0
        self.face_dir = 1  # 1: right, -1: left
        self.dir = 0 # 0 정지 1 오른쪽 -1 왼쪽
        self.width = 256
        self.height = 256
        self.is_attacking = False
        self.y_velocity = 0
        self.on_tile = False

        self.image = {}
        self.image['Idle'] = load_image('./resources/player/Player_IDLE.png')
        self.image['Run'] = load_image('./resources/player/Player_Run.png')
        self.image['Attack'] = load_image('./resources/player/Player_Attack.png')
        self.image['Hurt'] = load_image('./resources/player/Player_Hurt.png')
        self.image['Death'] = load_image('./resources/player/Player_Death.png')

        self.IDLE = Idle(self)
        self.RUN = Run(self)
        self.ATTACK = Attack(self)
        self.JUMP = Jump(self)
        self.HURT = Hurt(self)
        self.DEATH = Death(self)

        self.state_machine = StateMachine(self.IDLE, {
            self.IDLE: {left_down: self.RUN, right_down: self.RUN, space_down: self.JUMP, a_down: self.ATTACK},
            self.RUN: {left_down: self.IDLE, right_down: self.IDLE, left_up: self.IDLE, right_up: self.IDLE, space_down: self.JUMP, a_down: self.ATTACK},
            self.ATTACK: {time_out: self.IDLE},
            self.JUMP: {jump_end: self.IDLE},
            self.HURT: {},
            self.DEATH: {}
        })

    def update(self):
        self.state_machine.update()

    def handle_event(self, event):
        self.state_machine.handle_state_event(('INPUT', event))

    def draw(self):
        self.state_machine.draw()
        draw_rectangle(*self.get_bb())

    def get_bb(self):
        if self.is_attacking:
            if self.face_dir == 1:
                return self.x - 32, self.y - 50, self.x + 100, self.y + 64
            elif self.face_dir == -1:
                return self.x - 100, self.y - 50, self.x + 32, self.y + 64
        else:
            return self.x - 32, self.y - 50, self.x + 32, self.y + 64

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

def time_out(event):
    return event[0] == 'TIME_OUT'

def a_down(event):
    return event[0] == 'INPUT' and event[1].type == SDL_KEYDOWN and event[1].key == SDLK_a

def jump_end(event):
    return event[0] == 'JUMP_END'