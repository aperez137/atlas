import json
import numpy as np
import lightkurve as lk

from db import DbControl

class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        try:
            if isinstance(obj, np.ndarray):
                return obj.tolist()
            return json.JSONEncoder.default(self, obj)
        except Exception as ex:
            print("\n\n", 'JSON', "\n", ex, "\n\n")
            return '---'

def saveDataFrom(oid, coordinate):

    try:
        curvesPath = '/data-one/curves/'

        sql1 = """insert into curve (
                        `OID`, `SUB`, `author`, `dec`,
                        `ra`, `distance`, `exptime`, `mission`,
                        `zone`, `target_name`, `year`,`filename`
                    ) values (
                        %s, %s, %s, %s,
                        %s, %s, %s, %s,
                        %s, %s, %s, %s
                    )"""
        
        sql2 = """insert into meta (
                        `OID`, `SUB`, `data`
                    ) values (
                        %s, %s, %s
                    )"""

        dba = DbControl()
        dba.connect()

        res = lk.search_lightcurve(coordinate)

        if(len(res) > 0):

            curves = []
            metas  = []

            for i in range(len(res)):
                print("\n\t>>", i, "curve")
                tmp = str(res[i].mission[0]).split(' ')
                
                sub         = str(i)
                author      = ' '.join(res[i].author.data.tolist())
                dec         = str(res[i].dec[0])
                ra          = str(res[i].ra[0])
                distance    = str(res[i].distance[0])
                exptime     = str(res[i].exptime[0])
                mission     = tmp[0]
                zone        = tmp[1] + ' ' + tmp[2]
                target_name = str(res[i].target_name[0])
                year        = str(res[i].year[0])
                
                try:
                    print("\tDownload", i, "curve")
                    col = res[i].download(download_dir=curvesPath)
                    filename    = col.filename.replace(curvesPath, '')
                    print("\tOK")
                except Exception as ex:
                    filename    = 'NOT SUPPORTED'
                    print("\n\n", "CURVE", "\n", oid, "\n", ex, "\n\n")


                jsonData    = json.dumps(col[i].meta, cls=NumpyEncoder)
                
                curves.append([oid, sub, author, dec, ra, distance, exptime, mission, zone, target_name, year, filename])
                metas.append([oid, sub, jsonData])
                
            dba.cursor.executemany(sql1, curves)
            dba.cursor.executemany(sql2, metas)
            dba.commit()
                            
    except Exception as ex:
        print("\n\n", "PROCESS", "\n", oid, "\n", ex, "\n\n")
    finally:
        dba.close()
