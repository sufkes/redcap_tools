#!/usr/bin/env python

# Chloe wants the SIPS final missing data reports in the following format:
# - 1 file per site (i.e. missing variables from IPSS and SIPS II on same sheet; cohort I and cohort II patients on same sheet).
# - 1 row per patient
# - list of variable names sorted into columns by instrument, as usual
# - no links (they are there by default; I would need to remove them, which is fine)

# This is an ad hoc script to do that.

import os, sys
import csv
os.chdir('/Users/steven ufkes/Documents/stroke/redcap_qc/sips_final/site-form-field') for sipsfinal

path_list = os.listdir('.')

site_list = set()
for path in path_list:
    site = path.split('-')[-1].split('.')[0]
    site_list.add(site)

# Loop over all DAGs.
for site in site_list:

    master_site_report_name =  "all_"+site+".csv"
    
    # Build list of check report paths.
    report_path_list = []
    for check in ['cohort1_sips2_fields', 'cohort2_sips2_fields', 'cohort1_ipss_fields', 'cohort2_ipss_fields']:
        report_path = check+"-"+site+'.csv'
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

