from core.base_element import Context, BaseElement


def evaluate(expr: BaseElement, context: Context | None = None) -> BaseElement:
    """
    Evaluates a given expression.

    Args:
        expr (BaseElement): The expression to evaluate.

    Returns:
        BaseElement: The evaluated expression.
    """
    # Placeholder for evaluation logic
    if context is None:
        context = Context()
    return expr.evaluate(context)
