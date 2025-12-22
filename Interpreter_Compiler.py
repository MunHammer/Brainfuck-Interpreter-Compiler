#!/usr/bin/env python3
import re
import os
import json
path = os.path.dirname(os.path.realpath(__file__))


def numByte(integer: str | int) -> str:
    integer = int(integer)
    integer = bin(integer)[2:]
    if len(integer) < 8:
        less = 8 - len(integer)
        integer = '0' * less + integer
    return integer


def Byte(program: str) -> str:
    chars = []
    result = ''
    # [  0
    # ]  1
    # .  2
    # ,  3
    # +  4-66
    # -  67-129
    # > 130-192
    # < 193-254 11111111
    # # 255
    program = re.sub(r'[^+-.><\]\[]', '', program)
    if len(program) == 0:
        raise Exception(
            'Program is either entirely comments, or you ran it through Byte() twice')
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
                result += numByte(0)
            case ']':
                result += numByte(1)
            case '.':
                result += numByte(2)
            case ',':
                result += numByte(3)
            case '+':
                length = len(re.search(r'^[+]{1,63}', program).group())
                result += numByte(3 + length)
                program = program[length - 1:]
            case '-':
                length = len(re.search(r'^[-]{1,63}', program).group())
                result += numByte(66 + length)
                program = program[length - 1:]
            case '>':
                length = len(re.search(r'^[>]{1,63}', program).group())
                result += numByte(129 + length)
                program = program[length - 1:]
            case '<':
                length = len(re.search(r'^[<]{1,62}', program).group())
                result += numByte(192 + length)
                program = program[length - 1:]
            case '#':
                result += numByte(255)
        program = program[1:]
        if len(program) == 0:
            break
    return result


def Interpret(program: str, *, give: bool = False,
              write_to_file: bool = False) -> str | None:
    Memory = {'ptr': 0, 'tape': [0]*30000}
    tape = Memory['tape']  # 0 is position in memory, all others is just memory
    ptr = Memory['ptr']  # position in memory
    output = ''
    position = 0
    chars = []
    loops = []
    depth = 0
    for num in range(0, 256):
        chars.append(chr(num))
    if write_to_file:
        with open(f'{path}/MemoryDump.json', 'w') as file:
            json.dump([], file)
    while True:
        curbyte = program[position * 8:position * 8 + 8]
        if len(curbyte) < 8:
            break
        if depth > 0:
            if int(curbyte, 2) == 0:
                depth += 1
            elif int(curbyte, 2) == 1:
                depth -= 1
            position += 1
            if position*8 > len(program) - 1:
                raise Exception('Unmatched "["')
            continue
        elif depth < 0:
            raise Exception('Unmatched "]"')
        if int(curbyte, 2) == 0:
            if tape[ptr] != 0:
                loops.append(position)
            else:
                depth = 1
        elif int(curbyte, 2) == 1:
            if tape[ptr] != 0:
                position = loops[-1]
            else:
                loops.pop()
        elif int(curbyte, 2) == 2:
            if give:
                output += chr(tape[ptr])
            else:
                print(end=chr(tape[ptr]))
        elif int(curbyte, 2) == 3:
            tape[ptr] = ord(input('_\U00000008')[0])
        elif int(curbyte, 2) in range(4, 67):
            tape[ptr] += int(curbyte, 2) - 3
            if tape[ptr] > 255:
                tape[ptr] -= 256
        elif int(curbyte, 2) in range(67, 130):
            tape[ptr] -= int(curbyte, 2) - 66
            if tape[ptr] < 0:
                tape[ptr] += 256
        elif int(curbyte, 2) in range(130, 193):
            ptr += int(curbyte, 2) - 129
        elif int(curbyte, 2) in range(193, 255):
            ptr -= int(curbyte, 2) - 192
        elif int(curbyte, 2) == 255:
            if write_to_file:
                with open(f'{path}/MemoryDump.json') as file:
                    last = json.load(file)
                with open(f'{path}/MemoryDump.json', 'w') as file:
                    last.append(Memory)
                    json.dump(last, file, indent=None,
                              separators=(',', '\n:\n'))
        position += 1
        if ptr < 0:
            raise Exception(
                f'At character {position} in program: No negative cells available')
        elif ptr >= 30000:
            raise Exception(
                f'At character {position} in program: Only 30,000 cells available')
        if position > len(program) - 1:
            break
    if write_to_file:
        with open(f'{path}/MemoryDump.json') as file:
            last = json.load(file)
        with open(f'{path}/MemoryDump.json', 'w') as file:
            last.append(Memory)
            json.dump(last, file, indent=None, separators=(',', '\n:\n'))
    if give:
        return output
    else:
        return None


def run_Interpret(program: str) -> str:
    return Interpret(Byte(program), give=True)


def debug_Interpret(program: str) -> str:
    return Interpret(Byte(program), write_to_file=True)


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
        PYresult[1] += '\n' + ' ' * 4 * PYresult[0]
        CPPresult += '\n' + ' ' * 4 * (PYresult[0] + 1)
        program = program[1:]
        if len(program) == 0:
            break
    CPPresult += 'return 0;\n}'
    if file != None:
        with open(f'{file}.py', 'w') as f:
            f.write(PYresult[1])
        with open(f'{file}.cpp', 'w') as f:
            f.write(CPPresult)
