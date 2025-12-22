#!/usr/bin/env python3
import FileMan
import Interpreter-Compiler as Run

if __name__ == '__main__':
    FileMan.dirchoose()
    singleline = ''
    chosenfile = FileMan.filechoose()
    with open(chosenfile) as file:
        for line in file:
            singleline += line
    if input('Do you want to compile?\n- ')[0].upper() == 'Y':
        Run.Compile(singleline, chosenfile[:-3])
    else:
        Run.Interpret(singleline)
