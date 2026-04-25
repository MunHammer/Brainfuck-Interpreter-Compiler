#!/usr/bin/env python3
import re
from numpy import base_repr
from typing import Tuple
import logging

logger = logging.getLogger(__name__)
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


class Pair:
    def __init__(self, type: str, num: int):
        self.type = type
        self.num = num


def IR(program: str, rmcomments: bool = True, input: str = "") -> str:
    result = ""
    program = re.sub(r"[^+-.><\]\[#]", "", program)
    program = re.sub(r"\[\]", "", program)
    if len(program) == 0:
        raise Exception(
            "Program is either entirely comments, or you ran it through Byte() twice"
        )
    if rmcomments:
        while program[0] == "[":  # removes standard opening comments
            depth = 1
            while True:
                program = program[1:]
                if len(program) == 0:
                    raise Exception("Program is 100% comments")
                if program[0] == "]":
                    depth -= 1
                elif program[0] == "[":
                    depth += 1
                if depth == 0:
                    program = program[1:]
                    break
    while True:
        match program[0]:
            case "[":
                result += "s"
            case "]":
                result += "e"
            case ".":
                result += "o"
            case ",":
                result += "o-"
            case "+":
                result += "i"
            case "-":
                result += "i-"
            case ">":
                result += "m"
            case "<":
                result += "m-"
            case "#":
                result += "d1"
            case _:
                pass
        length = re.search(f"^[\\{program[0]}]+", program)
        if length is None:
            logger.debug(program)
            raise Exception(
                "You may have changed the code in some way or run it in a version where it does not work"
            )
        length = len(length.group())
        result += str(base_repr(length, 36))
        program = program[length:]
        if len(program) == 0:
            break
    return result + f"!{input}"


def Pairstr(program: str) -> Tuple[list[Pair], str]:
    out: list[Pair] = []
    while True:
        if program[0] == "!":
            break
        code = re.search("[^a-z!]+", program[1:])
        if code is None:
            logger.debug(program)
            break
        length = len(code.group())
        code = Pair(program[0], int(code.group(), 36))
        out.append(code)
        program = program[length + 1 :]
    return out, program[1:]


def OptimizePairsP1(arg: Tuple[list[Pair], str]) -> Tuple[list[Pair], str]:
    pos = 0
    program = arg[0]
    while True:
        if pos > len(program) - 2:
            break
        if program[pos].type == program[pos + 1].type:
            program[pos].num = program[pos + 1].num
            program.pop(pos + 1)
        else:
            pos += 1
    pos = 0
    while True:
        if program[pos].num == 0:
            program.pop(pos)
        else:
            pos += 1
        if pos > len(program) - 1:
            break
    return program, arg[1]


def OptimizePairsP2(arg: Tuple[list[Pair], str]) -> Tuple[list[Pair], str]:
    logger.debug("Pairs")
    for thing in arg[0]:
        logger.debug(f"{thing.type} {thing.num}")
    program = arg[0]
    tape = [0] * 30000
    ptr: int = 0
    loops: list[int] = []
    depth = 0
    pos: int = 0
    out: list[Pair] = []
    distance: int = 0
    while True:
        if ptr > distance:
            distance = ptr
        code = program[pos]
        if depth > 0:
            if code.type == "s":
                depth += code.num
            elif code.type == "e":
                depth -= code.num
            pos += 1
            if pos > len(program) - 1:
                raise Exception('Unmatched "["')
            continue
        elif depth < 0:
            raise Exception('Unmatched "]"')
        match code.type:
            case "s":
                if tape[ptr] != 0:
                    loops.append(pos)
                else:
                    depth = 1
            case "e":
                if tape[ptr] != 0:
                    try:
                        pos = loops[-1]
                    except IndexError:
                        raise Exception('unmatched "]"')
                else:
                    loops.pop()
            case "o" | "d":
                break
            case "i":
                tape[ptr] += code.num
                while tape[ptr] > 255:
                    tape[ptr] -= 256
                while tape[ptr] < 0:
                    tape[ptr] += 256
            case "m":
                ptr += code.num
                if ptr >= 30000:
                    raise Exception("Only 30,000 cells available")
                if ptr < 0:
                    raise Exception("No negative cells available")
            case "d":
                pass
            case _:
                logger.debug(code.type)
                raise Exception("Invalid IR")
        pos += 1
        if pos > len(program) - 1:
            break
    for cellnum in range(distance):
        if tape[cellnum] != 0:
            out.append(Pair("i", tape[cellnum]))
        out.append(Pair("m", 1))
    out.extend(program[pos:])
    return out, arg[1]


def OptimizePairs(program: Tuple[list[Pair], str]) -> Tuple[list[Pair], str]:
    return OptimizePairsP1(OptimizePairsP2(OptimizePairsP1(program)))


def full_IR(program: str, rmcomments: bool = True) -> Tuple[list[Pair], str]:
    return OptimizePairs(Pairstr(IR(program, rmcomments=rmcomments)))
