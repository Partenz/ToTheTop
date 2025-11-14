world = [[] for _ in range(4)]

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
            return
    raise ValueError('Cannot delete non existing object')


def clear():
    global world

    objects = [[] for _ in range(4)]

def collide(a,b):
    left_a, bottom_a, right_a, top_a = a.get_bb()
    left_b, bottom_b, right_b, top_b = b.get_bb()

    if left_a > right_b: return False
    if right_a < left_b: return False
    if top_a < bottom_b: return False
    if bottom_a > top_b: return False

    return True
