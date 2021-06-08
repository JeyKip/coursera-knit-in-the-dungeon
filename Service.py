import os
import random
from typing import Type, List

import yaml

import Objects
from Images import SpecialFixturesProvider, FixturesProvider, FixtureType
from Settings import SettingsProvider

OBJECT_TEXTURE = os.path.join("texture", "objects")
ENEMY_TEXTURE = os.path.join("texture", "enemies")
ALLY_TEXTURE = os.path.join("texture", "ally")


class Level:
    def __init__(self, level_map, level_objects):
        self.__level_map = level_map
        self.__level_objects = level_objects

    @property
    def level_map(self):
        return self.__level_map

    @property
    def level_objects(self):
        return self.__level_objects


class MapFactory:
    __settings_provider: SettingsProvider = None
    __fixtures_provider: FixturesProvider = None
    __special_fixtures_provider: SpecialFixturesProvider = None

    @classmethod
    def from_yaml(cls, loader, node) -> Level:
        _map = cls.create_map()
        _obj = cls.create_objects()

        return Level(_map, _obj)

    @classmethod
    def create_map(cls):
        # noinspection PyUnresolvedReferences
        return cls.Map(cls.__special_fixtures_provider)

    @classmethod
    def create_objects(cls):
        # noinspection PyUnresolvedReferences
        return cls.Objects(cls.__settings_provider, cls.__fixtures_provider)

    @classmethod
    def register_settings_provider(cls, settings_provider: SettingsProvider):
        cls.__settings_provider = settings_provider

    @classmethod
    def register_fixtures_provider(cls, fixtures_provider: FixturesProvider):
        cls.__fixtures_provider = fixtures_provider

    @classmethod
    def register_special_fixtures_provider(cls, special_fixtures_provider):
        cls.__special_fixtures_provider = special_fixtures_provider

    @staticmethod
    def calculate_object_coordinates(_map, _objects):
        coord = (random.randint(1, 39), random.randint(1, 39))
        intersect = True

        while intersect:
            intersect = False
            if _map[coord[1]][coord[0]].fixture_type == FixtureType.WALL:
                intersect = True
                coord = (random.randint(1, 39), random.randint(1, 39))
                continue
            for obj in _objects:
                if coord == obj.position or coord == (1, 1):
                    intersect = True
                    coord = (random.randint(1, 39), random.randint(1, 39))

        return coord


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
                    elif i == 1 and j == 1:
                        self.__map[j][i] = self.__special_fixtures_provider.get_floor_1()
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
                fixtures_provider: FixturesProvider
        ):
            self.__objects = []
            self.__settings_provider = settings_provider
            self.__fixtures_provider = fixtures_provider

        def get_objects(self, _map):
            for prop in self.__settings_provider.get_objects():
                self.__append_ally(_map, prop, OBJECT_TEXTURE)

            for prop in self.__settings_provider.get_ally():
                self.__append_ally(_map, prop, ALLY_TEXTURE)

            for prop in self.__settings_provider.get_enemies():
                self.__append_enemy(_map, prop, ENEMY_TEXTURE)

            return self.__objects

        def __append_ally(self, _map, prop, fixture_path):
            for i in range(random.randint(prop.min_count, prop.max_count)):
                coord = MapFactory.calculate_object_coordinates(_map, self.__objects)
                sprite = self.__fixtures_provider.load(os.path.join(fixture_path, prop.sprite))
                self.__objects.append(Objects.Ally(sprite, prop.action, coord))

        def __append_enemy(self, _map, prop, fixture_path):
            for i in range(random.randint(0, 5)):
                coord = MapFactory.calculate_object_coordinates(_map, self.__objects)
                sprite = self.__fixtures_provider.load(os.path.join(fixture_path, prop.sprite))
                self.__objects.append(Objects.Enemy(sprite, prop.statistic, prop.experience, coord))


# FIXME
# add classes for YAML !empty_map and !special_map{}


class LevelsProvider:
    def __init__(
            self,
            levels_settings_file_path: str,
            settings_provider: SettingsProvider,
            fixtures_provider: FixturesProvider,
            special_fixtures_provider: SpecialFixturesProvider
    ):
        self.__settings_provider = settings_provider
        self.__fixtures_provider = fixtures_provider
        self.__special_fixtures_provider = special_fixtures_provider
        self.__levels = self.__load_levels(levels_settings_file_path)

    def get_levels(self) -> List[Level]:
        return self.__levels

    def __load_levels(self, file_path) -> List[Level]:
        with open(file_path, "r") as file:
            yaml.add_constructor("!random_map", lambda loader, node: self.__create_level(RandomMap, loader, node))

            levels = yaml.load(file.read())['levels']
            levels.append(self.__create_end_level())

            return levels

    def __create_level(self, map_factory: Type[MapFactory], loader, node):
        map_factory.register_settings_provider(self.__settings_provider)
        map_factory.register_fixtures_provider(self.__fixtures_provider)
        map_factory.register_special_fixtures_provider(self.__special_fixtures_provider)

        return map_factory.from_yaml(loader, node)

    def __create_end_level(self):
        _map = EndMap.Map(self.__special_fixtures_provider)
        _obj = EndMap.Objects()

        return Level(_map, _obj)
