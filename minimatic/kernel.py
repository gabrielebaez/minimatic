from core.expression import Expression
from builtin.symbols import IntegerSymbol, StringSymbol, Executable, Atom
from builtin.arithmetic import LessThan as LT
from builtin.arithmetic import Plus, Subtract


if __name__ == "__main__":
    expr1 = Expression(LT, (IntegerSymbol(5), IntegerSymbol(10)), attributes=(Executable,))
    expr2 = Expression(Plus, (IntegerSymbol(20), IntegerSymbol(22)), attributes=(Executable,))
    expr3 = Expression(Subtract, (IntegerSymbol(15), IntegerSymbol(5)), attributes=(Executable,))
    expr4 = Expression(StringSymbol, ("Hello, World!",), attributes=(Atom,))

    print(f"Expression 1: {expr1} evaluates to {expr1.evaluate()}")
    print(f"Expression 2: {expr2} evaluates to {expr2.evaluate()}")
    print(f"Expression 3: {expr3} evaluates to {expr3.evaluate()}")
    print(f"Expression 4: {expr4} evaluates to {expr4.evaluate()}")
