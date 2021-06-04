import os
import random

import yaml

import Objects
from Images import SpecialFixturesProvider, FixturesProvider
from Settings import SettingsProvider

OBJECT_TEXTURE = os.path.join("texture", "objects")
ENEMY_TEXTURE = os.path.join("texture", "enemies")
ALLY_TEXTURE = os.path.join("texture", "ally")


def reload_game(engine, hero):
    global level_list
    level_list_max = len(level_list) - 1
    engine.level += 1
    hero.position = [1, 1]
    engine.objects = []
    generator = level_list[min(engine.level, level_list_max)]
    _map = generator['map'].get_map()
    engine.load_map(_map)
    engine.add_objects(generator['obj'].get_objects(_map))
    engine.add_hero(hero)


def restore_hp(engine, hero):
    engine.score += 0.1
    hero.hp = hero.max_hp
    engine.notify("HP restored")


def apply_blessing(engine, hero):
    gold_should_be_taken_from_hero = int(20 * 1.5 ** engine.level) - 2 * hero.stats.intelligence

    if hero.gold >= gold_should_be_taken_from_hero:
        engine.score += 0.2
        hero.gold -= gold_should_be_taken_from_hero
        if random.randint(0, 1) == 0:
            engine.hero = Objects.Blessing(hero)
            engine.notify("Blessing applied")
        else:
            engine.hero = Objects.Berserk(hero)
            engine.notify("Berserk applied")
    else:
        engine.score -= 0.1


def remove_effect(engine, hero):
    gold_should_be_taken_from_hero = int(10 * 1.5 ** engine.level) - 2 * hero.stats.intelligence

    if hero.gold >= gold_should_be_taken_from_hero and "base" in dir(hero):
        hero.gold -= gold_should_be_taken_from_hero
        engine.hero = hero.base
        engine.hero.calc_max_HP()
        engine.notify("Effect removed")


def add_gold(engine, hero):
    if random.randint(1, 10) == 1:
        engine.score -= 0.05
        engine.hero = Objects.Weakness(hero)
        engine.notify("You were cursed")
    else:
        engine.score += 0.1
        gold = int(random.randint(10, 1000) * (1.1 ** (engine.hero.level - 1)))
        hero.gold += gold
        engine.notify(f"{gold} gold added")


object_list_actions = {
    'reload_game': reload_game,
    'add_gold': add_gold,
    'apply_blessing': apply_blessing,
    'remove_effect': remove_effect,
    'restore_hp': restore_hp
}


class MapFactory:
    class Map:
        pass

    class Objects:
        pass

    @classmethod
    def from_yaml(cls, loader, node):
        # FIXME
        # get _map and _obj

        # return {'map': _map, 'obj': _obj}
        return {'map': cls.create_map(), 'obj': cls.create_objects()}

    @classmethod
    def create_map(cls):
        return cls.Map()

    @classmethod
    def create_objects(cls):
        return cls.Objects()


class EndMap(MapFactory):
    class Map:
        def __init__(self, special_fixtures_provider: SpecialFixturesProvider):
            self.__map = ['000000000000000000000000000000000000000',
                          '0                                     0',
                          '0                                     0',
                          '0  0   0   000   0   0  00000  0   0  0',
                          '0  0  0   0   0  0   0  0      0   0  0',
                          '0  000    0   0  00000  0000   0   0  0',
                          '0  0  0   0   0  0   0  0      0   0  0',
                          '0  0   0   000   0   0  00000  00000  0',
                          '0                                   0 0',
                          '0                                     0',
                          '000000000000000000000000000000000000000'
                          ]
            self.__map = list(map(list, self.__map))
            self.__special_fixtures_provider = special_fixtures_provider

            for i in self.__map:
                for j in range(len(i)):
                    i[j] = self.__special_fixtures_provider.get_wall() if i[j] == '0' \
                        else self.__special_fixtures_provider.get_floor_1()

        def get_map(self):
            return self.__map

    class Objects:
        def __init__(self):
            self.objects = []

        def get_objects(self, _map):
            return self.objects


