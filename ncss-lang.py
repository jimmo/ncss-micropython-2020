import sys


# An error while reading the program text.
class CompileError(Exception):
    def __init__(self, line_number, message):
        super().__init__(f'Compile error on line {line_number+1}: {message}')


# A logic error in the program.
class ProgramError(Exception):
    def __init__(self, line_number, message):
        super().__init__(f'Program error on line {line_number+1}: {message}')


# Raised by builtin exit to terminate the program.
class ProgramExit(Exception):
    pass


# Checks that the right number of arguments are available.
def check_arg(line_number, line, arg_type=str):
    if len(line) != 2:
        raise CompileError(line_number, f'Expected argument for {line[0]}.')
    try:
        return arg_type(line[1])
    except:
        raise CompileError(line_number, f'Invalid type for {line[0]}.')


# Pops the stack, but checks that it is non-empty first.
def stack_pop(line_number, stack):
    if len(stack) == 0:
        raise ProgramError(line_number, 'Stack is empty.')
    return stack.pop()


# Calls a built-in function (print, input, debug, etc)
def op_builtin(line_number, fn, stack, variables, labels):
    if fn == 'print':
        print(stack_pop(line_number, stack))
    elif fn == 'input':
        stack.append(input('? '))
    elif fn == 'debug':
        print(stack)
        print(variables)
        print(labels)
    elif fn == 'exit':
        raise ProgramExit()
    else:
        raise CompileError(line_number, f'Unknown function "{fn}".')


# Handles binary operators like add, sub, mul, div, mod.
def op_binary(line_number, line, stack, fn):
    b = int(stack_pop(line_number, stack))
    a = int(stack_pop(line_number, stack))
    stack.append(fn(a, b))


# Executes one line of code.
def execute_line(line_number, line, stack, variables, labels):
    # Ignore comments and blank lines.
    if line.startswith('#') or not line:
        return None

    # Tokenise the line into words. The first word is the "op".
    line = line.split(' ')
    op = line[0]

    # Handle each type of op.
    if op == 'builtin':
        fn = check_arg(line_number, line, str)
        op_builtin(line_number, fn, stack, variables, labels)
    elif op == 'load':
        name = check_arg(line_number, line, str)
        stack.append(variables[name])
    elif op == 'save':
        name = check_arg(line_number, line, str)
        variables[name] = stack_pop(line_number, stack)
    elif op == 'push':
        val = check_arg(line_number, line, int)
        stack.append(val)
    elif op == 'pop':
        stack.pop()
    elif op == 'add':
        op_binary(line_number, line, stack, lambda a, b: a + b)
    elif op == 'sub':
        op_binary(line_number, line, stack, lambda a, b: a - b)
    elif op == 'mul':
        op_binary(line_number, line, stack, lambda a, b: a * b)
    elif op == 'div':
        op_binary(line_number, line, stack, lambda a, b: a // b)
    elif op == 'mod':
        op_binary(line_number, line, stack, lambda a, b: a % b)
    elif op == 'jump':
        # Unconditionally jump to target label.
        label = check_arg(line_number, line, str)
        return label
    elif op == 'jumpzero':
        # Jump to target label if the top of the stack is zero.
        label = check_arg(line_number, line, str)
        if int(stack_pop(line_number, stack)) == 0:
            return label
    elif op == 'call':
        # Push return address and jump to label.
        stack.append(line_number + 1)
        label = check_arg(line_number, line, str)
        return label
    elif op == 'return':
        # Pop saved return address and jump to it.
        return stack_pop(line_number, stack)
    else:
        raise CompileError(line_number, f'Unknown op "{op}".')

    return None


def run(path):
    with open(path, 'r') as f:
        lines = [x.strip() for x in f.readlines()]

    # Program state:
    line_number = 0
    stack = []
    variables = {}
    labels = {}

    # Convert labels to line numbers.
    for i in range(len(lines)):
        if not lines[i].startswith('#') and lines[i].endswith(':'):
            label = lines[i][:-1]
            labels[label] = i
            lines[i] = ''

    # Run until we run out of lines.
    while line_number < len(lines):
        # Execute current line, possibly returning a new label to jump to.
        label = execute_line(line_number, lines[line_number], stack, variables, labels)

        if label is None:
            # Not a jump/call/return, just go to next line.
            line_number += 1
        else:
            if type(label) is int:
                # Op was a return, we now have a saved line number to return to.
                line_number = label
            else:
                # Op was a jump/call, look up label in the labels dict and jump
                # to the corresponding line.
                if label not in labels:
                    raise ProgramError(line_number, f'Undefined jump label {label}.')
                line_number = labels[label]


if __name__ == '__main__':
    try:
        run(sys.argv[1])
    except CompileError as e:
        print(e)
    except ProgramError as e:
        print(e)
    except ProgramExit:
        pass
