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

TIME_PER_ACTION = 2.0
ACTION_PER_TIME = 1.0 / TIME_PER_ACTION
FRAMES_PER_ACTION = {'Appearance': 8,'Idle': 8, 'Hurt' : 4, 'Death' : 6, 'Attack1' : 6, 'Attack2' : 6, 'Attack3' : 6, 'Attack4' : 6, 'Attack5' : 6, 'Attack6' : 6}

GRAVITY = 9.8  # 중력 가속도 (m/s²)
GRAVITY_PPS = GRAVITY * PIXEL_PER_METER  # 중력을 픽셀 단위로 변환

Attack = {
    'left': {'sweep': [(1220, 140), (1400, 140), (1400, 140), (1400, 140), (1000, 140), (1000, 140)],
             'smash': [(1220, 140), (1220, 250), (1220, 500), (1220, 500), (1220, 500), (1220, 140)]},
    'right': {'sweep': [(780, 140), (560, 140), (560, 140), (560, 140), (1000, 140), (1000, 140)],
              'smash': [(780, 140), (780, 250), (780, 500), (780, 500), (780, 500), (780, 500)]}
}

class BossAttack:
    def __init__(self, which_hand, which_attack):
        self.creation_time = get_time()
        self.which_hand = which_hand
        self.which_attack = which_attack
        self.frame = 0
        self.x = Attack[which_hand][which_attack][0][0]
        self.y = Attack[which_hand][which_attack][0][1]

    def update(self):
        if self.frame >= 5:
            game_world.remove_object(self)
            return

        self.frame = self.frame + 6 * ACTION_PER_TIME * game_framework.frame_time
        self.x = Attack[self.which_hand][self.which_attack][int(self.frame)][0]
        self.y = Attack[self.which_hand][self.which_attack][int(self.frame)][1]

    def get_bb(self):
        if int(self.frame) == 4 or int(self.frame) == 5:
            if self.which_attack == 'smash':
                return self.x - 50, self.y - 500, self.x + 50, self.y + 50
            elif self.which_attack == 'sweep':
                if self.which_hand == 'left':
                    return self.x - 50, self.y - 50, self.x + 500, self.y + 50
                elif self.which_hand == 'right':
                    return self.x - 500, self.y - 50, self.x + 50, self.y + 50
        else:
            return self.x - 50, self.y - 50, self.x + 50, self.y + 50

    def draw(self):
        # 디버깅용으로 바운딩 박스 그리기
        draw_rectangle(*self.get_bb())

    def handle_collision(self, group, other):
        if group == 'bossAttack:player':
            pass
        elif group == 'bossAttack:weapon':
            pass

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
        self.size = 1024
        self.state = 'Appearance'
        self.state_start_time = get_time()

        self.attack_cooldown = 2.0  # 2초 쿨타임
        self.last_attack_time = 0

        self.build_behavior_tree()

    def update(self):
        self.on_tile = False
        if self.state != 'Hurt' and self.state != 'Death' and not self.state.startswith('Attack'):
            self.bt.run()

        # 타일 위에 있지 않으면 추락
        if not self.on_tile:
            self.y_velocity -= GRAVITY_PPS * game_framework.frame_time
            self.y += self.y_velocity * game_framework.frame_time

        if self.state == 'Appearance':
            if get_time() - self.state_start_time > TIME_PER_ACTION:
                self.state_start_time = get_time()
                self.state = 'Idle'
        elif self.state.startswith('Attack'):
            if get_time() - self.state_start_time > TIME_PER_ACTION:
                self.state_start_time = get_time()
                self.state = 'Idle'
                self.last_attack_time = get_time()
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
        return self.x - 270, self.y - 512, self.x + 270, self.y

    def handle_event(self, event):
        pass

    def handle_collision(self, group, other):
        if group == 'player:boss':
            pass
        elif group == 'boss:weapon':
            if not self.if_hurt and not self.state == 'Death':
                self.hp -= 10
                self.if_hurt = True
                self.frame = 0
                self.state = 'Hurt'
                self.state_start_time = get_time()
            if self.hp <= 0:
                # 죽음 상태로 전환
                self.state = 'Death'
                self.if_hurt = False
        elif group == 'boss:tile':
            left_boss, bottom_boss, right_boss, top_boss = self.get_bb()
            left_tile, bottom_tile, right_tile, top_tile = other.get_bb()

            #  아래로 떨어지고 있고, 발이 타일 상단 근처에 있을 때
            if self.y_velocity <= 0 and abs(bottom_boss - top_tile) < 10: # 10은 약간의 오차 허용 범위
                #  타일의 좌우 범위 내에 있는지 확인
                if right_boss > left_tile and left_boss < right_tile:
                    self.on_tile = True
                    self.y += top_tile - bottom_boss
                    self.y_velocity = 0

    def is_player_near(self):
        distance = abs(common.player.x - self.x)
        if distance < 200:
            return BehaviorTree.SUCCESS
        else:
            return BehaviorTree.FAIL

    def is_player_far(self):
        distance = abs(common.player.x - self.x)
        if distance >= 200:
            return BehaviorTree.SUCCESS
        else:
            return BehaviorTree.FAIL

    def is_player_left(self):
        if common.player.x > self.x:
            return BehaviorTree.SUCCESS
        else:
            return BehaviorTree.FAIL

    def is_player_right(self):
        if common.player.x < self.x:
            return BehaviorTree.SUCCESS
        else:
            return BehaviorTree.FAIL

    def is_attack_all_hand(self):
        ran_choice = random.choice([True, False])

        if ran_choice:
            return BehaviorTree.SUCCESS
        else:
            return BehaviorTree.FAIL

    def is_what_attack(self):
        ran_choice = random.choice([True, False])

        if ran_choice:
            return BehaviorTree.SUCCESS
        else:
            return BehaviorTree.FAIL

    def set_state_idle(self):
        self.state = 'Idle'
        return BehaviorTree.SUCCESS

    def set_attack_state(self, attack_type):
        self.state = attack_type
        self.frame = 0
        self.state_start_time = get_time()
        if attack_type == 'Attack1':
            boss_hand_left = BossAttack('left', 'smash')
            boss_hand_right = BossAttack('right', 'smash')
            game_world.add_object(boss_hand_left, 3)
            game_world.add_object(boss_hand_right, 3)
            game_world.add_collision_pair('bossAttack:player', boss_hand_left, None)
            game_world.add_collision_pair('bossAttack:weapon', boss_hand_left, None)
            game_world.add_collision_pair('bossAttack:player', boss_hand_right, None)
            game_world.add_collision_pair('bossAttack:weapon', boss_hand_right, None)
        elif attack_type == 'Attack2':
            boss_hand = BossAttack('left', 'smash')
            game_world.add_object(boss_hand, 3)
            game_world.add_collision_pair('bossAttack:player', boss_hand, None)
            game_world.add_collision_pair('bossAttack:weapon', boss_hand, None)
        elif attack_type == 'Attack3':
            boss_hand = BossAttack('right', 'smash')
            game_world.add_object(boss_hand, 3)
            game_world.add_collision_pair('bossAttack:player', boss_hand, None)
            game_world.add_collision_pair('bossAttack:weapon', boss_hand, None)
        elif attack_type == 'Attack4':
            boss_hand_left = BossAttack('left', 'sweep')
            boss_hand_right = BossAttack('right', 'sweep')
            game_world.add_object(boss_hand_left, 3)
            game_world.add_object(boss_hand_right, 3)
            game_world.add_collision_pair('bossAttack:player', boss_hand_left, None)
            game_world.add_collision_pair('bossAttack:weapon', boss_hand_left, None)
            game_world.add_collision_pair('bossAttack:player', boss_hand_right, None)
            game_world.add_collision_pair('bossAttack:weapon', boss_hand_right, None)
        elif attack_type == 'Attack5':
            boss_hand = BossAttack('left', 'sweep')
            game_world.add_object(boss_hand, 3)
            game_world.add_collision_pair('bossAttack:player', boss_hand, None)
            game_world.add_collision_pair('bossAttack:weapon', boss_hand, None)
        elif attack_type == 'Attack6':
            boss_hand = BossAttack('right', 'sweep')
            game_world.add_object(boss_hand, 3)
            game_world.add_collision_pair('bossAttack:player', boss_hand, None)
            game_world.add_collision_pair('bossAttack:weapon', boss_hand, None)
        return BehaviorTree.SUCCESS

    def is_attack_ready(self):
        if get_time() - self.last_attack_time > self.attack_cooldown:
            return BehaviorTree.SUCCESS
        else:
            return BehaviorTree.FAIL

    def build_behavior_tree(self):
        # 조건 노드
        is_player_near = Condition('플레이어가 가까이 있는가?', self.is_player_near)
        # is_player_near의 반대 조건
        is_player_far = Condition('플레이어가 멀리 있는가?', self.is_player_far)
        is_player_left = Condition('플레이어가 왼쪽에 있는가?', self.is_player_left)
        # is_player_left의 반대 조건
        is_player_right = Condition('플레이어가 오른쪽에 있는가?', self.is_player_right)
        is_attack_all_hand = Condition('양손 공격 할 건가?', self.is_attack_all_hand)
        is_what_attack = Condition('양손 공격 중 어떤 공격을 할 건가?', self.is_what_attack)
        is_attack_ready = Condition('공격 준비가 되었는가?', self.is_attack_ready)

        # 대기 행동
        action_default = Action('대기', self.set_state_idle)
        # 공격 행동
        sweep_left = Action('왼쪽 쓸어오기 공격', self.set_attack_state, 'Attack5')
        sweep_right = Action('오른쪽 쓸어오기 공격', self.set_attack_state, 'Attack6')
        sweep_all = Action('양손 쓸어오기 공격', self.set_attack_state, 'Attack4')
        smash_ground_all = Action('양손 땅 내려찍기 공격', self.set_attack_state, 'Attack1')
        smash_ground_left = Action('왼손 땅 내려찍기 공격', self.set_attack_state, 'Attack2')
        smash_ground_right = Action('오른손 땅 내려찍기 공격', self.set_attack_state, 'Attack3')

        # 공격 시퀀스 노드
        attack1 = Sequence('왼쪽에 가까이 있다면 왼쪽 쓸어오기', is_attack_ready, is_player_near, is_player_left, sweep_left)
        attack2 = Sequence('왼쪽에 있지만 멀다면 왼쪽 내려찍기', is_attack_ready, is_player_far, is_player_left, smash_ground_left)
        attack3 = Sequence('오른쪽에 가까이 있다면 오른쪽 쓸어오기', is_attack_ready, is_player_near, is_player_right, sweep_right)
        attack4 = Sequence('오른쪽에 있지만 멀다면 오른쪽 내려찍기', is_attack_ready, is_player_far, is_player_right, smash_ground_right)
        attack5 = Sequence('양손 쓸어오기 공격', sweep_all)
        attack6 = Sequence('양손 땅 내려찍기 공격', smash_ground_all)

        # 양손 공격이라면 뭘로 공���할지 선택
        all_attack_sweep = Sequence('양손 쓸어오기 선택하기', is_what_attack, attack5)
        choice_all_attack = Selector('양손 공격 선택하기', all_attack_sweep, attack6)
        all_hand_attack = Sequence('양손 공격', is_attack_ready, is_attack_all_hand, choice_all_attack)

        # 무슨 공격할지
        choice_attack = Selector('어떤 공격을 할 것인가?', all_hand_attack, attack1, attack2, attack3, attack4, action_default)

        root = choice_attack
        self.bt = BehaviorTree(root)