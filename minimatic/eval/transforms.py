"""
Structural transformations for evaluation.

Implements Sequence flattening, Flat attribute application,
Orderless sorting, and Listable threading.
"""

from __future__ import annotations

from typing import Any, Iterable, List, Tuple

from minimatic.core import Expression, Symbol, is_expr, head_of
from minimatic.core.attributes import has_attribute, Flat, Orderless, Listable, SequenceHold


def flatten_sequences(expr: Expression, hold_sequence: bool = False) -> Expression:
    """
    Flatten Sequence objects within expression arguments.

    Sequence[] objects are spliced into the argument list:
        h[a, Sequence[x, y], b] -> h[a, x, y, b]
        h[a, Sequence[], b] -> h[a, b]  (empty vanishes)

    Args:
        expr: Expression to flatten
        hold_sequence: If True, don't flatten (SequenceHold attribute)

    Returns:
        New expression with sequences flattened
    """
    if hold_sequence or not is_expr(expr):
        return expr

    Sequence = Symbol("Sequence")

    new_args = []
    changed = False

    for arg in expr.args:
        if is_expr(arg) and head_of(arg) == Sequence:
            # Splice Sequence contents
            new_args.extend(arg.args)
            changed = True
        else:
            new_args.append(arg)

    if changed:
        return Expression(expr.head, *new_args, attributes=expr.attributes)
    return expr


def apply_flat(expr: Expression, is_flat: bool = True) -> Expression:
    """
    Apply Flat (associativity) attribute.

    Flat expressions are flattened: f[f[a,b], c] -> f[a, b, c]

    Args:
        expr: Expression to flatten
        is_flat: Whether to apply (usually from has_attribute(head, Flat))

    Returns:
        Flattened expression if applicable
    """
    if not is_flat or not is_expr(expr):
        return expr

    head = expr.head

    # Check if any argument has the same head
    needs_flatten = False
    flat_count = 0

    for arg in expr.args:
        if is_expr(arg) and arg.head == head:
            needs_flatten = True
            flat_count += 1

    if not needs_flatten:
        return expr

    # Flatten nested expressions
    new_args = []
    for arg in expr.args:
        if is_expr(arg) and arg.head == head:
            # Recursively flatten nested
            flattened = apply_flat(arg, True)
            new_args.extend(flattened.args)
        else:
            new_args.append(arg)

    return Expression(head, *new_args, attributes=expr.attributes)


def apply_orderless(expr: Expression, is_orderless: bool = True) -> Expression:
    """
    Apply Orderless (commutativity) attribute.

    Orderless expressions have their arguments sorted to canonical order.

    Args:
        expr: Expression to sort
        is_orderless: Whether to apply

    Returns:
        Expression with sorted arguments if applicable
    """
    if not is_orderless or not is_expr(expr) or len(expr.args) <= 1:
        return expr

    sorted_args = canonical_sort(expr.args)

    # Only create new expression if order changed
    if tuple(sorted_args) != expr.args:
        return Expression(expr.head, *sorted_args, attributes=expr.attributes)
    return expr


def canonical_sort(elements: Tuple[Any, ...]) -> Tuple[Any, ...]:
    """
    Sort elements into canonical order for Orderless matching.

    Ordering priority:
    1. Atoms (numbers < strings < symbols < other)
    2. Complexity (depth, leaf count)
    3. Alphabetically by string representation
    """
    def sort_key(elem):
        # Priority 1: Type
        if isinstance(elem, (int, float, complex)):
            type_order = 0
            # For numbers, use numeric value
            return (type_order, 0, 0, str(elem), elem)
        elif isinstance(elem, str):
            return (1, 0, 0, elem, 0)
        elif isinstance(elem, Symbol):
            return (2, 0, 0, elem.name, 0)
        elif is_expr(elem):
            # Expressions: sort by depth and complexity
            from minimatic.core import get_depth, leaf_count
            depth = get_depth(elem)
            leaves = leaf_count(elem)
            return (3, depth, leaves, str(elem), 0)
        else:
            return (4, 0, 0, str(elem), 0)

    return tuple(sorted(elements, key=sort_key))


def apply_listable(expr: Expression, is_listable: bool = True) -> Expression:
    """
    Apply Listable attribute (thread over Lists).

    Listable functions thread over List arguments:
        f[{a, b}, c] -> {f[a, c], f[b, c]}

    Args:
        expr: Expression to thread
        is_listable: Whether the head is Listable

    Returns:
        Threaded expression if applicable, otherwise original
    """
    if not is_listable or not is_expr(expr):
        return expr

    List = Symbol("List")

    # Find which arguments are Lists
    list_positions = []
    list_lengths = []

    for i, arg in enumerate(expr.args):
        if is_expr(arg) and head_of(arg) == List:
            list_positions.append(i)
            list_lengths.append(len(arg.args))

    if not list_positions:
        return expr  # No Lists to thread over

    # All Lists must have the same length (or be broadcastable)
    # For simplicity, require same length
    if len(set(list_lengths)) != 1:
        return expr  # Length mismatch, can't thread

    list_len = list_lengths[0]

    # Build result: List[f[...], f[...], ...]
    results = []
    for elem_idx in range(list_len):
        new_args = list(expr.args)
        for list_pos in list_positions:
            new_args[list_pos] = expr.args[list_pos].args[elem_idx]
        results.append(Expression(expr.head, *new_args, attributes=expr.attributes))

    return Expression(List, *results)
