import random
from pico2d import *

import game_framework
import game_world

from background import Background
from player import Player
from tiles import Tile

player = None
stage = None

def handle_events():
    event_list = get_events()
    for event in event_list:
        if event.type == SDL_QUIT:
            game_framework.quit()
        elif event.type == SDL_KEYDOWN and event.key == SDLK_ESCAPE:
            game_framework.quit()
        else:
            player.handle_event(event)

def init():
    global player, stage
    stage = 'stage1'

    player = Player()
    game_world.add_object(player, 3)

    background = Background()
    game_world.add_object(background, 0)

    tiles = [Tile(x * 64) for x in range(0, 10 + 1)]
    game_world.add_objects(tiles, 1)

def update():
    game_world.update()

def draw():
    clear_canvas()
    game_world.render()
    update_canvas()


def finish():
    game_world.clear()

def pause(): pass
def resume(): pass
