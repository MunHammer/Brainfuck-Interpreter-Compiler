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


class Compiler:
    def __init__(self, *, indent: bool = True,
                 autosemicolon: bool = False, autonewline: bool = True):
        self.__autoindent = indent
        self.__semicolon = autosemicolon
        self.__newline = autonewline
        self.__opening = ''
        self.__closing = {}
        self.__indent = 0
        self.__commands = {'[': None, ']': None, '.': None,
                           ',': None, '+': None, '-': None,
                           '>': None, '<': None, '#': None,
                           'check': None}

    def get_opening(self) -> str:
        return self.__opening

    def add_opening(self, compiled: str, *, semicolon: bool = True,
                    newline: bool = True, autoindent: bool = True,
                    add_indent: int = 0):
        '''change the booleans if there are exceptions to
        rules in the opening'''
        self.__opening += compiled
        self.__indent += add_indent
        if self.__semicolon and semicolon:
            self.__opening += ';'
        if self.__newline and newline:
            self.__opening += '\n'
        if self.__autoindent and autoindent:
            self.__opening += '    ' * self.__indent

    def get_closing(self) -> dict:
        return self.__closing

    def add_closing(self, compiled: str, *, semicolon: bool = True,
                    newline: bool = True, autoindent: bool = True,
                    add_indent: int = 0):
        '''change the booleans if there are exceptions to
        rules in the closing'''
        self.__closing[compiled] = {'semicolon': semicolon, 'newline': newline,
                                    'autoindent': autoindent,
                                    'add_indent': add_indent}

    def __eval_closing(self, string: str, options: dict):
        if self.__autoindent and options['autoindent']:
            self.result += '    ' * self.__indent
        self.__indent += options['add_indent']
        self.result += string
        if self.__newline and options['newline']:
            self.result += '\n'

    def add_command(self, command: str, compiled: str, *,
                    overwrite: bool = False):
        '''For a command such as + that can be repeated quite easily,
        you must use: {Num} to produce more optimised code'''
        match command:
            case '[' if self.__commands['['] is None or overwrite:
                self.__commands['['] = compiled
            case ']' if self.__commands[']'] is None or overwrite:
                self.__commands[']'] = compiled
            case '.' if self.__commands['.'] is None or overwrite:
                self.__commands['.'] = compiled
            case ',' if self.__commands[','] is None or overwrite:
                self.__commands[','] = compiled
            case '+' if self.__commands['+'] is None or overwrite:
                self.__commands['+'] = compiled
            case '-' if self.__commands['-'] is None or overwrite:
                self.__commands['-'] = compiled
            case '>' if self.__commands['>'] is None or overwrite:
                self.__commands['>'] = compiled
            case '<' if self.__commands['<'] is None or overwrite:
                self.__commands['<'] = compiled
            case '#' if self.__commands['#'] is None or overwrite:
                self.__commands['#'] = compiled
            case 'check' if self.__commands['check'] is None or overwrite:
                self.__commands['check'] = compiled
            case _:
                raise ValueError('Class method: add_command() requires '
                                 'a valid command to be entered or you '
                                 'entered a command that has already been'
                                 ' created, if so, please use use the '
                                 'overwrite flag if that was intentional')

    def __check_add(self):
        if self.__semicolon:
            self.result += ';'
        if self.__newline:
            self.result += '\n'
        if self.__autoindent:
            self.result += ' ' * 4 * self.__indent
        self.result += self.__commands['check']

    def run(self, bytecode: str, debug: bool = False):
        if len(bytecode) % 8 != 0:
            raise ValueError('Must be bytecode inputted')
        self.bytecode = bytecode
        self.result = self.__opening
        for command in self.__commands:
            if self.__commands[command] == None:
                raise ValueError('All commands must be added\n'
                                 f'Missing command: {command}')
        while True:
            self.curbyte = int(self.bytecode[:8], 2)
            if self.curbyte == 0:
                self.result += self.__commands['[']
                self.__indent += 1
            elif self.curbyte == 1:
                self.result += self.__commands[']']
                self.__indent -= 1
            elif self.curbyte == 2:
                self.result += self.__commands['.']
            elif self.curbyte == 3:
                self.result += self.__commands[',']
            elif self.curbyte in range(4, 67):
                self.result += self.__commands['+'].format(
                    Num=f'{self.curbyte - 3}')
                self.__check_add()
            elif self.curbyte in range(67, 130):
                self.result += self.__commands['-'].format(
                    Num=f'{self.curbyte - 66}')
                self.__check_add()
            elif self.curbyte in range(130, 193):
                self.result += self.__commands['>'].format(
                    Num=f'{self.curbyte - 129}')
                self.__check_add()
            elif self.curbyte in range(193, 255):
                self.result += self.__commands['<'].format(
                    Num=f'{self.curbyte - 192}')
                self.__check_add()
            elif self.curbyte == 255:
                self.result += self.__commands['#']
            self.bytecode = self.bytecode[8:]
            if self.__semicolon:
                self.result += ';'
            if self.__newline:
                self.result += '\n'
            if self.__autoindent:
                self.result += ' ' * 4 * self.__indent
            if len(self.bytecode) < 8:
                break
            if debug:
                # yield self.result
                print(self.result)
        for closing in self.__closing:
            self.__eval_closing(closing, self.__closing[closing])
        return self.result


