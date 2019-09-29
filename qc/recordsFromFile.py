import os
import pickle

def saveRecords(out_dir, records):
    with open(os.path.join(out_dir, "records"), "wb") as handle:
        pickle.dump(records, handle)

def loadRecords(out_dir):
    with open(os.path.join(out_dir, "records"), "rb") as handle:
        records = pickle.load(handle)
    return records
