import os

import pygame


class Fixture:
    def __init__(self, image_path, image_size):
        self.__image_size = image_size
        self.__image = ImageProcessor.load_image(image_path)
        self.__sprite = ImageProcessor.create_sprite(self.__image, image_size, image_size)

    def resize(self, image_size):
        if self.__image_size != image_size:
            self.__image_size = image_size
            self.__sprite = ImageProcessor.create_sprite(self.__image, image_size, image_size)

    @property
    def sprite(self):
        return self.__sprite


class ImageProcessor:
    @staticmethod
    def load_image(path):
        return pygame.image.load(path).convert_alpha()

    @staticmethod
    def create_sprite(image, width, height):
        icon = pygame.transform.scale(image, (width, height))
        sprite = pygame.Surface((width, height), pygame.HWSURFACE)
        sprite.blit(icon, (0, 0))

        return sprite


class FixturesProvider:
    __cache = dict()
    __sprite_size = None

    def __init__(self, sprite_size):
        self.set_sprite_size(sprite_size)

    def load(self, image_path):
        if image_path in self.__cache:
            return self.__cache[image_path]

        self.__cache[image_path] = Fixture(image_path, self.__sprite_size)

        return self.__cache[image_path]

    def set_sprite_size(self, sprite_size):
        if self.__sprite_size != sprite_size:
            self.__sprite_size = sprite_size

            for key in self.__cache:
                self.__cache[key].resize(sprite_size)


class SpecialFixturesProvider:

    def __init__(self, fixture_provider: FixturesProvider):
        self.__fixture_provider = fixture_provider

    def get_wall(self):
        return self.__fixture_provider.load(os.path.join("texture", "wall.png"))

    def get_floor_1(self):
        return self.__fixture_provider.load(os.path.join("texture", "Ground_1.png"))

    def get_floor_2(self):
        return self.__fixture_provider.load(os.path.join("texture", "Ground_2.png"))

    def get_floor_3(self):
        return self.__fixture_provider.load(os.path.join("texture", "Ground_3.png"))
