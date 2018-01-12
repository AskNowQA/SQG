import argparse
from common.utility.stats import Stats

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Analyse the input of ranking model')
    parser.add_argument("--file", help="file name to load the results", default="tmp", dest="file_name")
    args = parser.parse_args()

base_path = "../learning/treelstm/data/"
sets = ["train", "dev", "test"]
for item in sets:
    stats = Stats()
    with open("{}{}/{}/sim.txt".format(base_path, args.file_name, item)) as file_reader:
        file_data = file_reader.readlines()
        for line in file_data:
            stats.inc(line.replace("\n", ""))
    print item
    total = 0.0 + stats["1"] + stats["2"]
    print stats["1"] / total, stats["2"] / total
