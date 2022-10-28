import pandas as pd
from d_fuzzstream import DFuzzStreamSummarizer

idxSimilarity = 3
summarizer = DFuzzStreamSummarizer(idxSimilarity)

summary = {'x': [], 'y': [], 'weight': []}
timestamp = 0

# Read files in chunks
with pd.read_csv("https://raw.githubusercontent.com/CIG-UFSCar/DS_Datasets/master/Synthetic/Non-Stationary/Bench1_11k/Benchmark1_11000.csv",
                 dtype={"X1": float, "X2": float},
                 usecols=[0, 1],
                 chunksize=1000) as reader:
    for chunk in reader:
        print(f"Summarizing examples from {timestamp} to {timestamp + 999}")
        for index, example in chunk.iterrows():
            # Summarizing example
            summarizer.summarize(example, timestamp)
            timestamp += 1

    # Transforming FMiCs into dataframe
    for fmic in summarizer.summary():
        summary['x'].append(fmic.center[0])
        summary['y'].append(fmic.center[1])
        summary['weight'].append(fmic.m)

print(summary)
