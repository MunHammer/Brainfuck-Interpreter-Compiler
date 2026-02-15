#!/usr/bin/env python3
import IR
import sys
from typing import Tuple

# code description     char
# V     V         /------J
# [ loop start  s <base 36 num>
# ] loop end    e <base 36 num>
# . output      o <base 36 num>
# , input       o-<base 36 num>
# + increment   i <base 36 num>
# - decrement   i-<base 36 num>
# > move right  m <base 36 num>
# < move left   m-<base 36 num>
# # debug       d1


class Compiler:
    def __init__(self, *, autoindent: bool = True, indent: int = 0,
                 autosemicolon: bool = False, autonewline: bool = True):
        self.__autoindent = autoindent
        self.__semicolon = autosemicolon
        self.__newline = autonewline
        self.__opening = ''
        self.__closing: dict[str, dict[str, int]] = {}
        self.__indent = indent
        self.__commands: dict[str, str] = {'[': '', ']': '', '.': '',
                                           ',': '', 'increment': '',
                                           'move': '', '#': '',
                                           'addcheck': '', 'movecheck': ''}
    def get_opening(self) -> str:
        return self.__opening

    def add_opening(self, compiled: str, *, semicolon: bool = True,
                    newline: bool = True, indent: int = 0):
        '''change the booleans if there are exceptions to
        rules in the opening'''
        self.__opening += '    ' * indent
        self.__opening += compiled
        if self.__semicolon and semicolon:
            self.__opening += ';'
        if self.__newline and newline:
            self.__opening += '\n'

    def get_closing(self) -> dict[str, dict[str, int]]:
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
                    overwrite: bool = False, autosemicolon: bool = True):
        '''For a command such as + that can be repeated quite easily,
        you must use: {Num} to produce more optimised code'''
        match command:
            case '[' if self.__commands['['] == '' or overwrite:
                self.__commands['['] = compiled
            case ']' if self.__commands[']'] == '' or overwrite:
                self.__commands[']'] = compiled
            case '.' if self.__commands['.'] == '' or overwrite:
                self.__commands['.'] = compiled
            case ',' if self.__commands[','] == '' or overwrite:
                self.__commands[','] = compiled
            case 'increment' if (self.__commands['increment'] == ''
                                 or overwrite):
                self.__commands['increment'] = compiled
            case 'move' if self.__commands['move'] == '' or overwrite:
                self.__commands['move'] = compiled
            case '#' if self.__commands['#'] == '' or overwrite:
                self.__commands['#'] = compiled
            case 'addcheck' if (self.__commands['addcheck'] == ''
                                or overwrite):
                self.__commands['addcheck'] = compiled
            case 'movecheck' if (self.__commands['movecheck'] == ''
                                 or overwrite):
                self.__commands['movecheck'] = compiled
            case _:
                raise ValueError('Class method: add_command() requires '
                                 'a valid command to be entered or you '
                                 'entered a command that has already been'
                                 ' created, if so, please use use the '
                                 'overwrite flag if that was intentional')
        if autosemicolon and self.__semicolon:
            self.__commands[command] += ';'
        if self.__newline:
            self.__commands[command] += '\n'

    def __check_add(self, command: str):
        if self.__autoindent:
            self.result += ' ' * 4 * self.__indent
        self.result += self.__commands[f'{command}check']
        if self.__newline:
            self.result += '\n'

    def run(self, program: Tuple[list[IR.Pair], str]) -> str:
        code = program[0]
        self.result = self.__opening
        for command in self.__commands:
            if self.__commands[command] == '':
                raise ValueError('All commands must be added\n'
                                 f'Missing command: {command}')
        for command in code:
            if self.__autoindent:
                self.result += '    ' * self.__indent
            match command.type:
                case 's':
                    try:
                        self.result += self.__commands['['].format(
                            Num=command.num)
                        self.__indent += 1
                    except ValueError:
                        for _ in range(command.num):
                            self.result += self.__commands['[']
                            self.__indent += 1
                            if self.__autoindent:
                                self.result += '    ' * self.__indent
                    except IndexError:
                        self.result += self.__commands['[']
                        self.__indent += 1
                case 'e':
                    try:
                        self.__indent -= 1
                        self.result += self.__commands[']'].format(
                            Num=command.num)
                    except ValueError:
                        self.__indent += 1
                        for _ in range(command.num):
                            self.__indent -= 1
                            self.result += self.__commands[']']
                            if self.__autoindent:
                                self.result += '    ' * self.__indent
                    except IndexError:
                        self.__indent -= 1
                        self.result += self.__commands[']']
                case 'o' if command.num > 0:
                    try:
                        self.result += self.__commands['.'].format(
                            Num=command.num)
                    except ValueError:
                        for _ in range(command.num):
                            self.result += self.__commands['.']
                            if self.__autoindent:
                                self.result += '    ' * self.__indent
                    except IndexError:
                        self.result += self.__commands['.']
                case 'o' if command.num < 0:
                    try:
                        self.result += self.__commands[','].format(
                            Num=command.num)
                    except ValueError:
                        for _ in range(command.num):
                            self.result += self.__commands[',']
                            if self.__autoindent:
                                self.result += '    ' * self.__indent
                    except IndexError:
                        self.result += self.__commands[',']
                case 'i':
                    self.result += self.__commands['increment'].format(
                        Num=command.num)
                    self.__check_add('add')
                case 'm':
                    self.result += self.__commands['move'].format(
                        Num=command.num)
                    self.__check_add('move')
                case 'd':
                    self.result += self.__commands['#'].format(Num=command.num)
                case _:
                    raise ValueError('Invalid code')
        for closing in self.__closing:
            self.__eval_closing(closing, self.__closing[closing])
        return self.result


