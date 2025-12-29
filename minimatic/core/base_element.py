from typing import Any, Sequence
from abc import ABC


class BaseElement(ABC):

    def head(self) -> str:
        raise NotImplementedError("Subclasses should implement this method.")
    
    def tail(self) -> Sequence[Any]:
        raise NotImplementedError("Subclasses should implement this method.")

    def attributes(self) -> dict:
        raise NotImplementedError("Subclasses should implement this method.")
    
    def has_attribute(self, attr: str) -> bool:
        raise NotImplementedError("Subclasses should implement this method.")

    def add_attribute(self, attr: str) -> Any:
        raise NotImplementedError("Subclasses should implement this method.")

    def remove_attribute(self, attr: str) -> Any:
        raise NotImplementedError("Subclasses should implement this method.")

    def evaluate(self) -> Any:
        raise NotImplementedError("Subclasses should implement this method.")
