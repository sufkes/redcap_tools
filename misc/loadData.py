import os 
import pickle

def loadData(in_dir):
    """This function is used to load data saved data generated from the quality control script.
    This function is not used in the quality control script, but is used for custom report scripts."""

    # Load project
    with open(os.path.join(in_dir, "project"), "rb") as handle:
        project = pickle.load(handle)
    
    # Load forms
    with open(os.path.join(in_dir, "forms"), "rb") as handle:
        forms = pickle.load(handle)

    # Load project_info
    with open(os.path.join(in_dir, "project_info"), "rb") as handle:
        project_info = pickle.load(handle)

    # Load metadata_parsed (except branching logic function)
    with open(os.path.join(in_dir, "metadata_parsed"), "rb") as handle:
        metadata_parsed = pickle.load(handle)

    # Load record_ids
    with open(os.path.join(in_dir, "record_ids"), "rb") as handle:
        record_ids = pickle.load(handle)

    # Load dags_used
    with open(os.path.join(in_dir, "dags_used"), "rb") as handle:
        dags_used = pickle.load(handle)
    
    # Load dags
    if dags_used:
        with open(os.path.join(in_dir, "dags"), "rb") as handle:
            dags = pickle.load(handle)

    # Load check_results
    with open(os.path.join(in_dir, "check_results"), "rb") as handle:
        check_results = pickle.load(handle)

    return project, forms, project_info, metadata_parsed, record_ids, dags, check_results

