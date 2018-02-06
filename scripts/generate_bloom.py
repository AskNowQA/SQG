from pybloom import BloomFilter
import mmap
import argparse

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Generate SPARQL query')
    parser.add_argument("--file", help="intput file path", dest="file", required=True)
    parser.add_argument("--output", help="output file path", dest="output", required=True)
    args = parser.parse_args()

    if args.file != "":
        bloom = BloomFilter(capacity=200000000, error_rate=0.000001)

        with open(args.file) as infile:
            m = mmap.mmap(infile.fileno(), 0, access=mmap.ACCESS_READ)
            for line in iter(m.readline, ""):
                s, p, o = line.split(",")
                bloom.add(s + ":" + p)
                bloom.add(p + ":" + o)
            m.close()

        with open(args.output, "w") as outfile:
            bloom.tofile(outfile)
