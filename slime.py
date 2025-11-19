from pico2d import load_image, get_time, draw_rectangle

import random

import game_framework

PIXEL_PER_METER = (10.0 / 0.2)  # 10 pixel 20 cm
RUN_SPEED_KMPH = 10.0
RUN_SPEED_MPM = (RUN_SPEED_KMPH * 1000.0 / 60.0)
RUN_SPEED_MPS = (RUN_SPEED_MPM / 60.0)
RUN_SPEED_PPS = (RUN_SPEED_MPS * PIXEL_PER_METER)

TIME_PER_ACTION = 1.0
ACTION_PER_TIME = 1.0 / TIME_PER_ACTION
FRAMES_PER_ACTION = {'Idle': 6, 'Run': 8, 'Attack' : 10, 'Hurt' : 5, 'Death' : 10}

class Slime:
    image = None

    def __init__(self, x = 50, y = 100, hp = 20):
        if Slime.image is None:
            Slime.image = {}
            Slime.image['Idle'] = load_image('./resources/slime/Slime_IDLE.png')
            Slime.image['Run'] = load_image('./resources/slime/Slime_Run.png')
            Slime.image['Attack'] = load_image('./resources/slime/Slime_Attack.png')
            Slime.image['Hurt'] = load_image('./resources/slime/Slime_Hurt.png')
            Slime.image['Death'] = load_image('./resources/slime/Slime_Death.png')

        self.hp = hp

        self.x , self.y =  x, y
        self.start_x = x  # 초기 위치 저장
        self.patrol_range = 200  # 순찰 범위 (좌우 픽셀 수)
        self.frame = random.randint(0, 6)
        self.face_dir = 1  # 1: right, -1: left
        self.dir = 0 # 0 정지 1 오른쪽 -1 왼쪽
        self.size = 128
        self.state = 'Idle'
        self.state_start_time = get_time()

    def update(self):
        if get_time() - self.state_start_time > 2: # 2초마다 상태 변경
            self.state_start_time = get_time()
            self.state = random.choice(['Idle', 'Run'])
            if self.state == 'Run':
                self.dir = random.choice([-1, 1])
                self.face_dir = self.dir
            else:
                self.dir = 0

        if self.state == 'Run':
            self.x += RUN_SPEED_PPS * self.dir * game_framework.frame_time
            # 순찰 범위 제한
            if self.x > self.start_x + self.patrol_range:
                self.x = self.start_x + self.patrol_range
                self.dir = -1
                self.face_dir = -1

            elif self.x < self.start_x - self.patrol_range:
                self.x = self.start_x - self.patrol_range
                self.dir = 1
                self.face_dir = 1


        self.frame = (self.frame + FRAMES_PER_ACTION[self.state] * ACTION_PER_TIME * game_framework.frame_time) % FRAMES_PER_ACTION[self.state]

    def draw(self):
        if self.face_dir == 1:
            Slime.image[self.state].clip_draw(int(self.frame) * 64, 0, 64, 64, self.x, self.y, self.size, self.size)
        elif self.face_dir == -1:
            Slime.image[self.state].clip_draw(int(self.frame) * 64, 64, 64, 64, self.x, self.y, self.size, self.size)

        draw_rectangle(*self.get_bb())

    def get_bb(self):
        return self.x - 32, self.y - 20, self.x + 32, self.y + 32

    def handle_event(self, event):
        pass

    def handle_collision(self, group, other):
        if group == 'player:slime':
            pass