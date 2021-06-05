from Images import SpecialFixturesProvider


class GameEngine:
    def __init__(self, special_fixture_provider: SpecialFixturesProvider):
        self.__special_fixture_provider = special_fixture_provider
        self.__objects = []
        self.__map = None
        self.__hero = None
        self.__level = -1
        self.__working = True
        self.__subscribers = set()
        self.__score = 0.
        self.__game_process = True
        self.__show_help = False
        self.__sprite_size = None

    def subscribe(self, obj):
        self.__subscribers.add(obj)

    def unsubscribe(self, obj):
        if obj in self.__subscribers:
            self.__subscribers.remove(obj)

    def notify(self, message):
        for i in self.__subscribers:
            i.update(message)

    @property
    def level(self):
        return self.__level

    @level.setter
    def level(self, level):
        self.__level = level

    @property
    def score(self):
        return self.__score

    @score.setter
    def score(self, score):
        self.__score = score

    @property
    def working(self):
        return self.__working

    @working.setter
    def working(self, working):
        self.__working = working

    @property
    def game_process(self):
        return self.__game_process

    @game_process.setter
    def game_process(self, game_process):
        self.__game_process = game_process

    @property
    def show_help(self):
        return self.__show_help

    @show_help.setter
    def show_help(self, show_help):
        self.__show_help = show_help

    @property
    def sprite_size(self):
        return self.__sprite_size

    @sprite_size.setter
    def sprite_size(self, sprite_size):
        self.__sprite_size = sprite_size

    # HERO
    @property
    def hero(self):
        return self.__hero

    @hero.setter
    def hero(self, hero):
        self.__hero = hero

    def interact(self):
        for obj in self.__objects:
            if list(obj.position) == self.hero.position:
                self.delete_object(obj)
                obj.interact(self, self.hero)

    # MOVEMENT
    def move_up(self):
        self.__score -= 0.02
        if self.__map[self.hero.position[1] - 1][self.hero.position[0]] == self.__special_fixture_provider.get_wall():
            return
        self.hero.position[1] -= 1
        self.interact()

    def move_down(self):
        self.__score -= 0.02
        if self.__map[self.hero.position[1] + 1][self.hero.position[0]] == self.__special_fixture_provider.get_wall():
            return
        self.hero.position[1] += 1
        self.interact()

    def move_left(self):
        self.__score -= 0.02
        if self.__map[self.hero.position[1]][self.hero.position[0] - 1] == self.__special_fixture_provider.get_wall():
            return
        self.hero.position[0] -= 1
        self.interact()

    def move_right(self):
        self.__score -= 0.02
        if self.__map[self.hero.position[1]][self.hero.position[0] + 1] == self.__special_fixture_provider.get_wall():
            return
        self.hero.position[0] += 1
        self.interact()

    # MAP
    @property
    def map(self):
        return self.__map

    def load_map(self, game_map):
        self.__map = game_map

    # OBJECTS
    def get_objects(self):
        return self.__objects

    def add_object(self, obj):
        self.__objects.append(obj)

    def add_objects(self, objects):
        self.__objects.extend(objects)

    def delete_object(self, obj):
        self.__objects.remove(obj)

    def delete_objects(self):
        self.__objects.clear()
