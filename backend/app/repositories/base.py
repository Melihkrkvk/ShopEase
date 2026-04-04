from abc import ABC, abstractmethod


class BaseRepository(ABC):
    """
    Abstract base class for all repositories.

    Defines the domain-level interface that services depend on.
    Concrete repositories use a DAO internally for data access.
    """

    @abstractmethod
    def get_by_id(self, id: int): ...

    @abstractmethod
    def save(self, entity) -> object: ...

    @abstractmethod
    def delete(self, id: int) -> None: ...

    @abstractmethod
    def get_all(self) -> list: ...
