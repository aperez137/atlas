import pymysql

class DbControl:

    def __init__(self) -> None:
        self.host = 'localhost'
        self.user = 'astro'
        self.passwd = 'astro'
        self.db = 'astro'


    def connect(self):
        self.con = pymysql.connect(host=self.host, user=self.user, passwd=self.passwd, db=self.db)
        self.cursor = self.con.cursor()


    def commit(self):
        self.con.commit()

    
    def close(self):
        self.con.close()