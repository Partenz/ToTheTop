from pico2d import *

import game_framework
import game_world
import common

shop_image = None
font = None
shop_category = None
weapon_image = []
weapon_price = [50, 100, 100, 100]  # Sword1, Sword2, Helmet, Armor
drink_image = None
drink_price = 10  # Health Potion
# 각 'BUY' 버튼의 사각형 영역 정의 (x1, y1, x2, y2)
buy_buttons = {
    'weapon': [
        (790, 420, 860, 450),  # Sword 1
        (915, 420, 985, 450),  # Sword 2
        (1055, 420, 1125, 450), # Helmet
        (785, 230, 855, 260)   # Armor
    ],
    'drink': [
        (790, 420, 860, 450)   # Health Potion]
    ]
}

BUY_SOUND = None

def is_point_in_rect(x, y, rect):
    x1, y1, x2, y2 = rect
    return x1 <= x <= x2 and y1 <= y <= y2


def handle_events():
    event_list = get_events()
    for event in event_list:
        if event.type == SDL_QUIT:
            game_framework.quit()
        elif (event.type, event.key) == (SDL_KEYDOWN, SDLK_ESCAPE) or \
             (event.type, event.key) == (SDL_KEYDOWN, SDLK_e):
            game_framework.pop_mode()
        # 마우스 왼쪽 버튼 클릭 이벤트 처리
        elif event.type == SDL_MOUSEBUTTONDOWN and event.button == SDL_BUTTON_LEFT:
            # weapon 상점일 경우
            if shop_category == 'weapon':
                # weapon 상점의 각 버튼 확인
                for i, button_rect in enumerate(buy_buttons['weapon']):
                    # 마우스 클릭 위치가 버튼 영역 안에 있는지 확인
                    # pico2d의 y좌표는 위로 갈수록 증가하므로 변환 필요
                    if is_point_in_rect(event.x, get_canvas_height() - 1 - event.y, button_rect):
                        print(f'무기/방어구 {i + 1} 구매 시도')
                        # 여기에 실제 구매 로직을 추가합니다.
                        if common.player.coin >= weapon_price[i]:
                            common.player.coin -= weapon_price[i]
                            if i  == 0:
                                common.player.stat.bonus_attack += 15
                            elif i == 1:
                                common.player.stat.bonus_attack += 45
                            elif i == 2:
                                common.player.stat.bonus_defense += 10
                            elif i == 3:
                                common.player.stat.bonus_defense += 10
                            BUY_SOUND.play(1)
                            print(f'무기/방어구 {i + 1} 구매 완료! 남은 코인: {common.player.coin}')
                            print(f'현재 공격력 : {common.player.stat.attack}, 현재 방어력: {common.player.stat.defense}')
                        break
            elif shop_category == 'drink':
                for button_rect in buy_buttons['drink']:
                    if is_point_in_rect(event.x, get_canvas_height() - 1 - event.y, button_rect):
                        if common.player.coin >= drink_price:
                            common.player.coin -= drink_price
                            common.player.health_potion += 1
                            BUY_SOUND.play(1)
                            print(f'체력 물약 구매 완료! 남은 코인: {common.player.coin}, 현재 체력 물약 개수: {common.player.health_potion}')

def init():
    global shop_image, font, shop_category, weapon_image, drink_image, BUY_SOUND
    if shop_image is None:
        shop_image = {}
        shop_image['drink'] = load_image('./resources/gui/shop_drink.png')
        shop_image['weapon'] = load_image('./resources/gui/shop_weapon.png')
    if font is None:
        font = load_font('./resources/font/ENCR10B.TTF', 32)
    if len(weapon_image) == 0:
        weapon_image.append(load_image('./resources/gui/sword1.png'))
        weapon_image.append(load_image('./resources/gui/sword2.png'))
        weapon_image.append(load_image('./resources/gui/helmet.png'))
        weapon_image.append(load_image('./resources/gui/armor.png'))
    if drink_image is None:
        drink_image = load_image('./resources/gui/healthPotion.png')

    if BUY_SOUND is None:
        BUY_SOUND = load_wav('./resources/sound/Buy.mp3')
        BUY_SOUND.set_volume(30)

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
        if shop_category == 'weapon':
            weapon_image[0].draw(825, 520, 80, 80)
            weapon_image[1].draw(950, 520, 80, 80)
            weapon_image[2].draw(1090, 520, 80, 80)
            weapon_image[3].draw(820, 330, 80, 80)
            font.draw(790, 470, '50', (0, 0, 0))
            font.draw(920, 470, '100', (0, 0, 0))
            font.draw(1060, 470, '100', (0, 0, 0))
            font.draw(790, 280, '100', (0, 0, 0))
        elif shop_category == 'drink':
            drink_image.draw(825, 520, 80, 80)
            font.draw(790, 470, '10', (0, 0, 0))
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