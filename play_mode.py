import random
from pico2d import *

import game_framework
import game_world
import title_mode

from background import Background
from player import Player
from tiles import Tile

player = None
stage = None
tiles = None

def handle_events():
    event_list = get_events()
    for event in event_list:
        if event.type == SDL_QUIT:
            game_framework.quit()
        elif event.type == SDL_KEYDOWN and event.key == SDLK_ESCAPE:
            game_framework.change_mode(title_mode)
        else:
            player.handle_event(event)

def init():
    global player, stage, tiles
    stage = 'stage1'

    player = Player()
    game_world.add_object(player, 3)

    background = Background()
    game_world.add_object(background, 0)

    tiles = [Tile(x * 64) for x in range(0, 10 + 1)]
    tiles += [Tile(x * 64, 200) for x in range(11, 20 + 1)]
    game_world.add_objects(tiles, 1)

def update():
    game_world.update()

    global player, tiles, stage
    for tile in tiles:
        if game_world.collide(tile, player):
            player.onTile = True

            left_tile, bottom_tile, right_tile, top_tile = tile.get_bb()
            left_player, bottom_player, right_player, top_player = player.get_bb()

            if bottom_tile < bottom_player <= top_tile and player.velocity_y <= 0: # 낙하 중일 때 타일과 만나면 위치 조정
                player.y += top_tile - bottom_player
            break
        else:
            player.onTile = False


def draw():
    clear_canvas()
    game_world.render()
    update_canvas()


def finish():
    game_world.clear()

def pause(): pass
def resume(): pass
