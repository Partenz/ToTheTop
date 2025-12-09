from pico2d import load_image, get_time, draw_rectangle, load_font
from sdl2 import SDL_KEYDOWN, SDLK_LEFT, SDL_KEYUP, SDLK_RIGHT, SDLK_SPACE, SDLK_a, SDLK_e, SDLK_p, SDLK_h

import common
import game_framework
import game_world
import shop_mode
import stage1_mode
from Weapon import Weapon
from state_machine import StateMachine
from stats import Stat

PIXEL_PER_METER = (10.0 / 0.2)  # 10 pixel 20 cm
RUN_SPEED_KMPH = 10.0
RUN_SPEED_MPM = (RUN_SPEED_KMPH * 1000.0 / 60.0)
RUN_SPEED_MPS = (RUN_SPEED_MPM / 60.0)
RUN_SPEED_PPS = (RUN_SPEED_MPS * PIXEL_PER_METER)

TIME_PER_ACTION = 0.5
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

        # 무기 객체 생성 및 게임 월드에 추가
        weapon = Weapon(self.player)
        game_world.add_object(weapon, 3)
        game_world.add_collision_pair('enemy:weapon', None, weapon)
        game_world.add_collision_pair('boss:weapon', None, weapon)

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
        self.animation_start_time = None

    def enter(self, event):
        self.player.frame = 0
        self.animation_start_time = get_time()
        damage = max(1, 25 - self.player.stat.defense) # 최소 1의 데미지 ~ 최대 20의 데미지
        self.player.hp -= damage
        self.player.x -= self.player.face_dir * RUN_SPEED_PPS / 5  # 피격 시 약간 밀려남
        self.player.is_invincible = True
        self.player.invincibility_start_time = get_time()

    def exit(self, event):
        pass

    def do(self):
        self.player.frame = (self.player.frame + FRAMES_PER_ACTION['Hurt'] * ACTION_PER_TIME * game_framework.frame_time) % FRAMES_PER_ACTION['Hurt']

        if get_time() - self.animation_start_time >= TIME_PER_ACTION:
            self.player.state_machine.handle_state_event(('TIME_OUT', None))

        if self.player.hp <= 0:
            self.player.state_machine.handle_state_event(('DEATH', None))

    def draw(self):
        if self.player.face_dir == 1:  # 오른쪽
            self.player.image['Hurt'].clip_draw(int(self.player.frame) * 64, 64, 64, 64, self.player.x, self.player.y, self.player.width, self.player.height)
        elif self.player.face_dir == -1:  # 왼쪽
            self.player.image['Hurt'].clip_draw(int(self.player.frame) * 64, 128, 64, 64, self.player.x, self.player.y, self.player.width, self.player.height)



class Death:
    def __init__(self, player):
        self.player = player
        self.animation_start_time = None

    def enter(self, event):
        self.player.frame = 0
        self.animation_start_time = get_time()

    def exit(self, event):
        pass

    def do(self):
        self.player.frame = (self.player.frame + FRAMES_PER_ACTION['Death'] * ACTION_PER_TIME * game_framework.frame_time) % FRAMES_PER_ACTION['Death']

        if get_time() - self.animation_start_time >= TIME_PER_ACTION:
            game_world.stage = 'stage1'
            game_world.stage_from = None
            self.player.hp = 100
            self.player.frame = 0
            self.player.state_machine.handle_state_event(('TIME_OUT', None))
            game_framework.change_mode(stage1_mode)

    def draw(self):
        if self.player.face_dir == 1:  # 오른쪽
            self.player.image['Death'].clip_draw(int(self.player.frame) * 64, 64, 64, 64, self.player.x, self.player.y, self.player.width, self.player.height)
        elif self.player.face_dir == -1:  # 왼쪽
            self.player.image['Death'].clip_draw(int(self.player.frame) * 64, 128, 64, 64, self.player.x, self.player.y, self.player.width, self.player.height)


