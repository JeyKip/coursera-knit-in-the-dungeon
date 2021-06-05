import random
from abc import ABC, abstractmethod
from typing import Type

from Event import Event
from Logic import GameEngine
from Objects import Hero, Blessing, Berserk, Weakness
from Service import LevelsProvider

RELOAD_GAME_EVENT = "reload_game"
RESTORE_HP_EVENT = "restore_hp"
APPLY_BLESSING_EVENT = "apply_blessing"
REMOVE_EFFECT_EVENT = "remove_effect"
ADD_GOLD_EVENT = "add_gold"


class GameEventHandler(ABC):
    def __call__(self, *args, **kwargs):
        engine = self.__get_engine(*args)
        hero = self.__get_hero(*args)

        self.action(engine, hero)

    @abstractmethod
    def action(self, engine: GameEngine, hero: Hero):
        raise NotImplementedError

    def __get_engine(self, *args) -> GameEngine:
        return self.__get_arg_by_type(GameEngine, *args)

    def __get_hero(self, *args) -> Hero:
        return self.__get_arg_by_type(Hero, *args)

    @staticmethod
    def __get_arg_by_type(arg_type: Type, *args):
        try:
            return next(filter(lambda arg: isinstance(arg, arg_type), args))
        except StopIteration:
            raise ValueError(f"Cannot find argument of type {arg_type}.")


class ReloadGameEventHandler(GameEventHandler):
    def __init__(self, levels_provider: LevelsProvider):
        self.__levels_provider = levels_provider

    def action(self, engine: GameEngine, hero: Hero):
        engine.level += 1
        hero.position = [1, 1]
        engine.delete_objects()

        levels = self.__levels_provider.get_levels()
        level_max = len(levels) - 1
        level = levels[min(engine.level, level_max)]

        _map = level.level_map.get_map()
        _objects = level.level_objects.get_objects(_map)

        engine.load_map(_map)
        engine.add_objects(_objects)
        engine.hero = hero


class RestoreHPEventHandler(GameEventHandler):
    def action(self, engine: GameEngine, hero: Hero):
        engine.score += 0.1
        hero.hp = hero.max_hp
        engine.notify("HP restored")


class ApplyBlessingEventHandler(GameEventHandler):
    def action(self, engine: GameEngine, hero: Hero):
        gold_should_be_taken_from_hero = int(20 * 1.5 ** engine.level) - 2 * hero.stats.intelligence

        if hero.gold >= gold_should_be_taken_from_hero:
            engine.score += 0.2
            hero.gold -= gold_should_be_taken_from_hero
            if random.randint(0, 1) == 0:
                engine.hero = Blessing(hero)
                engine.notify("Blessing applied")
            else:
                engine.hero = Berserk(hero)
                engine.notify("Berserk applied")
        else:
            engine.score -= 0.1


class RemoveEffectEventHandler(GameEventHandler):
    def action(self, engine: GameEngine, hero: Hero):
        gold_should_be_taken_from_hero = int(10 * 1.5 ** engine.level) - 2 * hero.stats.intelligence

        if hero.gold >= gold_should_be_taken_from_hero and "base" in dir(hero) and hero.base is not None:
            hero.gold -= gold_should_be_taken_from_hero
            engine.hero = hero.base
            engine.hero.calc_max_HP()
            engine.notify("Effect removed")


class AddGoldEventHandler(GameEventHandler):
    def action(self, engine: GameEngine, hero: Hero):
        if random.randint(1, 10) == 1:
            engine.score -= 0.05
            engine.hero = Weakness(hero)
            engine.notify("You were cursed")
        else:
            engine.score += 0.1
            gold = int(random.randint(10, 1000) * (1.1 ** (engine.hero.level - 1)))
            hero.gold += gold
            engine.notify(f"{gold} gold added")


class MissingEventHandlerError(Exception):
    pass


class EventHandler:
    def __init__(self, engine: GameEngine, levels_provider: LevelsProvider):
        self.__engine = engine
        self.__event_handlers = {
            RELOAD_GAME_EVENT: ReloadGameEventHandler(levels_provider),
            RESTORE_HP_EVENT: RestoreHPEventHandler(),
            APPLY_BLESSING_EVENT: ApplyBlessingEventHandler(),
            REMOVE_EFFECT_EVENT: RemoveEffectEventHandler(),
            ADD_GOLD_EVENT: AddGoldEventHandler()
        }

        self.__engine.subscribe(self)

    def update(self, event):
        if isinstance(event, Event):
            if event.name in self.__event_handlers:
                self.__event_handlers[event.name](self.__engine, event.payload)
            else:
                raise MissingEventHandlerError(f"Cannot find event handler for {event.name}.")
