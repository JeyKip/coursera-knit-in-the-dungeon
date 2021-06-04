import os

import Logic
import Objects
import Service
from Images import FixturesProvider, SpecialFixturesProvider
from ScreenEngine import *
from Settings import ObjectStatistic, SettingsProvider

SCREEN_DIM = (800, 600)

pygame.init()
gameDisplay = pygame.display.set_mode(SCREEN_DIM)
pygame.display.set_caption("MyRPG")
KEYBOARD_CONTROL = True

if not KEYBOARD_CONTROL:
    import numpy as np

    answer = np.zeros(4, dtype=float)


def create_game(sprite_size):
    global hero, engine, drawer, iteration

    settings_provider = SettingsProvider("objects.yml")
    # todo: remove global variables
    global fixtures_provider
    fixtures_provider = FixturesProvider(sprite_size)
    special_fixtures_provider = SpecialFixturesProvider(fixtures_provider)

    hero_icon = fixtures_provider.load(os.path.join("texture", "Hero.png"))
    hero_statistic = ObjectStatistic(strength=20, endurance=20, intelligence=5, luck=5)
    hero = Objects.Hero(hero_statistic, hero_icon)
    engine = Logic.GameEngine(special_fixtures_provider)
    Service.service_init(settings_provider, fixtures_provider, special_fixtures_provider)
    Service.reload_game(engine, hero)
    drawer = GameSurface((640, 480), pygame.SRCALPHA, (0, 480),
                         ProgressBar((640, 120), (640, 0),
                                     InfoWindow((160, 600), (50, 50),
                                                HelpWindow((700, 500), pygame.SRCALPHA, (0, 0),
                                                           ScreenHandle(
                                                               (0, 0))
                                                           ))))

    engine.set_sprite_size(sprite_size)
    drawer.connect_engine(engine)

    iteration = 0


size = 60
create_game(size)

while engine.working:

    if KEYBOARD_CONTROL:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                engine.working = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_h:
                    engine.show_help = not engine.show_help
                if event.key == pygame.K_w:
                    # if event.key == pygame.K_KP_PLUS:
                    size = size + 1
                    fixtures_provider.set_sprite_size(size)
                    engine.set_sprite_size(size)
                # if event.key == pygame.K_KP_MINUS:
                if event.key == pygame.K_s:
                    size = size - 1
                    engine.set_sprite_size(size)
                    fixtures_provider.set_sprite_size(size)
                if event.key == pygame.K_r:
                    create_game(size)
                if event.key == pygame.K_ESCAPE:
                    engine.working = False
                if engine.game_process:
                    if event.key == pygame.K_UP:
                        engine.move_up()
                        iteration += 1
                    elif event.key == pygame.K_DOWN:
                        engine.move_down()
                        iteration += 1
                    elif event.key == pygame.K_LEFT:
                        engine.move_left()
                        iteration += 1
                    elif event.key == pygame.K_RIGHT:
                        engine.move_right()
                        iteration += 1
                else:
                    if event.key == pygame.K_RETURN:
                        create_game(size)
    else:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                engine.working = False
        if engine.game_process:
            actions = [
                engine.move_right,
                engine.move_left,
                engine.move_up,
                engine.move_down,
            ]
            answer = np.random.randint(0, 100, 4)
            prev_score = engine.score
            move = actions[np.argmax(answer)]()
            state = pygame.surfarray.array3d(gameDisplay)
            reward = engine.score - prev_score
            print(reward)
        else:
            create_game(size)

    gameDisplay.blit(drawer, (0, 0))
    drawer.draw(gameDisplay)

    pygame.display.update()

pygame.display.quit()
pygame.quit()
exit(0)
