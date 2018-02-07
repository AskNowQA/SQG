from pybloom import BloomFilter
import mmap
import argparse
from tqdm import tqdm
import subprocess
import os

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Generate SPARQL query')
    parser.add_argument("--file", help="intput file path", dest="file", required=True)
    parser.add_argument("--output", help="output file path", dest="output", required=True)
    args = parser.parse_args()

    if args.file != "":
        bloom = BloomFilter(capacity=400000000, error_rate=0.000001)

        lines_in_file = int(subprocess.check_output("wc -l " + args.file, shell=True).split()[0])
        with open(args.file) as infile:
            m = mmap.mmap(infile.fileno(), 0, access=mmap.ACCESS_READ)
            for line in tqdm(iter(m.readline, ""), total=lines_in_file):

                tmp = line.replace("\n", "").split(",http")
                for i in range(1, len(tmp)):
                    tmp[i] = "http" + tmp[i]
                if len(tmp) != 3:
                    # print tmp
                    continue

                s, p, o = tmp
                s1 = s + ":" + p
                s2 = p + ":" + o
                bloom.add(s1)
                bloom.add(s2)
        m.close()

    with open(args.output, "w") as outfile:
        bloom.tofile(outfile)
