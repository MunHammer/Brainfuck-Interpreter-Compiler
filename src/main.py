#!/usr/bin/env python3
import BFCompiler
import IR
import sys
import argparse
import pathlib
import logging

logger = logging.getLogger(__name__)

def main():
    parser = argparse.ArgumentParser(
        prog='BFTranspiler',
        description="A brainfuck transpiler that supports a number of targets",
        suggest_on_error = True,
        color = True,
        )
    parser.add_argument("input", type=pathlib.Path, help="File to read from")
    parser.add_argument("-t", "--target", nargs="?", choices=["py", "c", "cpp", "rust"], default="py", help="Target language to transpile to")
    parser.add_argument("-o", "--output", nargs="?", type=pathlib.Path, help="File to write output to", default="a.out")
    parser.add_argument("-v", "--verbose", action="count", default=0, help="Increases verbosity up to a level of two")
    args = parser.parse_args()
    try:
        logging.basicConfig(level=[logging.WARNING, logging.INFO, logging.DEBUG][args.verbose])
    except IndexError:
        logging.basicConfig(level=logging.DEBUG)
        logger.warning("Maximum verbosity is two, verbosity set to two")
    logger.info("Assembling transpiler")
    print("Compiling...")
    match args.target:
        case "py":
            transpiler = BFCompiler.makePY()
        case "c":
            # TODO: add C
            raise ValueError("TODO: add C")
        case "cpp":
            transpiler = BFCompiler.makeCPP()
        case "rust":
            transpiler = BFCompiler.makeRust()
        case _:
            raise ValueError("language does not exist")
    logger.info("Reading input file")
    with open(args.input, "r") as file:
        program = file.read()
    logger.info("Encoding & optimising program")
    program = IR.full_IR(program)
    logger.info("Compiling program")
    OUTPUT = transpiler.run(program)
    with open(args.output, "w") as file:
        file.write(OUTPUT)
    print("Compilation completed!")

if __name__ == '__main__':
    main()
    sys.exit(0)
