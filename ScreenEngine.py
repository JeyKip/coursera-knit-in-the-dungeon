import collections

import pygame

from Images import Fixture
from Settings import Colors


class ScreenHandle(pygame.Surface):
    def __init__(self, *args, **kwargs):
        self.background_color = Colors.WOODEN
        self.engine = None
        if len(args) > 1:
            self.successor = args[-1]
            self.next_coord = args[-2]
            args = args[:-2]
        else:
            self.successor = None
            self.next_coord = (0, 0)
        super().__init__(*args, **kwargs)

    def draw(self, canvas):
        if self.successor is not None:
            canvas.blit(self.successor, self.next_coord)
            self.successor.draw(canvas)

    def connect_engine(self, engine):
        self.engine = engine

        if self.successor is not None:
            self.successor.connect_engine(engine)


class GameSurface(ScreenHandle):
    def __init__(self, *args, **kwargs):
        self.__left_corner_x = 0
        self.__left_corner_y = 0
        self.__sprite_size = 1

        if len(args) > 2:
            self.__sprite_size = args[-3]
            args = args[:-3] + args[-2:]

        super().__init__(*args, **kwargs)

    def connect_engine(self, engine):
        super().connect_engine(engine)

    def set_sprite_size(self, value):
        if not isinstance(value, int) or value < 1:
            raise ValueError(f"Incorrect value '{value}' for sprite size: it should be a positive integer value.")

        self.__sprite_size = value

    def draw_hero(self):
        self.engine.hero.draw(self)

    @staticmethod
    def get_shift(current_coordinate, min_coordinate, max_coordinate):
        if current_coordinate > int(max_coordinate - 1):
            return int(current_coordinate - int(max_coordinate - 1))
        elif current_coordinate == max_coordinate - 1:
            return 1
        elif current_coordinate < int(min_coordinate + 1):
            return int(current_coordinate - int(min_coordinate + 1))
        elif current_coordinate == min_coordinate + 1:
            return -1

        return 0

    def get_hero_shift(self, screen_width, screen_height):
        hero_x, hero_y = self.engine.hero.position

        right_corner_x = self.__left_corner_x + screen_width
        right_corner_y = self.__left_corner_y + screen_height

        shift_x = self.get_shift(hero_x, self.__left_corner_x, right_corner_x)
        shift_y = self.get_shift(hero_y, self.__left_corner_y, right_corner_y)

        return shift_x, shift_y

    def recalculate_map_position(self):
        screen_width, screen_height = [size / self.__sprite_size for size in self.get_size()]
        map_height = len(self.engine.map)
        map_width = len(self.engine.map[0]) if map_height > 0 else 0
        shift_x, shift_y = self.get_hero_shift(screen_width, screen_height)

        self.__left_corner_x += shift_x
        self.__left_corner_y += shift_y

        if self.__left_corner_x < 0 or screen_width > map_width:
            self.__left_corner_x = 0
        elif self.__left_corner_x + screen_width > map_width - 1:
            self.__left_corner_x -= int(self.__left_corner_x + screen_width - map_width)

        if self.__left_corner_y < 0 or screen_height > map_height:
            self.__left_corner_y = 0
        elif self.__left_corner_y + screen_height > map_height - 1:
            self.__left_corner_y -= int(self.__left_corner_y + screen_height - map_height)

    def draw_map(self):
        if self.engine.map:
            for i in range(len(self.engine.map[0]) - self.__left_corner_x):
                for j in range(len(self.engine.map) - self.__left_corner_y):
                    cell = self.engine.map[self.__left_corner_y + j][self.__left_corner_x + i]
                    sprite = cell.sprite(self.__sprite_size, self.__sprite_size)
                    self.blit(sprite, (i * self.__sprite_size, j * self.__sprite_size))
        else:
            self.fill(Colors.WHITE)

    def draw_objects(self):
        for obj in self.engine.get_objects():
            obj.draw(self)

    def draw_object(self, fixture: Fixture, coord):
        self.blit(fixture.sprite(self.__sprite_size, self.__sprite_size),
                  ((coord[0] - self.__left_corner_x) * self.__sprite_size,
                   (coord[1] - self.__left_corner_y) * self.__sprite_size))

    def draw(self, canvas):
        self.recalculate_map_position()
        self.fill(self.background_color)
        self.draw_map()
        self.draw_objects()
        self.draw_hero()

        super().draw(canvas)


