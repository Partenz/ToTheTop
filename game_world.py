import common

world = [[] for _ in range(4)]

stage = 'stage1'
stage_from = None

collision_pairs = {}

def add_collision_pair(group, a, b):
    if group not in collision_pairs:
        collision_pairs[group] = [[],[]]
    if a:
        collision_pairs[group][0].append(a)
    if b:
        collision_pairs[group][1].append(b)

def remove_collision_pairs(o):
    for pairs in collision_pairs.values():
        if o in pairs[0]:
            pairs[0].remove(o)
        if o in pairs[1]:
            pairs[1].remove(o)

def add_object(obj, depth = 0):
    world[depth].append(obj)

def add_objects(objl, depth = 0):
    world[depth] += objl


def update():
    for layer in world:
        for obj in layer:
            obj.update()


def render():
    for layer in world:
        for obj in layer:
            obj.draw()

def remove_object(obj):
    for layer in world:
        if obj in layer:
            layer.remove(obj)
            remove_collision_pairs(obj)
            return
    raise ValueError('Cannot delete non existing object')


def clear():
    global world

    # 플레이어를 제외한 모든 객체를 월드에서 제거
    for layer in world:
        for obj in layer.copy():
            if obj != common.player:
                layer.remove(obj)
                remove_collision_pairs(obj)

def collide(a,b):
    left_a, bottom_a, right_a, top_a = a.get_bb()
    left_b, bottom_b, right_b, top_b = b.get_bb()

    if left_a > right_b: return False
    if right_a < left_b: return False
    if top_a < bottom_b: return False
    if bottom_a > top_b: return False

    return True


def handle_collisions():
    for group, pairs in collision_pairs.items():
        for a in pairs[0]:
            for b in pairs[1]:
                if collide(a,b):
                    a.handle_collision(group, b)
                    b.handle_collision(group, a)