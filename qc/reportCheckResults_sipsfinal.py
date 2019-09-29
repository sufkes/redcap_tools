# Standard modules
import os, sys
import csv

# My modules from current directory
from formatStrings import formatFieldName, formatDAGName

# My modules from other directories
sufkes_git_repo_dir = "/Users/steven ufkes/scripts" # change this to the path to which the sufkes Git repository was cloned.
sys.path.append(os.path.join(sufkes_git_repo_dir, "misc")) 
from Color import Color

## THIS SCRIPT SHOULD PROBABLY BE REWRITTEN USING PANDAS. SOME OF IT COULD BE DRASTICALLY SIMPLIFIED. 


def fancyNewLine(string):
    return "\n"+string * 80

def combineCheckReports(checklist, out_dir, dags, dags_used):
    """This script looks for site-specific reports in the output directory and combines all of the 
    checks into a single document."""

    # THIS IS NOT WELL ORGANIZED. PROBABLY THE BEST WAY IS IF THE CHECK DRIVER ONLY GENERATES THE LIST
    # OF CHECK RESULTS, AND ANOTHER FUNCTION GENERATES REPORTS BASED ON THOSE.

    ## DAG-Instrument-Count report
    master_report_name = os.path.join(out_dir, "all_checks.csv")

    # Build list of check report paths.
    report_path_list = []
    for check in checklist:
        report_path = os.path.join(os.path.join(out_dir, check.name+".csv"))
        if os.path.exists(report_path):
            report_path_list.append(report_path)

    # Append check reports to master report.
    if (len(report_path_list) > 0):
        with open(master_report_name, 'wb') as dest_csv:
            dest_writer = csv.writer(dest_csv, delimiter=",")
            for report_path in report_path_list:
                with open(report_path, 'rb') as src_csv:
                    src_reader = csv.reader(src_csv, delimiter=",")
                    for row in src_reader:
                        dest_writer.writerow(row)
                    dest_writer.writerow([""])

    ## DAG-Subject-Instrument-Field report
    # Loop over all DAGs.
    if dags_used:
        for dag in dags:
            dag_name = formatDAGName(dag) # format DAG name (turn blank DAG into "UNASSIGNED")
            master_site_report_name = os.path.join(os.path.join(out_dir, "site-form-field"), "all_checks_"+dag_name+".csv")
    
            # Build list of check report paths.
            report_path_list = []
            for check in checklist:
                report_path = os.path.join(os.path.join(out_dir, "site-form-field"), check.name+"-"+dag_name+".csv")
                if os.path.exists(report_path):
                    report_path_list.append(report_path)
                    
            # Append check reports to master report for each site.
            if (len(report_path_list) > 0):
                with open(master_site_report_name, 'wb') as dest_csv:
                    dest_writer = csv.writer(dest_csv, delimiter=",")
                    for report_path in report_path_list:
                        with open(report_path, 'rb') as src_csv:
                            src_reader = csv.reader(src_csv, delimiter=",")
                            for row in src_reader:
                                dest_writer.writerow(row)
                            dest_writer.writerow([""])
    return


