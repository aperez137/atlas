import shelve
import numpy as np
from scipy import signal

def getData(path, target):

    with shelve.open(path, flag='r') as db:
        data = db[target]
        return data


def getTargets(path):
    
    with shelve.open(path, flag='r') as db:
        targets = db['catalog']
        return targets


def findMiddle(array):
    
    size = len(array)
    pos = int( size / 2)

    if size % 2 == 0:
        pos -= 1
    
    return pos


def preGroup(path, package, prominence, bucket):

    for key in package:
        
        unit = getData(path=path, target=key)
        curve = unit['curve']

        sec = np.array(curve[1])
        peaks_idx, _    = signal.find_peaks(sec, prominence=prominence)
        valley_idx, _   = signal.find_peaks(-sec, prominence=prominence)

        joined = np.concatenate((peaks_idx, valley_idx))
        joined = np.sort(joined)

        marker = ''
        for pick in joined:
            if pick in peaks_idx:
                marker += 'P'
            else:
                marker += 'V'
        
        if marker == '':
            marker = 'NULL'

        if marker in bucket.keys():
            bucket[marker].append({'id': key, 'inflection': joined})
        else:
            bucket[marker] = [{'id': key, 'inflection': joined}]


def moveCurves(path, bucket):

    valid_keys = list(bucket.keys())

    if 'NULL' in valid_keys:
        valid_keys.remove('NULL')

    bucket['LIMITS'] = {}

    for grp in valid_keys:

        raid = bucket[grp]

        pivot = raid[0]
        
        idx = findMiddle(array=pivot['inflection'])
        stab = pivot['inflection'][idx]
        
        stabCurve = getData(path=path, target=pivot['id'])['curve']
        tx = np.array(stabCurve[0])
        ty = np.array(stabCurve[1])

        stabx = tx[stab]

        left = tx[0]
        right = tx[-1]

        bucket[grp][0]['curve'] = (tx, ty)

        limit = len(raid)
        i = 1

        while i < limit:
            c = raid[i]
            curve = getData(path=path, target=c['id'])['curve']

            spot = c['inflection'][idx]
            
            spotx = curve[0][spot]

            toMove = spotx - stabx
            
            sx = np.array(curve[0]) - toMove
            sy = np.array(curve[1])

            if sx[0] > left:
                left = sx[0]
            
            if sx[-1] < right:
                right = sx[-1]

            bucket[grp][i]['curve'] = (sx, sy)

            i += 1
        
        bucket['LIMITS'][grp] = (left, right) 


def cutCurves(bucket):

    valid_keys = list(bucket.keys())

    if 'NULL' in valid_keys:
        valid_keys.remove('NULL')

    valid_keys.remove('LIMITS')

    for grp in valid_keys:

        grplimits = bucket['LIMITS'][grp]

        for i in range(len(bucket[grp])):

            ax = bucket[grp][i]['curve'][0]
            ay = bucket[grp][i]['curve'][1]

            ix = np.where(np.logical_and(ax >=grplimits[0], ax<=grplimits[1]))
            lx = np.min(ix)
            rx = np.max(ix)

            ax = ax[lx: rx+1]
            ay = ay[lx: rx+1]

            cur = np.zeros((len( ax ), 2))
            cur[:, 0] = ax
            cur[:, 1] = ay
            
            bucket[grp][i]['curve'] = cur


def createFile(origin, output, bucket):

    with shelve.open(origin, flag='r') as ori:
        
        with shelve.open(output) as des:

            catalog = []

            valid_keys = list(bucket.keys())

            valid_keys.remove('LIMITS')

            groupCounter = 0

            for grp in valid_keys:

                raid = bucket[grp]
                total = len(raid)

                if total > 1 and grp != 'NULL':
                    groupCounter += 1
                    gMark = 'G_'+str(groupCounter)
                else:
                    gMark = 'NULL'

                for element in raid:

                    catalog.append(element['id'])
                    
                    unit = ori[element['id']]
                    unit['pgr'] = gMark
                    
                    if 'curve' in element.keys():
                        unit['curve'] = element['curve']
                    
                    des[element['id']] = unit
            
            des['catalog'] = catalog




def align(path, targets, prominence, output):

    bucket = {}

    print("\nCreating preliminary groups based on inflection points...")
    preGroup(path=path, package=targets, prominence=prominence, bucket=bucket)
    print("\tDone!")

    print("\nAligning curves by inflection points...")
    moveCurves(path=path, bucket=bucket)
    print("\tDone!")
    
    print("\nTrimming curves to optimal range...")
    cutCurves(bucket=bucket)
    print("\tDone!")

    print("\nCreating output file...")
    createFile(origin=path, output=output, bucket=bucket)
    print("\tDone!\n")

def main(args):

    if len(args) == 5:
        
        path = args[1]
        output = args[3]
        prominence = float(args[4])

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
        
        align(path=path, targets=package, prominence=prominence, output=output)

    else:
        print('\tPlease use: python align.py [Path to smooth light curves file] ["Types of stars to consider"] [Path to output file] [Min Prominence]')
        print('\tExample: python align.py /home/user/block_better_120_smooth_10.bin "DCEP,HADS,RR,TTS" /home/user/align.bin 0.2')


if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))