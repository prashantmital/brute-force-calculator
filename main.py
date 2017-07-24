from itertools import product
from IPython import embed
from math import fabs


class OperatorException(Exception):
    pass


class OperationFailedError(OperatorException):
    pass


class NoOperationError(OperatorException):
    pass


class FloatError(OperatorException):
    pass


class OutOfBoundsError(OperatorException):
    pass


class OperatorBase(object):
    """ Base class for operations available in the calculator game. """
    def operate(self, number):
        raise NotImplementedError

    def apply(self, number):
        try:
            result = self.operate(number)
        except:
            msg = "Operator {!r} failed when applied to {!r}.".format(
                type(self), number
            )
            raise OperationFailedError(msg)
        if result == number:
            msg = "Operator {!r} is a no-op when applied to {!r}.".format(
                type(self), number
            )
            raise NoOperationError(msg)
        elif fabs(result) > 999999:
            msg = "Result exceeds maximum display width."
            raise OutOfBoundsError(msg)
        return result


class Multiply(OperatorBase):
    def __init__(self, factor):
        self._factor = factor

    def __repr__(self):
        return "Multiply({})".format(self._factor)

    def operate(self, number):
        return number * self._factor


class Add(OperatorBase):
    def __init__(self, adder):
        self._adder = adder

    def __repr__(self):
        return "Add({})".format(self._adder)

    def operate(self, number):
        return number + self._adder


class Divide(OperatorBase):
    def __init__(self, divisor):
        self._divisor = divisor

    def __repr__(self):
        return "Divide({})".format(self._divisor)

    def operate(self, number):
        result = float(number) / self._divisor
        if result != int(result):
            # Revert to no-op if float is produced as floats are not
            # supported by the calculator game.
            return number
        else:
            return int(result)


class DigitReplace(OperatorBase):
    def __init__(self, inp, out):
        self._in = inp
        self._out = out

    def __repr__(self):
        return "Replace({}=>{})".format(self._in, self._out)

    def operate(self, number):
        str_number = str(number)
        return int(str_number.replace(str(self._in), str(self._out)))


class DigitSum(OperatorBase):
    def __repr__(self):
        return "Sum"

    def operate(self, number):
        cumsum = 0
        str_number = str(number)
        for str_digit in str_number:
            cumsum += int(str_digit)
        return cumsum


class DigitAppend(OperatorBase):
    def __init__(self, digit):
        self._digit = digit

    def __repr__(self):
        return "Append({})".format(self._digit)

    def operate(self, number):
        str_number = str(number)
        return int(str_number + str(self._digit))


class MirrorAppend(OperatorBase):
    def __repr__(self):
        return "Mirror"

    def operate(self, number):
        str_number = str(number)
        return int(str_number + str_number[::-1])


class Backspace(OperatorBase):
    def __repr__(self):
        return "Backspace"

    def operate(self, number):
        return int(divmod(number, 10)[0])


class ShiftLeft(OperatorBase):
    def __repr__(self):
        return "ShiftLeft"

    def operate(self, number):
        str_number = str(number)
        str_left, str_base = str_number[0], str_number[1:]
        return int(str_base + str_left)


class ShiftRight(OperatorBase):
    def __repr__(self):
        return "ShiftLeft"

    def operate(self, number):
        base, right = divmod(number, 10)
        return int(str(right) + str(base))


class OperationPipeline(object):
    def __init__(self, start, target):
        self._start = start
        self._target = target

    def _safe_compute(self, sequence):
        current = self._start
        for operator in sequence:
            try:
                current = operator.apply(current)
            except (FloatError, NoOperationError, OutOfBoundsError):
                # If a float is produced, stop the pipeline.
                # If a no-op is encountered, stop the pipeline.
                # If result exceeds max width of display, stop the pipeline.
                return self._start
        return current

    def compute(self, sequence):
        result = self._safe_compute(sequence)
        if result == self._target:
            return True
        else:
            return False


class BruteForceCalculator(object):
    def __init__(self, start, target, max_moves, operations):
        self._start = start
        self._target = target
        self._max_moves = max_moves
        self._operations = operations

    def operation_sequence_candidates(self):
        for op_sequence in product(self._operations, repeat=self._max_moves):
            yield op_sequence

    def run(self):
        pipeline = OperationPipeline(self._start, self._target)
        for op_sequence in self.operation_sequence_candidates():
            if pipeline.compute(op_sequence):
                print("Desired sequence of operations: {!r}".format(
                    op_sequence))


def example_level_123():
    brute_forcer = BruteForceCalculator(
        22, 3, 4, (DigitSum(), Divide(2), MirrorAppend(), Backspace())
    )
    brute_forcer.run()


def example_level_5():
    brute_forcer = BruteForceCalculator(
        3, 4, 3, (Add(4), Multiply(4), Divide(4))
    )
    brute_forcer.run()


if __name__ == '__main__':
    print("Type %whos to get an idea of the API.")
    print("Syntax: BruteForceCalculator(start, target, moves, operator_tuple)")
    embed()
