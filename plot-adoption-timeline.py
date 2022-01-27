import json
import analyze_utils as util
import os
import sys
import progressbar

type_series= {
    "x509": [0],
    "in-toto": [0],
    "hashed_rekord": [0],
    "minisign": [0],
    "pgp": [0],
    "Helm": [0],
    "RFC3161": [0],
    "rpm": [0],
    "Tuf": [0],
    "ssh": [0],
    "JAR": [0],
    "Alpine": [0],
    "Timestamp": [-1],
}

ignorelist = {}
#ignorelist = {'x509', 'in-toto', 'Helm', 'RFC3161', 'rpm', 'Tuf', 'ssh', 'JAR', 'Alpine'}

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
    if r._type in ignorelist:
        continue
    # ignore stress stest
    if r.timestamp > 1629000000 and r.timestamp < 1630123200 and (r._type == "x509" or r._type == "in-toto"):
        #print("skipping {}".format(r.timestamp))
        continue
    elements[i] = r
    i +=1 
    if i >= limit:
        break
print('done')

# we truncate
elements = elements[:i]

print("sorting...", end='')
sys.stdout.flush()
elements.sort(key=lambda x: int(x.timestamp))
print('done')

print("Building timeseries...")
for element in progressbar.progressbar(elements):
    for key in type_series.keys():
        if key == 'Timestamp':
            type_series[key].append(int(element.timestamp))
            continue
        if key == element._type:
            type_series[key].append(type_series[key][-1] + 1)
            continue
        if element._type not in type_series:
            import pdb; pdb.set_trace()
        type_series[key].append(type_series[key][-1])

type_series['Timestamp'][0] = type_series['Timestamp'][1] - 1

for key in type_series:
    type_series[key] = type_series[key][::100]

import seaborn as sns
import matplotlib.pyplot as plt
import pandas


df = pandas.DataFrame.from_dict(type_series)
df['Timestamp'] = pandas.to_datetime(df['Timestamp'], unit='s')
df = df.set_index("Timestamp")
print(df)
sns.lineplot(data=df)
sns.despine()
plt.ylabel("# of entries")
#plt.xlim((1626580800, 1642482000))
plt.title("Entry type adoption trend (no stress test)")
plt.tight_layout()
#plt.show()
plt.savefig('all-type-trend-no-stress-trest.png')
