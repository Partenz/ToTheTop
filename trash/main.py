from pico2d import *

game_running = True

frame = 0

open_canvas(800, 600)

image = load_image('PlayerIDLE.png')

while game_running:
    clear_canvas()
    image.clip_draw(frame * 270,300, 270, 400, 400, 300)
    update_canvas()

    frame = (frame + 1) % 4

    events = get_events()
    for event in events:
        if event.type == SDL_QUIT:
            game_running = False
        elif event.type == SDL_KEYDOWN and event.key == SDLK_ESCAPE:
            game_running = False

    delay(1)

close_canvas()