from abc import ABC, abstractmethod

from Event import Event


class AbstractObject(ABC):
    def __init__(self, image=None, position=None):
        self._image = image
        self._position = position

    @property
    def image(self):
        return self._image

    @image.setter
    def image(self, value):
        self._image = value

    @property
    def position(self):
        return self._position

    @position.setter
    def position(self, value):
        self._position = value

    def draw(self, display):
        display.draw_object(self.image.sprite, self.position)


class Interactive(ABC):
    @abstractmethod
    def interact(self, engine, hero):
        pass


class Ally(AbstractObject, Interactive):
    def __init__(self, image, action, position):
        super().__init__(image, position)

        self._action = action

    def interact(self, engine, hero):
        engine.notify(Event(self._action, hero))


class Creature(AbstractObject):
    def __init__(self, image, stats, position):
        super().__init__(image, position)

        self._stats = stats
        self._max_hp = self.calc_max_HP()
        self._hp = self._max_hp

    @property
    def hp(self):
        return self._hp

    @hp.setter
    def hp(self, value):
        self._hp = min(value, self._max_hp)

    @property
    def stats(self):
        return self._stats

    @stats.setter
    def stats(self, value):
        self._stats = value

    @property
    def max_hp(self):
        return self._max_hp

    @max_hp.setter
    def max_hp(self, value):
        self._max_hp = max(value, 0)

    # noinspection PyPep8Naming
    def calc_max_HP(self):
        return 5 + self._stats.endurance * 2


class Hero(Creature):
    _default_position = [1, 1]

    def __init__(self, stats, image):
        self._level = 1
        self._exp = 0
        self._next_level_exp = self._calc_next_level_exp()
        self._gold = 0

        super().__init__(image, stats, self._default_position.copy())

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
    def gold(self):
        return self._gold

    @gold.setter
    def gold(self, value):
        self._gold = value

    def level_up(self):
        while self._exp >= self._next_level_exp:
            self._level += 1
            self._stats.strength += 2
            self._stats.endurance += 2
            self._max_hp = self.calc_max_HP()
            self._hp = self._max_hp
            self._next_level_exp = self._calc_next_level_exp()

    def restore_hp(self):
        self.hp = self.max_hp

    def reset_position(self):
        self.position = self._default_position.copy()

    def _calc_next_level_exp(self):
        return 100 * (2 ** (self._level - 1))


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
        return self.base.exp

    @exp.setter
    def exp(self, value):
        self._base.exp = value

    @property
    def image(self):
        return self._base.image

    @property
    def next_level_exp(self):
        return self._base.next_level_exp

    @next_level_exp.setter
    def next_level_exp(self, value):
        self._base.next_level_exp = value

    @abstractmethod
    def apply_effect(self):
        raise NotImplementedError

    def update_health_points(self):
        self.max_hp = self.calc_max_HP()
        self.hp = min(self.hp, self.max_hp)


class Enemy(Creature, Interactive):
    def __init__(self, image, stats, xp, position):
        self.xp = xp

        super().__init__(image, stats, position)

    def interact(self, engine, hero):
        # todo: implement this method - it is unclear now how enemy should interact
        pass


class Berserk(Effect):
    def apply_effect(self):
        self.stats.strength += 7
        self.stats.endurance += 7
        self.stats.luck += 7
        self.stats.intelligence -= 3
        self.update_health_points()


class Blessing(Effect):
    def apply_effect(self):
        self.stats.strength += 2
        self.stats.endurance += 3
        self.stats.luck += 4
        self.stats.intelligence += 5
        self.update_health_points()


class Weakness(Effect):
    def apply_effect(self):
        self.stats.strength -= 4
        self.stats.endurance -= 6
        self.stats.intelligence -= 2
        self.update_health_points()
