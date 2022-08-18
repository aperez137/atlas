import os
import shelve
from turtle import color
import matplotlib.pyplot as plt
import numpy as np
from scipy import signal


def printGrafo(grafo):

    for key in grafo:

        print("Nodo", key)
        nodo = grafo[key]

        for arista in nodo:
            print("\t", arista)


def removeOver(grafo, over):

    result = {}

    for key in grafo:

        result[key] = []
        
        nodo = grafo[key]

        for arista in nodo:

            if arista['area'] < over:
                result[key].append(arista)    

    return result


def optimalGroups(grafo, over):

    grafo = removeOver(grafo=grafo, over=over)

    tamNodos = {}

    for key in grafo:

        nodo = grafo[key]
        
        tamNodos[key] = len(nodo)
   
    for key in grafo:

        if tamNodos[key] > 0:

            nodo = grafo[key]
            
            tamNodo = len(nodo)

            for arista in range(tamNodo):
                
                target = nodo[arista]['id']
                siPuede = True

                for posible in tamNodos.keys():
                    
                    tamLocal = tamNodos[posible]

                    if (posible != key) and (tamLocal > 0):

                        needEval = next((True for x in grafo[posible] if x['id'] == target), False)

                        if needEval or (posible == target):
                            puede = tamNodo >= tamLocal
                            siPuede = siPuede and puede

                if siPuede:

                    for posible in tamNodos.keys():
                        
                        tamLocal = tamNodos[posible]

                        if (posible != key) and (tamLocal > 0):
                            
                            grafo[posible] = [ x for x in grafo[posible] if x['id'] != target and x['id'] != key ]
                            tamNodos[posible] = len(grafo[posible])
                
                else:
                    
                    grafo[key] = [ x for x in grafo[key] if x['id'] != target ]
                    tamNodos[key] = len(grafo[key])
                    
            
    grupos = []
    descartados = list(grafo.keys())

    for key in grafo:

        nodo = grafo[key]
        tamNodo = len(nodo)

        if tamNodo > 0:
            
            miembros = [key]
            
            for arista in nodo:
                miembros.append( arista['id'] )

            for miembro in miembros:
                if miembro in descartados:
                    descartados.remove( miembro )
            
            grupos.append(miembros)

    return grupos, descartados


def summarize(curve):

    time = curve[0]
    n = len(time)
    signal = curve[1]
    absRate = n

    rateFactor = 1/10  
    wingFactor = 0.01
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


def antialiasing(noise):

    scur = summarize(curve=noise)

    tam = len(scur[0])
    fur = 5

    while(True):
        
        sy = signal.savgol_filter(scur[1], int(tam / fur), fur)
        
        sy = sy[~np.isnan(sy)]
        sy = sy[np.where(sy>= 0)]

        if(len(sy) == tam):
            break
        else:
            fur -= 1

    return (scur[0], scur[1], sy)


def getCatalog(path):

    with shelve.open(path, flag='r') as pod:
        return pod['catalog']


def getData(path, key):

    with shelve.open(path, flag='r') as pod:
        return pod[key]


def binSummary(path, filename, content):

    with shelve.open(path + filename, flag='c') as summary:
        for key in content.keys():
            summary[key] = content[key]


def sortArea(vector):
    
    vector = sorted(vector, key= lambda element: element['area'])
    return vector


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
        
        needHeader = True

        for group in content:
            
            members = group['members']

            if needHeader:
                headers     = list(members[0].keys())
                txtHeader   = ','.join(headers)
                wf.writelines(txtHeader + "\n")
                needHeader = False

            for member in members:
                
                txtLine = list(member.values())
                txtLine = [ str(cell) for cell in txtLine ]
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
    plt.figure(figsize=(12.8*4, 9.6*4))
    
    for line in content:
        idx = line['id']
        unit = getData(path=source, key=idx)

        try:
            plt.plot(unit['curve'][:, 0], unit['curve'][:, 1], label=idx, linewidth=3)
            magnax = np.concatenate((magnax, unit['curve'][:, 0]))
            magnay = np.concatenate((magnay, unit['curve'][:, 1]))
        except:
            pass

    plt.xlabel("Phase [JD]")
    plt.ylabel("Normalized Flux")
    plt.legend()
    plt.savefig(path + filename)
    plt.close()

    xindexer = magnax.argsort()
    sorted_magnax = magnax[xindexer[::]]
    sorted_magnay = magnay[xindexer[::]]

    return (sorted_magnax, sorted_magnay)


def graphicNoise(path, filename, noise, curve):

    plt.style.use('ggplot')
    plt.figure(figsize=(12.8*2, 9.6*2))
    
    plt.plot(noise[0], noise[1], color='palegreen')
    plt.plot(curve[0], curve[1], color='red', linewidth=3)

    plt.xlabel("Phase [JD]")
    plt.ylabel("Normalized Flux")
    plt.title("Noise Profile")
    plt.savefig(path + 'noise_'+filename)
    plt.close()


