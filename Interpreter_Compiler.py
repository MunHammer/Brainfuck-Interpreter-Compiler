#!/usr/bin/env python3
import re


def Translate(Memory, operation='.'):
    # Translator
    if operation == '.':
        return chr(Memory)
    elif operation == ',':
        return ord(input('Input a single character please\n')[0])
    else:
        raise ValueError


def Interpret(program):
    Memory = [0, 0]  # 0 is position in memory, all others is just memory
    pointer = 0  # position in memory
    position = 0  # position in program
    loops = []
    skip = [False, '', 0]
    result = ''
    while position < len(program):
        while len(Memory) <= pointer + 2:
            Memory.append(0)

        if skip[0] is True:
            if skip[1] == 'loop':
                if program[position] == ']':
                    skip[2] -= 1
                elif program[position] == '[':
                    skip[2] += 1
                if skip[2] == 0:
                    skip = [False, '', 0]
            elif skip[1] == 'comment':
                if program[position] == '|':
                    skip = [False, '', 0]
            position += 1
            continue

        match program[position]:
            case '>':
                pointer += 1
            case '<' if pointer > 0:
                pointer -= 1
            case '+':
                Memory[pointer] += 1
            case '-':
                Memory[pointer] -= 1
            case '[':
                if Memory[pointer] != 0:
                    loops.append(position)
                else:
                    skip[0] = True
                    skip[1] = 'loop'
                    skip[2] += 1
            case ']':
                if Memory[pointer] != 0:
                    position = loops[-1]
                else:
                    del loops[-1]
            case '.':
                print(end=Translate(Memory[pointer]))
            case ',':
                Memory[pointer] = Translate(Memory[pointer], operation=',')
        if Memory[pointer] > 255:
            Memory[pointer] = 0
        elif Memory[pointer] < 0:
            Memory[pointer] = 255
        position += 1


def tab(num: int = 0) -> str:
    return '    ' * num


def Compile(program: str, file=None) -> None:
    CPPresult = '#include <iostream>\nusing namespace std;\n'
    CPPresult += 'int main() {\n    int tape[30000]={0};\n    int ptr=0;\n    int out;\n'
    PYresult = [0, 'tape=[0]*30000\nptr=0\n']
    # removes non-valid characters
    program = re.sub(r'[^+-.><\]\[]', '', program)
    while program[0] == '[':  # removes standard opening comments
        depth = 1
        while True:
            program = program[1:]
            if len(program) == 0:
                raise Exception('Program is 100% comments')
            if program[0] == ']':
                depth -= 1
            elif program[0] == '[':
                depth += 1
            if depth == 0:
                program = program[1:]
                break
    depth = 0
    for char in program:
        if char == '[':
            depth += 1
        elif char == ']':
            depth -= 1
    if depth != 0:
        raise Exception('Unmatched loop')
    while True:
        match program[0]:
            case '[':
                PYresult[1] += 'while tape[ptr] != 0:'
                PYresult[0] += 1
                CPPresult += 'while (tape[ptr] != 0) {'
            case ']':
                PYresult[0] -= 1
                CPPresult += '}'
            case '+':
                length = len(re.search(r'^[+]+', program).group())
                PYresult[1] += f'tape[ptr] += {length}'
                CPPresult += f'tape[ptr] += {length};'
                program = program[length - 1:]
            case '-':
                length = len(re.search(r'^[-]+', program).group())
                PYresult[1] += f'tape[ptr] -= {length}'
                CPPresult += f'tape[ptr] -= {length};'
                program = program[length - 1:]
            case '>':
                length = len(re.search(r'^[>]+', program).group())
                PYresult[1] += f'ptr += {length}'
                CPPresult += f'ptr += {length};'
                program = program[length - 1:]
            case '<':
                length = len(re.search(r'^[<]+', program).group())
                PYresult[1] += f'ptr -= {length}'
                CPPresult += f'ptr -= {length};'
                program = program[length - 1:]
            case '.':
                PYresult[1] += 'print(end=chr(tape[ptr]))'
                CPPresult += 'cout << char(tape[ptr]);'
            case ',':
                PYresult[1] += 'tape[ptr]=ord(input()[0])'
                CPPresult += 'cin >> tape[ptr];'
        PYresult[1] += '\n' + tab(PYresult[0])
        CPPresult += '\n' + tab(PYresult[0] + 1)
        program = program[1:]
        if len(program) == 0:
            break
    CPPresult += 'return 0;\n}'
    if file != None:
        with open(f'{file}.py', 'w') as f:
            f.write(PYresult[1])
        with open(f'{file}.cpp', 'w') as f:
            f.write(CPPresult)
