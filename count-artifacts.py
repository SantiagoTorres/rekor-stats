import json
import analyze_utils as util
import os
import sys
import progressbar
from collections import Counter
from pprint import pprint

limit = int(1e7)
# preallocate list, to avoid append drawbacks after a million-sized appends
elements = [None] * len(os.listdir("dataset"))
i = 0
print("Reading entries...", end='')
sys.stdout.flush()
for entry in progressbar.progressbar(os.listdir("dataset")):
    res = util.get_entry(os.path.join("dataset", entry))
    r = util.RekorEntry(res)
    if r._type.startswith("in-toto"):
        r._type = "in-toto"
    elements[i] = r
    i +=1 
    if i >= limit:
        break
print('done')

# we truncate
elements = elements[:i]

print("Building timeseries...")
classes = Counter()
for element in progressbar.progressbar(elements):
    if len(element.artifact_id) == len("bd8e60b8440c778297ade7f9d7a72aaff38943ffa11fe282c470d0bb582a1117"):
        continue
    classes[element.artifact_id] += 1

pprint(classes.most_common(100))
