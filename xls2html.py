#!/usr/bin/env python

import os
from xlsx2html import xlsx2html

def addCustoMark(path, post, custom):

    base = os.path.splitext(path)
    return base[0] + post + custom

def getFileName(path):

    _, tail = os.path.split(path)
    return tail


def convert(path):

    rpath = addCustoMark(path=path, post='', custom='.html')
    xlsx2html(path, rpath)


def main(args):

    if len(args) == 2:
        
        path = args[1]
        convert(path=path)

    else:
        print('\tPlease use: python xls2html.py [Path to XLSX file]')
        print('\tExample: python xls2html.py /home/user/data.xlsx')


if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))