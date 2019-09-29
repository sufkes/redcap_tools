import os
import pickle

def saveRecords(out_dir, records):
    with open(os.path.join(out_dir, "records"), "wb") as handle:
        pickle.dump(records, handle)
