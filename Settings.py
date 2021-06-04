from typing import List

import yaml


class ObjectStatistic:
    def __init__(self, strength=None, endurance=None, intelligence=None, luck=None):
        self.__strength = strength
        self.__endurance = endurance
        self.__intelligence = intelligence
        self.__luck = luck

    @property
    def strength(self):
        return self.__strength

    @property
    def endurance(self):
        return self.__endurance

    @property
    def intelligence(self):
        return self.__intelligence

    @property
    def luck(self):
        return self.__luck

    def copy(self):
        return ObjectStatistic(self.__strength, self.__endurance, self.__intelligence, self.__luck)


class BaseObjectSetting:
    def __init__(self, name, sprite=None):
        self.__name = name
        self.__sprite = sprite[0] if sprite is not None and isinstance(sprite, list) else sprite

    @property
    def name(self):
        return self.__name

    @property
    def sprite(self):
        return self.__sprite


class ObjectSetting(BaseObjectSetting):
    def __init__(self, name, sprite=None, action=None, min_count=None, max_count=None):
        super().__init__(name, sprite)

        self.__action = action
        self.__min_count = min_count
        self.__max_count = max_count

    @property
    def action(self):
        return self.__action

    @property
    def min_count(self):
        return self.__min_count

    @property
    def max_count(self):
        return self.__max_count


class AllySetting(ObjectSetting):
    def __init__(self, name, sprite=None, action=None, min_count=None, max_count=None):
        super().__init__(name, sprite, action, min_count, max_count)


class EnemySetting(BaseObjectSetting):
    def __init__(self, name, sprite=None, experience=None, **kwargs):
        super().__init__(name, sprite)

        self.__experience = experience
        self.__statistic = ObjectStatistic(**kwargs)

    @property
    def experience(self):
        return self.__experience

    @property
    def statistic(self):
        return self.__statistic


class Settings:
    def __init__(self, objects=None, ally=None, enemies=None):
        self.__objects: List[ObjectSetting] = []
        self.__ally: List[AllySetting] = []
        self.__enemies: List[EnemySetting] = []

        if objects is not None:
            for key in objects:
                self.__objects.append(ObjectSetting(key, **self.__replace_dash_with_underscore_in_keys(objects[key])))

        if ally is not None:
            for key in ally:
                self.__ally.append(AllySetting(key, **self.__replace_dash_with_underscore_in_keys(ally[key])))

        if enemies is not None:
            for key in enemies:
                self.__enemies.append(
                    EnemySetting(key, **self.__replace_dash_with_underscore_in_keys(enemies[key])))

    @staticmethod
    def __replace_dash_with_underscore_in_keys(args: dict):
        return dict((k.replace('-', '_'), v) for k, v in args.items())

    @property
    def objects(self) -> List[ObjectSetting]:
        return self.__objects.copy()

    @property
    def ally(self) -> List[AllySetting]:
        return self.__ally.copy()

    @property
    def enemies(self) -> List[EnemySetting]:
        return self.__enemies.copy()


class Colors:
    BLACK = (0, 0, 0, 255)
    WHITE = (255, 255, 255, 255)
    RED = (255, 0, 0, 255)
    GREEN = (0, 255, 0, 255)
    BLUE = (0, 0, 255, 255)
    WOODEN = (153, 92, 0, 255)


class SettingsProvider:
    __settings_file_path: str = None
    __settings: Settings = None

    def __init__(self, file_path):
        if self.__settings_file_path != file_path or self.__settings is None:
            with open(file_path, "r") as file:
                self.__settings_file_path = file_path
                self.__settings = Settings(**yaml.load(file.read()))

    def get_objects(self) -> List[ObjectSetting]:
        return self.__settings.objects

    def get_ally(self) -> List[AllySetting]:
        return self.__settings.ally

    def get_enemies(self) -> List[EnemySetting]:
        return self.__settings.enemies
