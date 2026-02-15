#!/usr/bin/env python3
import sys
import IR
import re

# code description     char
# V     V         /------J
# [ loop start  s1
# ] loop end    e <base 36 num>
# . output      o <base 36 num>
# , input       o-<base 36 num>
# + increment   i <base 36 num>
# - decrement   i-<base 36 num>
# > move right  m <base 36 num>
# < move left   m-<base 36 num>
# # debug       d1


<<<<<<< HEAD
def Interpret(program: list[IR.Pair], give: bool = False) -> str:
    tape = [0]*30000
    ptr = 0
    output = ''
    pos: int = 0
    loops: list[int] = []
    depth = 0
    distance: int = 0
=======
def Interpret(program: list, give: bool = False) -> str | None:
    tape = [0]*30000
    ptr = 0
    output = ''
    pos = 0
    loops = []
    depth = 0
    distance = 0
>>>>>>> 5050f2239228a59f5b2cb61258247a2bbb5569d7
    while True:
        if ptr > distance:
            distance = ptr
        code = program[pos]
        if depth > 0:
<<<<<<< HEAD
            if code.type == 's':
                depth += code.num
            elif code.type == 'e':
                depth -= code.num
=======
            if code[0] == 's':
                depth += code[1]
            elif code[0] == 'e':
                depth -= code[1]
>>>>>>> 5050f2239228a59f5b2cb61258247a2bbb5569d7
            pos += 1
            if pos > len(program) - 1:
                raise Exception('Unmatched "["')
            continue
        elif depth < 0:
            raise Exception('Unmatched "]"')
<<<<<<< HEAD
        match code.type:
=======
        match code[0]:
>>>>>>> 5050f2239228a59f5b2cb61258247a2bbb5569d7
            case 's':
                if tape[ptr] != 0:
                    loops.append(pos)
                else:
                    depth = 1
            case 'e':
                if tape[ptr] != 0:
                    try:
                        pos = loops[-1]
                    except:
                        raise Exception('unmatched "]"')
                else:
                    loops.pop()
            case 'o':
<<<<<<< HEAD
                if code.num < 0:
=======
                if code[1] < 0:
>>>>>>> 5050f2239228a59f5b2cb61258247a2bbb5569d7
                    put = input('_\U00000008')
                    tape[ptr] = ord(put[0])
                    print(end=f'\033[F{" " * len(put)}' +
                          "\U00000008" * len(put))
                elif give:
<<<<<<< HEAD
                    output += chr(tape[ptr]) * code.num
                else:
                    print(end=chr(tape[ptr]) * code.num)
            case 'i':
                tape[ptr] += code.num
=======
                    output += chr(tape[ptr]) * code[1]
                else:
                    print(end=chr(tape[ptr]) * code[1])
            case 'i':
                tape[ptr] += code[1]
>>>>>>> 5050f2239228a59f5b2cb61258247a2bbb5569d7
                while tape[ptr] > 255:
                    tape[ptr] -= 256
                while tape[ptr] < 0:
                    tape[ptr] += 256
            case 'm':
<<<<<<< HEAD
                ptr += code.num
=======
                ptr += code[1]
>>>>>>> 5050f2239228a59f5b2cb61258247a2bbb5569d7
                if ptr >= 30000:
                    raise Exception('Only 30,000 cells available')
                if ptr < 0:
                    raise Exception('No negative cells available')
            case 'd':
                output += f'\nDebug info: at {ptr}\n{tape[:distance + 1]}\n'
            case _:
                raise Exception('Invalid IR')
        pos += 1
        if pos > len(program) - 1:
            break
<<<<<<< HEAD
    return output
=======
    if give:
        return output
    else:
        return None
>>>>>>> 5050f2239228a59f5b2cb61258247a2bbb5569d7


def run_Interpret(program: str) -> str:
    return Interpret(IR.full_IR(program), give=True)


<<<<<<< HEAD
=======
def debug_Interpret(program: str) -> str:
    return Interpret(IR.full_IR(program), write_to_file=True)


>>>>>>> 5050f2239228a59f5b2cb61258247a2bbb5569d7
def repl():
    tape = [0]*30000
    ptr = 0
    depth = 0
    distance = 0
    print(
        f'Brainfuck 1 (main, Dec 23 2025) [Python 3.11.2+] on {sys.platform}')
    print('Type "help" for more information')
    while True:
        run = input('>>> ')
        if run[:4] == 'exit':
            sys.exit(0)
        elif run[:5] == 'clear':
            ptr = 0
            distance = 0
            tape = [0]*30000
            continue
        elif run[:4] == 'help':
            print('')