def reportCheckResults(elements_to_check, bad_elements, check, out_dir, def_field, project_info, project_longitudinal, project_repeating, events, forms, form_repetition_map, metadata, records, record_id_map, dags_used, dags, dag_record_map): # WRITTEN FOR A SINGLE-FIELD CHECK; EXTEND TO MULTI-FIELD CHECKS.
    # Print a description of the check being performed.
    print fancyNewLine("#")
    print "Performing check:", check.description

    # Whole-row checks, intra-row (e.g. invalid event, form, instance for row).
    # report: 1 report
    # rows: row indices in records
    # columns: None
    if (check.whole_row_check) and (not check.inter_row):
        print fancyNewLine("-")
        print "Whole-row check report; intra-row"

        # Open report file handle
        report_filepath = os.path.join(out_dir, check.name+".csv")
        report_handle = open(report_filepath, 'w')
        report_writer = csv.writer(report_handle, delimiter=",")
        
        # Write description of check at top of spreadsheet.
        zeroth_row = ["Check" , check.description]
        report_writer.writerow(zeroth_row)

        # Write first row of report spreadsheet.
        first_row = ["row index"]
        report_writer.writerow(first_row)

        # Add problematic row indices to report.
        for element in bad_elements:
            row_index = element[0]
            new_row = [row_index]
            report_writer.writerow(new_row)
        report_handle.close()


    # Whole-row checks, inter-row (e.g. duplicate records, invalid rows)
    # report: 1 report
    # rows: row indices in records
    # columns: row indices of other records if specified (e.g. of duplicate record)
    if (check.whole_row_check) and (check.inter_row):
        print fancyNewLine("-")
        print "Whole-row check report; inter-row"

        # Open report file handle
        report_filepath = os.path.join(out_dir, check.name+".csv")
        report_handle = open(report_filepath, 'w')
        report_writer = csv.writer(report_handle, delimiter=",")
        
        # Write description of check at top of spreadsheet.
        zeroth_row = ["Check" , check.description]
        report_writer.writerow(zeroth_row)

        # Write first row of report spreadsheet.
        first_row = ["row index", "other row index"]
        report_writer.writerow(first_row)

        # Add problematic row indices to report.
        for element in bad_elements:
            row_index = element[0]
            other_row_indices = element[1] # e.g. row indices of duplicate records.
            new_row = [row_index]
            new_row.extend(other_row_indices)
            
            report_writer.writerow(new_row)
        report_handle.close()
            


    # DAG-Instrument-Count report
    # report: 1 report
    # rows: site
    # columns: instrument
    # entries: count

    if dags_used and (not check.whole_row_check):
        print fancyNewLine("-")
        print "DAG-instrument-count Report"

        # Open report file handle. 
        report_filepath = os.path.join(out_dir, check.name+".csv")
        report_handle = open(report_filepath, 'w')
        report_writer = csv.writer(report_handle, delimiter=",")

        # Write description of check at top of spreadsheet.
        zeroth_row = ["Check", check.description]
        report_writer.writerow(zeroth_row)

        # Write first row of report spreadsheet.
        first_row = ["Site"]
        if (check.report_forms):
            for form in forms:
                form_label = form["instrument_label"]
                first_row.append(form_label)
        first_row.append("Rate (# cases found / # times check performed)")
        first_row.append("Subject rate (# subjects with condition / # subjects in DAG)")
        report_writer.writerow(first_row)

        # Initialize last row for totals.
        if (check.report_forms):
            last_row = [0]*(len(forms)+1)
        else:
            last_row = [None]
        last_row[0] = "Total"
        total_errors = 0
        total_checks = 0  
        total_subjects_with_errors = 0
        total_subjects = 0

        num_dags = len(dags)
        dag_index = 0
        for dag in dags:
            
            # Print progress
            sys.stdout.write('\r')
            sys.stdout.write('%.2f%% complete' % (float(dag_index)/float(num_dags)*1e2,))
            sys.stdout.flush()
            dag_index += 1
            
            form_column_index = 1 # column number corresponding to form

            num_errors_dag = 0
            new_row = [formatDAGName(dag)]
            for form in forms:
                form_name = form["instrument_name"] # Internal instrument name (e.g. 'patient_information')
                form_label = form["instrument_label"] # Online-displayed instrument name (e.g. 'Patient Information')
                num_errors_dag_form = 0
                for bad_element in bad_elements:                
                    bad_row_index = bad_element[0]
                    bad_field_name = bad_element[1]
                    bad_field = metadata[bad_field_name]
                    bad_dag = records[bad_row_index]["redcap_data_access_group"]
                    bad_form_name = bad_field.form_name
    
                    if bad_dag == dag:
                        if bad_form_name == form_name:
                            num_errors_dag_form += 1
                            num_errors_dag += 1
