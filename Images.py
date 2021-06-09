import os

import pygame


class Fixture:
    def __init__(self, fixture_path, fixture_type=None):
        self.__fixture_type = fixture_type
        self.__fixture_path = fixture_path

    def sprite(self, width, height):
        return ImagesProvider.load_sprite(self.__fixture_path, width, height)

    @property
    def fixture_type(self):
        return self.__fixture_type


class FixtureType:
    WALL = "wall"
    FLOOR_1 = "floor_1"
    FLOOR_2 = "floor_2"
    FLOOR_3 = "floor_3"


class SpecialFixtures:
    WALL = Fixture(os.path.join("texture", "wall.png"), FixtureType.WALL)
    FLOOR_1 = Fixture(os.path.join("texture", "Ground_1.png"), FixtureType.FLOOR_1)
    FLOOR_2 = Fixture(os.path.join("texture", "Ground_2.png"), FixtureType.FLOOR_2)
    FLOOR_3 = Fixture(os.path.join("texture", "Ground_3.png"), FixtureType.FLOOR_3)


class ImagesProvider:
    _images_cache = dict()
    _sprites_cache = dict()

    @classmethod
    def load_sprite(cls, path, width, height):
        key = f"{path}-{width}-{height}"

        if key not in cls._sprites_cache:
            image = cls.load_image(path)
            sprite = cls.create_sprite(image, width, height)

            cls._sprites_cache[key] = sprite

            return sprite

        return cls._sprites_cache[key]

    @classmethod
    def load_image(cls, path):
        if path not in cls._images_cache:
            cls._images_cache[path] = pygame.image.load(path).convert_alpha()

        return cls._images_cache[path]

    @staticmethod
    def create_sprite(image, width, height):
        icon = pygame.transform.scale(image, (width, height))
        sprite = pygame.Surface((width, height), pygame.HWSURFACE)
        sprite.blit(icon, (0, 0))

        return sprite
