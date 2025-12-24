#!/usr/bin/env python3
import BFCompiler
import BFInterpreter
import IR
import sys
if __name__ == '__main__':
    if sys.argv[1].lower() == 'bf':
        if sys.argv[2].lower() == 'compile':
            if sys.argv[3].lower() == 'py':
                compiler = BFCompiler.makePY()
            elif sys.argv[3].lower() == 'cpp':
                compiler = BFCompiler.makeCPP()
            else:
                raise ValueError('Language does not exist')
            with open(sys.argv[4]) as file:
                program = ''
                for line in file:
                    program += line
            print('Encoding & optimising program...')
            program = IR.full_IR(program)
            print(f'Turning code into a {sys.argv[3]} program')
            program = compiler.run(program)
            if len(sys.argv) > 5:
                with open(sys.argv[5], 'w') as file:
                    file.write(program)
            else:
                print('Your file outputted:')
                print(program)
            print('\nDone!')
        elif sys.argv[2].lower() == 'interpret':
            if len(sys.argv) == 3:
                BFInterpreter.repl()
            elif sys.argv[3][-2:] == '.b' or sys.argv[3][-3:] == '.bf':
                with open(sys.argv[3]) as file:
                    program = ''
                    for line in file:
                        program += line
            else:
                program = sys.argv[3]
            print('Encoding & optimising program...')
            program = IR.full_IR(program)
            print(f'Interpreting program...')
            if len(sys.argv) < 5:
                print('Your file outputted:')
                BFInterpreter.Interpret(program)
                print()
            else:
                with open(sys.argv[4], 'w') as file:
                    file.write(BFInterpreter.Interpret(program))
                print(f'Output written to {sys.argv[4]}')
    elif sys.argv[1].lower() == 'bf++':
        print('Not implemented yet')
