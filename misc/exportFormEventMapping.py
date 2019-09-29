def exportFormEventMapping(project, project_longitudinal):
    """List of dicts of the form:
    {u'arm_num': 1, u'unique_event_name': u'acute_arm_1', u'form': u'patient_information'}
    List includes a separate dict for each (form, event) pair.
    """
    if (project_longitudinal):
        form_event_mapping = project.export_fem()
    else:
        form_event_mapping = None
    return form_event_mapping