def graphicCurve(path, filename, curve):

    plt.style.use('ggplot')
    plt.figure(figsize=(12.8*2, 9.6*2))
    
    plt.plot(curve[0], curve[1], color='purple', linewidth=3)

    plt.xlabel("Phase [JD]")
    plt.ylabel("Normalized Flux")
    plt.title("Smooth Curve")
    plt.savefig(path + 'smooth_'+filename)
    plt.close()


def groupPackage(path, targets):

    packages = {}

    for key in targets:

        unit = getData(path=path, key = key)

        if not unit['pgr'] in packages.keys():
            packages[unit['pgr']] = []
        
        packages[unit['pgr']].append(key)
    
    return packages


def compare(podFile, lcFile, areaLimit, outPath):

    print("\nStarting group filtering...\n")

    catalog = getCatalog(podFile)

    pre = groupPackage(path=podFile, targets=catalog)
    
    pgr = {}
    groupCounter = 1;
    nulos = []

    for key in pre.keys():

        raid = pre[key]

        if key != 'NULL':
        
        
            grafo = {}

            for ele in raid:

                unit = getData(path=podFile, key=ele)
                areaU   = sortArea(unit['vector'])
                
                grafo[ele] = areaU

            grupos, sobrantes = optimalGroups(grafo=grafo, over=areaLimit)
        
        else:
            grupos = []
            sobrantes = raid
        
        for g in grupos:

            pgr['S_'+str(groupCounter)] = []

            for e in g:
                unit = getData(path=lcFile, key=e)
                pgr['S_'+str(groupCounter)].append({'members': unit['members'], 'id':e})

            groupCounter += 1
        
        for s in sobrantes:
            unit = getData(path=lcFile, key=s)
            nulos.append({'members': unit['members'], 'id':s})

    total = 0

    for key in pgr.keys():
        
        count = len(pgr[key])
        
        total += count

    print('Groups In Catalog', "\t", len(catalog))
    print('Unmatched Groups', "\t", len(nulos))
    print('Total Consolidated Groups', "\t", total)
    print('Total Super Groups Created', "\t", len(pgr.keys()), "\n")

    
    print("\nCreating output directory.")
    makeDirectory(path=outPath)
    
    print("\nCreating summary file.")
    sumaryDic = {}
    sumaryDic['Pod File']    = podFile
    sumaryDic['Lc File']     = lcFile
    sumaryDic['Area Limit']  = areaLimit
    sumaryDic['Groups In Catalog'] =  len(catalog)
    sumaryDic['Unmatched Groups'] = len(nulos)
    sumaryDic['Total Consolidated Groups.'] = total
    sumaryDic['Total Super Groups Created'] = len(pgr.keys())
    writeFileSummary(path=outPath, filename='summary.csv', content=sumaryDic)

    print("\nCreating file of unmatched elements.")
    writeFileTable(path=outPath, filename='unmatched.csv', content=nulos)
    
    print("\nCreating files for the found groups.")
    cntf = 0
    for key in pgr.keys():
        cntf += 1
        writeFileTable(path=outPath, filename=key+'.csv', content=pgr[key])
    print("\tHas been created:", cntf, "Group Files!")
    
    print("\nCreating charts.")
    
    summaryBin = {}
    for key in pgr.keys():
        
        print("\r\tAll "+key+"...        ", end='')
        noise = graphicAll(path=outPath, filename='all_'+key+'.png', content=pgr[key], source=lcFile)
        
        if(noise):
            
            paraCurve = antialiasing(noise=noise)
            print("\r\tNoise  "+key+"...      ", end='')
            graphicNoise(path=outPath, filename=key+'.png', noise=(paraCurve[0], paraCurve[1]), curve=(paraCurve[0], paraCurve[2]))

            print("\r\tSmooth "+key+"...      ", end='')
            graphicCurve(path=outPath, filename=key+'.png', curve=(paraCurve[0], paraCurve[2]))
            summaryBin[key] = {'id': key, 'members': pgr[key], 'curve': (paraCurve[0], paraCurve[2])}
    
    print("\r\tUnmatched chart...                            ", end='')
    graphicAll(path=outPath, filename='unmatched.png', content=nulos, source=lcFile)
    
    
    print("\n\nCreating binary summary file.!\n")
    summaryBin['catalog'] = list(pgr.keys())
    binSummary(path=outPath, filename='summary.bin', content=summaryBin)

    print("\nDone!\n")


def main(args):

    if len(args) == 5:
        
        lcFile  = args[1]
        podFile = args[2]
        outPath = args[3]
        area    = float(args[4])

        compare(podFile=podFile, lcFile=lcFile, areaLimit=area, outPath=outPath)

    else:
        print('\tPlease use: python super_compare.py [Path to aligned summary light curves file] [Path to summary pod file] [Path to output directory] [Max Area]')
        print('\tExample: python super_compare.py /home/user/summay_align.bin /home/user/summay_align.pod /home/user/super/ 10')


if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))