class RandomMap(MapFactory):
    class Map:

        def __init__(self, special_fixtures_provider: SpecialFixturesProvider):
            self.__map = [[0 for _ in range(41)] for _ in range(41)]
            self.__special_fixtures_provider = special_fixtures_provider

            for i in range(41):
                for j in range(41):
                    if i == 0 or j == 0 or i == 40 or j == 40:
                        self.__map[j][i] = self.__special_fixtures_provider.get_wall()
                    else:
                        self.__map[j][i] = [
                            self.__special_fixtures_provider.get_wall(),
                            self.__special_fixtures_provider.get_floor_1(),
                            self.__special_fixtures_provider.get_floor_2(),
                            self.__special_fixtures_provider.get_floor_3(),
                            self.__special_fixtures_provider.get_floor_1(),
                            self.__special_fixtures_provider.get_floor_2(),
                            self.__special_fixtures_provider.get_floor_3(),
                            self.__special_fixtures_provider.get_floor_1(),
                            self.__special_fixtures_provider.get_floor_2()
                        ][random.randint(0, 8)]

        def get_map(self):
            return self.__map

    class Objects:

        def __init__(
                self,
                settings_provider: SettingsProvider,
                fixtures_provider: FixturesProvider,
                special_fixtures_provider: SpecialFixturesProvider
        ):
            self.__objects = []
            self.__settings_provider = settings_provider
            self.__fixtures_provider = fixtures_provider
            self.__special_fixtures_provider = special_fixtures_provider

        def get_objects(self, _map):

            for prop in self.__settings_provider.get_objects():
                for i in range(random.randint(prop.min_count, prop.max_count)):
                    coord = (random.randint(1, 39), random.randint(1, 39))
                    intersect = True
                    while intersect:
                        intersect = False
                        if _map[coord[1]][coord[0]] == self.__special_fixtures_provider.get_wall():
                            intersect = True
                            coord = (random.randint(1, 39),
                                     random.randint(1, 39))
                            continue
                        for obj in self.__objects:
                            if coord == obj.position or coord == (1, 1):
                                intersect = True
                                coord = (random.randint(1, 39),
                                         random.randint(1, 39))

                    sprite = self.__fixtures_provider.load(os.path.join(OBJECT_TEXTURE, prop.sprite))
                    action = object_list_actions[prop.action]
                    self.__objects.append(Objects.Ally(sprite, action, coord))

            for prop in self.__settings_provider.get_ally():
                for i in range(random.randint(prop.min_count, prop.max_count)):
                    coord = (random.randint(1, 39), random.randint(1, 39))
                    intersect = True
                    while intersect:
                        intersect = False
                        if _map[coord[1]][coord[0]] == self.__special_fixtures_provider.get_wall():
                            intersect = True
                            coord = (random.randint(1, 39),
                                     random.randint(1, 39))
                            continue
                        for obj in self.__objects:
                            if coord == obj.position or coord == (1, 1):
                                intersect = True
                                coord = (random.randint(1, 39),
                                         random.randint(1, 39))

                    sprite = self.__fixtures_provider.load(os.path.join(ALLY_TEXTURE, prop.sprite))
                    action = object_list_actions[prop.action]
                    self.__objects.append(Objects.Ally(sprite, action, coord))

            for prop in self.__settings_provider.get_enemies():
                for i in range(random.randint(0, 5)):
                    coord = (random.randint(1, 30), random.randint(1, 22))
                    intersect = True
                    while intersect:
                        intersect = False
                        if _map[coord[1]][coord[0]] == self.__special_fixtures_provider.get_wall():
                            intersect = True
                            coord = (random.randint(1, 39),
                                     random.randint(1, 39))
                            continue
                        for obj in self.__objects:
                            if coord == obj.position or coord == (1, 1):
                                intersect = True
                                coord = (random.randint(1, 39),
                                         random.randint(1, 39))

                    sprite = self.__fixtures_provider.load(os.path.join(ENEMY_TEXTURE, prop.sprite))
                    self.__objects.append(Objects.Enemy(sprite, prop.statistic, prop.experience, coord))

            return self.__objects


# FIXME
# add classes for YAML !empty_map and !special_map{}

def create_random_map(
        settings_provider: SettingsProvider,
        fixtures_provider: FixturesProvider,
        special_fixtures_provider: SpecialFixturesProvider
):
    return {
        'map': RandomMap.Map(special_fixtures_provider),
        'obj': RandomMap.Objects(settings_provider, fixtures_provider, special_fixtures_provider)
    }


def service_init(
        settings_provider: SettingsProvider,
        fixtures_provider: FixturesProvider,
        special_fixtures_provider: SpecialFixturesProvider
):
    global level_list

    with open("levels.yml", "r") as file:
        yaml.add_constructor(
            "!random_map",
            lambda loader, node: create_random_map(settings_provider, fixtures_provider, special_fixtures_provider)
        )

        level_list = yaml.load(file.read())['levels']
        level_list.append({'map': EndMap.Map(special_fixtures_provider), 'obj': EndMap.Objects()})
