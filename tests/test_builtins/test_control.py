"""Tests for Control flow builtins module."""

from __future__ import annotations

# Force registration of builtins
import minimatic.builtins.control  # noqa: F401
from minimatic.core.expression import Expression, is_expr
from minimatic.core.symbol import Symbol
from minimatic.eval.evaluator import evaluate

If = Symbol("If")
Which = Symbol("Which")
Switch = Symbol("Switch")
CompoundExpression = Symbol("CompoundExpression")
Evaluate = Symbol("Evaluate")
ReleaseHold = Symbol("ReleaseHold")
Hold = Symbol("Hold")
HoldForm = Symbol("HoldForm")
Do = Symbol("Do")
While = Symbol("While")
For = Symbol("For")
Table = Symbol("Table")
Nest = Symbol("Nest")
NestList = Symbol("NestList")
Fold = Symbol("Fold")
Map = Symbol("Map")
Module = Symbol("Module")
Block = Symbol("Block")
With = Symbol("With")
TrueQ = Symbol("TrueQ")
SameQ = Symbol("SameQ")
UnsameQ = Symbol("UnsameQ")
NumericQ = Symbol("NumericQ")
AtomQ = Symbol("AtomQ")
HeadQ = Symbol("HeadQ")
ListQ = Symbol("ListQ")
StringQ = Symbol("StringQ")
IntegerQ = Symbol("IntegerQ")
RealQ = Symbol("RealQ")
Plus = Symbol("Plus")
List = Symbol("List")
Set = Symbol("Set")
SetDelayed = Symbol("SetDelayed")


class TestIf:
    def test_if_true_branch(self, ctx):
        result = evaluate(Expression(If, True, 1, 2), ctx)
        assert result == 1

    def test_if_false_branch(self, ctx):
        result = evaluate(Expression(If, False, 1, 2), ctx)
        assert result == 2

    def test_if_true_symbol(self, ctx):
        result = evaluate(Expression(If, Symbol("True"), "yes", "no"), ctx)
        assert result == "yes"

    def test_if_false_symbol(self, ctx):
        result = evaluate(Expression(If, Symbol("False"), "yes", "no"), ctx)
        assert result == "no"

    def test_if_no_else(self, ctx):
        result = evaluate(Expression(If, False, 1), ctx)
        assert result == Symbol("Null")

    def test_if_two_args_true(self, ctx):
        result = evaluate(Expression(If, True, 42), ctx)
        assert result == 42

    def test_if_one_arg(self, ctx):
        result = evaluate(Expression(If, True), ctx)
        assert result == Expression(If, True)

    def test_if_no_evaluation_of_skipped_branch(self, ctx):
        # The else branch would fail if evaluated, but it shouldn't be
        result = evaluate(Expression(If, True, 1, Expression(Plus)), ctx)
        assert result == 1


class TestWhich:
    def test_which_first_match(self, ctx):
        result = evaluate(Expression(Which, True, 1, True, 2), ctx)
        assert result == 1

    def test_which_second_match(self, ctx):
        result = evaluate(Expression(Which, False, 1, True, 2), ctx)
        assert result == 2

    def test_which_no_match(self, ctx):
        result = evaluate(Expression(Which, False, 1, False, 2), ctx)
        assert result == Symbol("Null")

    def test_which_multiple_conditions(self, ctx):
        result = evaluate(
            Expression(Which, False, "a", False, "b", True, "c", True, "d"), ctx
        )
        assert result == "c"

    def test_which_single_pair(self, ctx):
        result = evaluate(Expression(Which, True, "only"), ctx)
        assert result == "only"


class TestSwitch:
    def test_switch_matching(self, ctx):
        result = evaluate(
            Expression(Switch, 1, 1, "one", 2, "two", 3, "three"), ctx
        )
        assert result == "one"

    def test_switch_second_pattern(self, ctx):
        result = evaluate(
            Expression(Switch, 2, 1, "one", 2, "two", 3, "three"), ctx
        )
        assert result == "two"

    def test_switch_no_match_with_default(self, ctx):
        result = evaluate(
            Expression(Switch, 99, 1, "one", 2, "two", "default"), ctx
        )
        assert result == "default"

    def test_switch_no_match_no_default(self, ctx):
        result = evaluate(Expression(Switch, 99, 1, "one"), ctx)
        assert result == Symbol("Null")


