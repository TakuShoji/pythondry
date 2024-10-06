# -*- coding: utf-8 -*-
"""
Created on Sat Oct  5 13:31:04 2024

@author: Taku
"""
# -*- coding: utf-8 -*-

import numpy as np
from enum import Enum
from dataclasses import dataclass, replace, fields

rng = np.random.default_rng()

class Status(Enum):
    NORMAL = "正常"
    SLEEP = "睡眠"
    PANIC = "恐慌"
    PARALYSIS = "麻痺"
    PETRIFICATION = "石化"
    DEATH = "死亡"
    ASH = "灰化"
    DISAPPEARANCE = "消失"

class Sex(Enum):
    MALE = "男"
    FEMALE = "女"

class Alignment(Enum):
    GOOD = "善"
    NEUTRAL = "中立"
    EVIL = "悪"

class Race(Enum):
    HUMAN = "人間"
    ELF = "エルフ"
    DWARF = "ドワーフ"
    GNOME = "ノーム"
    HALFLING = "ハーフリング"

class Class(Enum):
    FIGHTER = "戦士"
    MAGE = "魔術師"
    PRIEST = "僧侶"
    THIEF = "盗賊"
    BISHOP = "司教"
    SAMURAI = "侍"
    LORD = "君主"
    NINJA = "忍者"

@dataclass(frozen=True)
class Ability:
    strength: int
    intelligence: int
    piety: int
    vitality: int
    agility: int
    luck: int
    
    @classmethod
    def get_attributes(cls):
        return [field.name for field in fields(cls)]
    
    @classmethod
    def japanized_names(cls):
        jnp_val = ["力", "知恵", "信仰心", "生命力", "素早さ", "運"]
        return dict(zip(cls.get_attributes(), jnp_val))
        

ABILITIES = {
    Race.HUMAN: Ability(8, 8, 5, 8, 8, 9),
    Race.ELF: Ability(7, 10, 10, 6, 9, 6),
    Race.DWARF: Ability(10, 7, 10, 10, 5, 6),
    Race.GNOME: Ability(7, 7, 10, 8, 10, 7),
    Race.HALFLING: Ability(5, 7, 7, 6, 10, 15)
}

FIRST_HP_RANGE = {
    Class.FIGHTER: (8, 15),
    Class.MAGE: (2, 7),
    Class.PRIEST: (6, 13),
    Class.THIEF: (4, 9),
    Class.BISHOP: (4, 9),
    Class.SAMURAI: (12, 19),
    Class.LORD: (8, 15),
    Class.NINJA: (6, 12)
}

CLASS_FORTUNES = {
    Class.FIGHTER: dict(zip(range(1, 6), [3, 0, 0, 0, 0])),
    Class.MAGE: dict(zip(range(1, 6), [0, 0, 0, 0, 3])),
    Class.PRIEST: dict(zip(range(1, 6), [0, 3, 0, 0, 0])),
    Class.THIEF: dict(zip(range(1, 6), [0, 0, 0, 3, 0])),
    Class.BISHOP: dict(zip(range(1, 6), [0, 2, 2, 0, 2])),
    Class.SAMURAI: dict(zip(range(1, 6), [2, 0, 0, 0, 2])),
    Class.LORD: dict(zip(range(1, 6), [2, 2, 0, 0, 0])),
    Class.NINJA: dict(zip(range(1, 6), [3, 2, 4, 3, 2]))
    }

RACE_FORTUNES = {
    Race.HUMAN: dict(zip(range(1, 6), [1, 0, 0, 0, 0])),
    Race.ELF: dict(zip(range(1, 6), [0, 0, 2, 0, 0])),
    Race.DWARF: dict(zip(range(1, 6), [0, 0, 0, 4, 0])),
    Race.GNOME: dict(zip(range(1, 6), [0, 2, 0, 0, 0])),
    Race.HALFLING: dict(zip(range(1, 6), [0, 0, 0, 0, 3]))
    }