#                if (num_errors_dag_form != 0):
#                    print
#                    print Color.blue+"DAG:"+Color.end, dag
#                    print Color.blue+"form:"+Color.end, form_label
#                    print Color.blue+"count:"+Color.end, num_errors_dag_form
                if (check.report_forms):
                    new_row.append(num_errors_dag_form)
                
                    last_row[form_column_index] += num_errors_dag_form
                    form_column_index += 1

            # Calculate the error rate for the current dag.
            num_checks_performed_dag = 0 # Number of times this check was performed for this DAG.
            for element in elements_to_check:
                element_row_index = element[0]
                element_dag = records[element_row_index]["redcap_data_access_group"]
                if (dag == element_dag):
                    num_checks_performed_dag += 1
            if (num_checks_performed_dag == 0):
                error_rate = "N/A"
                new_row.append(error_rate)
            else:
                error_rate = float(num_errors_dag)/float(num_checks_performed_dag)
                new_row.append("{:.2f}".format(error_rate*100)+"%"+" ("+str(num_errors_dag)+"/"+str(num_checks_performed_dag)+")")

            total_errors += num_errors_dag
            total_checks += num_checks_performed_dag

            # Calculate the subject-wise error rate (number of patients with error in DAG/number of patients in DAG -- not the number checked)
            num_bad_records_in_dag = 0
            for record_id in dag_record_map[dag]["record_ids"]:
                for bad_element in bad_elements:
                    bad_row_index = bad_element[0]
                    bad_record_id = records[bad_row_index][def_field]
                    if (bad_record_id == record_id):
                        num_bad_records_in_dag += 1
                        break
            subject_wise_error_rate = float(num_bad_records_in_dag)/float(dag_record_map[dag]["num_records"])
            new_row.append("{:.2f}".format(subject_wise_error_rate*100)+"%"+" ("+str(num_bad_records_in_dag)+"/"+str(dag_record_map[dag]["num_records"])+")")
            
            total_subjects_with_errors += num_bad_records_in_dag
            total_subjects += dag_record_map[dag]["num_records"]

            # Add row for current DAG.
            report_writer.writerow(new_row)

        # Add total error rates in last row.
        if (total_checks == 0):
            error_rate = "N/A"
            last_row.append(error_rate)
        else:
            error_rate = float(total_errors)/float(total_checks)
            last_row.append("{:.2f}".format(error_rate*100)+"%"+" ("+str(total_errors)+"/"+str(total_checks)+")")            

        subject_wise_error_rate = float(total_subjects_with_errors)/float(total_subjects)
        last_row.append("{:.2f}".format(subject_wise_error_rate*100)+"%"+" ("+str(total_subjects_with_errors)+"/"+str(total_subjects)+")")                    

        report_writer.writerow(last_row)        

        # Close the report file handle.
        report_handle.close()

    # DAG-Subject-Instrument-Field report
    # report: site
    # rows: subject
    # columns: instrument
    # entries: fields
    if dags_used and project_longitudinal and project_repeating and (not check.whole_row_check):
        print fancyNewLine("-")
        print "DAG-subject-instrument-field Report:"
  
        # Create a subdirectory to store the site-specific reports.
        out_sub_dir = os.path.join(out_dir, "site-form-field")
        if (not os.path.isdir(out_sub_dir)):
            os.mkdir(out_sub_dir)

        # Create dict with DAG names as keys, and reports (lists) as entries.
        reports = {}
        tab_reports = {} #&&&&&&&&&&&&&& TAB REPORTS &&&&&&&&&&&&&&&

        # Write description of check at top of spreadsheet
        zeroth_row = ["Check", check.description]

        # Write column headers of reports.
        first_row = ["Patient"]

        form_event_column_map = {} # key is form name; elements are dicts; key of dicts are event names; elements are column numbers 
        form_event_column_index = 1 # First column is the record ID.
#        form_event_tab_map = {} #&&&&&&&&&&&&&& TAB REPORTS &&&&&&&&&&&&&&&
        for form in forms:
            form_name = form["instrument_name"]
            if (not form_name in ['patient_information', 'cardiac_and_arteriopathy_risk_factors', 'other_child_and_neonatal_risk_factors', 'maternal_pregnancy_and_delivery_risk_factors', 'arteriopathy_diagnosis_classification', 'clinical_presentation', 'clinical_investigations', 'prothrombotichypercoaguability_state', 'radiographic_features_at_presentation', 'treatment', 'tpa_specific_questions', 'additional_thromboembolic_events_during_initial_ho', 'status_at_discharge', 'post_discharge_followup', 'outcome', 'recovery_and_recurrence', 'patient_summary', 'acute_crf', 'follow_up_crf']):
                continue
            form_label = form["instrument_label"]
            form_event_column_map[form_name] = {}
