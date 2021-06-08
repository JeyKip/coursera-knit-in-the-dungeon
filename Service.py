import os
import random
from typing import Type, List, Tuple

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
    MAP_WIDTH = 41
    MAP_HEIGHT = 41

    __settings_provider: SettingsProvider = None
    __fixtures_provider: FixturesProvider = None
    __special_fixtures_provider: SpecialFixturesProvider = None

    @classmethod
    def from_yaml(cls, loader, node) -> Level:
        _config = loader.construct_mapping(node, deep=True)
        _map = cls.create_map()
        _obj = cls.create_objects(_config)

        return Level(_map, _obj)

    @classmethod
    def create_map(cls):
        # noinspection PyUnresolvedReferences
        return cls.Map()

    @classmethod
    def create_objects(cls, config):
        # noinspection PyUnresolvedReferences
        return cls.Objects(cls.__settings_provider, config)

    @classmethod
    def register_settings_provider(cls, settings_provider: SettingsProvider):
        cls.__settings_provider = settings_provider

    @classmethod
    def register_fixtures_provider(cls, fixtures_provider: FixturesProvider):
        cls.__fixtures_provider = fixtures_provider

    @classmethod
    def register_special_fixtures_provider(cls, special_fixtures_provider):
        cls.__special_fixtures_provider = special_fixtures_provider

    @classmethod
    def generate_map(cls):
        _map = [[0 for _ in range(cls.MAP_WIDTH)] for _ in range(cls.MAP_HEIGHT)]

        for i in range(cls.MAP_WIDTH):
            for j in range(cls.MAP_HEIGHT):
                if i == 0 or j == 0 or i == cls.MAP_HEIGHT - 1 or j == cls.MAP_WIDTH - 1:
                    _map[j][i] = cls.__special_fixtures_provider.get_wall()
                elif i == 1 and j == 1:
                    _map[j][i] = cls.__special_fixtures_provider.get_floor_1()
                else:
                    _map[j][i] = [
                        cls.__special_fixtures_provider.get_wall(),
                        cls.__special_fixtures_provider.get_floor_1(),
                        cls.__special_fixtures_provider.get_floor_2(),
                        cls.__special_fixtures_provider.get_floor_3(),
                        cls.__special_fixtures_provider.get_floor_1(),
                        cls.__special_fixtures_provider.get_floor_2(),
                        cls.__special_fixtures_provider.get_floor_3(),
                        cls.__special_fixtures_provider.get_floor_1(),
                        cls.__special_fixtures_provider.get_floor_2()
                    ][random.randint(0, 8)]

        return _map

    @classmethod
    def calculate_object_coordinates(cls, _map, _objects) -> Tuple[int, int]:
        while True:
            coord = cls.generate_random_coordinates()

            if not cls._coord_intersect_with_hero(coord) and \
                    not cls._coord_intersect_with_wall(coord, _map) and \
                    not cls._coord_intersect_with_object(coord, _objects):
                return coord

    @classmethod
    def generate_random_coordinates(cls) -> Tuple[int, int]:
        return random.randint(1, cls.MAP_WIDTH - 2), random.randint(1, cls.MAP_HEIGHT - 2)

    @staticmethod
    def _coord_intersect_with_hero(coord):
        return coord == (1, 1)

    @staticmethod
    def _coord_intersect_with_wall(coord, _map):
        return _map[coord[1]][coord[0]].fixture_type == FixtureType.WALL

    @staticmethod
    def _coord_intersect_with_object(coord, _objects):
        for obj in _objects:
            if coord == obj.position:
                return True

        return False

    @classmethod
    def generate_objects(cls, _map, _existing_objects, min_count, max_count, action, sprite):
        return cls._generate_allies_internal(_map, _existing_objects, min_count, max_count, action, sprite,
                                             OBJECT_TEXTURE)

    @classmethod
    def generate_allies(cls, _map, _existing_objects, min_count, max_count, action, sprite):
        return cls._generate_allies_internal(_map, _existing_objects, min_count, max_count, action, sprite,
                                             ALLY_TEXTURE)

    @classmethod
    def generate_enemies(cls, _map, _existing_objects, min_count, max_count, stats, image_name, experience):
        for i in range(random.randint(min_count, max_count)):
            coord = cls.calculate_object_coordinates(_map, _existing_objects)
            sprite = cls.__fixtures_provider.load(os.path.join(ENEMY_TEXTURE, image_name))
            yield Objects.Enemy(sprite, stats, experience, coord)

    @classmethod
    def _generate_allies_internal(cls, _map, _existing_objects, min_count, max_count, action, image_name, texture_path):
        for i in range(random.randint(min_count, max_count)):
            coord = cls.calculate_object_coordinates(_map, _existing_objects)
            sprite = cls.__fixtures_provider.load(os.path.join(texture_path, image_name))
            yield Objects.Ally(sprite, action, coord)


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


