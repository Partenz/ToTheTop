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

TIME_PER_ACTION = 0.5
ACTION_PER_TIME = 1.0 / TIME_PER_ACTION
FRAMES_PER_ACTION = {'Idle': 4, 'Run': 6, 'Attack' : 8, 'Hurt' : 4, 'Death' : 9}

GRAVITY = 9.8  # 중력 가속도 (m/s²)
GRAVITY_PPS = GRAVITY * PIXEL_PER_METER  # 중력을 픽셀 단위로 변환

class Mushroom:
    image = None

    def __init__(self, x = 50, y = 150, hp = 50):
        if Mushroom.image is None:
            Mushroom.image = {}
            Mushroom.image['Idle'] = load_image('./resources/mushroom/Mushroom_Idle.png')
            Mushroom.image['Run'] = load_image('./resources/mushroom/Mushroom_Run.png')
            Mushroom.image['Attack'] = load_image('./resources/mushroom/Mushroom_Attack.png')
            Mushroom.image['Hurt'] = load_image('./resources/mushroom/Mushroom_Hurt.png')
            Mushroom.image['Death'] = load_image('./resources/mushroom/Mushroom_Death.png')

        self.hp = hp
        self.if_hurt = False

        self.on_tile = False
        self.y_velocity = 0
        self.x , self.y =  x, y
        self.tx = None
        self.frame = random.randint(0, 6)
        self.face_dir = 1  # 1: right, -1: left
        self.dir = 0 # 0 정지 1 오른쪽 -1 왼쪽
        self.size = 256
        self.state = 'Idle'
        self.state_start_time = get_time()

        self.build_behavior_tree()

    def update(self):
        self.on_tile = False
        if self.state != 'Hurt' and self.state != 'Death' and self.state != 'Attack':
            self.bt.run()

        # 타일 위에 있지 않으면 추락
        if not self.on_tile:
            self.y_velocity -= GRAVITY_PPS * game_framework.frame_time
            self.y += self.y_velocity * game_framework.frame_time

        if self.state == 'Attack':
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
        if self.face_dir == 1:
            self.image[self.state].clip_draw(int(self.frame) * 64, 0, 64, 64, self.x, self.y, self.size, self.size)
        elif self.face_dir == -1:
            self.image[self.state].clip_draw(int(self.frame) * 64, 64, 64, 64, self.x, self.y, self.size, self.size)

        draw_rectangle(*self.get_bb())

    def get_bb(self):
        if self.state == 'Attack':
            if self.face_dir == 1:
                return self.x - 50, self.y - 40, self.x + 80, self.y + 70
            elif self.face_dir == -1:
                return self.x - 80, self.y - 40, self.x + 50, self.y + 70
        else:
            return self.x - 50, self.y - 40, self.x + 50, self.y + 70

    def handle_event(self, event):
        pass

    def handle_collision(self, group, other):
        if group == 'player:enemy':
            pass
        elif group == 'enemy:weapon':
            if not self.if_hurt and not self.state == 'Death':
                self.hp -= common.player.stat.attack()
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

    def set_patrol_location(self):
        self.tx = random.randint(int(self.x) - 100, int(self.x) + 100)
        return BehaviorTree.SUCCESS

    def move_to_location(self):
        self.state = 'Run'
        if abs(self.tx - self.x) < 5:
            self.dir = 0
            self.state = 'Idle'
            return BehaviorTree.SUCCESS
        elif self.tx > self.x:
            self.dir = 1
            self.face_dir = 1
        else:
            self.dir = -1
            self.face_dir = -1

        self.x += self.dir * RUN_SPEED_PPS * game_framework.frame_time
        return BehaviorTree.RUNNING

    def attack(self):
        self.state = 'Attack'
        self.frame = 0
        self.state_start_time = get_time()
        self.dir = 0  # 공격하는 동안 멈춤
        if common.player.x > self.x:
            self.face_dir = 1
        else:
            self.face_dir = -1

        return BehaviorTree.SUCCESS

    def wait_after_attack(self):
        if get_time() - self.state_start_time < 2.0:
            return BehaviorTree.RUNNING
        else:
            return BehaviorTree.SUCCESS

    def distance_less_than(self, x1, y1, x2, y2, r):
        distance2 = (x2 - x1) ** 2 + (y2 - y1) ** 2
        return distance2 < (PIXEL_PER_METER * r) ** 2

    def if_nearby_player(self, r):
        if self.distance_less_than(self.x, self.y, common.player.x, common.player.y, r):
            return BehaviorTree.SUCCESS
        else:
            return BehaviorTree.FAIL

    def build_behavior_tree(self):

        a1 = Action('순찰 위치 설정', self.set_patrol_location)
        a2 = Action('지점으로 이동', self.move_to_location)
        a3 = Action('공격', self.attack)
        a4 = Action('공격 후 대기', self.wait_after_attack)

        c1 = Condition('플레이어가 가까이 있는가?', self.if_nearby_player, 2)

        attack_if_nearby_player = Sequence('플레이어가 가까이 있다면 공격', c1, a3, a4)
        patrol = Sequence('주변을 순찰', a1, a2)



        root = attack_or_patrol = Selector('공격 아니면 순찰', attack_if_nearby_player, patrol)
        self.bt = BehaviorTree(root)