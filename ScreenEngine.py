import collections

import pygame

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
        self.left_corner_x = 0
        self.left_corner_y = 0

        super().__init__(*args, **kwargs)

    def connect_engine(self, engine):
        super().connect_engine(engine)

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

        right_corner_x = self.left_corner_x + screen_width
        right_corner_y = self.left_corner_y + screen_height

        shift_x = self.get_shift(hero_x, self.left_corner_x, right_corner_x)
        shift_y = self.get_shift(hero_y, self.left_corner_y, right_corner_y)

        return shift_x, shift_y

    def recalculate_map_position(self):
        sprite_size = self.engine.sprite_size
        screen_width, screen_height = [size / sprite_size for size in self.get_size()]
        map_height = len(self.engine.map)
        map_width = len(self.engine.map[0]) if map_height > 0 else 0
        shift_x, shift_y = self.get_hero_shift(screen_width, screen_height)

        self.left_corner_x += shift_x
        self.left_corner_y += shift_y

        if self.left_corner_x < 0 or screen_width > map_width:
            self.left_corner_x = 0
        elif self.left_corner_x + screen_width > map_width - 1:
            self.left_corner_x -= int(self.left_corner_x + screen_width - map_width)

        if self.left_corner_y < 0 or screen_height > map_height:
            self.left_corner_y = 0
        elif self.left_corner_y + screen_height > map_height - 1:
            self.left_corner_y -= int(self.left_corner_y + screen_height - map_height)

    def draw_map(self):
        if self.engine.map:
            for i in range(len(self.engine.map[0]) - self.left_corner_x):
                for j in range(len(self.engine.map) - self.left_corner_y):
                    self.blit(self.engine.map[self.left_corner_y + j][self.left_corner_x + i].sprite,
                              (i * self.engine.sprite_size, j * self.engine.sprite_size))
        else:
            self.fill(Colors.WHITE)

    def draw_objects(self):
        for obj in self.engine.get_objects():
            obj.draw(self)

    def draw_object(self, sprite, coord):
        self.blit(sprite, ((coord[0] - self.left_corner_x) * self.engine.sprite_size,
                           (coord[1] - self.left_corner_y) * self.engine.sprite_size))

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

        pygame.draw.rect(self, Colors.RED, (50, 30, 200 * self.engine.hero.hp / self.engine.hero.max_hp, 30))
        pygame.draw.rect(self, Colors.GREEN, (50, 70,
                                              200 * self.engine.hero.exp / (
                                                      100 * (2 ** (self.engine.hero.level - 1))), 30))

        font = pygame.font.SysFont("comicsansms", 20)
        self.blit(font.render(f'Hero at {self.engine.hero.position}', True, Colors.BLACK),
                  (250, 0))

        self.blit(font.render(f'{self.engine.level} floor', True, Colors.BLACK),
                  (10, 0))

        self.blit(font.render(f'HP', True, Colors.BLACK),
                  (10, 30))
        self.blit(font.render(f'Exp', True, Colors.BLACK),
                  (10, 70))

        self.blit(font.render(f'{self.engine.hero.hp}/{self.engine.hero.max_hp}', True, Colors.BLACK),
                  (60, 30))
        self.blit(
            font.render(f'{self.engine.hero.exp}/{(100 * (2 ** (self.engine.hero.level - 1)))}', True, Colors.BLACK),
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
        self.len = 30
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
        self.data.append(["Num+", "Zoom +"])
        self.data.append(["Num-", "Zoom -"])
        self.data.append([" R ", "Restart Game"])

    # FIXME You can add some help information

    def connect_engine(self, engine):
        super().connect_engine(engine)

    def draw(self, canvas):
        alpha = 0
        if self.engine.show_help:
            alpha = 128
        self.fill((0, 0, 0, alpha))
        font1 = pygame.font.SysFont("courier", 24)
        font2 = pygame.font.SysFont("serif", 24)
        if self.engine.show_help:
            pygame.draw.lines(self, (255, 0, 0, 255), True, [
                (0, 0), (700, 0), (700, 500), (0, 500)], 5)
            for i, text in enumerate(self.data):
                self.blit(font1.render(text[0], True, (128, 128, 255)),
                          (50, 50 + 30 * i))
                self.blit(font2.render(text[1], True, (128, 128, 255)),
                          (150, 50 + 30 * i))

        super().draw(canvas)
