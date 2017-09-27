import argparse


# ---------

# Calculator

def add(num1, num2):
    return num1 + num2


def subtract(num1, num2):
    return num1 - num2


def multiply(num1, num2):
    return num1 * num2


def divide(num1, num2):
    try:
        return num1 / num2
    except ZeroDivisionError:
        return "Can't divide by 0"


func_mapping = {
    'add': add,
    'sub': subtract,
    'mult': multiply,
    'div': divide,
}


def not_implemented(*args, **kwargs):
    return 'not implemented'


# ---------

# ArgParse Section
parser = argparse.ArgumentParser()

# Command Line Arguments
parser.add_argument(
    'operation',
    # choices=['add', 'sub', 'mult', 'div'], # the right way to do this
    help='operation to perform (add, sub, mult, div)',
)
parser.add_argument(
    'x',
    type=int,
    help='first number',
)
parser.add_argument(
    'y',
    type=int,
    help='second number',
)

args = parser.parse_args()
answer = func_mapping.get(
    args.operation,
    not_implemented
)(args.x, args.y)

print(answer)
