class Stat:
    def __init__(self, hp=100, attack=10, defense=5):
        self.base_hp = hp
        self.base_attack = attack
        self.base_defense = defense

        self.bonus_hp = 0
        self.bonus_attack = 0
        self.bonus_defense = 0

    @property
    def max_hp(self):
        return self.base_hp + self.bonus_hp

    @property
    def attack(self):
        return self.base_attack + self.bonus_attack

    @property
    def defense(self):
        return self.base_defense + self.bonus_defense

