from core.expression import Expression
from core.attributes import Integer, Atom, Executable
from builtin.arithmetic import LessThan as LT
from builtin.arithmetic import Plus


if __name__ == "__main__":
    a = Expression(Integer, 2, attributes=(Atom,))
    b = Expression(Integer, 3, attributes=(Atom,))
    d = Expression(LT, (b, a), attributes=(Executable,)).evaluate()
    c = Expression(Plus, (a, b), attributes=(Executable,)).evaluate()

    big_a = Expression(Integer, 100, attributes=(Atom,))
    big_b = Expression(Integer, 200, attributes=(Atom,))
    big_c = Expression(Plus, (big_a, big_b), attributes=(Executable,)).evaluate()
    print(a)  # Should print Integer(2)
    print(b)  # Should print Integer(3)
    print(d)  # Should print Boolean(True)
    print(c)  # Should print Integer(5)
    print(big_c)  # Should print Integer(300)