def makeCPP():
    CPPcompiler = Compiler(autosemicolon=True)
    CPPcompiler.add_opening('#include <iostream>',
                            semicolon=False)
    CPPcompiler.add_opening('#include <stdexcept>',
                            semicolon=False)
    CPPcompiler.add_opening('using namespace std')
    CPPcompiler.add_opening('int check(int ptr, int cell) {',
                            add_indent=1, semicolon=False)
    CPPcompiler.add_opening('if (ptr < 0 or ptr > 30000) {',
                            add_indent=1, semicolon=False)
    CPPcompiler.add_opening('throw out_of_range("No negative cells or cells '
                            '> 30,''000 exist")', add_indent=-1)
    CPPcompiler.add_opening('}',
                            semicolon=False)
    CPPcompiler.add_opening('while (cell > 255) {',
                            add_indent=1, semicolon=False)
    CPPcompiler.add_opening('cell -= 256', add_indent=-1)
    CPPcompiler.add_opening('}',
                            semicolon=False)
    CPPcompiler.add_opening('while (cell < 0) {',
                            add_indent=1, semicolon=False)
    CPPcompiler.add_opening('cell += 256', add_indent=-1)
    CPPcompiler.add_opening('}',
                            semicolon=False)
    CPPcompiler.add_opening('return cell', add_indent=-1)
    CPPcompiler.add_opening('}',
                            semicolon=False)
    CPPcompiler.add_opening('int main {',
                            semicolon=False, add_indent=1)
    CPPcompiler.add_opening('int tape[30000]={0}')
    CPPcompiler.add_opening('int ptr = 0')

    CPPcompiler.add_command('[', compiled='while (tape[ptr] != 0) {')
    CPPcompiler.add_command(']', compiled='}')
    CPPcompiler.add_command('.', compiled='cout << char(tape[ptr])')
    CPPcompiler.add_command(',', compiled='cin >> tape[ptr]')
    CPPcompiler.add_command('+', compiled='tape[ptr] += {Num}')
    CPPcompiler.add_command('-', compiled='tape[ptr] -= {Num}')
    CPPcompiler.add_command('>', compiled='ptr += {Num}')
    CPPcompiler.add_command('<', compiled='ptr += {Num}')
    CPPcompiler.add_command('#', compiled='cout << tape')
    CPPcompiler.add_command(
        'check', compiled='tape[ptr] = check(ptr, tape[ptr])')

    CPPcompiler.add_closing('return 0', add_indent=-1)
    CPPcompiler.add_closing('}', semicolon=False)
    return CPPcompiler


def makePY():
    PYcompiler = Compiler()
    PYcompiler.add_opening('tape = [0]*30000')
    PYcompiler.add_opening('ptr = 0')
    PYcompiler.add_opening('def check():', add_indent=1)
    PYcompiler.add_opening('if ptr > 30000 or < 0:', add_indent=1)
    PYcompiler.add_opening('raise Exception("No memory adresses exist '
                           'beyond 0 & 30,000")', add_indent=-1)
    PYcompiler.add_opening('if tape[ptr] > 255:', add_indent=1)
    PYcompiler.add_opening('tape[ptr] -= 256', add_indent=-1)
    PYcompiler.add_opening('elif tape[ptr] < 0:', add_indent=1)
    PYcompiler.add_opening('tape[ptr] += 256', add_indent=-2)

    PYcompiler.add_command('[', 'while tape[ptr] != 0:')
    PYcompiler.add_command(']', '')
    PYcompiler.add_command('.', 'print(chr(tape[ptr]))')
    PYcompiler.add_command(',', 'tape[ptr] = ord(input()[0])')
    PYcompiler.add_command('+', 'tape[ptr] += {Num}')
    PYcompiler.add_command('-', 'tape[ptr] -= {Num}')
    PYcompiler.add_command('>', 'ptr -= {Num}')
    PYcompiler.add_command('<', 'ptr += {Num}')
    PYcompiler.add_command('#', 'print(tape)')
    PYcompiler.add_command('check', 'check()')
    return PYcompiler


if __name__ == '__main__':
    CPPcompiler = makeCPP()
    PYcompiler = makePY()
    print(CPPcompiler.run(Byte('+++++')))
    print('-' * 10 + 'Same code in python:')
    print(PYcompiler.run(Byte('+++++')))
