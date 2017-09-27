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


# ---------

# ArgParse Section
parser = argparse.ArgumentParser()

# Command Line Arguments
parser.add_argument(
    'operation',
    choices=['add', 'sub', 'mult', 'div'],
    help='operation to perform',
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
answer = func_mapping[args.operation](args.x, args.y)

print(answer)
