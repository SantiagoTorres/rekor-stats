"""Query and store rekor's full database in JSON files.

Uses caching to avoid re-downloading records.

Usage from command line:
>>> python query.py
"""

# import concurrent.futures
from multiprocessing import Pool
import os
import subprocess
import time

# folder name for storing dataset
BASENAME = "dataset"
# number of simultaneous processes to use
NUM_PROCESSES = 20


def detect_filenames(height, basename=BASENAME):
    """Find records not yet downloaded.

    Args:
        height (int): number of records in rekor database
        basename (str): folder containing records

    Returns:
        target (set) - entries not yet downloaded
    """
    # range is NOT inclusive
    target = set(range(0, height))
    print(target)

    for entry in os.listdir(basename):
        filename = os.path.basename(entry)
        # TODO: make parsing less brittle
        # extract index number from filename
        index = int(os.path.splitext(filename)[0].split("-", 2)[1])
        target.remove(index)

    return target


def fetch_record(index, basename=BASENAME):
    """Retrieve desired record from rekor database.

    Args:
        index (int): record index
        basename (str): folder containing records

    Returns:
        record (json) - Rekor record in json blob
        filename (str)
    """
    filename = os.path.join(basename, f"rekor_obj-{index}.json")
    print("filename", filename)
    print(f"Getting entry {index}...")

    # use rekor-cli to query database
    try:
        record = subprocess.check_output(
            ["rekor-cli", "--format", "json", "get", "--log-index", str(index)]
        )
    except Exception as e:
        print(result, f"failed! Exception: {e}")
        record = ""

    return record, filename


def store_record(record, filename):
    """Store record from rekor database.

    Args:
        record(json): json blob containing record
        filename (str): record index

    Returns:
        None
    """
    with open(filename, "wt") as fp:
        fp.write(record.decode("utf-8"))

    # TODO: Is this sleep necessary?
    time.sleep(0.001)


def process_record(index, basename=BASENAME):
    """Retrieve and store a Rekor record.

    Args:
        index (int): record index
        basename (str): folder containing records

    Returns:
        None
    """
    record, filename = fetch_record(index, basename)
    store_record(record, filename)


if __name__ == "__main__":

    if not os.path.exists(BASENAME):
        os.mkdir(BASENAME)

    # determine total number of records currently in database
    output = subprocess.check_output(["rekor-cli", "loginfo"])
    # TODO: make parsing less brittle
    height = 2 # int(output.decode("utf-8").split("\n")[1].split()[2].strip())
    print(f"log height: {height}")

    # check cache and print count of records requiring download
    print("Identifying locally-cached entries...", end="")
    need_to_download = detect_filenames(height)
    print("done")
    print(f"There are {len(need_to_download)} entries to download")

    # use multiprocessing to speed up download
    with Pool(NUM_PROCESSES) as p:
        p.map(process_record, need_to_download)

    # alternative method of speeding up download
    # TODO: Will require some rewriting to use
    # with concurrent.futures.ProcessPoolExecutor(max_workers=100) as executor:
    #     print("setting up process pool...", end='')
    #     futures = executor.map(fetch_obj, to_download, chunksize=64)
    #     print("done")
