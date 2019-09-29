# Standard modules
import os, sys

# My modules from other directories
sufkes_git_repo_dir = '/Users/steven ufkes/scripts'
sys.path.append(os.path.join(sufkes_git_repo_dir, "misc")) 
from Color import Color

def formatFieldName(field_name, metadata):
    """This function is used to convert checkbox field names, e.g. var1___1 into var1
    for reporting. This function is also used to flag fields for which there are 
    errors in the branching logic."""
    # COLOR OUTPUT USED HERE. VERIFY COMPATIBILITY ACROSS OPERATING SYSTEMS/TERMINALS.
    field = metadata[field_name]
    if (not field.field_type == "checkbox"):
        field_name_formatted = field_name
    else:
        field_name_formatted = field_name.split("___")[0]
    if (len(metadata[field_name].branching_logic_errors) > 0): # if there are errors in the branching logic for this field
        field_name_formatted = Color.red + field_name_formatted + Color.end
    return field_name_formatted

def formatDAGName(dag):
    if (not dag.strip() == ""):
        formatted_dag = dag
    else:
        formatted_dag = "UNASSIGNED"
    return formatted_dag
