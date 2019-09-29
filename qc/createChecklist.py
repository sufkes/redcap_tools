import os, sys

def createChecklist(checklist_name_list):
    checklist_full = [] # list containing all checks (default and project-specific)
    for checklist_name in checklist_name_list:
#        exec "sufkes_git_repo_dir = '/Users/steven ufkes/scripts'"
#        exec 'sys.path.append(os.path.join(sufkes_git_repo_dir, "redcap_qc"))'
        exec "from "+checklist_name+" import checklist"
        checklist_full.extend(checklist)
    return checklist_full