#            form_event_tab_map[form_name] = {} #&&&&&&&&&&&&&& TAB REPORTS &&&&&&&&&&&&&&&&
            if (len(form_repetition_map[form_name]["events"]) > 1): # Specify event if form is in many events.
                for event in form_repetition_map[form_name]["events"]:
                    column_header = form_label+" ("+events[event]["event_name"]+")"
                    first_row.append(column_header)
                    
                    form_event_column_map[form_name][event] = form_event_column_index
#                    form_event_tab_map[form_name][event] = form_event_column_index #&&&&&&&&&&&&&& TAB REPORTS &&&&&&&&&&&&&&&&
                    form_event_column_index += 1

            else: # Do not specify event if form is only in one event.
                first_row.append(form_label)
                
                event = form_repetition_map[form_name]["events"][0]
                form_event_column_map[form_name][event] = form_event_column_index 
                form_event_column_index += 1
        num_form_event_pairs = form_event_column_index - 1
        num_columns = form_event_column_index

        # Add success rate column if check is performed multiple times for a single record.
        first_row.append("Rate (# cases found / # times check performed)")
        num_columns += 1
        
        # Add column for links to edit forms containing problematic fields.
#        first_row.append("Links")
#        num_columns += 1

        # Create a dictionary for each DAG which will later become a report spreadsheet.
        record_id_row_map = {}
        for dag in dags:
            reports[dag] = [zeroth_row]
            reports[dag].append(first_row)
            record_id_row_map[dag] = {"num_rows":2} # dict mapping record ID to row index; also keeps track of number of rows in DAG's report

        # Create a dictionary which stores the number of errors found for each record.
        record_id_num_errors = {}

        num_bad_elements = len(bad_elements)
        bad_element_index = 0

        # Build reports by sorting each bad entry.
        for bad_element in bad_elements:
            
            # Print progress
            sys.stdout.write('\r')
            sys.stdout.write('%.2f%% complete' % (float(bad_element_index)/float(num_bad_elements)*1e2,))
            sys.stdout.flush()
            bad_element_index += 1

            bad_row_index = bad_element[0]
            bad_field_name = bad_element[1]
            bad_row = records[bad_row_index]
            bad_field = metadata[bad_field_name]
            bad_record_id = bad_row[def_field]
            bad_dag = bad_row["redcap_data_access_group"]
            bad_event = bad_row["redcap_event_name"]
            bad_instance = bad_row["redcap_repeat_instance"]
            bad_form_name = bad_field.form_name
            
            # Incremenet the error count for the current record ID.
            if (bad_record_id in record_id_num_errors):
                record_id_num_errors[bad_record_id] += 1
            else:
                record_id_num_errors[bad_record_id] = 1

            # Check whether record ID already has a row in a report, otherwise determine the row index for the current record ID and add empty row to report.
            if (not bad_record_id in record_id_row_map[bad_dag]): # if record ID does not have a row
                record_id_row_map[bad_dag][bad_record_id] = record_id_row_map[bad_dag]["num_rows"]
                reports[bad_dag].append([""]*(num_form_event_pairs+2)) # Add list with length equal to number of columns.
                reports[bad_dag][-1][0] = bad_record_id # Set first element in row to the record ID.
                record_id_row_map[bad_dag]["num_rows"] += 1
            report_row_index = record_id_row_map[bad_dag][bad_record_id]
            
            # Get column index for current entry.
            report_column_index = form_event_column_map[bad_form_name][bad_event]
 
            # Set the marker for the entry in the report. # ASSUMES LONGITUDINAL PROJECT WITH REPEATING FORMS.
            if (not check.specify_fields):
                entry_marker = formatFieldName(bad_field_name, metadata) # Mark the error in the report with this string.
                link = "https://redcapexternal.research.sickkids.ca/redcap_v8.11.2/DataEntry/index.php"
                project_id = str(project_info["project_id"])
                event_id = events[bad_event]["event_id"]
                if (not event_id == None):
                    link += "?pid="+project_id+"&page="+bad_form_name+"&event_id="+event_id+"&id="+bad_record_id
                    if (not bad_instance == ""):
                        link += "&instance="+str(bad_instance)
                else:
                    link = None

                # Append the instance number to the marker if the form is repeating.
                if (bad_instance != ""):
                    entry_marker += " (#"+str(bad_instance)+")"