class EmptyMap(MapFactory):
    class Map:
        def __init__(self):
            self.__map = EmptyMap.generate_map()

        def get_map(self):
            return self.__map

    class Objects:
        def __init__(self, settings_provider: SettingsProvider, config):
            self.__objects = []
            self.__settings_provider = settings_provider
            self.__config = config or {}

        def get_objects(self, _map):
            objects = self.__settings_provider.get_objects()
            stairs = list(filter(lambda obj: obj.name == "stairs", objects))

            # we need to add stairs only in the empty map so player will be able to find it and go to the next level
            if len(stairs) > 0:
                self.__objects.extend(
                    EmptyMap.generate_objects(_map, self.__objects, 1, 1, stairs[0].action, stairs[0].sprite))

            return self.__objects


class SpecialMap(MapFactory):
    class Map:
        def __init__(self):
            self.__map = SpecialMap.generate_map()

        def get_map(self):
            return self.__map

    class Objects:
        def __init__(self, settings_provider: SettingsProvider, config):
            self.__objects = []
            self.__settings_provider = settings_provider
            self.__config = config or {}

        def get_objects(self, _map):
            for prop in self.__settings_provider.get_objects():
                self.__objects.extend(
                    list(SpecialMap.generate_objects(_map, self.__objects, prop.min_count, prop.max_count, prop.action,
                                                     prop.sprite)))

            for prop in self.__settings_provider.get_ally():
                if prop.name in self.__config:
                    count = int(self.__config[prop.name])
                    self.__objects.extend(
                        list(SpecialMap.generate_allies(_map, self.__objects, count, count, prop.action, prop.sprite)))

            for prop in self.__settings_provider.get_enemies():
                if prop.name in self.__config:
                    count = int(self.__config[prop.name])
                    self.__objects.extend(
                        list(SpecialMap.generate_enemies(_map, self.__objects, count, count, prop.statistic,
                                                         prop.sprite, prop.experience)))

            return self.__objects


class RandomMap(MapFactory):
    class Map:
        def __init__(self):
            self.__map = RandomMap.generate_map()

        def get_map(self):
            return self.__map

    class Objects:
        def __init__(self, settings_provider: SettingsProvider, config):
            self.__objects = []
            self.__settings_provider = settings_provider
            self.__config = config or {}

        def get_objects(self, _map):
            for prop in self.__settings_provider.get_objects():
                self.__objects.extend(
                    list(RandomMap.generate_objects(_map, self.__objects, prop.min_count, prop.max_count, prop.action,
                                                    prop.sprite)))

            for prop in self.__settings_provider.get_ally():
                self.__objects.extend(
                    list(RandomMap.generate_allies(_map, self.__objects, prop.min_count, prop.max_count, prop.action,
                                                   prop.sprite)))

            for prop in self.__settings_provider.get_enemies():
                self.__objects.extend(
                    list(RandomMap.generate_enemies(_map, self.__objects, 0, 5, prop.statistic,
                                                    prop.sprite, prop.experience)))

            return self.__objects


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
            yaml.add_constructor("!empty_map", lambda loader, node: self.__create_level(EmptyMap, loader, node))
            yaml.add_constructor("!special_map", lambda loader, node: self.__create_level(SpecialMap, loader, node))
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
