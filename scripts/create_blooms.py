from tqdm import tqdm
import argparse
import os
from pybloom_live import BloomFilter, ScalableBloomFilter
from itertools import (takewhile, repeat)

from parser.lc_quad_linked import LC_Qaud_Linked


def rawincount(filename):
    f = open(filename, 'rb')
    bufgen = takewhile(lambda x: x, (f.raw.read(1024 * 1024) for _ in repeat(None)))
    return sum(buf.count(b'\n') for buf in bufgen)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generate bloom filter files')
    parser.add_argument("--base_path", default='../')
    parser.add_argument("--path", help="dataset path", default="data/LC-QUAD/linked_answer6.json",
                        dest="dataset_path")
    parser.add_argument('--create', action='store_true')
    args = parser.parse_args()

    bloom = BloomFilter(capacity=200000000, error_rate=0.000001)

    dbpedia_path = os.path.join(args.base_path, 'data', 'dbpedia')
    blooms_path = os.path.join(args.base_path, 'data', 'blooms')
    if args.create:
        for ttl_file in os.listdir(dbpedia_path):
            if '.ttl' not in ttl_file:
                continue
            print(ttl_file)
            file_path = os.path.join(dbpedia_path, ttl_file)
            with open(file_path, 'r') as f:
                for line in tqdm(f, total=rawincount(file_path)):
                    items = line.split(' ')
                    if len(items) != 4:
                        continue
                    items = items[:-1]
                    if not all([item.startswith('<') and item.endswith('>') for item in items]):
                        continue

                    for i in range(2):
                        key = ':'.join([items[i][1:-1], items[i + 1][1:-1]])
                        bloom.add(key)

        with open(os.path.join(blooms_path, 'spo1.bloom'), 'wb') as f:
            bloom.tofile(f)

    with open(os.path.join(blooms_path, 'spo1.bloom'), 'rb') as f:
        one_hop_bloom = BloomFilter.fromfile(f)

        ds = LC_Qaud_Linked(path=os.path.join(args.base_path, args.dataset_path))
        ds.load()
        ds.parse()
        for row in ds.qapairs:
            for item in row.sparql.where_clause:
                if item[0].startswith('<'):
                    key = ':'.join([item[0][1:-1], item[1][1:-1]])
                elif item[2].startswith('<'):
                    key = ':'.join([item[1][1:-1], item[2][1:-1]])
                else:
                    key = ''
                if '#type' not in key and key != '' and key not in one_hop_bloom:
                    print(key)

        # print('http://dbpedia.org/resource/Actrius:http://dbpedia.org/property/director' in one_hop_bloom)
