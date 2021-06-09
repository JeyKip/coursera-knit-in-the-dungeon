import random
from abc import ABC, abstractmethod

from Event import Event, EventPayload


class AbstractObject(ABC):
    def __init__(self, fixture=None, position=None):
        self._fixture = fixture
        self._position = position

    @property
    def fixture(self):
        return self._fixture

    @fixture.setter
    def fixture(self, value):
        self._fixture = value

    @property
    def position(self):
        return self._position

    @position.setter
    def position(self, value):
        self._position = value

    def draw(self, display):
        display.draw_object(self.fixture, self.position)


class Interactive(ABC):
    @abstractmethod
    def interact(self, engine, hero):
        pass


class Ally(AbstractObject, Interactive):
    class InteractedWithHeroEventPayload(EventPayload):
        def __init__(self, hero):
            self.__hero = hero

        @property
        def hero(self):
            return self.__hero

    def __init__(self, fixture, action, position):
        super().__init__(fixture, position)

        self._action = action

    def interact(self, engine, hero):
        engine.notify(Event(self._action, Ally.InteractedWithHeroEventPayload(hero)))


class Creature(AbstractObject):
    def __init__(self, fixture, stats, position):
        super().__init__(fixture, position)

        self._stats = stats
        self._max_hp = self.calc_max_HP()
        self._hp = self._max_hp

    @property
    def hp(self):
        return self._hp

    @hp.setter
    def hp(self, value):
        self._hp = value

    @property
    def stats(self):
        return self._stats

    @stats.setter
    def stats(self, value):
        self._stats = value

    @property
    def strength(self):
        return self._stats.strength

    @strength.setter
    def strength(self, value):
        self._stats.strength = value

    @property
    def endurance(self):
        return self._stats.endurance

    @endurance.setter
    def endurance(self, value):
        self._stats.endurance = value

    @property
    def intelligence(self):
        return self._stats.intelligence

    @intelligence.setter
    def intelligence(self, value):
        self._stats.intelligence = value

    @property
    def luck(self):
        return self._stats.luck

    @luck.setter
    def luck(self, value):
        self._stats.luck = value

    @property
    def max_hp(self):
        return self._max_hp

    @max_hp.setter
    def max_hp(self, value):
        self._max_hp = value

    # noinspection PyPep8Naming
    def calc_max_HP(self):
        return 5 + self.stats.endurance * 2


class Hero(Creature):
    _default_position = [1, 1]

    def __init__(self, stats, fixture):
        self._level = 1
        self._exp = 0
        self._prev_level_exp = 0
        self._next_level_exp = self.calc_next_level_exp()
        self._gold = 0

        super().__init__(fixture, stats, self._default_position.copy())

    @property
    def level(self):
        return self._level

    @level.setter
    def level(self, value):
        self._level = value

    @property
    def exp(self):
        return self._exp

    @exp.setter
    def exp(self, value):
        self._exp = value

    @property
    def next_level_exp(self):
        return self._next_level_exp

    @next_level_exp.setter
    def next_level_exp(self, value):
        self._next_level_exp = value

    @property
    def prev_level_exp(self):
        return self._prev_level_exp

    @prev_level_exp.setter
    def prev_level_exp(self, value):
        self._prev_level_exp = value

    @property
    def gold(self):
        return self._gold

    @gold.setter
    def gold(self, value):
        self._gold = value

    def level_up(self):
        old_level = self.level

        while self.exp >= self.next_level_exp:
            self.level += 1
            self.strength += 2
            self.endurance += 2
            self.max_hp = self.calc_max_HP()
            self.restore_hp()
            self.prev_level_exp = self.next_level_exp
            self.next_level_exp = self.calc_next_level_exp()

        return old_level, self.level

    def restore_hp(self):
        self.hp = self.max_hp

    def reset_position(self):
        self.position = self._default_position.copy()

    def calc_next_level_exp(self):
        return 100 * (2 ** (self.level - 1))

    def update_health_points(self):
        self.max_hp = self.calc_max_HP()
        self.hp = min(self.hp, self.max_hp)


