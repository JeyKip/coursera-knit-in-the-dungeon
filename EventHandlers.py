import random
from abc import ABC, abstractmethod
from typing import Type

from Event import Event, EventPayload
from Logic import GameEngine
from Objects import Blessing, Berserk, Weakness, Anger, Ally, Enemy
from Service import LevelsProvider

RELOAD_GAME_EVENT = "reload_game"
RESTORE_HP_EVENT = "restore_hp"
APPLY_BLESSING_EVENT = "apply_blessing"
REMOVE_EFFECT_EVENT = "remove_effect"
ADD_GOLD_EVENT = "add_gold"
MAKE_ME_ANGRY_EVENT = "make_me_angry"
ENEMY_INTERACTED_WITH_HERO_EVENT = "enemy_interacted_with_hero"


class GameEventHandler(ABC):
    def __call__(self, *args, **kwargs):
        engine = self.__get_engine(*args)
        payload = self.__get_payload(*args)

        self.action(engine, payload)

    @abstractmethod
    def action(self, engine: GameEngine, payload: EventPayload):
        raise NotImplementedError

    def __get_engine(self, *args) -> GameEngine:
        return self.__get_arg_by_type(GameEngine, *args)

    def __get_payload(self, *args) -> EventPayload:
        return self.__get_arg_by_type(EventPayload, *args)

    @staticmethod
    def __get_arg_by_type(arg_type: Type, *args):
        try:
            return next(filter(lambda arg: isinstance(arg, arg_type), args))
        except StopIteration:
            raise ValueError(f"Cannot find argument of type {arg_type}.")


class ReloadGameEventHandler(GameEventHandler):
    def __init__(self, levels_provider: LevelsProvider):
        self.__levels_provider = levels_provider

    def action(self, engine: GameEngine, payload: Ally.InteractedWithHeroEventPayload):
        engine.level += 1
        payload.hero.reset_position()
        engine.delete_objects()

        levels = self.__levels_provider.get_levels()
        level_max = len(levels) - 1
        level = levels[min(engine.level, level_max)]

        _map = level.level_map.get_map()
        _objects = level.level_objects.get_objects(_map)

        engine.load_map(_map)
        engine.add_objects(_objects)
        engine.hero = payload.hero


class RestoreHPEventHandler(GameEventHandler):
    def action(self, engine: GameEngine, payload: Ally.InteractedWithHeroEventPayload):
        engine.score += 0.1
        payload.hero.restore_hp()
        engine.notify("HP restored")


class ApplyBlessingEventHandler(GameEventHandler):
    def action(self, engine: GameEngine, payload: Ally.InteractedWithHeroEventPayload):
        gold_should_be_taken_from_hero = int(20 * 1.5 ** engine.level) - 2 * payload.hero.stats.intelligence

        if payload.hero.gold >= gold_should_be_taken_from_hero:
            engine.score += 0.2
            payload.hero.gold -= gold_should_be_taken_from_hero
            if random.randint(0, 1) == 0:
                engine.hero = Blessing(payload.hero)
                engine.notify("Blessing applied")
            else:
                engine.hero = Berserk(payload.hero)
                engine.notify("Berserk applied")
            engine.check_game_is_over()
        else:
            engine.score -= 0.1


class RemoveEffectEventHandler(GameEventHandler):
    def action(self, engine: GameEngine, payload: Ally.InteractedWithHeroEventPayload):
        gold_should_be_taken_from_hero = int(10 * 1.5 ** engine.level) - 2 * payload.hero.stats.intelligence

        if payload.hero.gold >= gold_should_be_taken_from_hero and "base" in dir(payload.hero):
            payload.hero.gold -= gold_should_be_taken_from_hero
            engine.hero = payload.hero.base
            engine.hero.update_health_points()
            engine.check_game_is_over()
            engine.notify("Effect removed")


class AddGoldEventHandler(GameEventHandler):
    def action(self, engine: GameEngine, payload: Ally.InteractedWithHeroEventPayload):
        if random.randint(1, 10) == 1:
            engine.score -= 0.05
            engine.hero = Weakness(payload.hero)
            engine.notify("You were cursed")
        else:
            engine.score += 0.1
            gold = int(random.randint(10, 1000) * (1.1 ** (payload.hero.level - 1)))
            payload.hero.gold += gold
            engine.notify(f"{gold} gold added")
            engine.check_game_is_over()


class MakeMeAngryEventHandler(GameEventHandler):
    def action(self, engine: GameEngine, payload: Ally.InteractedWithHeroEventPayload):
        engine.score += 1.0
        engine.hero = Anger(payload.hero)
        engine.hero.restore_hp()
        engine.notify("Hero became angry")
        engine.check_game_is_over()


class EnemyInteractedWithHeroEventHandler(GameEventHandler):
    def action(self, engine: GameEngine, payload: Enemy.InteractedWithHeroEventPayload):
        payload.hero.hp -= payload.damage

        if engine.check_game_is_over():
            engine.notify("Hero was killed")
        else:
            payload.hero.exp += payload.enemy.xp
            engine.notify(f"Got {payload.enemy.xp} experience.")

            old_level, new_level = payload.hero.level_up()

            if old_level != new_level:
                engine.notify(f"Level updated: {old_level} -> {new_level}.")


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
            ADD_GOLD_EVENT: AddGoldEventHandler(),
            MAKE_ME_ANGRY_EVENT: MakeMeAngryEventHandler(),
            ENEMY_INTERACTED_WITH_HERO_EVENT: EnemyInteractedWithHeroEventHandler()
        }

        self.__engine.subscribe(self)

    def update(self, event):
        if isinstance(event, Event):
            if event.name in self.__event_handlers:
                self.__event_handlers[event.name](self.__engine, event.payload)
            else:
                raise MissingEventHandlerError(f"Cannot find event handler for {event.name}.")
