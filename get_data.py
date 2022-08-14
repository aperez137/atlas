import pandas as pd
import pymysql
from astroquery.vizier import Vizier

total_records = 0

def persist(data):
    global total_records
    block_size = len(data)
    total_records += block_size
    
    con = pymysql.connect(host="localhost", user="astro", passwd="astro", db="astro")
    cursor = con.cursor()
    df = pd.DataFrame(data)
    val_to_insert = df.values.tolist()
    cursor.executemany("insert into vsx (`OID`, `n_OID`, `Name`, `V`, `Type`, `l_max`, `max`, `u_max`, `n_max`, `f_min`, `l_min`, `min`, `u_min`, `n_min`, `l_Period`, `Period`, `u_Period`, `RAJ2000`, `DEJ2000`) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", val_to_insert)
    con.commit()
    con.close()

    print("Persist: "+str( block_size )+" Total Records: "+str(total_records))

def get_data():

    Vizier.ROW_LIMIT = -1
    LIMIT = 10000
    buffer = []
    
    catalog_data = Vizier.get_catalogs('B/vsx/vsx')
    
    for table in catalog_data:
        
        for row in table:
            buffer.append(list(row.values()))
            if(len(buffer) == LIMIT):
                persist(buffer)
                buffer = []

    if(len(buffer) > 0):
        persist(buffer)

if __name__ == '__main__':
    get_data()