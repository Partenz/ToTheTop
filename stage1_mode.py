import random
from pico2d import *

import game_framework
import game_world
import stage2_mode
import title_mode

from background import Background
from npc import TraderDrink, TraderWeapon
from player import Player
from tiles import Tile

tiles = None
portal = None

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
    global tiles, portal

    if game_world.player is None:
        game_world.player = Player()
        game_world.add_object(game_world.player, 3)
        game_world.add_collision_pair('player:tile', game_world.player, None)
        game_world.add_collision_pair('player:enemy', game_world.player, None)

    # 스테이지 이동에 따른 플레이어 위치 조정
    if game_world.stage_from == 'stage2':
        game_world.player.x, game_world.player.y = 1800, 128
    else:
        game_world.player.x, game_world.player.y = 50, 128

    background = Background()
    game_world.add_object(background, 0)

    tiles = [Tile(x * 64) for x in range(0, 30 + 1)]
    tiles += [Tile(x * 64, 200) for x in range(4, 7 + 1)]
    tiles += [Tile(x * 64, 340) for x in range(9, 12 + 1)]
    game_world.add_objects(tiles, 1)

    for tile in tiles:
        game_world.add_collision_pair('player:tile', None, tile)

    portal = Portal(1950, 150)
    game_world.add_object(portal, 1)

    trader_drink = TraderDrink()
    game_world.add_object(trader_drink, 2)

    trader_weapon = TraderWeapon()
    game_world.add_object(trader_weapon, 2)




def update():
    game_world.update()
    game_world.handle_collisions()

    global tiles, portal
    player = game_world.player

    if game_world.collide(player, portal):
        print("다음 스테이지로 이동")
        game_world.stage = 'stage2'
        game_world.stage_from = 'stage1'
        game_framework.change_mode(stage2_mode)


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