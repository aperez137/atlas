import os
import shelve
import numpy as np
import similaritymeasures as sm
from multiprocessing import Process


def addCustoMark(path, post, custom):

    base = os.path.splitext(path)
    return base[0] + post + custom


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

    try:
        with open(output+".a.tmp", mode='r') as tmp:
            buffer += tmp.read()
        os.remove(output+".a.tmp")
    except:
        pass
    
    try:
        with open(output+".b.tmp", mode='r') as tmp:
            buffer += tmp.read()
        os.remove(output+".b.tmp")
    except:
        pass

    try:
        with open(output+".c.tmp", mode='r') as tmp:
            buffer += tmp.read()
        os.remove(output+".c.tmp")
    except:
        pass

    try:
        with open(output+".d.tmp", mode='r') as tmp:
            buffer += tmp.read()
        os.remove(output+".d.tmp")
    except:
        pass
    
    buffer  = buffer.split("\n")
    
    areaArr = []

    catalog = []
    db = {}
    for i in range(len(buffer)):

        tmp   = buffer[i].split(',')

        if(len(tmp) == 4):
        
            key = tmp[1]

            if  not (key in catalog):
                catalog.append(key)
                db[key] = {'pgr': tmp[0], 'id': key, 'vector': []}
            
            area = float(tmp[3])

            if(tmp[0] != 'NULL'):
                areaArr.append(area)

            sub = {'id': tmp[2], 'area': area}
            db[key]['vector'].append(sub)

    with shelve.open(output) as pod:
        pod['catalog'] = catalog

        for key in catalog:
            pod[key] = db[key]
    
    areaArr = np.array(areaArr)

    descriptors = {}
    descriptors['Min Area ']= np.min(areaArr)
    descriptors['Max Area ']= np.max(areaArr)
    descriptors['Avg Area ']= np.mean(areaArr)

    return descriptors


def do(match, targets, origin, output):
    
    print("\tStart", match)

    idx = targets.index(match)
    del(targets[idx])

    total = len(targets)

    external = getData(path=origin, target=match)
    pivot = external['curve']

    buffer = []

    i = 0
    
    while(i < total):

        internal = getData(path=origin, target=targets[i])
        case = internal['curve']

        if external['pgr'] != 'NULL':
            area = sm.area_between_two_curves(pivot, case) * 100
        else:
            area = -1

        buffer.append(external['pgr']+","+match+","+targets[i]+","+str(area))

        if(len(buffer) == 100):
            persist(output, buffer)
            buffer = []

        i = i + 1
    
    if(len(buffer) > 0):
        persist(output, buffer)

    print("\tReady", match)


def produce(match, targets, origin, output):

    do(match, targets, origin, output)


def groupPackage(path, targets):

    packages = {}

    for key in targets:

        unit = getData(path=path, target=key)

        if not unit['pgr'] in packages.keys():
            packages[unit['pgr']] = []
        
        packages[unit['pgr']].append(key)
    
    return packages


def dispatch(path, targets, output, start_at=0):

    grpTargets = groupPackage(path=path, targets=targets)

    print("\n", len(grpTargets.keys()), "alignment groups have been found in the file.\n")

    for gKey in grpTargets:

        print("\nProcessing elements for the group:", gKey, "\n")

        targets = grpTargets[gKey]

        fraction = targets[:]

        skip_counter = 0

        while len(fraction) > 0:
            
            if skip_counter >= start_at:
                limit = len(fraction)
                
                print(limit, "IN QUEUE FOR PREGROUP ", gKey)
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
                
                if 'p1' in locals():
                    p1.join()
                
                if 'p2' in locals():
                    p2.join()
                
                if 'p3' in locals():
                    p3.join()
                
                if 'p4' in locals():
                    p4.join()

                print("Ready Block\n\n")

            else:

                print(fraction[:4], "Skiped!")

            fraction = fraction[4:]
            skip_counter += 1
        
        print("\tDone!")

    print("\nCreating Pod File...")
    descriptors = createPod(output=output)
    print("\nDone!.")

    print("\nSummary:")
    for key in descriptors:
        print("\t", key, descriptors[key])
    print("\n")


def main(args):

    if len(args) == 2:
        
        path = args[1]
        output = addCustoMark(path=path, post='', custom='.pod')

        with shelve.open(path, flag='r') as db:

            catalog = db['catalog']
            
        dispatch(path=path, targets=catalog, output=output)

    else:
        print('\tPlease use: python similarity.py [Path to aligned summary light curves file]')
        print('\tExample: python similarity.py /home/user/summary_align.bin')


if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))