class ProgressBar(ScreenHandle):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def connect_engine(self, engine):
        super().connect_engine(engine)

    def draw(self, canvas):
        self.fill(self.background_color)
        pygame.draw.rect(self, Colors.BLACK, (50, 30, 200, 30), 2)
        pygame.draw.rect(self, Colors.BLACK, (50, 70, 200, 30), 2)

        hp_percentage = 0 if self.engine.hero.max_hp == 0 else self.engine.hero.hp / self.engine.hero.max_hp
        current_level_points = self.engine.hero.exp - self.engine.hero.prev_level_exp
        current_level_required_points = self.engine.hero.next_level_exp - self.engine.hero.prev_level_exp
        exp_percentage = current_level_points / current_level_required_points

        pygame.draw.rect(self, Colors.RED, (50, 30, 200 * hp_percentage, 30))
        pygame.draw.rect(self, Colors.GREEN, (50, 70, 200 * exp_percentage, 30))

        font = pygame.font.SysFont("comicsansms", 20)
        self.blit(font.render(f'Hero at {self.engine.hero.position}', True, Colors.BLACK),
                  (250, 0))

        self.blit(font.render(f'{self.engine.level + 1} floor', True, Colors.BLACK),
                  (10, 0))

        self.blit(font.render(f'HP', True, Colors.BLACK),
                  (10, 30))
        self.blit(font.render(f'Exp', True, Colors.BLACK),
                  (10, 70))

        self.blit(font.render(f'{self.engine.hero.hp}/{self.engine.hero.max_hp}', True, Colors.BLACK),
                  (60, 30))
        self.blit(
            font.render(f'{self.engine.hero.exp}/{self.engine.hero.next_level_exp}', True, Colors.BLACK),
            (60, 70))

        self.blit(font.render(f'Level', True, Colors.BLACK),
                  (300, 30))
        self.blit(font.render(f'Gold', True, Colors.BLACK),
                  (300, 70))

        self.blit(font.render(f'{self.engine.hero.level}', True, Colors.BLACK),
                  (360, 30))
        self.blit(font.render(f'{self.engine.hero.gold}', True, Colors.BLACK),
                  (360, 70))

        self.blit(font.render(f'Str', True, Colors.BLACK),
                  (420, 30))
        self.blit(font.render(f'Luck', True, Colors.BLACK),
                  (420, 70))

        self.blit(font.render(f'{self.engine.hero.stats.strength}', True, Colors.BLACK),
                  (480, 30))
        self.blit(font.render(f'{self.engine.hero.stats.luck}', True, Colors.BLACK),
                  (480, 70))

        self.blit(font.render(f'SCORE', True, Colors.BLACK),
                  (550, 30))
        self.blit(font.render(f'{self.engine.score:.4f}', True, Colors.BLACK),
                  (550, 70))

        super().draw(canvas)


class InfoWindow(ScreenHandle):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.len = 25
        clear = []
        self.data = collections.deque(clear, maxlen=self.len)

    def update(self, value):
        if isinstance(value, str):
            self.data.append(f"> {str(value)}")

    def draw(self, canvas):
        self.fill(self.background_color)

        font = pygame.font.SysFont("comicsansms", 18)
        for i, text in enumerate(self.data):
            self.blit(font.render(text, True, Colors.BLACK),
                      (5, 20 + 18 * i))

        super().draw(canvas)

    def connect_engine(self, engine):
        engine.subscribe(self)
        super().connect_engine(engine)


class HelpWindow(ScreenHandle):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.len = 30
        clear = []
        self.data = collections.deque(clear, maxlen=self.len)
        self.data.append([" →", "Move Right"])
        self.data.append([" ←", "Move Left"])
        self.data.append([" ↑ ", "Move Top"])
        self.data.append([" ↓ ", "Move Bottom"])
        self.data.append([" H ", "Show Help"])
        self.data.append([" W ", "Zoom +"])
        self.data.append([" S ", "Zoom -"])
        self.data.append([" R ", "Restart Game"])

    def connect_engine(self, engine):
        super().connect_engine(engine)

    def draw(self, canvas):
        alpha = 0
        show_help = self.engine.show_help and self.engine.game_process

        if show_help:
            alpha = 128
        self.fill((0, 0, 0, alpha))
        font1 = pygame.font.SysFont("courier", 24)
        font2 = pygame.font.SysFont("serif", 24)
        if show_help:
            pygame.draw.lines(self, (255, 0, 0, 255), True, [
                (0, 0), (700, 0), (700, 500), (0, 500)], 5)
            for i, text in enumerate(self.data):
                self.blit(font1.render(text[0], True, (128, 128, 255)),
                          (50, 50 + 30 * i))
                self.blit(font2.render(text[1], True, (128, 128, 255)),
                          (150, 50 + 30 * i))

        super().draw(canvas)


class GameOverWindow(ScreenHandle):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def connect_engine(self, engine):
        super().connect_engine(engine)

    def draw(self, canvas):
        alpha = 0
        if not self.engine.game_process:
            alpha = 128
        self.fill((0, 0, 0, alpha))
        font1 = pygame.font.SysFont("courier", 35)
        font1.set_bold(True)
        font2 = pygame.font.SysFont("courier", 24)
        font2.set_bold(True)
        if not self.engine.game_process:
            pygame.draw.lines(self, (255, 0, 0, 255), True, [
                (0, 0), (500, 0), (500, 200), (0, 200)], 5)
            self.blit(font1.render("Game Over", True, (255, 0, 0)), (145, 50))
            self.blit(font2.render("Press R to start a new game.", True, (255, 0, 0)), (30, 100))

        super().draw(canvas)
