import shelve
import numpy as np

def getData(path, target):

    with shelve.open(path, flag='r') as db:
        data = db[target]
        return data


def getCatalog(path):
    
    with shelve.open(path, flag='r') as db:
        catalog = db['catalog']
        return catalog


def groupPackage(path, targets):

    packages = {}

    for key in targets:

        unit = getData(path=path, target=key)

        if not unit['pgr'] in packages.keys():
            packages[unit['pgr']] = []
        
        packages[unit['pgr']].append(key)
    
    return packages


def describe(podFile):
    
    catalog = getCatalog(podFile)
    pre = groupPackage(path=podFile, targets=catalog)
    
    gKeys = sorted(pre.keys())

    print( "\n\tTotal groups found", len(pre.keys()),"\n" )

    arrArea = []

    for g in gKeys:

        if g != 'NULL':
            raid = pre[g]
            print("\t"+g+":\t", len(raid), "elements.")
            tmp = []
            for e in raid:
                unit = getData(path=podFile, target=e)

                for v in unit['vector']:
                    tmp.append(v['area'])
            
            arrArea = arrArea + tmp
            print("\tMin Area:", np.min(tmp), "Max Area:", np.max(tmp), "Avg Area:", np.mean(tmp),"\n")
        else:
            print("\tNull Elements:", len(raid))
        
    print("\n\tTotal Min Area:", np.min(arrArea))
    print("\tTotal Max Area:", np.max(arrArea))
    print("\tTotal Avg Area:", np.mean(arrArea),"\n")


def main(args):

    if len(args) == 2:
        
        podFile = args[1]
        describe(podFile=podFile)

    else:
        print('\tPlease use: python describe.py [Path to pod file]')
        print('\tExample: python describe.py /home/user/star_120.pod')


if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))