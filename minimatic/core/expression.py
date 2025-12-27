from typing import Any, Sequence
from abc import ABC


class BaseElement(ABC):

    def get_head(self) -> str:
        raise NotImplementedError("Subclasses should implement this method.")
    
    def get_tail(self) -> Sequence[Any]:
        raise NotImplementedError("Subclasses should implement this method.")
    
    def get_attributes(self) -> dict:
        raise NotImplementedError("Subclasses should implement this method.")
    
    def get_value(self) -> Any:
        raise NotImplementedError("Subclasses should implement this method.")
    
    def get_sort_key(self) -> str:
        raise NotImplementedError("Subclasses should implement this method.")
    
    def sameQ(self, other: Any) -> bool:
        raise NotImplementedError("Subclasses should implement this method.")
    
    def evaluate(self) -> Any:
        raise NotImplementedError("Subclasses should implement this method.")


class Expression(BaseElement):
    def __init__(self, 
                 head: BaseElement, 
                 tail: tuple[BaseElement],
                 attributes: tuple[str]=()):
        self._head = head
        self._tail = tail
        self._attributes = attributes
    
    def __repr__(self):
        return f"{self._head}({self._tail})"
    
    @property
    def get_head(self) -> BaseElement:
        return self._head

    @property
    def get_tail(self) -> tuple[BaseElement]:
        return self._tail
    
    @property
    def get_attributes(self) -> tuple[str]:
        return self._attributes
    
    @property
    def get_value(self) -> BaseElement | None:
        return self._tail if self._tail else None
    
    def evaluate(self):
        if "Executable" in self._attributes:
            return self._head(self._tail).evaluate()
        else:
            return self