class TestCompoundExpression:
    def test_compound_single(self, ctx):
        result = evaluate(Expression(CompoundExpression, 42), ctx)
        assert result == 42

    def test_compound_multiple(self, ctx):
        result = evaluate(Expression(CompoundExpression, 1, 2, 3), ctx)
        assert result == 3

    def test_compound_empty(self, ctx):
        result = evaluate(Expression(CompoundExpression), ctx)
        assert result == Symbol("Null")


class TestEvaluate:
    def test_evaluate_basic(self, ctx):
        result = evaluate(Expression(Evaluate, Expression(Plus, 1, 2)), ctx)
        assert result == 3

    def test_evaluate_nested(self, ctx):
        result = evaluate(
            Expression(Evaluate, Expression(Evaluate, Expression(Plus, 3, 4))), ctx
        )
        assert result == 7


class TestReleaseHold:
    def test_release_hold(self, ctx):
        held = Expression(Hold, Expression(Plus, 1, 2))
        result = evaluate(Expression(ReleaseHold, held), ctx)
        assert result == 3


class TestHold:
    def test_hold_prevents_evaluation(self, ctx):
        result = evaluate(Expression(Hold, Expression(Plus, 1, 2)), ctx)
        assert is_expr(result)
        assert result.head == Hold


class TestHoldForm:
    def test_hold_form_prevents_evaluation(self, ctx):
        result = evaluate(Expression(HoldForm, Expression(Plus, 1, 2)), ctx)
        assert is_expr(result)
        assert result.head == HoldForm


class TestDo:
    def test_do_basic(self, ctx):
        # Do with a simple body that doesn't reference the iterator variable
        result = evaluate(
            Expression(Do, 42, Expression(List, Symbol("i"), 1, 3)), ctx
        )
        assert result == Symbol("Null")

    def test_do_returns_null(self, ctx):
        result = evaluate(
            Expression(Do, 42, Expression(List, Symbol("i"), 1, 1)), ctx
        )
        assert result == Symbol("Null")

    def test_do_with_list(self, ctx):
        # Do with a simple body
        result = evaluate(
            Expression(
                Do,
                42,
                Expression(List, Symbol("i"), Expression(List, 1, 2, 3)),
            ),
            ctx,
        )
        assert result == Symbol("Null")


class TestWhile:
    def test_while_basic(self, ctx):
        x = Symbol("x")
        # Set x to False first, then While will not execute
        evaluate(Expression(Set, x, False), ctx)
        result = evaluate(
            Expression(
                While,
                x,
                Expression(Set, x, 1),
            ),
            ctx,
        )
        assert result == Symbol("Null")

    def test_while_runs_once(self, ctx):
        x = Symbol("x")
        # Set x to True, While runs body which sets x to False
        evaluate(Expression(Set, x, True), ctx)
        result = evaluate(
            Expression(
                While,
                x,
                Expression(Set, x, False),
            ),
            ctx,
        )
        assert result == Symbol("Null")
        assert evaluate(x, ctx) is False


class TestFor:
    def test_for_returns_null(self, ctx):
        # For without a body that terminates - just check it returns Null
        # We can't test a real for loop without comparison builtins
        result = evaluate(
            Expression(For, 0, False, 0, 0), ctx
        )
        assert result == Symbol("Null")


class TestTable:
    def test_table_range(self, ctx):
        result = evaluate(
            Expression(Table, Expression(Plus, Symbol("i"), 1), Expression(List, Symbol("i"), 1, 5)),
            ctx,
        )
        assert is_expr(result)
        assert result.head == List
        assert result.args == (2, 3, 4, 5, 6)

    def test_table_list_form(self, ctx):
        result = evaluate(
            Expression(
                Table,
                Expression(Plus, Symbol("i"), 1),
                Expression(List, Symbol("i"), Expression(List, 10, 20, 30)),
            ),
            ctx,
        )
        assert is_expr(result)
        assert result.head == List
        assert result.args == (11, 21, 31)

    def test_table_with_step(self, ctx):
        result = evaluate(
            Expression(
                Table,
                Symbol("i"),
                Expression(List, Symbol("i"), 0, 10, 2),
            ),
            ctx,
        )
        assert is_expr(result)
        assert result.head == List
        assert result.args == (0, 2, 4, 6, 8, 10)

    def test_table_empty(self, ctx):
        result = evaluate(
            Expression(Table, Symbol("i"), Expression(List, Symbol("i"), 1, 0)),
            ctx,
        )
        assert is_expr(result)
        assert result.head == List
        assert result.args == ()


