import random
from pico2d import *

import game_framework
import game_world
import stage1_mode
import title_mode

from background import Background
from player import Player
from slime import Slime
from tiles import Tile

tiles = None
portal_left = None
portal_right = None

def handle_events():
    event_list = get_events()
    for event in event_list:
        if event.type == SDL_QUIT:
            game_framework.quit()
        elif event.type == SDL_KEYDOWN and event.key == SDLK_ESCAPE:
            game_framework.change_mode(title_mode)
        else:
            game_world.player.handle_event(event)

def init():
    global tiles, portal_left, portal_right

    # 스테이지 이동에 따른 플레이어 위치 조정
    if game_world.stage_from == 'stage1':
        game_world.player.x, game_world.player.y = 50, 128
    else:
        game_world.player.x, game_world.player.y = 1800, 128

    background = Background()
    game_world.add_object(background, 0)

    tiles = [Tile(x * 64) for x in range(0, 30 + 1)]
    game_world.add_objects(tiles, 1)

    # 충돌 쌍 추가
    for tile in tiles:
        game_world.add_collision_pair('player:tile', None, tile)

    portal_left = Portal(-100, 150)
    game_world.add_object(portal_left, 1)

    portal_right = Portal(1950, 150)
    game_world.add_object(portal_right, 1)

    slimes = [Slime(x * 256) for x in range(2, 4 + 1)]
    game_world.add_objects(slimes, 2)

def update():
    game_world.update()
    game_world.handle_collisions() # handle_collisions 호출

    global tiles, portal_left, portal_right
    player = game_world.player

    if game_world.collide(player, portal_left):
        print("이전 스테이지로 이동")
        game_world.stage = 'stage1'
        game_world.stage_from = 'stage2'
        game_framework.change_mode(stage1_mode)

    if game_world.collide(player, portal_right):
        print("다음 스테이지로 이동")


def draw():
    clear_canvas()
    game_world.render()
    update_canvas()


def finish():
    game_world.clear()

def pause(): pass
def resume(): pass

class Portal:
    def __init__(self, x, y, width = 100, height = 100):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def update(self):
        pass

    def draw(self):
        draw_rectangle(*self.get_bb())

    def get_bb(self):
        return self.x - self.width // 2, self.y - self.height // 2, self.x + self.width // 2, self.y + self.height // 2