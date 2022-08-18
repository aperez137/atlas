import lightkurve as lk

def putCandidate(fname, line):
    f = open('have_data.txt', mode='a')
    f.write(line)
    f.close()

f = open('candidates.txt', mode='r')
data = f.readlines()
f.close()

offset = 0
data = data[offset:]

total = len(data)
c = 0
for line in data:
    try:
        c = c + 1
        print("\t", str(c)+' / ' + str(total) + ': ' + str((c / total) * 100) + '%' )
        parts = line.split("\t")
        res = lk.search_lightcurve(parts[1].replace("\n", ""))
        
        if(len(res) > 0):
            print("\n\t >>", line,"\n")
            putCandidate('have_data.txt', line)


    except Exception as e:
        print(e)