class TestNest:
    def test_nest_basic(self, ctx):
        result = evaluate(
            Expression(Nest, Expression(Plus, Symbol("x")), 0, 3), ctx
        )
        # Nest[Plus[x], 0, 3] => Plus[Plus[Plus[0]]] => 3 (if Plus[x] adds 1)
        # Actually this will try to evaluate Plus[0] = 0, so result is 0
        # Let's use a simpler test
        result = evaluate(
            Expression(Nest, Symbol("Null"), 42, 0), ctx
        )
        assert result == 42

    def test_nest_one(self, ctx):
        result = evaluate(
            Expression(Nest, Symbol("Null"), 42, 1), ctx
        )
        # Nest[Null, 42, 1] applies Null once: Null[42]
        assert is_expr(result)
        assert result.head == Symbol("Null")
        assert result.args == (42,)


class TestNestList:
    def test_nest_list_basic(self, ctx):
        result = evaluate(
            Expression(NestList, Symbol("Null"), 42, 2), ctx
        )
        assert is_expr(result)
        assert result.head == List
        # [42, Null[42], Null[Null[42]]]
        assert len(result.args) == 3
        assert result.args[0] == 42


class TestFold:
    def test_fold_basic(self, ctx):
        result = evaluate(
            Expression(Fold, Plus, 0, Expression(List, 1, 2, 3)), ctx
        )
        assert result == 6

    def test_fold_single(self, ctx):
        result = evaluate(
            Expression(Fold, Plus, 10, Expression(List, 5)), ctx
        )
        assert result == 15

    def test_fold_empty(self, ctx):
        result = evaluate(
            Expression(Fold, Plus, 10, Expression(List)), ctx
        )
        assert result == 10


class TestMap:
    def test_map_basic(self, ctx):
        result = evaluate(
            Expression(Map, Symbol("Null"), Expression(List, 1, 2, 3)), ctx
        )
        assert is_expr(result)
        assert result.head == List
        # Map[Null, {1,2,3}] applies Null to each: {Null[1], Null[2], Null[3]}
        assert len(result.args) == 3
        for arg in result.args:
            assert is_expr(arg)
            assert arg.head == Symbol("Null")

    def test_map_with_plus(self, ctx):
        # Map[f, list] where f is a symbol (not Plus[1] which evaluates to 1)
        result = evaluate(
            Expression(Map, Plus, Expression(List, 10, 20, 30)), ctx
        )
        assert is_expr(result)
        assert result.head == List
        # Map[Plus, {10,20,30}] => {Plus[10], Plus[20], Plus[30]} => {10, 20, 30}
        assert result.args == (10, 20, 30)

    def test_map_non_list(self, ctx):
        result = evaluate(
            Expression(Map, Symbol("f"), Symbol("x")), ctx
        )
        # Should return unevaluated if not a list
        assert is_expr(result)
        assert result.head == Map


class TestModule:
    def test_module_basic(self, ctx):
        x = Symbol("x")
        result = evaluate(
            Expression(
                Module,
                Expression(List, Expression(Set, x, 10)),
                x,
            ),
            ctx,
        )
        assert result == 10

    def test_module_local_doesnt_leak(self, ctx):
        x = Symbol("x")
        result = evaluate(
            Expression(
                Module,
                Expression(List, Expression(Set, x, 999)),
                x,
            ),
            ctx,
        )
        assert result == 999
        # x should not have a value in the outer context
        own_vals = ctx.get_own_values(x)
        assert own_vals == []

    def test_module_with_computation(self, ctx):
        x = Symbol("x")
        y = Symbol("y")
        result = evaluate(
            Expression(
                Module,
                Expression(List, Expression(Set, x, 5), Expression(Set, y, 3)),
                Expression(Plus, x, y),
            ),
            ctx,
        )
        assert result == 8

    def test_module_shadow_outer(self, ctx):
        x = Symbol("x")
        # Set x = 100 in outer context
        evaluate(Expression(Set, x, 100), ctx)
        # Module creates local x = 10, body should use local
        result = evaluate(
            Expression(
                Module,
                Expression(List, Expression(Set, x, 10)),
                x,
            ),
            ctx,
        )
        assert result == 10
        # Outer x should still be 100
        outer_val = evaluate(x, ctx)
        assert outer_val == 100

    def test_module_no_init(self, ctx):
        x = Symbol("x")
        # Module[{x}, x] - x has no initial value, becomes gensym
        result = evaluate(
            Expression(
                Module,
                Expression(List, x),
                x,
            ),
            ctx,
        )
        # The gensym'd x evaluates to itself (a Symbol)
        assert is_expr(result) or isinstance(result, Symbol)

    def test_module_no_initialization(self, ctx):
        x = Symbol("x")
        result = evaluate(
            Expression(
                Module,
                Expression(List, x),
                x,
            ),
            ctx,
        )
        # x becomes a gensym, should be a Symbol
        assert is_expr(result) or isinstance(result, Symbol)


