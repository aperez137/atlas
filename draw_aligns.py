import os
import shelve
import matplotlib.pyplot as plt
import numpy as np

def getCatalog(path):

    with shelve.open(path, flag='r') as pod:
        return pod['catalog']


def getData(path, key):

    with shelve.open(path, flag='r') as pod:
        return pod[key]


def makeDirectory(path):

    try:
        os.mkdir(path)
    except OSError as error: 
        print("\tWarning: Output directory already exists, some files may be overwritten!")


def graphicAll(path, filename, content, source):

    if(len(content) == 0):
        print("\tEmpty chart, skipped!")
        return

    magnax = np.array([])
    magnay = np.array([])

    plt.style.use('ggplot')
    plt.figure(figsize=(12.8*4, 9.6*4))
    
    for idx in content:
        
        unit = getData(path=source, key=idx)

        try:
            plt.plot(unit['curve'][:, 0], unit['curve'][:, 1], label=idx)
            magnax = np.concatenate((magnax, unit['curve'][:, 0]))
            magnay = np.concatenate((magnay, unit['curve'][:, 1]))
        except:
            pass

    plt.xlabel("Phase [JD]")
    plt.ylabel("Normalized Flux")
    plt.legend()
    plt.savefig(path + filename)
    plt.close()


def groupPackage(path, targets):

    packages = {}

    for key in targets:

        unit = getData(path=path, key = key)

        if not unit['pgr'] in packages.keys():
            packages[unit['pgr']] = []
        
        packages[unit['pgr']].append(key)
    
    return packages


def export(lcFile, outPath):

    catalog = getCatalog(lcFile)

    pre = groupPackage(path=lcFile, targets=catalog)
    
    print( "\nTotal groups found", len(pre.keys()),"\n" )

    print("\n\tCreating output directory.")
    makeDirectory(path=outPath)
    
    print("\n\tCreating charts.")
    
    for key in pre.keys():
        
        print("\r\t"+key+"...        ", end='')
        graphicAll(path=outPath, filename=key+'.png', content=pre[key], source=lcFile)

    print("\nDone!\n")


def main(args):

    if len(args) == 3:
        
        lcFile  = args[1]
        outPath = args[2]
        
        export(lcFile=lcFile, outPath=outPath)

    else:
        print('\tPlease use: python draw_aligns.py [Path to aligned light curves file] [Path to output directory] ')
        print('\tExample: python compare.py /home/user/align_120.bin /home/user/charts/')


if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))