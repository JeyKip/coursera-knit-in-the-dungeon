from abc import ABC


class EventPayload(ABC):
    pass


class Event:
    def __init__(self, name, payload: EventPayload):
        self.__name = name
        self.__payload = payload

    @property
    def name(self):
        return self.__name

    @property
    def payload(self):
        return self.__payload
