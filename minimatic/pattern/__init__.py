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
"""

from .blanks import (
    # Blank types
    Blank,
    BlankSequence,
    BlankNullSequence,
    # Constructors
    blank,
    blank_seq,
    blank_null_seq,
    # Predicates
    is_blank,
    is_blank_sequence,
    is_blank_null_sequence,
    is_any_blank,
    is_sequence_blank,
    # Utilities
    blank_head_constraint,
)

from .structural import (
    # Pattern constructs
    pattern,
    condition,
    alternatives,
    pattern_test,
    optional,
    repeated,
    repeated_null,
    except_pattern,
    verbatim,
    hold_pattern,
    # Predicates
    is_pattern,
    is_condition,
    is_alternatives,
    is_pattern_test,
    is_optional,
    is_repeated,
    is_except,
    is_verbatim,
    is_hold_pattern,
    # Utilities
    pattern_name,
    pattern_blank,
    get_default_value,
)

from .bindings import (
    # Bindings class
    Bindings,
    # Factory functions
    empty_bindings,
    single_binding,
    # Operations
    merge_bindings,
    bindings_compatible,
)

from .matcher import (
    # Main matching functions
    match,
    match_sequence,
    matches,
    # Match result
    MatchResult,
    NO_MATCH,
    # Utilities
    replace_with_bindings,
    find_matches,
    find_all_matches,
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
    # Structural
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
    "is_except",
    "is_verbatim",
    "is_hold_pattern",
    "pattern_name",
    "pattern_blank",
    "get_default_value",
    # Bindings
    "Bindings",
    "empty_bindings",
    "single_binding",
    "merge_bindings",
    "bindings_compatible",
    # Matcher
    "match",
    "match_sequence",
    "matches",
    "MatchResult",
    "NO_MATCH",
    "replace_with_bindings",
    "find_matches",
    "find_all_matches",
]
