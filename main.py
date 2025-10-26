from pico2d import *

open_canvas()
player = load_image('player_idle.png')

while True:
    clear_canvas()
    player.clip_draw()
    update_canvas()
    delay(1)

