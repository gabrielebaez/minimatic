from core.expression import Expression
from core.evaluation import Context, evaluate
from builtin.symbols import IntegerSymbol, StringSymbol, Atom
from builtin.arithmetic import LessThan
from builtin.arithmetic import Plus, Subtract


if __name__ == "__main__":
    a = IntegerSymbol(10)
    b = IntegerSymbol(20)

    expr1 = LessThan((IntegerSymbol(5), IntegerSymbol(10)))
    expr2 = Plus((IntegerSymbol(20), IntegerSymbol(22)))
    expr3 = Subtract((IntegerSymbol(15), IntegerSymbol(15)))
    expr4 = StringSymbol("Hello, World!")

    print(f"Expression 1: {expr1} evaluates to {evaluate(expr1)}")
    print(f"Expression 2: {expr2} evaluates to {evaluate(expr2)}")
    print(f"Expression 3: {expr3} evaluates to {evaluate(expr3)}")
    print(f"Expression 4: {expr4} evaluates to {evaluate(expr4)}")
    print(f"Expression 5: {expr4.has_attribute(Atom)}")
    print(f"a: {a}, b: {b}")
