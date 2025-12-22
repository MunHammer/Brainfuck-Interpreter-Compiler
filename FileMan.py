#!/usr/bin/env python3
import os
import colorama
from colorama import Fore, Style

colorama.init()

def dirchoose():
    os.walk
    while True:
        os.system('clear')
        print(f'{Style.BRIGHT}{Fore.RESET}Input the path to the file.\n' \
              f'your current path is: {Fore.CYAN}{os.getcwd()}\n')
        print(f'{Fore.RED}Guide to changing cwd\n' \
            '.. - Exits a folder\n' \
            'folder_name - Enters the folder\n' \
            'nothing - Indicate that you\'re satisfied & would like to go to the next step.\n\n' \
            f'{Fore.WHITE}Folders in this directory:{Fore.CYAN}')
        for folder in next(os.walk('.'))[1]:
            print(folder)
        if len(next(os.walk('.'))[1]) == 0:
            print('There are no more folders to enter, please go to the next step or exit this directory using ..')
        dir = input(f'{Fore.GREEN}- ')
        if dir != '':
            os.chdir(dir)
        else:
            break
    print(f'{Fore.WHITE}{Style.RESET_ALL}')
    os.system('clear')

def filechoose():
    while True:
        print(f'{Fore.WHITE}{Style.BRIGHT}Choose a file.{Fore.CYAN}')
        os.system('ls -p | grep -v /')
        file = input(f'{Fore.GREEN}- ')
        path = os.getcwd()
        final = f'{path}/{file}'
        if os.path.exists(final) and len(file) > 0:
            print(f'{Fore.WHITE}{Style.RESET_ALL}')
            return final
        else:
            os.system('clear')
            print(final)
            print(f"{Fore.RED}That file doesn't exist, try again")
        print(f'{Fore.WHITE}{Style.RESET_ALL}')