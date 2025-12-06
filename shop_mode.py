from pico2d import *

import game_framework
import game_world
import common

shop_image = None
font = None
shop_category = None

def handle_events():
    event_list = get_events()
    for event in event_list:
        if event.type == SDL_QUIT:
            game_framework.quit()
        elif (event.type, event.key) == (SDL_KEYDOWN, SDLK_ESCAPE) or \
             (event.type, event.key) == (SDL_KEYDOWN, SDLK_e):
            game_framework.pop_mode()
        elif (event.type, event.key) == (SDL_KEYDOWN, SDLK_1):
            # 아이템 구매 로직 (예시)
            if shop_category == 'drink':
                print("포션 구매 시도")
            elif shop_category == 'weapon':
                print("무기1 구매 시도")
        elif (event.type, event.key) == (SDL_KEYDOWN, SDLK_2):
            if shop_category == 'weapon':
                print("무기2 구매 시도")

def init():
    global shop_image, font, shop_category
    if shop_image is None:
        shop_image = {}
        shop_image['drink'] = load_image('./resources/gui/shop_drink.png')
        shop_image['weapon'] = load_image('./resources/gui/shop_weapon.png')
    if font is None:
        font = load_font('./resources/font/ENCR10B.TTF', 32)

    # 어떤 상점과 상호작용했는지 확인
    if game_world.collide(common.player, common.trader_drink):
        shop_category = 'drink'
    elif game_world.collide(common.player, common.trader_weapon):
        shop_category = 'weapon'

    # 상호작용이 없으면 모드 종료
    if shop_category is None:
        game_framework.pop_mode()

def update():
    #game_world.update()
    #game_world.handle_collisions()
    pass

def draw():
    clear_canvas()
    game_world.render()
    if shop_category and shop_category in shop_image:
        # 상점 GUI를 화면 중앙에 그림
        shop_image[shop_category].draw(1920 // 2, 720 // 2, 500, 500)
    update_canvas()


def finish():
    #game_world.clear()
    pass

def pause():
    pass

def resume():
    global shop_category
    # resume 시 상호작용 상태를 다시 확인
    shop_category = None
    if game_world.collide(common.player, common.trader_drink):
        shop_category = 'drink'
    elif game_world.collide(common.player, common.trader_weapon):
        shop_category = 'weapon'

    if shop_category is None:
        game_framework.pop_mode()