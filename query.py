#!/usr/bin/env python

import subprocess
import os
import time
import concurrent.futures

BASENAME = "dataset"
output = subprocess.check_output(['rekor-cli', 'loginfo'])

if not os.path.exists(BASENAME):
    os.mkdir(BASENAME)

# this is finnicky and dependent on output, so it will need to be updated
height = int(output.decode("utf-8").split("\n")[1].split()[2].strip())
print(f"log height: {height}")

# notice though range is not inclusive, this is what we want.

def detect_filenames(height, basename = BASENAME):

    target = set(range(0, height))
    for entry in os.listdir(basename):
        filename = os.path.basename(entry)
        index = int(os.path.splitext(filename)[0].split("-", 2)[1])
        target.remove(index)

    return target

print("Identifying locally-cached entries...", end='')
to_download = detect_filenames(height)
print("done")
print("There are {} entries to download".format(len(to_download)))

def fetch_obj(index):
    filename = os.path.join(BASENAME, f"rekor_obj-{index}.json")
    result = f"Getting entry {index}..."
    try:
        output = subprocess.check_output(['rekor-cli', '--format', 'json', 'get', '--log-index', str(index)])
    except Exception as e:
        return result + "failed!"

    with open(filename, "wt") as fp:
        fp.write(output.decode("utf-8"))
    time.sleep(.001)
    return result + "done."

with concurrent.futures.ProcessPoolExecutor(max_workers=200) as executor:
    print("setting up process pool...", end='')
    futures = executor.map(fetch_obj, to_download, chunksize=64)
    print("done")
