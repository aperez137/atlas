import os
import shelve
import matplotlib.pyplot as plt
import numpy as np

def smooth(curve):

    time = curve[0]
    n = len(time)
    signal = curve[1]
    absRate = n

    rateFactor = 1/3  
    wingFactor = 0.025
    fwhm       = int(wingFactor * absRate)
    k          = 2 * fwhm

    sigRate   = int(absRate * rateFactor)
    gauss_time = absRate * np.arange(-k,k) / sigRate
    gauss_win  = np.exp( -( 4 * np.log(2) * gauss_time ** 2 ) / ( fwhm ** 2 ) )

    filtSig_Gauss = np.zeros(n)

    left_wing  = k+1
    right_wing = -k-1

    for i in range(left_wing, n+right_wing):
        filtSig_Gauss[i] = np.sum( signal[i-k:i+k]*gauss_win )
    
    cropTime = time[left_wing: right_wing]
    cropSmoth = filtSig_Gauss[left_wing: right_wing]

    targetMaxY = np.max( cropSmoth )
    targetMinY = np.min( cropSmoth )
    ampY = targetMaxY - targetMinY
    facAmpY = 1 / ampY
    filtScale = cropSmoth * facAmpY
    targetMinY = np.min( filtScale )
    dif = 0 - targetMinY
    filtScale = filtScale + dif

    targetMaxX = np.max( cropTime )
    targetMinX = np.min( cropTime )
    ampX = targetMaxX - targetMinX
    facAmpX = 1 / ampX
    timeScale = cropTime * facAmpX
    targetMinX = np.min( timeScale )
    dif = 0 - targetMinX
    timeScale = timeScale + dif

    return(timeScale, filtScale)


def getCatalog(path):

    with shelve.open(path, flag='r') as pod:
        return pod['catalog']


def getData(path, key):

    with shelve.open(path, flag='r') as pod:
        return pod[key]


def sortCl(vector):

    vector = sorted(vector, key= lambda element: element['cl'])
    return vector


def sortPcm(vector):
    
    vector = sorted(vector, key= lambda element: element['pcm'])
    return vector


def isMatch(cl, pcm, element):

    return (element['cl'] <= cl) and (element['pcm'] <= pcm)


def searchInGroups(groups, key):

    for gkey in groups.keys():

        if key in groups[gkey]:
            return gkey


def makeDirectory(path):

    try:
        os.mkdir(path)
    except OSError as error: 
        print("\tWarning: Output directory already exists, some files may be overwritten!")


def writeFileTable(path, filename, content):

    if(len(content) == 0):
        print("\tEmpty file, skipped!")
        return

    with open(path + filename, mode='w') as wf:
        
        headers     = list(content[0].keys())
        txtHeader   = ','.join(headers)
        wf.writelines(txtHeader + "\n")

        for line in content:
            
            txtLine = list(line.values())
            txtLine = [ str(cell) for cell in txtLine]
            txtLine = ','.join(txtLine)
            wf.writelines(txtLine + "\n")


def writeFileSummary(path, filename, content):

    with open(path + filename, mode='w') as wf:
        
        for key in content.keys():

            txtLine = []
            txtLine.append(key)
            txtLine.append(str(content[key]))
            txtLine = ','.join(txtLine)
            wf.writelines(txtLine + "\n")


def graphicAll(path, filename, content, source):

    if(len(content) == 0):
        print("\tEmpty chart, skipped!")
        return

    magnax = np.array([])
    magnay = np.array([])

    plt.style.use('ggplot')
    plt.figure(figsize=(12.8*2, 9.6*2))
    
    for line in content:
        idx = line['id']
        unit = getData(source, idx)

        plt.plot(unit['curve'][0], unit['curve'][1])
        magnax = np.concatenate((magnax, unit['curve'][0]))
        magnay = np.concatenate((magnay, unit['curve'][1]))

    plt.xlabel("Phase [JD]")
    plt.ylabel("Normalized Flux")
    plt.savefig(path + filename)
    plt.close()

    xindexer = magnax.argsort()
    sorted_magnax = magnax[xindexer[::-1]]
    sorted_magnay = magnay[xindexer[::-1]]

    return (sorted_magnax, sorted_magnay)


def graphicSmooth(path, filename, noise):

    plt.style.use('ggplot')
    plt.figure(figsize=(12.8*2, 9.6*2))
    
    scur = smooth(curve=noise)
    plt.plot(scur[0], scur[1])

    plt.xlabel("Phase [JD]")
    plt.ylabel("Normalized Flux")
    plt.title("Smooth Curve")
    plt.savefig(path + filename)
    plt.close()

    return scur


