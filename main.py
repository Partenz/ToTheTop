from pico2d import *

open_canvas()
player = load_image('player_walk.png')

player2 = load_image('player_attack.png')

frame = 0
frame2 = 0

while True:
    clear_canvas()

    player.clip_draw(100 * frame, 0 , 100, 165, 200, 300)
    frame = (frame + 1) % 3

    player2.clip_draw(150 * frame2, 0 , 150, 165, 400, 300)
    frame2 = (frame2 + 1) % 4

    update_canvas()

    delay(0.1)

close_canvas()