class Player:
    INVINCIBILITY_DURATION = 1.5  # 무적 시간 (초)

    def __init__(self, x = 50, y = 128):
        self.stat = Stat()
        self.hp = self.stat.max_hp
        self.coin = 50
        self.health_potion = 0

        self.x , self.y =  x, y
        self.frame = 0
        self.face_dir = 1  # 1: right, -1: left
        self.dir = 0 # 0 정지 1 오른쪽 -1 왼쪽
        self.width = 256
        self.height = 256
        self.is_attacking = False
        self.y_velocity = 0
        self.on_tile = False
        self.is_invincible = False
        self.invincibility_start_time = 0

        self.image = {}
        self.image['Idle'] = load_image('./resources/player/Player_IDLE.png')
        self.image['Run'] = load_image('./resources/player/Player_Run.png')
        self.image['Attack'] = load_image('./resources/player/Player_Attack.png')
        self.image['Hurt'] = load_image('./resources/player/Player_Hurt.png')
        self.image['Death'] = load_image('./resources/player/Player_Death.png')
        self.hp_image = load_image('./resources/gui/hp.png')
        self.font = load_font('./resources/font/ENCR10B.TTF', 32)

        self.IDLE = Idle(self)
        self.RUN = Run(self)
        self.ATTACK = Attack(self)
        self.JUMP = Jump(self)
        self.HURT = Hurt(self)
        self.DEATH = Death(self)

        self.state_machine = StateMachine(self.IDLE, {
            self.IDLE: {left_down: self.RUN, right_down: self.RUN, space_down: self.JUMP, a_down: self.ATTACK, hurt:self.HURT},
            self.RUN: {left_down: self.IDLE, right_down: self.IDLE, left_up: self.IDLE, right_up: self.IDLE, space_down: self.JUMP, a_down: self.ATTACK, hurt:self.HURT},
            self.ATTACK: {time_out: self.IDLE, hurt:self.HURT},
            self.JUMP: {jump_end: self.IDLE, hurt:self.HURT},
            self.HURT: {time_out: self.IDLE, death: self.DEATH},
            self.DEATH: {time_out: self.IDLE}
        })

    def update(self):
        if self.is_invincible and get_time() - self.invincibility_start_time > self.INVINCIBILITY_DURATION:
            self.is_invincible = False

        self.on_tile = False
        self.state_machine.update()

    def handle_event(self, event):
        if event.type == SDL_KEYDOWN and event.key == SDLK_e:
            # 포션 상인과 상호작용
            if game_world.collide(self, common.trader_drink):
                print('포션 상인과 상호작용')
                game_framework.push_mode(shop_mode)
            # 무기 상인과 상호작용
            elif game_world.collide(self, common.trader_weapon):
                print('무기 상인과 상호작용')
                game_framework.push_mode(shop_mode)
        elif event.type == SDL_KEYDOWN and event.key == SDLK_p:
            self.coin += 50
        elif event.type == SDL_KEYDOWN and event.key == SDLK_h:
            self.hp = self.stat.max_hp

        self.state_machine.handle_state_event(('INPUT', event))

    def draw(self):
        # 무적 상태일 때 깜빡임 효과
        if self.is_invincible:
            if int(get_time() * 10) % 2 == 0:
                self.state_machine.draw()
        else:
            self.state_machine.draw()

        draw_rectangle(*self.get_bb())
        hp_ratio = self.hp / self.stat.max_hp
        hp_bar_width = max(0, 500 * hp_ratio)
        hp_bar_x = 50 + hp_bar_width / 2
        self.hp_image.draw(hp_bar_x, 700, hp_bar_width, 40)
        self.font.draw(1400, 700, f'Coin : {self.coin}, Potion : {self.health_potion}', (255, 255, 0))

    def get_bb(self):
        return self.x - 32, self.y - 50, self.x + 32, self.y + 64

    def handle_collision(self, group, other):
        if group == 'player:tile':
            left_player, bottom_player, right_player, top_player = self.get_bb()
            left_tile, bottom_tile, right_tile, top_tile = other.get_bb()

            # 플레이어가 아래로 떨어지고 있고, 발이 타일 상단 근처에 있을 때
            if self.y_velocity <= 0 and abs(bottom_player - top_tile) < 20: # 20은 약간의 오차 허용 범위
                # 플레이어가 타일의 좌우 범위 내에 있는지 확인
                if right_player > left_tile and left_player < right_tile:
                    self.on_tile = True
                    self.y += top_tile - bottom_player
                    self.y_velocity = 0
                    if self.state_machine.cur_state == self.JUMP:
                        self.state_machine.handle_state_event(('JUMP_END', None))
        elif (group == 'player:enemy' or group == 'bossAttack:player') and not self.is_invincible:
            self.state_machine.handle_state_event(('HURT', None))


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

def hurt(event):
    return event[0] == 'HURT'

def death(event):
    return event[0] == 'DEATH'