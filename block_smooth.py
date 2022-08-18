import shelve
import numpy as np
import time


def store(path, key, unit):

    with shelve.open(path) as db:
        db[key]  = unit


def toNpArray(dx, dy):

    cx = []
    cy = []

    q = len(dx)
    
    for i in range(q):
        cx.append(dx[i])
        cy.append(dy[i])
    
    return [np.array(cx), np.array(cy)]


def smoothGauss(curve, wing_factor):

    time = curve[0]
    n = len(time)
    signal = curve[1]

    absRate = n
    rateFactor = 1/3                                
    wingFactor = float(wing_factor) / 100           
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
    
    return [cropTime, cropSmoth]


def scaleX(curve):

    targetMaxX = np.max( curve[0] )
    targetMinX = np.min( curve[0] )
    ampX = targetMaxX - targetMinX
    facAmpX = 1 / ampX
    filtScale = curve[0] * facAmpX
    targetMinX = np.min( filtScale )
    dif = 0 - targetMinX
    filtScale = filtScale + dif

    return [filtScale, curve[1]]


def scaleY(curve):

    targetMaxY = np.max( curve[1] )
    targetMinY = np.min( curve[1] )
    ampY = targetMaxY - targetMinY
    facAmpY = 1 / ampY
    filtScale = curve[1] * facAmpY
    targetMinY = np.min( filtScale )
    dif = 0 - targetMinY
    filtScale = filtScale + dif

    return [curve[0], filtScale]


def getData(path, target):

    with shelve.open(path, flag='r') as db:
        data = db[target]
        return data


def getTargets(path):
    
    with shelve.open(path, flag='r') as db:
        targets = db['catalog']
        return targets


def do(path, wingfactor):

    savePath = path+"_smooth"

    start = time.time()
    print("Get star identifiers from file...")
    targets = getTargets(path)
    print("\t Total identifiers:", len(targets))
    print("Time: ", time.time() - start)

    for t in targets:
        
        start = time.time()
        
        print("\nProcessing star:", t)
        
        midTime = time.time()
        print("\tGet the data from file...")
        data = getData(path, target=t)
        print("\tTime: ", time.time() - midTime)
        
        midTime = time.time()
        print("\tCreate [X, Y] Arrays...")
        tmp = toNpArray(data['curve'][0], data['curve'][1])
        print("\tTime: ", time.time() - midTime)
        
        midTime = time.time()
        print("\tApply Gauss Kernel...")
        tmp = smoothGauss(tmp, wing_factor=wingfactor)
        print("\tTime: ", time.time() - midTime)
        
        midTime = time.time()
        print("\tScale X asxis...")
        tmp = scaleX(tmp)
        print("\tTime: ", time.time() - midTime)
        
        midTime = time.time()
        print("\tScale Y asxis...")
        tmp = scaleY(tmp)
        print("\tTime: ", time.time() - midTime)
        
        midTime = time.time()
        print("\tSave to file...")
        data['curve'] = tmp
        store(savePath, key=t, unit=data)
        print("\tTime: ", time.time() - midTime)

        print("Total Time: ", time.time() - start,"\n")
    
    store(savePath, key='catalog', unit=targets)


def main(args):

    init_time = time.time()

    if(len(args) >= 2):
        do(args[1], args[2])
    else:
        print("Please use python block_smooth.py [path] [wingfactor %]")

    print("\n\t>>", "ALL TIME:", time.time()-init_time,"<<\n\n")

    return 0


if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))