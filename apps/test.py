import json

def main(args):
    inputs = args
    outputs = args
    print(json.dumps(outputs))

if __name__ == '__main__':
    import sys
    main(json.loads(sys.argv[1]))