#!/usr/bin/env python

import os

HtmlStart = """
<!DOCTYPE html>
<html lang="es">
    <head>
        <meta charset="UTF-8">
        <title>|||</title>
    </head>
    <body>    
"""

HtmlStyle = """
    <style>
        table {
            border-collapse: collapse;
        }

        td {
            border: 1px solid #ccc;
            padding: 2px 10px 2px 10px;
            font-family: monospace, monospace;
        }
    </style>
"""

HtmlEnd = """
    </body>
</html>
"""

def addCustoMark(path, post, custom):

    base = os.path.splitext(path)
    return base[0] + post + custom

def getFileName(path):

    _, tail = os.path.split(path)
    return tail


def convert(path):

    with open(path, mode='r') as f:
        data = f.read()

    doc = HtmlStart + HtmlStyle;
    doc = doc.replace('|||', getFileName(path=path))

    doc += '<table>'

    data = data.split("\n")
    for line in data:
        if line != '':
            
            doc += '<tr>'

            colums = line.split(',')
            for c in colums:
                doc += '<td>'+c+'</td>' 

            doc += '</tr>'

    
    doc += '</table>'
    doc += HtmlEnd
    
    rpath = addCustoMark(path=path, post='', custom='.html')

    with open(rpath, mode='w') as f:
        f.write(doc)


def main(args):

    if len(args) == 2:
        
        path = args[1]
        convert(path=path)

    else:
        print('\tPlease use: python csv2html.py [Path to CSV file]')
        print('\tExample: python csv2html.py /home/user/data.csv')


if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))