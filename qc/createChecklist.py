import os, sys

def createChecklist(checklist_name_list):
    checklist_full = [] # list containing all checks (default and project-specific)
    for checklist_name in checklist_name_list:
        exec "from "+checklist_name+" import checklist"
        checklist_full.extend(checklist)
    return checklist_full
