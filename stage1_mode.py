import random
from pico2d import *

import game_framework
import game_world
import stage2_mode
import title_mode

from background import Background
from player import Player
from tiles import Tile

player = None
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
            player.handle_event(event)

def init():
    global player, tiles, portal

    if game_world.stage_from == 'stage2':
        player = Player(1800, 128)
    else:
        player = Player()

    game_world.add_object(player, 3)

    background = Background()
    game_world.add_object(background, 0)

    tiles = [Tile(x * 64) for x in range(0, 30 + 1)]
    tiles += [Tile(x * 64, 200) for x in range(11, 13 + 1)]
    tiles += [Tile(x * 64, 340) for x in range(15, 18 + 1)]
    game_world.add_objects(tiles, 1)

    portal = Portal(1900, 150)
    game_world.add_object(portal, 1)

def update():
    game_world.update()

    global player, tiles, portal
    for tile in tiles:
        if game_world.collide(tile, player):
            left_tile, bottom_tile, right_tile, top_tile = tile.get_bb()
            left_player, bottom_player, right_player, top_player = player.get_bb()

            if  player.y_velocity <= 0 and bottom_player <= top_tile and top_player > top_tile:
                player.onTile = True
                player.y += top_tile - bottom_player
                if player.state_machine.cur_state == player.JUMP:
                    player.y_velocity = 0
                    player.state_machine.handle_state_event(('JUMP_END', None))
                break
        else:
            player.onTile = False

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