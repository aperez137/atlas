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

        if(len(tmp) == 6):
        
            key = tmp[2]

            if  not (key in catalog):
                catalog.append(key)
                db[key] = {'type': tmp[0], 'id': key, 'vector': []}
            
            sub = {'type': tmp[1], 'id': tmp[3], 'cl': float(tmp[4]), 'pcm': float(tmp[5])}
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


def do(match, targets, origin, output):
    
    print("\tStart", match)

    idx = targets.index(match)
    del(targets[idx])

    total = len(targets)

    external = getData(path=origin, target=match)
    pivot = external['curve']
    pkgPivot = makeFormat(pivot)

    buffer = []

    i = 0
    
    while(i < total):

        internal = getData(path=origin, target=targets[i])
        case = internal['curve']
        pkgCase = makeFormat(case)

        cl = sm.curve_length_measure(pkgPivot, pkgCase)
        pcm = sm.pcm(pkgPivot, pkgCase)
        
        buffer.append(external['type']+","+internal['type']+","+match+","+targets[i]+","+str(cl)+","+str(pcm))

        if(len(buffer) == 100):
            persist(output, buffer)
            buffer = []

        i = i + 1
    
    if(len(buffer) > 0):
        persist(output, buffer)

    print("\tReady", match)


def produce(match, targets, origin, output):

    do(match, targets, origin, output)


def dispatch(path, targets, output, start_at=0):

    fraction = targets[:]

    skip_counter = 0

    while len(fraction) > 0:
        
        if skip_counter >= start_at:
            limit = len(fraction)
            
            print(limit, "IN QUEUE")
            print("Start Block")
            
            if(limit >= 1):
                p1 = Process(target=produce, args=(fraction[0], targets, path, output+".a.tmp"))
                p1.start()
            
            if(limit >= 2):
                p2 = Process(target=produce, args=(fraction[1], targets, path, output+".b.tmp"))
                p2.start()
            
            if(limit >= 3):
                p3 = Process(target=produce, args=(fraction[2], targets, path, output+".c.tmp"))
                p3.start()
            
            if(limit >= 4):
                p4 = Process(target=produce, args=(fraction[3], targets, path, output+".d.tmp"))
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

        else:

            print(fraction[:4], "Skiped!")

        fraction = fraction[4:]
        skip_counter += 1

    print("\nCreating Pod File...")
    createPod(output=output)
    print("\nDone!.\n")

def main(args):

    if len(args) == 4:
        
        path = args[1]
        output = args[3]

        wanteds = args[2].split(',')
        package = []

        with shelve.open(path, flag='r') as db:

            catalog = db['catalog']
            for c in catalog:
                e = db[c]

                for w in wanteds:
                    if w in e['type']:
                        package.append(c)
                        break
        
        dispatch(path=path, targets=package, output=output)

    else:
        print('\tPlease use: python similarity.py [Path to smooth light curves file] ["Types of stars to consider"] [Path to output file]')
        print('\tExample: python similarity.py /home/user/block_better_120_smooth_10.bin "DCEP,HADS,RR,TTS" /home/user/set.pod')


if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))
