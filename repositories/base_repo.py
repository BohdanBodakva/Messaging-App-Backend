from abc import ABC, abstractmethod


class BaseCrudRepo(ABC):
    @abstractmethod
    def get_all(self): pass

    @abstractmethod
    def get_by_id(self, item_id): pass

    @abstractmethod
    def create(self, item): pass

    @abstractmethod
    def update(self, item_id, new_item): pass

    @abstractmethod
    def delete(self, item_id): pass
