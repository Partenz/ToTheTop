from pico2d import *

open_canvas()
player = load_image('playerGPT.png')

width = 0
height = 256
while True:
    clear_canvas()
    player.clip_draw(256 * width, 280 * 1, 256, 300, 400, 300)
    update_canvas()

    width = (width + 1) % 4

    delay(1)