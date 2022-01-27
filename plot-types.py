#!/usr/bin/env python

import seaborn as sns
import matplotlib.pyplot as plt
import pandas
import json

with open("type_breakdown.json") as fp:
    data = json.load(fp)

# XXX: aggregate in-toto
#in_toto_all = 0
#newdata = {} 
#for key in data:
#    if key.startswith("in-toto"):
#        if 'in-toto' not in newdata:
#            newdata['in-toto'] = 0
#        in_toto_all += data[key]
#    else:
#        newdata[key] = data[key]
#newdata["in-toto"] = in_toto_all

# XXX: only in-toto types
newdata = {} 
for key in data:
    if key.startswith("in-toto cosign"):
        if "cosign.sigstore.dev/attestation/v1" not in newdata:
            newdata["cosign.sigstore.dev/attestation/v1"] = 0
        newdata["cosign.sigstore.dev/attestation/v1"] += data[key]
    elif key.startswith("in-toto"):
        newdata[key.replace("in-toto https://", "")] = data[key]
data = newdata

ymax = max([data[x] for x in data])
df = pandas.DataFrame.from_dict(data, orient='index').reset_index()
df = df.rename(columns={'index':'type', 0:'count'})
print(df)
plt.ylim((1, ymax + 1000))
#plt.yscale('log')
#plt.xticks(rotation=90)
sns.barplot(data=df, x='count', y='type', orient='h')
sns.despine()
plt.tight_layout()
plt.savefig('all-types.png')