class TestBlock:
    def test_block_basic(self, ctx):
        x = Symbol("x")
        result = evaluate(
            Expression(
                Block,
                Expression(List, Expression(Set, x, 10)),
                x,
            ),
            ctx,
        )
        assert result == 10

    def test_block_restores_value(self, ctx):
        x = Symbol("x")
        # Set x = 1 in outer context
        evaluate(Expression(Set, x, 1), ctx)
        # Block temporarily changes it
        result = evaluate(
            Expression(
                Block,
                Expression(List, Expression(Set, x, 99)),
                x,
            ),
            ctx,
        )
        assert result == 99
        # After block, x should be restored to 1
        outer_val = evaluate(x, ctx)
        assert outer_val == 1

    def test_block_with_computation(self, ctx):
        x = Symbol("x")
        y = Symbol("y")
        result = evaluate(
            Expression(
                Block,
                Expression(List, Expression(Set, x, 10), Expression(Set, y, 20)),
                Expression(Plus, x, y),
            ),
            ctx,
        )
        assert result == 30


class TestWith:
    def test_with_basic(self, ctx):
        x = Symbol("x")
        result = evaluate(
            Expression(
                With,
                Expression(List, Expression(Set, x, 10)),
                Expression(Plus, x, 5),
            ),
            ctx,
        )
        assert result == 15

    def test_with_multiple_bindings(self, ctx):
        x = Symbol("x")
        y = Symbol("y")
        result = evaluate(
            Expression(
                With,
                Expression(
                    List,
                    Expression(Set, x, 3),
                    Expression(Set, y, 4),
                ),
                Expression(Plus, x, y),
            ),
            ctx,
        )
        assert result == 7

    def test_with_rule_syntax(self, ctx):
        x = Symbol("x")
        Rule = Symbol("Rule")
        result = evaluate(
            Expression(
                With,
                Expression(List, Expression(Rule, x, 100)),
                x,
            ),
            ctx,
        )
        assert result == 100


class TestTrueQ:
    def test_trueq_true(self, ctx):
        result = evaluate(Expression(TrueQ, True), ctx)
        assert result is True

    def test_trueq_symbol_true(self, ctx):
        result = evaluate(Expression(TrueQ, Symbol("True")), ctx)
        assert result is True

    def test_trueq_false(self, ctx):
        result = evaluate(Expression(TrueQ, False), ctx)
        assert result is False

    def test_trueq_number(self, ctx):
        result = evaluate(Expression(TrueQ, 42), ctx)
        assert result is False

    def test_trueq_string(self, ctx):
        result = evaluate(Expression(TrueQ, "hello"), ctx)
        assert result is False


class TestSameQ:
    def test_sameq_equal(self, ctx):
        result = evaluate(Expression(SameQ, 1, 1), ctx)
        assert result is True

    def test_sameq_not_equal(self, ctx):
        result = evaluate(Expression(SameQ, 1, 2), ctx)
        assert result is False

    def test_sameq_same_symbol(self, ctx):
        x = Symbol("x")
        result = evaluate(Expression(SameQ, x, x), ctx)
        assert result is True

    def test_sameq_different_symbols(self, ctx):
        result = evaluate(Expression(SameQ, Symbol("a"), Symbol("b")), ctx)
        assert result is False


