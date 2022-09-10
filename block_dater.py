import shelve
import pymysql
import lightkurve as lk
import numpy as np
from tabulate import tabulate


def store(path, key, unit):

    with shelve.open(path) as db:
        db[key]  = unit


def do(exptime):

    catalog = []

    curve_path = '/data-one/curves/'
    store_path = '/data-one/final/block_dater_'+exptime+'.bin'

    con = pymysql.connect(host='localhost', user='astro', passwd='astro', db='astro')
    cursor = con.cursor()
    sql = "select target_name, filename, period, max, type from vsx, curve where vsx.oid=curve.oid and exptime='"+exptime+".0 s' and filename<>'NOT SUPPORTED' and mission='TESS' order by type asc"
    print("\n", sql, "\n")
    cursor.execute(sql)
    data = cursor.fetchall()
    con.close()

    buckets = {}
    for row in data:

        tmp = {'file': row[1], 'period': row[2], 'magnitude': row[3], 'type': row[4]}

        if row[0] in buckets.keys():
            buckets[row[0]].append( tmp )
        else:
            buckets[row[0]] = [ tmp ]

    del(data)

    if len(buckets.keys()) == 0:
        print("No light curve with useful data.", "\n")
        exit(0)

    for target in buckets.keys():

        curves = []

        for row in buckets[target]:
            curve = lk.read(curve_path + row['file'])
            
            for k in curve.meta.keys():
                print(k)
            input()

            magnitude = np.float64(curve.meta['TESSMAG'])
            before = len(curve)
            curve = curve.remove_nans()
            curve = curve.remove_nans(column='flux_err')
            size = len(curve)

            if(size > 0):
                reduction = ( before - size ) / before
                mean_err  = curve.flux_err.mean().to_value()

                better = ( size * (1 - reduction) ) / mean_err

                tmp = {'curve': curve, 'reduction': reduction, 'mean_err': mean_err, 'size': size, 'better': better, 'period': row['period'], 'vsx_magnitude': row['magnitude'], 'calculate_magnitude': magnitude, 'type': row['type']}
                curves.append(tmp)

        print("\n")
        print("\t\t", "Star: ", target)
        
        if len(curves) > 0:

            table_data = []
            curves = sorted(curves, key = lambda x: x['better'], reverse=True)
            better = curves[0]
            better['target'] = target
            
            for curve in curves:
                table_data.append([curve['type'], curve['reduction'], curve['mean_err'], curve['size'], curve['better']])
            print(tabulate(table_data, headers=['Type', 'NaN Reduction', 'Mean Error', 'Size', 'Better Factor'], ))

            norm = better['curve']
            lsperiod = norm.to_periodogram('bls')
            lsmax = lsperiod.period_at_max_power
            dmagnitude = better['vsx_magnitude']
            cmagnitude = better['calculate_magnitude']
            cperiod = lsmax
            dperiod = float(better['period'])
            print("\t ::::>", cperiod, dperiod, cmagnitude, dmagnitude)
            nzdata = norm.fold(cperiod * 2)

            dx = nzdata.time.value.tolist()
            dy = nzdata.flux.value.tolist()

            unit = {'target': better['target'], 'type': better['type'], 'vsx_period': better['period'], 'calculate_period': cperiod, 'curve': [dx, dy], 'vsx_magnitude': dmagnitude, 'calculate_magnitude': cmagnitude}
            catalog.append(better['target'])
            store(store_path, key=better['target'], unit=unit)
            
        else:

            print("\t\t", "No valid light curves found.")
    
    store(store_path, key='catalog', unit=catalog)


def main(args):

    if(len(args) >= 2):
        do(args[1])
    else:
        print("Please use python block_dater.py [exptime]")

    return 0


if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))