def makeCPP():
    CPPcompiler = Compiler(autosemicolon=True, indent=1)
    CPPcompiler.add_opening('#include <iostream>',
                            semicolon=False)
    CPPcompiler.add_opening('#include <stdexcept>',
                            semicolon=False)
    CPPcompiler.add_opening('using namespace std')
    CPPcompiler.add_opening('void movecheck(int ptr) {',
                            semicolon=False)
    CPPcompiler.add_opening('if (ptr < 0 or ptr > 30000) {',
                            indent=1, semicolon=False)
    CPPcompiler.add_opening('throw out_of_range("No negative cells or cells '
                            '> 30,''000 exist")', indent=2)
    CPPcompiler.add_opening('}',
                            semicolon=False, indent=1)
    CPPcompiler.add_opening('}',
                            semicolon=False)
    CPPcompiler.add_opening('int addcheck(int cell) {',
                            semicolon=False)
    CPPcompiler.add_opening('while (cell > 255) {',
                            indent=1, semicolon=False)
    CPPcompiler.add_opening('cell -= 256',
                            indent=2)
    CPPcompiler.add_opening('}',
                            semicolon=False, indent=1)
    CPPcompiler.add_opening('while (cell < 0) {',
                            indent=1, semicolon=False)
    CPPcompiler.add_opening('cell += 256', indent=2)
    CPPcompiler.add_opening('}',
                            semicolon=False, indent=1)
    CPPcompiler.add_opening('return cell',
                            indent=1)
    CPPcompiler.add_opening('}',
                            semicolon=False)
    CPPcompiler.add_opening('int main() {',
                            semicolon=False)
    CPPcompiler.add_opening('int tape[30000]={0}',
                            indent=1)
    CPPcompiler.add_opening('int ptr = 0',
                            indent=1)

    CPPcompiler.add_command(
        '[', compiled='while (tape[ptr] != 0) {', autosemicolon=False)
    CPPcompiler.add_command(']', compiled='}', autosemicolon=False)
    CPPcompiler.add_command('.', compiled='cout << char(tape[ptr])')
    CPPcompiler.add_command(',', compiled='cin >> tape[ptr]')
    CPPcompiler.add_command('increment', compiled='tape[ptr] += {Num}')
    CPPcompiler.add_command('move', compiled='ptr += {Num}')
    CPPcompiler.add_command('#', compiled='cout << tape')
    CPPcompiler.add_command(
        'addcheck', compiled='tape[ptr] = addcheck(tape[ptr])')
    CPPcompiler.add_command('movecheck', compiled='movecheck(ptr)')

    CPPcompiler.add_closing('return 0;', add_indent=-1)
    CPPcompiler.add_closing('}', semicolon=False)
    return CPPcompiler


