from pico2d import *

open_canvas()
player = load_image('player_idle.png')

width = 0
height = 256
while True:
    clear_canvas()
    player.clip_draw(256 * width, height, 256, 256, 400, 300)
    update_canvas()

    width = (width + 1) % 4
    if width == 0 and height == 256:
        height -= 256
    elif width == 0 and height == 0:
        height += 256

    delay(1)