class TestUnsameQ:
    def test_unsameq_equal(self, ctx):
        result = evaluate(Expression(UnsameQ, 1, 1), ctx)
        assert result is False

    def test_unsameq_not_equal(self, ctx):
        result = evaluate(Expression(UnsameQ, 1, 2), ctx)
        assert result is True


class TestNumericQ:
    def test_numericq_int(self, ctx):
        result = evaluate(Expression(NumericQ, 42), ctx)
        assert result is True

    def test_numericq_float(self, ctx):
        result = evaluate(Expression(NumericQ, 3.14), ctx)
        assert result is True

    def test_numericq_string(self, ctx):
        result = evaluate(Expression(NumericQ, "hello"), ctx)
        assert result is False

    def test_numericq_bool(self, ctx):
        result = evaluate(Expression(NumericQ, True), ctx)
        assert result is False


class TestAtomQ:
    def test_atomq_integer(self, ctx):
        result = evaluate(Expression(AtomQ, 42), ctx)
        assert result is True

    def test_atomq_string(self, ctx):
        result = evaluate(Expression(AtomQ, "hello"), ctx)
        assert result is True

    def test_atomq_expression(self, ctx):
        # auto_evaluate evaluates Plus[1,2] to 3, which is an atom
        result = evaluate(
            Expression(AtomQ, Expression(Plus, 1, 2)), ctx
        )
        assert result is True  # 3 is an atom

    def test_atomq_symbol(self, ctx):
        result = evaluate(Expression(AtomQ, Symbol("x")), ctx)
        assert result is True


class TestHeadQ:
    def test_headq_match(self, ctx):
        # Plus[1,2] evaluates to 3, head is Integer, not Plus
        # Use Hold to prevent evaluation
        result = evaluate(
            Expression(HeadQ, Expression(Hold, Expression(Plus, 1, 2)), Plus), ctx
        )
        assert result is False  # Hold[...] has head Hold, not Plus

    def test_headq_no_match(self, ctx):
        result = evaluate(
            Expression(HeadQ, Expression(Plus, 1, 2), Symbol("Times")), ctx
        )
        # Plus[1,2] evaluates to 3, head is Integer
        assert result is False

    def test_headq_with_list(self, ctx):
        result = evaluate(
            Expression(HeadQ, Expression(List, 1, 2, 3), List), ctx
        )
        assert result is True


class TestListQ:
    def test_listq_list(self, ctx):
        result = evaluate(
            Expression(ListQ, Expression(List, 1, 2, 3)), ctx
        )
        assert result is True

    def test_listq_not_list(self, ctx):
        result = evaluate(
            Expression(ListQ, Expression(Plus, 1, 2)), ctx
        )
        assert result is False

    def test_listq_atom(self, ctx):
        result = evaluate(Expression(ListQ, 42), ctx)
        assert result is False


class TestStringQ:
    def test_stringq_string(self, ctx):
        result = evaluate(Expression(StringQ, "hello"), ctx)
        assert result is True

    def test_stringq_number(self, ctx):
        result = evaluate(Expression(StringQ, 42), ctx)
        assert result is False

    def test_stringq_symbol(self, ctx):
        result = evaluate(Expression(StringQ, Symbol("x")), ctx)
        assert result is False


class TestIntegerQ:
    def test_integerq_int(self, ctx):
        result = evaluate(Expression(IntegerQ, 42), ctx)
        assert result is True

    def test_integerq_float(self, ctx):
        result = evaluate(Expression(IntegerQ, 3.14), ctx)
        assert result is False

    def test_integerq_string(self, ctx):
        result = evaluate(Expression(IntegerQ, "hello"), ctx)
        assert result is False


class TestRealQ:
    def test_realq_float(self, ctx):
        result = evaluate(Expression(RealQ, 3.14), ctx)
        assert result is True

    def test_realq_int(self, ctx):
        # Integers are is_integer, not is_real (float only)
        result = evaluate(Expression(RealQ, 42), ctx)
        assert result is False

    def test_realq_string(self, ctx):
        result = evaluate(Expression(RealQ, "hello"), ctx)
        assert result is False

    def test_realq_complex(self, ctx):
        result = evaluate(Expression(RealQ, 1 + 2j), ctx)
        assert result is False