#            elif (not check.inter_row):
            else: # if check.specify_fields
                # THIS COULD BE COMPLICATED FOR INTER-EVENT/INSTANCE CHECKS.
                entry_marker_dict = {} # key is target_field_name; item is dict with information required to mark the field in the report.
                checkbox_fields_printed = [] # list of checkboxes which have already been printed to the report (don't report all options).
                for target_field_name in check.target_fields:
                    if (not target_field_name in checkbox_fields_printed):
                        target_entry_marker = formatFieldName(target_field_name, metadata)
                        target_form_name = metadata[target_field_name].form_name

                        # Append the instance number to the marker if the form is repeating.
                        if (bad_instance != ""):
                            target_entry_marker += " (#"+str(bad_instance)+")"
                        
                        checkbox_fields_printed.extend(metadata[target_field_name].choices)
                        
#                        target_link = None
                        target_link = "https://redcapexternal.research.sickkids.ca/redcap_v8.11.2/DataEntry/index.php"
                        project_id = str(project_info["project_id"])
                        event_id = events[bad_event]["event_id"]
                        if (not event_id == None):
                            target_link += "?pid="+project_id+"&page="+target_form_name+"&event_id="+event_id+"&id="+bad_record_id
                            if (not bad_instance == ""):
                                target_link += "&instance="+str(bad_instance)
                        else:
                            target_link = None

                        entry_marker_dict[target_field_name] = {}
                        entry_marker_dict[target_field_name]["target_entry_marker"] = target_entry_marker
                        entry_marker_dict[target_field_name]["target_form_name"] = target_form_name
                        entry_marker_dict[target_field_name]["target_link"] = target_link

#            else: # ADD HANDLING OF INTER-EVENT/INSTANCE CHECKS.
#                entry_marker = "X"
#                link = None
#
#                # Append the instance number to the marker if the form is repeating.
#                if (bad_instance != ""):
#                    entry_marker += " (#"+str(bad_instance)+")"

            if (not check.specify_fields):
                # Add entry for current bad entry to correct report, row, and column.
                if (reports[bad_dag][report_row_index][report_column_index] == ""):
                    reports[bad_dag][report_row_index][report_column_index] = entry_marker
                else:
                    reports[bad_dag][report_row_index][report_column_index] += ", "+entry_marker
    
                # ADD LINK TO THE END OF THE ROW IN FORMAT form [(event name)] [(instance number)]
                if False:
#                if (link != None):
                    hyperlink_friendly_name = reports[bad_dag][1][report_column_index]
                    if (bad_instance != ""):
                        hyperlink_friendly_name += " (#"+str(bad_instance)+")"
                    hyperlink = '=HYPERLINK("'+link+'","'+hyperlink_friendly_name+'")'
                    if (not hyperlink in reports[bad_dag][report_row_index][num_form_event_pairs+1:]):
                        reports[bad_dag][report_row_index].append(hyperlink)
                        num_columns += 1

