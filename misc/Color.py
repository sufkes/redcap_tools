# This is a class that is used for printing colored text in Mac and Linux using ANSI escape codes. These do not work in Windows, so the script first checks the operating system.

import os

class Color:
   if (os.name == 'posix'): # If operating system looks like Mac or Linux.
        bold = '\033[1m'
        underline = '\033[4m'

        blue = '\033[94m'
        red ='\033[31m'
        green ='\033[32m'
        end = '\033[0m'
    
        Red = '\033[91m'
        Green = '\033[92m'
        Blue = '\033[94m'
        Cyan = '\033[96m'
        White = '\033[97m'
        Yellow = '\033[93m'
        Magenta = '\033[95m'
        Grey = '\033[90m'
        Black = '\033[90m'
   else:
        bold = ''
        blue = ''
        red =''
        green =''
        end = ''

        Red = ''
        Green = ''
        Blue = ''
        Cyan = ''
        White = ''
        Yellow = ''
        Magenta = ''
        Grey = ''
        Black = ''