def compare(podFile, lcFile, clLimit, pcmLimit, outPath):

    print("\nStarting element grouping...")

    catalog = getCatalog(podFile)
    pgr = {}

    collect = []
    nulos   = []
    repeat  = []

    for key in catalog:
        
        if not(key in collect):
            
            pgr[key] = []
            unit = getData(podFile, key)
            
            for ele in unit['vector']:

                    if isMatch(cl=clLimit, pcm=pcmLimit, element=ele):
                        pgr[key].append(ele)

                        if not (ele['id'] in collect):
                            collect.append(ele['id'])
                        else:
                            if not (ele['id'] in repeat):
                                repeat.append(ele['id'])
            
            if len(pgr[key]) > 0:
                pgr[key].append({'id':key, 'cl': 0, 'pcm': 0})
                collect.append(key)
            else:
                del(pgr[key])
                nulos.append({'id':key, 'cl': 0, 'pcm': 0})


    total = 0

    for key in pgr.keys():
        
        count = len(pgr[key])
        
        total += count

    print('\nUnmatched Elements', "\t", len(nulos))
    print('Matched Elements', "\t", len(collect))
    print('Repeated Elements', "\t", len(repeat))
    print('Elements In Catalog', "\t", len(catalog))
    print('Total Grouped Elements', "\t", total, "\n")

    print("Removing repeated elements...")

    totrep = 0
    for rep in repeat:
        
        tgroup = []

        for key in pgr.keys():
            exist = next((x for x in pgr[key] if x["id"] == rep), False)
            
            if(exist):
                tgroup.append({'id': key, 'factor': exist['cl'] * exist['pcm'] })

        tgroup = sorted(tgroup, key=lambda t: t['factor'])

        totrep += (len(tgroup)-1)

        for vic in tgroup[1:]:
            exist = next(x for x in pgr[ vic['id'] ] if x["id"] == rep)
            pgr[ vic['id'] ].remove(exist)

    alone = []
    aloneKeys = []
    totGr = 0

    for key in pgr.keys():
        
        count = len(pgr[key])
        
        if(count == 1):
            aloneKeys.append(key)
            alone.append(pgr[key][0])
        else:
            totGr += count
    
    for key in aloneKeys:
        del(pgr[key])

    print("\nRepeats Removed", "\t", totrep)
    print("Alone Elements", "\t\t", len(alone))
    print("Elements Grouped Effectively", "\t", totGr, "\n")

    print("\nCreating output directory.")
    makeDirectory(path=outPath)
    
    print("\nCreating summary file.")
    sumaryDic = {}
    sumaryDic['Pod File']    = podFile
    sumaryDic['Lc File']     = lcFile
    sumaryDic['Cl Limit']    = clLimit
    sumaryDic['Pcm Limit']   = pcmLimit
    sumaryDic['Unmatched Elements'] = len(nulos)
    sumaryDic['Matched Elements'] = len(collect)
    sumaryDic['Repeated Elements'] = len(repeat)
    sumaryDic['Elements In Catalog'] =  len(catalog)
    sumaryDic['Total Grouped Elements'] = total
    sumaryDic["Repeats Removed"] = totrep
    sumaryDic["Alone Elements"] = len(alone)
    sumaryDic["Elements Grouped Effectively"] = totGr
    writeFileSummary(path=outPath, filename='summary.csv', content=sumaryDic)

    print("\nCreating file of unmatched elements.")
    writeFileTable(path=outPath, filename='unmatched.csv', content=nulos)
    
    print("\nCreating file of alone elements.")
    writeFileTable(path=outPath, filename='alone.csv', content=alone)

    print("\nCreating files for the found groups.")
    cntf = 0
    for key in pgr.keys():
        cntf += 1
        writeFileTable(path=outPath, filename='group_'+key+'.csv', content=pgr[key])
    print("\tHas been created:", cntf, "Group Files!")
    
    print("\nCreating charts.")
    cntg = 0
    
    for key in pgr.keys():
        
        cntg += 1
        
        print("\r\tAll  G"+str(cntg)+": "+key+"...        ", end='')
        noise = graphicAll(path=outPath, filename='all_'+key+'.png', content=pgr[key], source=lcFile)
        
        if(noise):
            
            print("\r\tSmooth  G"+str(cntg)+": "+key+"...      ", end='')
            graphicSmooth(path=outPath, filename='smooth_'+key+'.png', noise=noise)
    
    print("\r\tUnmatched chart...                            ", end='')
    graphicAll(path=outPath, filename='unmatched.png', content=nulos, source=lcFile)
    
    print("\r\tAlone chart...                            ", end='')
    graphicAll(path=outPath, filename='alone.png', content=alone, source=lcFile)
    print("\r\tCharts ready!.                           ", end='')

    print("\nDone!\n")


def main(args):

    if len(args) == 4:
        
        lcFile  = args[1] + "summary.bin"
        podFile = args[1] + "super.pod"
        outPath = args[1] + "super/"
        cl      = int(args[2])
        pcm     = int(args[3])

        compare(podFile=podFile, lcFile=lcFile, clLimit=cl, pcmLimit=pcm, outPath=outPath)

    else:
        print('\tPlease use: python super_compare.py [Path to directory containing summary.bin and super.pod files] [Max CL] [Max PCM]')
        print('\tExample: python super_compare.py /home/user/out/ 100 1000')


if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))