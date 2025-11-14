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

TIME_PER_ACTION = 0.5
ACTION_PER_TIME = 1.0 / TIME_PER_ACTION
FRAMES_PER_ACTION = {'Idle': 12, 'Run': 8, 'Attack' : 8}

GRAVITY = 9.8  # 중력 가속도 (m/s²)
GRAVITY_PPS = GRAVITY * PIXEL_PER_METER  # 중력을 픽셀 단위로 변환

JUMP_SPEED = 8.0  # 점프 초기 속도 (m/s)
JUMP_SPEED_PPS = JUMP_SPEED * PIXEL_PER_METER  # 점프 속도를 픽셀 단위로 변환

pi = 3.141592

class Idle:
    def __init__(self, player):
        self.player = player

    def enter(self, event):
        self.player.dir = 0

    def exit(self, event):
        if space_down(event):
            self.player.jump()
        if a_down(event):
            self.player.attack()

    def do(self):
        self.player.frame = (self.player.frame + FRAMES_PER_ACTION['Idle'] * ACTION_PER_TIME * game_framework.frame_time) % FRAMES_PER_ACTION['Idle']

        # 중력 적용
        self.player.velocity_y -= GRAVITY_PPS * game_framework.frame_time
        self.player.y += self.player.velocity_y * game_framework.frame_time

        # 지면 충돌 처리
        if self.player.y <= self.player.ground_y:
            self.player.y = self.player.ground_y
            self.player.velocity_y = 0

    def draw(self):
        # 공격 중이면 공격 애니메이션 표시
        if self.player.is_attacking:
            attack_frame = int((get_time() - self.player.attack_start_time) / TIME_PER_ACTION * FRAMES_PER_ACTION['Attack']) % FRAMES_PER_ACTION['Attack']
            if self.player.face_dir == 1:
                self.player.image['Attack'].clip_draw(attack_frame * 64, 64, 64, 64, self.player.x, self.player.y, self.player.width, self.player.height)
            elif self.player.face_dir == -1:
                self.player.image['Attack'].clip_draw(attack_frame * 64, 128, 64, 64, self.player.x, self.player.y, self.player.width, self.player.height)
        else:
            if self.player.face_dir == 1: # 오른쪽
                self.player.image['Idle'].clip_draw(int(self.player.frame) * 64, 64, 64, 64, self.player.x, self.player.y, self.player.width, self.player.height)
            elif self.player.face_dir == -1: # 왼쪽
                self.player.image['Idle'].clip_draw(int(self.player.frame) * 64, 128, 64, 64, self.player.x, self.player.y, self.player.width, self.player.height)

class Run:
    def __init__(self, player):
        self.player = player

    def enter(self, event):
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
        if space_down(event):
            self.player.jump()
        if a_down(event):
            self.player.attack()

    def do(self):
        if not self.player.is_attacking:
            self.player.frame = (self.player.frame + FRAMES_PER_ACTION['Run'] * ACTION_PER_TIME * game_framework.frame_time) % FRAMES_PER_ACTION['Run']
            self.player.x += self.player.dir * RUN_SPEED_PPS * game_framework.frame_time

        # 중력 적용
        self.player.velocity_y -= GRAVITY_PPS * game_framework.frame_time
        self.player.y += self.player.velocity_y * game_framework.frame_time

        # 지면 충돌 처리
        if self.player.y <= self.player.ground_y:
            self.player.y = self.player.ground_y
            self.player.velocity_y = 0

    def draw(self):
        # 공격 중이면 공격 애니메이션 표시
        if self.player.is_attacking:
            attack_frame = int((get_time() - self.player.attack_start_time) / TIME_PER_ACTION * FRAMES_PER_ACTION['Attack']) % FRAMES_PER_ACTION['Attack']
            if self.player.face_dir == 1:
                self.player.image['Attack'].clip_draw(attack_frame * 64, 64, 64, 64, self.player.x, self.player.y, self.player.width, self.player.height)
            elif self.player.face_dir == -1:
                self.player.image['Attack'].clip_draw(attack_frame * 64, 128, 64, 64, self.player.x, self.player.y, self.player.width, self.player.height)
        else:
            if self.player.face_dir == 1:  # 오른쪽
                self.player.image['Run'].clip_draw(int(self.player.frame) * 64, 64, 64, 64, self.player.x, self.player.y, self.player.width, self.player.height)
            elif self.player.face_dir == -1:  # 왼쪽
                self.player.image['Run'].clip_draw(int(self.player.frame) * 64, 128, 64, 64, self.player.x, self.player.y, self.player.width, self.player.height)


class Player:
    def __init__(self):
        self.x , self.y =  50, 128
        self.frame = 0
        self.face_dir = 1  # 1: right, -1: left
        self.dir = 0 # 0 정지 1 오른쪽 -1 왼쪽
        self.width = 256
        self.height = 256

        # 점프 관련 변수
        self.velocity_y = 0
        self.ground_y = 128  # 지면 높이

        # 공격 관련 변수
        self.is_attacking = False
        self.attack_start_time = 0

        self.image = {}
        self.image['Idle'] = load_image('./resources/player/Player_IDLE.png')
        self.image['Run'] = load_image('./resources/player/Player_Run.png')
        self.image['Attack'] = load_image('./resources/player/Player_Attack.png')
        self.IDLE = Idle(self)
        self.RUN = Run(self)
        self.state_machine = StateMachine(self.IDLE, {
            self.IDLE: {left_down: self.RUN, right_down: self.RUN, left_up: self.RUN, right_up: self.RUN, space_down: self.IDLE, a_down: self.IDLE},
            self.RUN: {left_down: self.IDLE, right_down: self.IDLE, left_up: self.IDLE, right_up: self.IDLE, space_down: self.RUN, a_down: self.RUN},
        })

    def update(self):
        self.state_machine.update()

        # 공격 애니메이션 시간 체크
        if self.is_attacking and get_time() - self.attack_start_time > TIME_PER_ACTION:
            self.is_attacking = False

    def handle_event(self, event):
        self.state_machine.handle_state_event(('INPUT', event))

    def draw(self):
        self.state_machine.draw()
        draw_rectangle(*self.get_bb())

    def jump(self):
        # 지면에 있을 때만 점프 가능
        if self.y <= self.ground_y:
            self.velocity_y = JUMP_SPEED_PPS

    def attack(self):
        # 공격 시작
        self.is_attacking = True
        self.attack_start_time = get_time()


    def get_bb(self):
        if self.is_attacking:
            if self.face_dir == 1:
                return self.x - 32, self.y - 64, self.x + 100, self.y + 64
            elif self.face_dir == -1:
                return self.x - 100, self.y - 64, self.x + 32, self.y + 64
        else:
            return self.x - 32, self.y - 64, self.x + 32, self.y + 64

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