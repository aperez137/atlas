import os
import shelve
import numpy as np
import similaritymeasures as sm
from multiprocessing import Process

def persist(path, data):

    data = "\n".join(data)

    with open(path, mode='a') as f:
        f.write(data+"\n")


def getData(path, target):

    with shelve.open(path, flag='r') as db:
        data = db[target]
        return data


def getTargets(path):
    
    with shelve.open(path, flag='r') as db:
        targets = db['catalog']
        return targets

def createPod(output):

    buffer = ''

    with open(output+".a.tmp", mode='r') as tmp:
        buffer += tmp.read()
    os.remove(output+".a.tmp")
    
    with open(output+".b.tmp", mode='r') as tmp:
        buffer += tmp.read()
    os.remove(output+".b.tmp")

    with open(output+".c.tmp", mode='r') as tmp:
        buffer += tmp.read()
    os.remove(output+".c.tmp")

    with open(output+".d.tmp", mode='r') as tmp:
        buffer += tmp.read()
    os.remove(output+".d.tmp")
    
    buffer  = buffer.split("\n")
    
    catalog = []
    db = {}
    for i in range(len(buffer)):

        tmp   = buffer[i].split(',')

        if(len(tmp) == 4):
        
            key = tmp[0]

            if  not (key in catalog):
                catalog.append(key)
                db[key] = {'id': key, 'vector': []}
            
            sub = {'id': tmp[1], 'cl': float(tmp[2]), 'pcm': float(tmp[3])}
            db[key]['vector'].append(sub)

    with shelve.open(output) as pod:
        pod['catalog'] = catalog

        for key in catalog:
            pod[key] = db[key]


def makeFormat(curve_1):

    x = curve_1[0]
    y = curve_1[1]
    exp_data = np.zeros((len(x), 2))
    exp_data[:, 0] = x
    exp_data[:, 1] = y

    return exp_data


def do(match, targets, output, curves):
    
    print("\tStart", match)

    idx = targets.index(match)
    del(targets[idx])

    total = len(targets)

    pivot = curves[match]
    pkgPivot = makeFormat(pivot)

    buffer = []

    i = 0
    
    while(i < total):

        case = curves[targets[i]]
        pkgCase = makeFormat(case)

        cl = sm.curve_length_measure(pkgPivot, pkgCase)
        pcm = sm.pcm(pkgPivot, pkgCase)
        
        buffer.append(match+","+targets[i]+","+str(cl)+","+str(pcm))

        if(len(buffer) == 100):
            persist(output, buffer)
            buffer = []

        i = i + 1
    
    if(len(buffer) > 0):
        persist(output, buffer)

    print("\tReady", match)


def produce(match, targets, output, curves):

    do(match, targets, output, curves)


def dispatch(path, targets, curves):

    fraction = targets[:]

    while len(fraction) > 0:
        
        limit = len(fraction)
        
        print(limit, "IN QUEUE")
        print("Start Block")
        
        if(limit >= 1):
            p1 = Process(target=produce, args=(fraction[0], targets, path + "super.pod.a.tmp", curves))
            p1.start()
        
        if(limit >= 2):
            p2 = Process(target=produce, args=(fraction[1], targets, path + "super.pod.b.tmp", curves))
            p2.start()
        
        if(limit >= 3):
            p3 = Process(target=produce, args=(fraction[2], targets, path + "super.pod.c.tmp", curves))
            p3.start()
        
        if(limit >= 4):
            p4 = Process(target=produce, args=(fraction[3], targets, path + "super.pod.d.tmp", curves))
            p4.start()

        if p1:
            p1.join()
        
        if p2:
            p2.join()
        
        if p3:
            p3.join()
        
        if p4:
            p4.join()

        print("Ready Block\n\n")

        fraction = fraction[4:]
    
    print("\nCreating Pod File...")
    createPod(output= path + 'super.pod')
    print("\nDone!.\n")

def reduceCurves(path, targets, result):

    total = len(targets)

    i = 0
    while(i < total):
        
        unit = getData(path=path, target=targets[i])
        curve = unit['curve']
        
        limit = len(curve[0])
        
        x = [curve[0][0]]
        y = [curve[1][0]]
        
        k = 0
        j = 1
        relevant = 0.0001

        while(j < limit):
            
            difX = abs(curve[0][j] - curve[0][k])
            difY = abs(curve[1][j] - curve[1][k])
            
            if not (difX +  difY) <= relevant:
                x.append(curve[0][j])
                y.append(curve[1][j])
                k = j

            j += 1

        i += 1
        actual = len(x)
        result[unit['id']] = (x, y)
        print("\t", unit['id'], "Initial", limit, "Actual", actual, "Reduce", limit - actual)


def main(args):

    if len(args) == 2:
        
        path = args[1]
    

        with shelve.open(path + 'summary.bin', flag='r') as db:

            package = db['catalog']
        
        print("\nSimplify curves.\n")
        simplify = {}
        reduceCurves(path=path + 'summary.bin', targets=package, result=simplify)
        print("\n")
        dispatch(path=path, targets=package, curves=simplify)

    else:
        print('\tPlease use: python super_similarity.py [Path to directory containing summary.bin file]')
        print('\tExample: python super_similarity.py /home/user/out/')


if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))
