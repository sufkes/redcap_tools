#!/usr/bin/env python

import sys
import glob

## Combine site-specific reports output by the QC script.
# Usage:
# combineSiteReports.py REPORT_PREFIX
#
# where:
#   REPORT_PREFIX : file path prefix that appears in all the files to be combined.
#


search_prefix = str(sys.argv[1])
report_list = glob.glob(search_prefix+"*")

wrote_header = False
for report in report_list:
    if (not wrote_header):
        master_report = open(search_prefix+'_all_sites.csv','wb')
        with open(report,'r') as handle:
            master_report.writelines(handle.readlines())
        wrote_header = True
    else:
        with open(report,'r') as handle:
            master_report.writelines(handle.readlines()[2:])

master_report.close()