#            elif (not check.inter_row): # if specifying fields, put entry for each target field.
            else:
                for target_field_name in entry_marker_dict:
                    target_entry_marker = entry_marker_dict[target_field_name]["target_entry_marker"]
                    target_form_name = entry_marker_dict[target_field_name]["target_form_name"]
                    target_link = entry_marker_dict[target_field_name]["target_link"]

                    # Determine the column in which the entry should go.
                    target_report_column_index = form_event_column_map[target_form_name][bad_event]

                    # Add entry for current bad entry to correct report, row, and column.
                    if (reports[bad_dag][report_row_index][target_report_column_index] == ""):
                        reports[bad_dag][report_row_index][target_report_column_index] = target_entry_marker        
                    else:
                        reports[bad_dag][report_row_index][target_report_column_index] += ", "+target_entry_marker
        
                    # ADD LINK TO THE END OF THE ROW IN FORMAT form [(event name)] [(instance number)]
                    if (target_link != None):
                        hyperlink_friendly_name = reports[bad_dag][1][target_report_column_index]
                        if (bad_instance != ""):
                            hyperlink_friendly_name += " (#"+str(bad_instance)+")"
                        hyperlink = '=HYPERLINK("'+target_link+'","'+hyperlink_friendly_name+'")'
                        if (not hyperlink in reports[bad_dag][report_row_index][num_form_event_pairs+1:]):
                            reports[bad_dag][report_row_index].append(hyperlink)
                            num_columns += 1
#            else: # if inter-row
#                # Add entry for current bad entry to correct report, row, and column.
#                if (reports[bad_dag][report_row_index][report_column_index] == ""):
#                    reports[bad_dag][report_row_index][report_column_index] = entry_marker
#                else:
#                    reports[bad_dag][report_row_index][report_column_index] += ", "+entry_marker
#    
#                # ADD LINK TO THE END OF THE ROW IN FORMAT form [(event name)] [(instance number)]
#                if (link != None):
#                    hyperlink_friendly_name = reports[bad_dag][1][report_column_index]
#                    if (bad_instance != ""):
#                        hyperlink_friendly_name += " (#"+str(bad_instance)+")"
#                    hyperlink = '=HYPERLINK("'+link+'","'+hyperlink_friendly_name+'")'
#                    if (not hyperlink in reports[bad_dag][report_row_index][num_form_event_pairs+1:]):
#                        reports[bad_dag][report_row_index].append(hyperlink)
#                        num_columns += 1                

        # Calculate the number of times the check was performed for each record ID.
        record_id_num_checks = {} # key is record ID; element is number of times checks performed for record
        for element in elements_to_check:
            element_row_index = element[0]
            element_record_id = records[element_row_index][def_field]
            if (element_record_id in record_id_num_checks):
                record_id_num_checks[element_record_id] += 1
            else:
                record_id_num_checks[element_record_id] = 1

        # Write the report for each DAG. Also calculate the error rate for each record in this step.
        for dag in reports:
            if (record_id_row_map[dag]["num_rows"] > 2): # if errors found for this DAG.
                formatted_dag = formatDAGName(dag)
                report_filepath = os.path.join(out_sub_dir, check.name+"-"+formatted_dag+".csv")
                report_handle = open(report_filepath, "w")
                report_writer = csv.writer(report_handle, delimiter=",")
                for row in reports[dag][:2]: # Write first two rows.
                    report_writer.writerow(row)
                for row in reports[dag][2:]: # Write the rest of the rows.
                    record_id = row[0]
                    num_errors = record_id_num_errors[record_id]
                    num_checks = record_id_num_checks[record_id]
                    error_rate_record = float(num_errors)/float(num_checks)
                    row[num_form_event_pairs+1] = "{:.2f}".format(error_rate_record*100)+"%"+" ("+str(num_errors)+"/"+str(num_checks)+")"

                    # Reorder the links to match the column headers. The instance number appear to be sorted already.
                    # NOW APPEARS UNNECESSARY SINCE metadata IS AN OrderedDict
                    # NOW IT APPEARS NECESSARY SINCE FIELD-SPECIFYING CHECKS WON'T NECESSARILY PRINT FIELDS IN ORDER.
                    links_unsorted = row[num_form_event_pairs+2:]
                    links_sorted = []
                    for column_header in reports[dag][1][1:num_form_event_pairs+1]:
                        for link in links_unsorted:
                            if column_header in link:
                                if (not link in links_sorted):
                                    links_sorted.append(link)
                    row[num_form_event_pairs+2:] = links_sorted[:]

                    report_writer.writerow(row)
                report_handle.close()
    return
