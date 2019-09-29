"""This module defines a class for the checks to be performed. For each check, a 
description is provided, the considtions under which the check is performed, and the
function defining the check to be performed are specified."""

class Check:
    def __init__(self, name, description, report_forms, inter_project, whole_row_check, check_invalid_entries, inter_record, inter_row, specify_fields, target_fields, rowConditions, fieldConditions, checkFunction):
        self.name = name # Short name of check used in names of output files.
        self.description = description # Brief text describing check to perform
        self.report_forms = report_forms # Whether or not to break down the reports by instrument
        self.inter_project = inter_project # True if check compares data between different projects.
        self.whole_row_check = whole_row_check # True if check is for the whole row rather than certain fields (e.g. finding invalid rows, duplicate rows)
        self.check_invalid_entries = check_invalid_entries # True if check is performed on (row, field)s which should not exist based on events, repeating forms, and branching logic.
        self.inter_record = inter_record # True if check compares data between different records.
#        self.inter_event = inter_event # True if check compares data between different events or arms.
#        self.inter_instance = inter_instance # True if check compares data between different instances of a repeating event.
        self.inter_row = inter_row # True if check refers to different event, record, or instance.
        self.specify_fields = specify_fields # True if check is performed only on user-specified fields (possibly multiple fields)
        self.target_fields = target_fields # Specify a list of fields targeted by check if only specific fields are involved
        self.rowConditions = rowConditions # Conditions which determine if a row should be checked, and can be determined using the row information only  (excluding considerations of whether the event, form contains the field)
        self.fieldConditions = fieldConditions # Conditions which determine if a field should be checked, and can be determined using the field information only (excluding branching logic).
        self.checkFunction = checkFunction # The function which performs the actual quality check.