class Effect(Hero):
    # noinspection PyMissingConstructor
    def __init__(self, base):
        self._base = base
        self._stats = base.stats.copy()
        self.apply_effect()

    @property
    def base(self):
        return self._base

    @base.setter
    def base(self, value):
        self._base = value

    @property
    def stats(self):
        return self._stats

    @stats.setter
    def stats(self, value):
        self._stats = value

    @property
    def hp(self):
        return self._base.hp

    @hp.setter
    def hp(self, value):
        self._base.hp = value

    @property
    def max_hp(self):
        return self._base.max_hp

    @max_hp.setter
    def max_hp(self, value):
        self._base.max_hp = value

    @property
    def position(self):
        return self._base.position

    @position.setter
    def position(self, value):
        self._base.position = value

    @property
    def level(self):
        return self._base.level

    @level.setter
    def level(self, value):
        self._base.level = value

    @property
    def gold(self):
        return self._base.gold

    @gold.setter
    def gold(self, value):
        self._base.gold = value

    @property
    def exp(self):
        return self._base.exp

    @exp.setter
    def exp(self, value):
        self._base.exp = value

    @property
    def fixture(self):
        return self._base.fixture

    @property
    def next_level_exp(self):
        return self._base.next_level_exp

    @next_level_exp.setter
    def next_level_exp(self, value):
        self._base.next_level_exp = value

    @property
    def prev_level_exp(self):
        return self._base.prev_level_exp

    @prev_level_exp.setter
    def prev_level_exp(self, value):
        self._base.prev_level_exp = value

    @property
    def strength(self):
        return self._stats.strength

    @strength.setter
    def strength(self, value):
        difference = self._stats.strength - value

        self._stats.strength = value
        self._base.strength -= difference

    @property
    def endurance(self):
        return self._stats.endurance

    @endurance.setter
    def endurance(self, value):
        difference = self._stats.endurance - value

        self._stats.endurance = value
        self._base.endurance -= difference

    @property
    def intelligence(self):
        return self._stats.intelligence

    @intelligence.setter
    def intelligence(self, value):
        difference = self._stats.intelligence - value

        self._stats.intelligence = value
        self._base.intelligence -= difference

    @property
    def luck(self):
        return self._stats.luck

    @luck.setter
    def luck(self, value):
        difference = self._stats.luck - value

        self._stats.luck = value
        self._base.luck -= difference

    @abstractmethod
    def apply_effect(self):
        raise NotImplementedError


class Enemy(Creature, Interactive):
    class InteractedWithHeroEventPayload(EventPayload):
        def __init__(self, damage, hero, enemy):
            self.__damage = damage
            self.__hero = hero
            self.__enemy = enemy

        @property
        def damage(self):
            return self.__damage

        @property
        def hero(self):
            return self.__hero

        @property
        def enemy(self):
            return self.__enemy

    def __init__(self, fixture, stats, xp, position):
        self.xp = xp

        super().__init__(fixture, stats, position)

    def interact(self, engine, hero):
        # min damage is 50% of the strength of enemy
        min_damage = int(0.5 * self.stats.strength)

        # max damage is 100% of the strength of enemy
        max_damage = self.stats.strength

        damage = random.randint(min_damage, max_damage)

        engine.notify(Event("enemy_interacted_with_hero", Enemy.InteractedWithHeroEventPayload(damage, hero, self)))


class Berserk(Effect):
    def apply_effect(self):
        self._stats.strength += 7
        self._stats.endurance += 7
        self._stats.luck += 7
        self._stats.intelligence -= 3
        self.update_health_points()


class Blessing(Effect):
    def apply_effect(self):
        self._stats.strength += 2
        self._stats.endurance += 3
        self._stats.luck += 4
        self._stats.intelligence += 5
        self.update_health_points()


class Weakness(Effect):
    def apply_effect(self):
        self._stats.strength -= 4
        self._stats.endurance -= 6
        self._stats.intelligence -= 2
        self.update_health_points()


class Anger(Effect):
    def apply_effect(self):
        self._stats.strength += 10
        self._stats.endurance += 15
        self._stats.luck -= 5
        self._stats.intelligence -= 5
        self.update_health_points()
