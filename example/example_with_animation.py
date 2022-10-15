import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter
from d_fuzzstream import DFuzzStreamSummarizer


summarizer = DFuzzStreamSummarizer()

chunk_size = 100
figure = plt.figure()
scatter = plt.scatter('x', 'y', s='radius', data={'x': [], 'y': [], 'radius': []})

# Read files in chunks
csv = pd.read_csv("https://raw.githubusercontent.com/CIG-UFSCar/DS_Datasets/master/Synthetic/Non-Stationary/Bench1_11k/Benchmark1_11000.csv",
                  dtype={"X1": float, "X2": float},
                  usecols=[0, 1],
                  chunksize=chunk_size)


# Function to animate GIF
def summarize(frame):
    plt.cla()
    plt.xlim(0, 1)
    plt.ylim(0, 1)
    chunk = next(csv)

    timestamp = chunk_size * frame

    print(f"Summarizing examples from {timestamp} to {timestamp + chunk_size - 1}")
    for index, example in chunk.iterrows():
        # Summarizing example
        summarizer.summarize(example, timestamp)
        timestamp += 1

    data = {'x': [], 'y': [], 'radius': []}

    for fmic in summarizer.summary():
        data['x'].append(fmic.center[0])
        data['y'].append(fmic.center[1])
        data['radius'].append(fmic.radius * 100000)
    # Plot radius
    plt.scatter('x', 'y', s='radius', color='Blue', data=data, alpha=0.1)
    # Plot centroids
    plt.scatter('x', 'y', s=1, color='Black', data=data)


anim = FuncAnimation(
    figure,
    summarize,
    frames=11000//chunk_size,
    interval=1000,
    repeat=False,
    init_func=lambda: None
)

writer_gif = PillowWriter(fps=60)

anim.save("summary.gif", writer=writer_gif)

plt.close()
csv.close()
