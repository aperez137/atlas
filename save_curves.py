import subprocess as sp
from process import saveDataFrom

f = open('candidates.txt', 'r')
data = f.readlines()
f.close()

offset = 1821580
data = data[offset:]

for line in data:
    try:
        parts = line.split("\t")
        print("\n\n===", parts[0], "===\n\n")
        saveDataFrom(parts[0], parts[1].replace("\n", ""))
        print("\n\n===", parts[0], "===\n\n")
    except Exception as ex:
        print("\n\n", "GENRAL", "\n", ex, "\n\n")
    finally:
        sp.getoutput("echo '"+parts[0]+"' >> index.txt")
