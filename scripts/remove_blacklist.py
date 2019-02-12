import mmap
import argparse
import subprocess
from tqdm import tqdm
import os


def file_append(file_path, data):
    with open(file_path, "a") as file_handler:
        file_handler.write("".join(data))


if __name__ == "__main__":
    black_list = ["http://dbpedia.org/ontology/wikiPageWikiLink",
                  "http://www.w3.org/2002/07/owl#sameAs",
                  "http://purl.org/dc/terms/subject",
                  "http://www.w3.org/2000/01/rdf-schema#label",
                  "http://dbpedia.org/ontology/wikiPageRevisionID",
                  "http://www.w3.org/ns/prov#wasDerivedFrom",
                  "http://dbpedia.org/ontology/wikiPageID",
                  "http://dbpedia.org/ontology/wikiPageOutDegree",
                  "http://dbpedia.org/ontology/wikiPageLength",
                  "http://xmlns.com/foaf/0.1/primaryTopic",
                  "http://xmlns.com/foaf/0.1/isPrimaryTopicOf",
                  "http://purl.org/dc/elements/1.1/language",
                  "http://dbpedia.org/ontology/wikiPageExternalLink",
                  "http://dbpedia.org/ontology/wikiPageRedirects",
                  "http://dbpedia.org/ontology/abstract",
                  "http://www.w3.org/2000/01/rdf-schema#comment",
                  "http://dbpedia.org/property/wikiPageUsesTemplate",
                  "http://dbpedia.org/ontology/wikiPageDisambiguates"]

    parser = argparse.ArgumentParser(description='Generate SPARQL query')
    parser.add_argument("--file", help="intput file path", dest="file", required=True)
    parser.add_argument("--output", help="output file path", dest="output", required=True)
    parser.add_argument("--buffer_threshold", help="buffer threshold", dest="buffer_threshold", type=int, default=10)
    parser.add_argument("--max", help="buffer threshold", dest="max", type=int, default=-1)
    args = parser.parse_args()

    if os.path.exists(args.output):
        os.remove(args.output)

    with open(args.file) as infile:
        i = 0
        lines_in_file = 602259225  # int(subprocess.check_output("wc -l " + args.file, shell=True).split()[0])
        print(lines_in_file)
        m = mmap.mmap(infile.fileno(), 0, access=mmap.ACCESS_READ)
        buffer = []
        for line in tqdm(iter(m.readline, ""), total=lines_in_file):
            i += 1
            found = False
            for item in black_list:
                if item in line:
                    found = True
                    break
            if not found:
                buffer.append(line)
            if len(buffer) == args.buffer_threshold:
                file_append(args.output, buffer)
                buffer = []
            if args.max != 1 - 1 and i == args.max:
                break
        file_append(args.output, buffer)
        m.close()
