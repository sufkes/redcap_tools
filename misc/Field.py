class Field:
    def __init__(self,  form_name, field_type, field_label, choices, text_validation_type, text_validation_min, text_validation_max, identifier, branching_logic, required_field, matrix_group_name, matrix_ranking, field_annotation, branching_logic_errors, events_containing_field, choices_dictionary):
        # Information from metadata
        # self.field_name = field_name # removed since metadata now stored as dict with field names as keys
        self.form_name = form_name # 
        # self.section_header = section_header
        self.field_type = field_type
        self.field_label = field_label
        self.choices = choices
        # self.field_note = field_note
        self.text_validation_type = text_validation_type
        self.text_validation_min = text_validation_min
        self.text_validation_max = text_validation_max
        self.identifier = identifier
        self.branching_logic = branching_logic
        self.required_field = required_field
        # self.custom_alignment = custom_alignment
        # self.question_number = question_number
        self.matrix_group_name = matrix_group_name
        self.matrix_ranking = matrix_ranking
        self.field_annotation = field_annotation

        # THE FOLLOWING SECTION SHOULD PERHAPS BE REMOVED IN FAVOUR OF A MORE GENERAL METHOD TO MAP
        # BETWEEN FORMS, EVENTS, FIELDS, INSTANCES, RECORD IDS, AND ROWS IN RECORDS.
        ## Things not stored in the REDCap Data Dictionary, but useful. 
        self.branching_logic_errors = branching_logic_errors

        # Information from instrument-event mapping
        self.events_containing_field = events_containing_field

        # Information from repeating forms events

        # Dict mapping choice indices to choice text for checkbox, radio, dropdown fields.
        self.choices_dictionary = choices_dictionary
