from pico2d import get_time, draw_rectangle

import game_world


class Weapon:
    def __init__(self, player):
        self.player = player
        self.creation_time = get_time()
        self.x = None
        self.y = None

    def update(self):
        if self.player.face_dir == 1:
            self.x = self.player.x + 66
            self.y = self.player.y + 5
        else:
            self.x = self.player.x - 66
            self.y = self.player.y + 5

        # 일정 시간 후 자동 소멸
        if get_time() - self.creation_time > 0.5: # 예: 0.5초
            game_world.remove_object(self)

    def get_bb(self):
        # 무기의 바운딩 박스 반환
        return [(self.x - 34, self.y - 50, self.x + 34, self.y + 25)]

    def draw(self):
        # 디버깅용으로 바운딩 박스 그리기
        draw_rectangle(*self.get_bb()[0])