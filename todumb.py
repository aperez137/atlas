import shelve
import pickle
import dbm

def convert(path):

    with shelve.open(path, flag='r') as data:
        
        with dbm.dumb.open(path+".dumb") as dumb_data:
            
            for key, value in data.items():
                print("\r\t"+key, end='')
                dumb_data[key] = pickle.dumps(value)
    
    print("\nDone!\n")

def main(args):

    convert(args[1])

if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))