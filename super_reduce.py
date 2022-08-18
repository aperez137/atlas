import os
import shelve
import numpy as np


def addCustoMark(path, post, custom):

    base = os.path.splitext(path)
    return base[0] + post + custom


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


def reduceCurves(path, relevantFactor, maxJump):

    persist_path = addCustoMark(path, '_reduce', '.bin')
    
    targets = getTargets(path=path)
    readyCurves = []
    
    total = len(targets)
    relevant = 1.0 / (10 ** relevantFactor)
    cutter   = maxJump
    cutCruves = []

    i = 0
    while(i < total):
        
        
        unit = getData(path=path, target=targets[i])
        curve = unit['curve']
        
        limit = len(curve[0])
        
        x = [curve[0][0]]
        y = [curve[1][0]]
        
        k = 0
        j = 1

        isCut = False

        while(j < limit):
            
            difX = abs(curve[0][j] - curve[0][k])
            difY = abs(curve[1][j] - curve[1][k])
            distance = difX +  difY
            step = abs(curve[0][j] - curve[0][j-1])

            if distance >= relevant:

                if(step <= cutter):
                    x.append(curve[0][j])
                    y.append(curve[1][j])
                    k = j
                else:
                    isCut = True
                    break

            j += 1

        i += 1

        if isCut:
            cutCruves.append(unit['id']+"\t"+str(distance))
            print("\t", i, '/', total, unit['id'], "The curve is not continuous, it is removed from the set.")

        else:
            actual = len(x)
            unit['curve'] = (np.array(x), np.array(y))
            reduction = ( (limit - actual) / limit) * 100
            readyCurves.append(unit['id'])
            setData(path=persist_path, target=unit['id'], data=unit)
            
            print("\t", i, '/', total, unit['id'], "Initial", limit, "Actual", actual, "Reduce", format(reduction, ".2f"), "%")
        
    if(len(cutCruves) > 0):
        
        logPath = addCustoMark(path, '_removes', '.log')

        print("\n"+str(len(cutCruves))+" curves have been eliminated, since they do not respect the continuity threshold: [", cutter, "].")
        print("\tFull list on file:", logPath)
        
        with open(logPath, mode='w') as log:
            
            log.writelines("Maximum jump allowed on the X axis: "+str(cutter)+"\n")

            for cc in cutCruves:
                log.writelines(cc+"\n")
    
    setData(path=persist_path, target='catalog', data=readyCurves)

    print("\nDone!\n")

def main(args):

    if len(args) == 4:
        
        path = args[1]
        factor = int(args[2])
        jump   = float(args[3])
    
        reduceCurves(path=path, relevantFactor=factor, maxJump=jump)

    else:
        print('\tPlease use: python super_reduce.py [Path to summary.bin file] [Min Relevant] [Max Jump]')
        print('\tExample: python super_reduce.py /home/user/out/summary.bin 4 0.025')


if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))