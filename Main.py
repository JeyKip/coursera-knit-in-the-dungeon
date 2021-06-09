import os

import numpy as np

import EventHandlers
from Event import Event
from EventHandlers import EventHandler
from Logic import GameEngine
from Objects import Hero, Ally
from ScreenEngine import *
from Service import LevelsProvider
from Settings import SettingsProvider, ObjectStatistic


class KnightInTheDungeonGame:
    SCREEN_DIM = (800, 600)
    KEYBOARD_CONTROL = True
    DEFAULT_SPRITE_SIZE = 60
    SETTINGS_FILE_PATH = "objects.yml"
    LEVELS_FILE_PATH = "levels.yml"
    HERO_FIXTURE_PATH = os.path.join("texture", "Hero.png")

    def __enter__(self):
        pygame.init()
        pygame.display.set_caption("MyRPG")

        self.__display = pygame.display.set_mode(self.SCREEN_DIM)
        self.__settings_provider = SettingsProvider(self.SETTINGS_FILE_PATH)
        self.__start_game(self.DEFAULT_SPRITE_SIZE)

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pygame.display.quit()
        pygame.quit()

    def __start_game(self, sprite_size):
        self.__levels_provider = LevelsProvider(self.LEVELS_FILE_PATH, self.__settings_provider)
        self.__hero = self.__create_hero()
        self.__engine = GameEngine()
        self.__engine.sprite_size = sprite_size

        # initialize map and statistic for the beginning of the game
        self.__event_handler = EventHandler(self.__engine, self.__levels_provider)
        self.__event_handler.update(
            Event(EventHandlers.RELOAD_GAME_EVENT, Ally.InteractedWithHeroEventPayload(self.__hero)))

        self.__drawer = self.__create_drawer(sprite_size)
        self.__drawer.connect_engine(self.__engine)

    def __create_hero(self):
        hero_icon = Fixture(self.HERO_FIXTURE_PATH)
        hero_statistic = ObjectStatistic(strength=20, endurance=20, intelligence=5, luck=5)
        hero = Hero(hero_statistic, hero_icon)

        return hero

    @staticmethod
    def __create_drawer(sprite_size):
        screen_handler = ScreenHandle((0, 0))
        game_over_window = GameOverWindow((500, 200), pygame.SRCALPHA, (0, 0), screen_handler)
        help_window = HelpWindow((700, 500), pygame.SRCALPHA, (150, 140), game_over_window)
        info_window = InfoWindow((160, 480), (50, 50), help_window)
        progress_bar = ProgressBar((640, 120), (640, 0), info_window)
        mini_map_surface = GameSurface((160, 120), pygame.SRCALPHA, 8, (0, 480), progress_bar)
        game_surface = GameSurface((640, 480), pygame.SRCALPHA, sprite_size, (640, 480), mini_map_surface)

        return game_surface

    def run(self):
        while self.__engine.working:
            if self.KEYBOARD_CONTROL:
                self.__handle_keyboard_events()
            else:
                self.__handle_autoplay_events()
            self.__update_screen()

    def __handle_keyboard_events(self):
        for event in pygame.event.get():
            self.__handle_quit_event(event)
            self.__handle_show_help_event(event)
            self.__handle_resize_event(event)
            self.__handle_restart_game_event(event)
            self.__handle_move_event(event)

    def __handle_quit_event(self, event):
        if event.type == pygame.QUIT:
            self.__engine.working = False
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.__engine.working = False

    def __handle_show_help_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_h:
            self.__engine.show_help = not self.__engine.show_help

    def __handle_resize_event(self, event):
        sprite_size = self.__engine.sprite_size

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_w:
                self.__change_sprite_size(sprite_size + 1)
            elif event.key == pygame.K_s:
                self.__change_sprite_size(sprite_size - 1)

    def __change_sprite_size(self, sprite_size):
        if 1 <= sprite_size <= 80:
            self.__drawer.set_sprite_size(sprite_size)
            self.__engine.sprite_size = sprite_size

    def __handle_restart_game_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r or (event.key == pygame.K_RETURN and not self.__engine.game_process):
                self.__start_game(self.__engine.sprite_size)

    def __handle_move_event(self, event):
        if event.type == pygame.KEYDOWN and self.__engine.game_process:
            if event.key == pygame.K_UP:
                self.__engine.move_up()
            elif event.key == pygame.K_DOWN:
                self.__engine.move_down()
            elif event.key == pygame.K_LEFT:
                self.__engine.move_left()
            elif event.key == pygame.K_RIGHT:
                self.__engine.move_right()

    def __handle_autoplay_events(self):
        for event in pygame.event.get():
            self.__handle_quit_event(event)

        if self.__engine.game_process:
            actions = [
                self.__engine.move_right,
                self.__engine.move_left,
                self.__engine.move_up,
                self.__engine.move_down,
            ]
            answer = np.random.randint(0, 100, 4)
            prev_score = self.__engine.score
            actions[np.argmax(answer)]()
            pygame.surfarray.array3d(self.__display)
            reward = self.__engine.score - prev_score
            print(reward)
        else:
            self.__start_game(self.__engine.sprite_size)

    def __update_screen(self):
        self.__display.blit(self.__drawer, (0, 0))
        self.__drawer.draw(self.__display)
        pygame.display.update()


if __name__ == "__main__":
    with KnightInTheDungeonGame() as game:
        game.run()
        exit(0)