def required_exp(target_level, ones_class):
    def func(x , a, b):
        result = np.exp(a * x + b)
        return int(round(result, 0)) + 1
    
    coefs = dict(
        zip(
            Class,
            [[0.5447447747283312, 5.817734123206997],
             [0.5447457590750674, 5.912557376890108],
             [0.5447461113352284, 5.866302632956038],
             [0.5447457844727372, 5.711980964858709],
             [0.5621341620328307, 5.965181579854299],
             [0.5621341620328307, 5.965181579854299],
             [0.5621317663057328, 6.045232902446928],
             [0.5621314991474423, 6.15432123265716]]
            )
        )
    master_value = dict(zip(Class, [289709, 318529, 304132, 260639, 428479, 428479, 475008, 529756]))
    
    if target_level < 1:
        return -1
    
    elif target_level == 1:
        return 0
    
    elif 1 < target_level <= 13:
        return func(target_level, *coefs[ones_class])
    
    else:
        exp_value = func(13, *coefs[ones_class]) + master_value[ones_class] * (target_level - 13)
        return exp_value


class Adventurer:
    def __init__(self, name, sex, race, alignment, class_):
        self.name = name
        self.level = 1
        self.sex = self.validate_attribute(sex, Sex)
        self.race = self.validate_attribute(race, Race)
        self.alignment = self.validate_attribute(alignment, Alignment)
        self.class_ = self.validate_attribute(class_, Class)
        self.age = rng.integers(14, 17)
        self.experience = 0
        self.gold = rng.integers(100, 200)
        self.ability = self.initial_ability()
        self.poison = 0
        self.silence = 0
        self.status = 0
        self.max_hp = self.initial_hp()
        self.hp = self.max_hp
        self.base_ac = 10
        self.ac = self.base_ac
        self.belongings = []
        self.max_mage_mp = dict(zip(range(1, 8), [0] * 7))
        self.mage_mp = self.max_mage_mp.copy()
        self.max_priest_mp = dict(zip(range(1, 8), [0] * 7))
        self.priest_mp = self.max_priest_mp.copy()
        self.learned_spells = {
            Class.MAGE: dict(zip(range(1, 8), [[]] * 7)),
            Class.PRIEST: dict(zip(range(1, 8), [[]] * 7))
        }
        self.apply_sex_bonus()
    
    def is_level_up(self):
        if self.experience >= required_exp(self.level+1, self.class_):
            return True
        else:
            return False

    def validate_attribute(self, attribute, enum_class):
        return attribute if attribute in enum_class else "異常"

    def initial_ability(self):
        if self.race != "異常":
            return ABILITIES[self.race]
        else:
            return Ability(-1, -1, -1, -1, -1, -1)
    
    def initialize_ability(self):
        self.ability = self.initial_ability()
        self.apply_sex_bonus()

    def initial_hp(self):
        if self.class_ != "異常":
            return rng.integers(*FIRST_HP_RANGE[self.class_])
        else:
            return -1
    
    def get_status(self):
        status_dict = dict(zip(range(8), list(Status)))
        return status_dict[self.status].value
    
    def get_max_ability(self, ability_name):
        value = getattr(ABILITIES[self.race], ability_name) + 10
        if (self.sex == Sex.MALE) & (ability_name == "strength"):
            value += 1
        elif (self.sex == Sex.FEMALE) & (ability_name == "vitality"):
            value += 1
        else:
            pass
            
        return value
    
    def increase_ability(self, ability_name, amount):
        if hasattr(self.ability, ability_name):
            new_value = np.clip(getattr(self.ability, ability_name) + amount, 0, self.get_max_ability(ability_name))
            self.ability = replace(self.ability, **{ability_name: new_value})

    def apply_sex_bonus(self):
        if self.sex == Sex.MALE:
            self.increase_ability("strength", 1)
        elif self.sex == Sex.FEMALE:
            self.increase_ability("vitality", 1)

    def get_fortune(self, number):
        # numberは1~5
        if all(map(lambda x, y: x in y, [self.race, self.class_], [Race, Class])):
            value = 19
            value -= np.clip(self.level, 1, 255) // 5
            value -= self.ability.luck // 6
            # クラスと種族のフォーチュンを適用
            value -= CLASS_FORTUNES[self.class_][number]
            value -= RACE_FORTUNES[self.race][number]
            return max(value, 0)
        else:
            return -1

    def get_str_bonus(self):
        x = self.ability.strength
        return np.piecewise(x, [x >= 16, 16 > x >= 6, 6 > x], [lambda x: x - 15, 0, lambda x: x - 6])

    def get_hitting_power(self, eq_str=0):
        lv_bonus = self.calculate_level_bonus()
        hitting_power = lv_bonus + self.get_str_bonus() + eq_str
        return hitting_power

    def calculate_level_bonus(self):
        lv_bonus = self.level
        if self.class_ in [Class.FIGHTER, Class.PRIEST, Class.SAMURAI, Class.LORD, Class.NINJA]:
            lv_bonus //= 3
            lv_bonus += 2
        elif self.class_ in [Class.MAGE, Class.THIEF, Class.BISHOP]:
            lv_bonus //= 5
        else:
            lv_bonus //= self.level
        return lv_bonus

    def get_hitting_rate(self, eq_str=0, enemy_group_num=7, enemy_ac=10):
        judge_value = 19 + enemy_group_num - enemy_ac - self.get_hitting_power(eq_str)
        judge_value = np.clip(judge_value, 0, 19)
        return (19 - judge_value) / 20

    def get_attack_time(self, eq_at=1):
        def calc_value(denominator, bonus, limit, eq_at_value):
            result = max(min(self.level // denominator + bonus, limit), eq_at_value)
            return max(result, 1)

        if self.class_ in [Class.MAGE, Class.BISHOP]:
            return calc_value(10, 0, 5, eq_at)
        elif self.class_ in [Class.PRIEST, Class.THIEF]:
            return calc_value(10, 0, 10, eq_at)
        elif self.class_ in [Class.FIGHTER, Class.SAMURAI, Class.LORD]:
            return calc_value(5, 1, 24, eq_at)
        elif self.class_ in [Class.NINJA]:
            return calc_value(5, 2, 36, eq_at)

    def get_damage(self, dice_num=1, dice=6, bonus=0):
        damage = rng.integers(1, dice + 1, size=dice_num).sum() + bonus + self.get_str_bonus()
        return max(damage, 0)

    def attack_test(self, eq_str, dice_num, dice, bonus, enemy_ac):
        attack_time = self.get_attack_time()
        hit_time = 0
        hit_rate = self.get_hitting_rate(eq_str, enemy_ac=enemy_ac)
        damage = 0
        for _ in range(attack_time):
            if hit_rate >= rng.random():
                hit_time += 1
                damage += self.get_damage(dice_num, dice, bonus)
        if hit_time <= 0:
            print(f"{self.name}は攻撃を外した！")
        else:
            print(f"{self.name}はグレーターデーモンに切りかかった！")
            print(f"そして{hit_time}回あたり{damage}のダメージ！")

def main():
    man = Adventurer("戦士1", Sex.MALE, Race.HUMAN, Alignment.NEUTRAL, Class.FIGHTER)
    print("名前：　", man.name)
    print("状態： ", man.get_status())
    man.level += 0
    print("HP： ", man.max_hp)
    print(man.class_.value)
    for k in man.ability.__dict__.keys():
        print(Ability.japanized_names()[k], ": ", man.get_max_ability(k))
    weapon_str = 6
    e_ac = -2
    man.increase_ability("strength", 10)
    print("--------------")
    for k, v in man.ability.__dict__.items():
        print(Ability.japanized_names()[k], ": ", v)
    print("攻撃回数：　", man.get_attack_time())
    print("命中率：　", man.get_hitting_rate(weapon_str, enemy_ac=e_ac))
    man.attack_test(weapon_str, 1, 3, 9, e_ac)
    man.initialize_ability()
    print("--------------")
    for k, v in man.ability.__dict__.items():
        print(Ability.japanized_names()[k], ": ", v)
    
    man.experience += 10000
    while man.is_level_up():
        man.level += 1
        print(man.level)
    print("次のレベルまであと",required_exp(man.level+1, man.class_)-man.experience,"の経験が必要です")
    
if __name__ == "__main__":
    main()