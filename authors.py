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
authors = Counter()
providers = Counter()
print("Reading entries...", end='')
sys.stdout.flush()
for entry in progressbar.progressbar(os.listdir("dataset")):
    res = util.get_entry(os.path.join("dataset", entry))
    r = util.RekorEntry(res)
    if r._type == "x509":
        if r.author and r.provider:
            authors[r.author] += 1
            providers[r.provider] += 1


print('done')

pprint(authors.most_common(20))
pprint(providers.most_common(20))