<<<<<<< HEAD
        while len(re.findall(r'\[', run)) > len(re.findall(r'\]', run)):
            run += input('... ')
        run = IR.full_IR(run, rmcomments=False)
        pos: int = 0
        loops: list[int] = []
=======
        while len(re.findall('\[', run)) > len(re.findall('\]', run)):
            run += input('... ')
        run = IR.full_IR(run, rmcomments=False)
        pos = 0
        loops = []
>>>>>>> 5050f2239228a59f5b2cb61258247a2bbb5569d7
        output = ''
        while True:
            if ptr > distance:
                distance = ptr
            code = run[pos]
            if depth > 0:
<<<<<<< HEAD
                if code.type == 's':
                    depth += code.num
                elif code.type == 'e':
                    depth -= code.num
=======
                if code[0] == 's':
                    depth += code[1]
                elif code[0] == 'e':
                    depth -= code[1]
>>>>>>> 5050f2239228a59f5b2cb61258247a2bbb5569d7
                pos += 1
                if pos > len(run) - 1:
                    raise Exception('Unmatched "["')
                continue
            elif depth < 0:
                raise Exception('Unmatched "]"')
<<<<<<< HEAD
            match code.type:
=======
            match code[0]:
>>>>>>> 5050f2239228a59f5b2cb61258247a2bbb5569d7
                case 's':
                    if tape[ptr] != 0:
                        loops.append(pos)
                    else:
                        depth = 1
                case 'e':
                    if tape[ptr] != 0:
                        try:
                            pos = loops[-1]
                        except:
                            raise Exception('unmatched "]"')
                    else:
                        loops.pop()
                case 'o':
<<<<<<< HEAD
                    if code.num < 0:
=======
                    if code[1] < 0:
>>>>>>> 5050f2239228a59f5b2cb61258247a2bbb5569d7
                        put = input('_\U00000008')
                        tape[ptr] = ord(put[0])
                        print(end=f'\033[F{" " * len(put)}' +
                              "\U00000008" * len(put))
                    else:
<<<<<<< HEAD
                        output += chr(tape[ptr]) * code.num
                case 'i':
                    tape[ptr] += code.num
=======
                        output += chr(tape[ptr]) * code[1]
                case 'i':
                    tape[ptr] += code[1]
>>>>>>> 5050f2239228a59f5b2cb61258247a2bbb5569d7
                    while tape[ptr] > 255:
                        tape[ptr] -= 256
                    while tape[ptr] < 0:
                        tape[ptr] += 256
                case 'm':
<<<<<<< HEAD
                    ptr += code.num
=======
                    ptr += code[1]
>>>>>>> 5050f2239228a59f5b2cb61258247a2bbb5569d7
                    if ptr >= 30000:
                        raise Exception('Only 30,000 cells available')
                    if ptr < 0:
                        raise Exception('No negative cells available')
                case 'd':
                    output += f'\nDebug info: at {ptr}\n' \
                        f'{tape[:distance + 1]}\n'
                case _:
                    raise Exception('Invalid IR')
            pos += 1
            if pos > len(run) - 1:
                break
        if len(output) > 0:
            print(output)


if __name__ == '__main__':
    if len(sys.argv) == 1:
        repl()
<<<<<<< HEAD
        sys.exit(0)
    elif sys.argv[1][-2:] == '.b' or sys.argv[1][-3:] == '.bf':
        with open(sys.argv[1]) as file:
            programstr: str = ''
            for line in file:
                programstr += line
    else:
        programstr = sys.argv[1]
    print('Encoding & optimising program...')
    program = IR.full_IR(programstr)
=======
    elif sys.argv[1][-2:] == '.b' or sys.argv[1][-3:] == '.bf':
        with open(sys.argv[1]) as file:
            program = ''
            for line in file:
                program += line
    else:
        program = sys.argv[1]
    print('Encoding & optimising program...')
    program = IR.full_IR(program)
>>>>>>> 5050f2239228a59f5b2cb61258247a2bbb5569d7
    print(f'Interpreting program...')
    if len(sys.argv) < 3:
        print('Your file outputted:')
        Interpret(program)
        print()
    else:
        with open(sys.argv[2], 'w') as file:
            file.write(Interpret(program))
        print(f'Output written to {sys.argv[2]}')
