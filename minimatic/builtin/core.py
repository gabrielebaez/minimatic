from typing import Optional
from core.base_element import Expression, BaseElement, Context, Literal
from builtin.heads import Bool, Integer, Number, Float, Atom


class If(Expression):
    """
    If(condition, true_case, false_case)
    Evaluates condition and returns either true_case or false_case
    based on truthiness rules.
    """

    def __init__(self, *tail: tuple[BaseElement, ...]):
        super().__init__('If', *tail)
        if len(tail) != 3:
            raise ValueError("If requires exactly 3 arguments: condition, true_case, false_case")
        

    def evaluate(self, context: Optional[Context]) -> BaseElement:
        condition, true_case, false_case = self._tail

        # Evaluate the condition
        evaluated_condition = condition.evaluate(context)

        # Determine truthiness and return appropriate branch
        if self._is_truthy(evaluated_condition):
            return true_case.evaluate(context)
        else:
            return false_case.evaluate(context) 


    def _is_truthy(self, element: BaseElement) -> bool:
        """
        Determine truthiness based on element type and value:

        - Bool(True) -> True
        - Bool(False) -> False
        - Numeric > 0 -> True
        - Numeric <= 0 -> False
        - Other -> False
        """
        # Check for Bool type
        if isinstance(element, Literal):
            if element.head == Bool:
                if element.value:
                    return True
                else:
                    return False

            # Check for numeric types (Integer, Number, Float, etc.)
            if element.head in (Integer, Number, Float):
                if element.value > 0:
                    return True
                else:
                    return False

        # Default to False for any other type
        return False


class While(Expression):
    pass