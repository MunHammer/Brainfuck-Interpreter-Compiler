#!/usr/bin/env python3
import FileMan
import Interpreter

if __name__ == '__main__':
    FileMan.dirchoose()
    singleline = ''
    chosenfile = FileMan.filechoose()
    with open(chosenfile) as file:
        for line in file:
            singleline += line
    if input('Do you want to compile?\n- ')[0].upper() == 'Y':
        Interpreter.Compile(singleline, chosenfile[:-3])
    else:
        Interpreter.Interpret(singleline)
