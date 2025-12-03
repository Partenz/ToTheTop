from pico2d import load_image, get_time, draw_rectangle

import random

import game_framework
import game_world
import common
import stage2_mode
from behavior_tree import BehaviorTree, Action, Sequence, Condition, Selector


PIXEL_PER_METER = (10.0 / 0.2)  # 10 pixel 20 cm
RUN_SPEED_KMPH = 10.0
RUN_SPEED_MPM = (RUN_SPEED_KMPH * 1000.0 / 60.0)
RUN_SPEED_MPS = (RUN_SPEED_MPM / 60.0)
RUN_SPEED_PPS = (RUN_SPEED_MPS * PIXEL_PER_METER)

TIME_PER_ACTION = 1.0
ACTION_PER_TIME = 1.0 / TIME_PER_ACTION
FRAMES_PER_ACTION = {'Appearance': 8,'Idle': 8, 'Hurt' : 4, 'Death' : 6, 'Attack1' : 6, 'Attack2' : 6, 'Attack3' : 6, 'Attack4' : 6, 'Attack5' : 6, 'Attack6' : 6}

GRAVITY = 9.8  # 중력 가속도 (m/s²)
GRAVITY_PPS = GRAVITY * PIXEL_PER_METER  # 중력을 픽셀 단위로 변환

class Boss:
    image = None

    def __init__(self, x = 50, y = 150, hp = 500):
        if Boss.image is None:
            Boss.image = {}
            Boss.image['Appearance'] = load_image('./resources/boss/Appearance.png')
            Boss.image['Idle'] = load_image('./resources/boss/Idle.png')
            Boss.image['Attack1'] = load_image('./resources/boss/Attack1.png')
            Boss.image['Attack2'] = load_image('./resources/boss/Attack2.png')
            Boss.image['Attack3'] = load_image('./resources/boss/Attack3.png')
            Boss.image['Attack4'] = load_image('./resources/boss/Attack4.png')
            Boss.image['Attack5'] = load_image('./resources/boss/Attack5.png')
            Boss.image['Attack6'] = load_image('./resources/boss/Attack6.png')
            Boss.image['Hurt'] = load_image('./resources/boss/Hurt.png')
            Boss.image['Death'] = load_image('./resources/boss/Death.png')

        self.hp = hp
        self.if_hurt = False

        self.on_tile = False
        self.y_velocity = 0
        self.x , self.y =  x, y
        self.tx = None
        self.frame = 0
        self.dir = 0 # 0 정지 1 오른쪽 -1 왼쪽
        self.size = 1024
        self.state = 'Appearance'
        self.state_start_time = get_time()

        #self.build_behavior_tree()

    def update(self):
        #elf.on_tile = False
        #if self.state != 'Hurt' and self.state != 'Death' and self.state != 'Attack':
         #   self.bt.run()

        # 타일 위에 있지 않으면 추락
        if not self.on_tile:
            self.y_velocity -= GRAVITY_PPS * game_framework.frame_time
            self.y += self.y_velocity * game_framework.frame_time

        if self.state == 'Appearance':
            if get_time() - self.state_start_time > TIME_PER_ACTION:
                self.state_start_time = get_time()
                self.state = 'Idle'
        elif self.state == 'Attack':
            if get_time() - self.state_start_time > TIME_PER_ACTION:
                self.state_start_time = get_time()
                self.state = 'Idle'
        elif self.state == 'Hurt':
            if get_time() - self.state_start_time > TIME_PER_ACTION:
                self.state_start_time = get_time()
                self.state = 'Idle'
                self.dir = 0
                self.if_hurt = False
        elif self.state == 'Death':
            if get_time() - self.state_start_time > TIME_PER_ACTION:
                # 죽음 애니메이션이 끝난 후 객체 제거
                game_world.remove_object(self)
                return


        self.frame = (self.frame + FRAMES_PER_ACTION[self.state] * ACTION_PER_TIME * game_framework.frame_time) % FRAMES_PER_ACTION[self.state]

    def draw(self):
        self.image[self.state].clip_draw(int(self.frame) * 256, 0, 256, 256, self.x, self.y, self.size, self.size)

        draw_rectangle(*self.get_bb())

    def get_bb(self):
        return self.x - 320, self.y - 512, self.x + 320, self.y

    def handle_event(self, event):
        pass

    def handle_collision(self, group, other):
        if group == 'player:enemy':
            pass
        elif group == 'enemy:weapon':
            if not self.if_hurt and not self.state == 'Death':
                self.hp -= 10
                self.if_hurt = True
                self.frame = 0
                self.dir = 0  # 멈춤
                self.state = 'Hurt'
                self.state_start_time = get_time()
            if self.hp <= 0:
                # 죽음 상태로 전환
                self.state = 'Death'
                self.if_hurt = False
        elif group == 'enemy:tile':
            left_enemy, bottom_enemy, right_enemy, top_enemy = self.get_bb()
            left_tile, bottom_tile, right_tile, top_tile = other.get_bb()

            #  아래로 떨어지고 있고, 발이 타일 상단 근처에 있을 때
            if self.y_velocity <= 0 and abs(bottom_enemy - top_tile) < 10: # 10은 약간의 오차 허용 범위
                #  타일의 좌우 범위 내에 있는지 확인
                if right_enemy > left_tile and left_enemy < right_tile:
                    self.on_tile = True
                    self.y += top_tile - bottom_enemy
                    self.y_velocity = 0

    def build_behavior_tree(self):
        root = None
        self.bt = BehaviorTree(root)