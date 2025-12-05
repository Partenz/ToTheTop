import random
from pico2d import *

import game_framework
import game_world
import stage1_mode
import stage2_mode
import stage3_mode
import title_mode
import common

from background import Background
from boss import Boss
from mushroom import Mushroom
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
            game_world.stage = 'stage1'
        else:
            common.player.handle_event(event)

def init():
    global tiles, portal_left, portal_right

    if common.player is None:
        common.player = Player()
        game_world.add_object(common.player, 3)
        game_world.add_collision_pair('player:tile', common.player, None)
        game_world.add_collision_pair('player:enemy', common.player, None)
        game_world.add_collision_pair('player:boss', common.player, None)
        game_world.add_collision_pair('bossAttack:player', None, common.player)


    # 스테이지 이동에 따른 플레이어 위치 조정
    if game_world.stage_from == 'stage3':
        common.player.x, common.player.y = 50, 128
    else:
        common.player.x, common.player.y = 1800, 128

    background = Background()
    game_world.add_object(background, 0)

    tiles = [Tile(x * 64) for x in range(0, 30 + 1)]
    game_world.add_objects(tiles, 1)

    # 충돌 쌍 추가
    for tile in tiles:
        game_world.add_collision_pair('player:tile', None, tile)
        game_world.add_collision_pair('enemy:tile', None, tile)
        game_world.add_collision_pair('boss:tile', None, tile)

    portal_left = Portal(-100, 150)
    game_world.add_object(portal_left, 1)

    portal_right = Portal(1950, 150)
    game_world.add_object(portal_right, 1)

    boss = Boss(1000, 600)
    game_world.add_object(boss, 2)
    game_world.add_collision_pair('player:boss', None, boss)
    game_world.add_collision_pair('boss:weapon', boss, None)
    game_world.add_collision_pair('boss:tile', boss, None)

def update():
    game_world.update()
    game_world.handle_collisions() # handle_collisions 호출

    global tiles, portal_left, portal_right

    if game_world.collide(common.player, portal_left):
        print("이전 스테이지로 이동")
        game_world.stage = 'stage3'
        game_world.stage_from = 'stage4'
        game_framework.change_mode(stage3_mode)

    if game_world.collide(common.player, portal_right):
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