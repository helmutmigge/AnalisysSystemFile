import argparse
import os
import pandas as pd
import AnalysisFileTree as at
import matplotlib.pyplot as plt

parser = argparse.ArgumentParser(
    description="Creates statistics from a directory structure")
parser.add_argument('-i',
                    action='store',
                    dest='directoryPath',
                    help='input directory path')
parser.add_argument('-o',
                    action='store',
                    dest='outputFilePath',
                    default=None,
                    help='output filepath, CVs and JSon supported')
parser.add_argument('-c',
                    action='store',
                    dest='hash_name',
                    default=None,
                    help='hash function for checksum')
parser.add_argument('-data',
                    action='store',
                    dest='dataFilePath',
                    default=None,
                    help='output filepath, CVs and JSon supported')

args = parser.parse_args()

if args.dataFilePath and os.path.isfile(args.dataFilePath):
    df = pd.read_csv(args.dataFilePath)
    with plt.style.context('ggplot'):
        df['extension'].value_counts().plot( kind='bar', color='C1', title='Extension distribution by count')
    plt.show()
    exit(0)

if not os.path.isdir(args.directoryPath):
    print('FilePath is not a directory: ', args.directoryPath)
    exit(-1)

if args.outputFilePath and not args.outputFilePath.endswith(('.csv', '.json')):
    print('Output type not supported : ', args.outputFilePath)
    exit(-1)

fileTree = at.AnalysisFileTree(args.directoryPath, verbose=True, hash_name=args.hash_name)

df = fileTree.stats()

if args.outputFilePath:
        if args.outputFilePath.endswith('.csv'):
            df.to_csv(args.outputFilePath, index=False)
        elif args.outputFilePath.endswith('.json'):
            df.to_json(args.outputFilePath, index=False)
else:
    with plt.style.context('ggplot'):
        df['extension'].value_counts().plot( kind='bar', color='C1', title='Extension distribution by count')
    plt.show()

