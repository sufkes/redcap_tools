import os
import pickle

def saveData(out_dir, project, forms, project_info, metadata, record_id_map, dags_used, dags, check_results, save_all=False):
    """This function is used to save data exported from REDCap, and the results of the checks performed.
    Functions such as the branching logic functions are not saved, as functions are not straigtforward
    to pickle in Python (and aren't needed currently)."""

    # Save project
    with open(os.path.join(out_dir, "project"), "wb") as handle:
        pickle.dump(project, handle)
    
    # Save forms
    with open(os.path.join(out_dir, "forms"), "wb") as handle:
        pickle.dump(forms, handle)

    # Save project_info
    with open(os.path.join(out_dir, "project_info"), "wb") as handle:
        pickle.dump(project_info, handle)

    # Save metadata (except branching logic function)
    for field_name, field in metadata.iteritems():
        metadata[field_name].branching_logic = None
    with open(os.path.join(out_dir, "metadata"), "w") as handle:
        pickle.dump(metadata, handle)

    # Save record_id_map
    with open(os.path.join(out_dir, "record_id_map"), "wb") as handle:
        pickle.dump(record_id_map, handle)

    # Save dags_used
    with open(os.path.join(out_dir, "dags_used"), "wb") as handle:
        pickle.dump(dags_used, handle)

    # Save dags
    with open(os.path.join(out_dir, "dags"), "wb") as handle:
        pickle.dump(dags, handle)

    # Save check_results
    for result in check_results:
        # Remove the check functions since they can't be pickled.
        result[0].rowConditions = None
        result[0].fieldConditions = None
        result[0].checkFunction = None
    with open(os.path.join(out_dir, "check_results"), "wb") as handle:
        pickle.dump(check_results, handle)

    return

