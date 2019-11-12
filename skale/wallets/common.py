from abc import ABC, abstractmethod


class BaseWallet(ABC):
    @abstractmethod
    def sign(self, tx):
        pass

    @property
    @abstractmethod
    def address(self):
        pass

    @property
    @abstractmethod
    def public_key(self):
        pass
