import os
import shelve
import numpy as np

def addPostMark(path, post):

    base = os.path.splitext(path)
    return base[0] + post + base[1]


def getTargets(path):
    
    with shelve.open(path, flag='r') as db:
        targets = db['catalog']
        return targets


def getData(path, target):

    with shelve.open(path, flag='r') as db:
        data = db[target]
        return data

def setData(path, target, data):

    with shelve.open(path) as db:
        db[target] = data


def reduceCurves(path, factor):

    persist_path = addPostMark(path, '_reduce_' + str(factor) )
    
    targets = getTargets(path)
    
    setData(path=persist_path, target='catalog', data=targets)

    total = len(targets)
    relevant = 1.0 / (10 ** factor)

    i = 0
    while(i < total):
        
        
        unit = getData(path=path, target=targets[i])
        curve = unit['curve']
        
        limit = len(curve[0])
        
        x = [curve[0][0]]
        y = [curve[1][0]]
        
        k = 0
        j = 1

        while(j < limit):
            
            difX = abs(curve[0][j] - curve[0][k])
            difY = abs(curve[1][j] - curve[1][k])
            
            if not (difX +  difY) <= relevant:
                x.append(curve[0][j])
                y.append(curve[1][j])
                k = j

            j += 1

        actual = len(x)
        unit['curve'] = (np.array(x), np.array(y))
        reduction = ( (limit - actual) / limit) * 100
        setData(path=persist_path, target=targets[i], data=unit)
        i += 1
        print("\t", i, '/', total, unit['target'], "Initial", limit, "Actual", actual, "Reduce", format(reduction, ".2f"), "%")


def main(args):

    if len(args) == 3:
        
        path = args[1]
        factor = int(args[2])
    
        
        reduceCurves(path=path, factor=factor)

    else:
        print('\tPlease use: python reduce.py [Path to smooth curve file] [Reduction Limit]')
        print('\tExample: python reduce.py /home/user/block_better_120_smooth_10.bin 4')


if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))