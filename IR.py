#!/usr/bin/env python3
import re
from numpy import base_repr

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


def IR(program: str, rmcomments: bool = True) -> str:
    result = ''
    program = re.sub(r'[^+-.><\]\[#]', '', program)
    program = re.sub(r'\[\]', '', program)
    if len(program) == 0:
        raise Exception(
            'Program is either entirely comments, or you ran it through Byte() twice')
    if rmcomments:
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
    while True:
        match program[0]:
            case '[':
                length = len(re.search(r'^[\[]+', program).group())
                result += f's{base_repr(length, 36)}'
                program = program[length - 1:]
            case ']':
                length = len(re.search(r'^[\]]+', program).group())
                result += f'e{base_repr(length, 36)}'
                program = program[length - 1:]
            case '.':
                length = len(re.search(r'^[.]+', program).group())
                result += f'o{base_repr(length, 36)}'
                program = program[length - 1:]
            case ',':
                length = len(re.search(r'^[,]+', program).group())
                result += f'o-{base_repr(length, 36)}'
                program = program[length - 1:]
            case '+':
                length = len(re.search(r'^[+]+', program).group())
                result += f'i{base_repr(length, 36)}'
                program = program[length - 1:]
            case '-':
                length = len(re.search(r'^[-]+', program).group())
                result += f'i-{base_repr(length, 36)}'
                program = program[length - 1:]
            case '>':
                length = len(re.search(r'^[>]+', program).group())
                result += f'm{base_repr(length, 36)}'
                program = program[length - 1:]
            case '<':
                length = len(re.search(r'^[<]+', program).group())
                result += f'm-{base_repr(length, 36)}'
                program = program[length - 1:]
            case '#':
                result += 'd1'
        program = program[1:]
        if len(program) == 0:
            break
    return result


def Pair(program: str) -> list:
    out = []
    while True:
        code = [program[0], re.search('[^a-z]+', program[1:]).group(), 36]
        out.append([code[0], int(code[1], 36)])
        program = program[len(code[1]) + 1:]
        if len(program) < 2:
            break
    return out


def OptimizePairsP1(program: list) -> list:
    pos = 0
    while True:
        if pos > len(program) - 2:
            break
        if program[pos][0] == program[pos + 1][0]:
            program[pos][1] += program[pos + 1][1]
            program.pop(pos + 1)
        else:
            pos += 1
    pos = 0
    while True:
        if program[pos][1] == 0:
            program.pop(pos)
        else:
            pos += 1
        if pos > len(program) - 1:
            break
    return program


def OptimizePairsP2(program: list) -> list:
    return program


def OptimizePairs(program: list) -> list:
    return OptimizePairsP2(OptimizePairsP1(program))


def full_IR(program: str, rmcomments: bool = True) -> list:
    return OptimizePairs(Pair(IR(program, rmcomments=rmcomments)))