def makePY():
    PYcompiler = Compiler()
    PYcompiler.add_opening('#!/usr/bin/env python3')
    PYcompiler.add_opening('tape = [0]*30000')
    PYcompiler.add_opening('ptr = 0')
    PYcompiler.add_opening('def movecheck():')
    PYcompiler.add_opening('if ptr > 30000 or ptr < 0:', indent=1)
    PYcompiler.add_opening('raise Exception("No memory adresses exist '
                           'beyond 0 & 30,000")', indent=2)
    PYcompiler.add_opening('def addcheck():')
    PYcompiler.add_opening('if tape[ptr] > 255:', indent=1)
    PYcompiler.add_opening('tape[ptr] -= 256', indent=2)
    PYcompiler.add_opening('elif tape[ptr] < 0:', indent=1)
    PYcompiler.add_opening('tape[ptr] += 256', indent=2)

    PYcompiler.add_command('[', 'while tape[ptr] != 0:')
    PYcompiler.add_command(']', '')
    PYcompiler.add_command('.', 'print(end=chr(tape[ptr]))')
    PYcompiler.add_command(',', 'tape[ptr] = ord(input()[0])')
    PYcompiler.add_command('increment', 'tape[ptr] += {Num}')
    PYcompiler.add_command('move', 'ptr += {Num}')
    PYcompiler.add_command('#', 'print(tape)')
    PYcompiler.add_command('addcheck', 'addcheck()')
    PYcompiler.add_command('movecheck', 'movecheck()')
    return PYcompiler

def makeRust():
    Rustcompiler = Compiler(autosemicolon=True, indent=1)
    Rustcompiler.add_opening('use std::io::{Read, Write}')
    Rustcompiler.add_opening('fn inp(cell: &mut u8) {', semicolon=False)
    Rustcompiler.add_opening('let mut buf: [u8;1] = [0]', indent=1)
    Rustcompiler.add_opening('std::io::stdin().read_exact(&mut buf).unwrap()', indent=1)
    Rustcompiler.add_opening('*cell = buf[0]', indent=1)
    Rustcompiler.add_opening('}', semicolon=False)
    Rustcompiler.add_opening('fn inc(cell: &mut u8, incrementation: i16) {', semicolon=False)
    Rustcompiler.add_opening('if incrementation < 0 {', indent=1, semicolon=False)
    Rustcompiler.add_opening('*cell = cell.wrapping_sub(incrementation as u8)', indent=2)
    Rustcompiler.add_opening('} else {', indent=1, semicolon=False)
    Rustcompiler.add_opening('*cell = cell.wrapping_add(incrementation as u8)')
    Rustcompiler.add_opening('}', indent=1, semicolon=False)
    Rustcompiler.add_opening('}', semicolon=False)
    Rustcompiler.add_opening('fn main() {', semicolon=False)
    Rustcompiler.add_opening('let mut tape: [u8; 30_000] = [0; 30_000]', indent=1)
    Rustcompiler.add_opening('let mut ptr: usize = 0', indent=1)
    Rustcompiler.add_command('[', 'while tape[ptr] != 0 {', autosemicolon=False)
    Rustcompiler.add_command(']', '}', autosemicolon=False)
    Rustcompiler.add_command('.', 'print!("{}", tape[ptr] as char); std::io::stdout().flush().unwrap()')
    Rustcompiler.add_command(',', 'inp(&mut tape[ptr])')
    Rustcompiler.add_command('increment', 'inc(&mut tape[ptr], {Num})')
    Rustcompiler.add_command('move', 'ptr = ptr.strict_add({Num})')
    Rustcompiler.add_command('#', 'dbg!(tape)')
    Rustcompiler.add_command('addcheck', ' ', autosemicolon=False)
    Rustcompiler.add_command('movecheck', ' ', autosemicolon=False)
    Rustcompiler.add_closing('}', add_indent=-1, semicolon=False)
    return Rustcompiler


if __name__ == '__main__':
    if sys.argv[1].lower() == 'py':
        compiler = makePY()
    elif sys.argv[1].lower() == 'cpp':
        compiler = makeCPP()
    elif sys.argv[1].lower() == 'rust':
        compiler = makeRust()
    else:
        raise ValueError('Language does not exist')
    with open(sys.argv[2]) as file:
        programstr: str = ''
        for line in file:
            programstr += line
    print('Encoding & optimising program...')
    program: list[IR.Pair] = IR.full_IR(programstr)
    print(f'Turning code into a {sys.argv[1]} program')
    programout = compiler.run(program)
    if len(sys.argv) > 3:
        with open(sys.argv[3], 'w') as file:
            file.write(programout)
    else:
        print('Your file outputted:')
        print(program)
    print('\nDone!')
