"""
Minimatic Pattern Module - Pattern matching for symbolic computation.

This module provides Wolfram Language-style pattern matching:
    - Blanks: Wildcard patterns (_, __, ___)
    - Structural: Named patterns, conditions, alternatives
    - Matcher: The pattern matching engine
    - Bindings: Match result management

Pattern Syntax (conceptual):
    _           Blank           matches any single expression
    __          BlankSequence   matches one or more expressions
    ___         BlankNullSequence matches zero or more expressions
    x_          Pattern[x, _]   named pattern
    _Integer    Blank[Integer]  matches expressions with head Integer
    x_ /; x>0   Condition       conditional pattern
    a | b       Alternatives    matches a or b
    x_?f        PatternTest     matches if f[x] is True
    x_:0        Optional        optional with default
    x_..        Repeated        one or more
    x_...       RepeatedNull    zero or more
"""

from .bindings import (
    BindingConflict,
    Bindings,
    bindings_compatible,
    bindings_from_pairs,
    empty_bindings,
    merge_bindings,
    single_binding,
)
from .blanks import (
    Blank,
    BlankNullSequence,
    BlankSequence,
    blank,
    blank_head_constraint,
    blank_matches_head,
    blank_null_seq,
    blank_seq,
    is_any_blank,
    is_blank,
    is_blank_null_sequence,
    is_blank_sequence,
    is_sequence_blank,
)
from .matcher import (
    NO_MATCH,
    MatchResult,
    count_matches,
    find_all_matches,
    find_matches,
    match,
    match_sequence,
    matches,
    replace_with_bindings,
)
from .structural import (
    Alternatives,
    Condition,
    Except,
    HoldPattern,
    Pattern,
    PatternTest,
    Repeated,
    RepeatedNull,
    Verbatim,
    alternatives,
    collect_pattern_names,
    condition,
    except_pattern,
    get_condition_pattern,
    get_condition_test,
    get_default_value,
    hold_pattern,
    is_alternatives,
    is_condition,
    is_except,
    is_hold_pattern,
    is_optional,
    is_pattern,
    is_pattern_construct,
    is_pattern_test,
    is_repeated,
    is_repeated_null,
    is_verbatim,
    optional,
    pattern,
    pattern_blank,
    pattern_name,
    pattern_test,
    repeated,
    repeated_null,
    unwrap_hold_pattern,
    verbatim,
)
from .structural import (
    Optional as OptionalPattern,
)

__all__ = [
    # Blanks
    "Blank",
    "BlankSequence",
    "BlankNullSequence",
    "blank",
    "blank_seq",
    "blank_null_seq",
    "is_blank",
    "is_blank_sequence",
    "is_blank_null_sequence",
    "is_any_blank",
    "is_sequence_blank",
    "blank_head_constraint",
    "blank_matches_head",
    # Structural
    "Pattern",
    "Condition",
    "Alternatives",
    "PatternTest",
    "OptionalPattern",
    "Repeated",
    "RepeatedNull",
    "Except",
    "Verbatim",
    "HoldPattern",
    "pattern",
    "condition",
    "alternatives",
    "pattern_test",
    "optional",
    "repeated",
    "repeated_null",
    "except_pattern",
    "verbatim",
    "hold_pattern",
    "is_pattern",
    "is_condition",
    "is_alternatives",
    "is_pattern_test",
    "is_optional",
    "is_repeated",
    "is_repeated_null",
    "is_except",
    "is_verbatim",
    "is_hold_pattern",
    "is_pattern_construct",
    "pattern_name",
    "pattern_blank",
    "get_default_value",
    "get_condition_test",
    "get_condition_pattern",
    "unwrap_hold_pattern",
    "collect_pattern_names",
    # Bindings
    "Bindings",
    "BindingConflict",
    "empty_bindings",
    "single_binding",
    "merge_bindings",
    "bindings_compatible",
    "bindings_from_pairs",
    # Matcher
    "match",
    "match_sequence",
    "matches",
    "MatchResult",
    "NO_MATCH",
    "replace_with_bindings",
    "find_matches",
    "find_all_matches",
    "count_matches",
]
