import sys

def dateToNum(date_string, date_format):
    """This function converts a date stored in a REDCap text field with date type
    validation to a number. E.g. it converts the string 2001-09-11 to the number
    20010911. If the input string is not the expected size, or the validation type
    is not one of the REDCap options, an error is raised."""
    if (len(date_string) == 10): # if date string unexpected size
        if (date_format == "date_ymd"):
            # 2001-09-11
            year  = date_string[:4]
            month = date_string[5:7]
            day   = date_string[8:]
        elif (date_format == "date_dmy"):
            # 11-09-2001
            year  = date_string[6:]
            month = date_string[3:5]
            day   = date_string[:2]
        elif (date_format == "date_mdy"):
            # 09-11-2001
            year  = date_string[6:]
            month = date_string[:2]
            day   = date_string[3:5]
        else:
            print "ERROR IN dateToNum(): Unrecognized date format"
            sys.exit()
    else:
        print len(date_string)
        print "ERROR IN dateToNum(): Input date string incorrect size"
        sys.exit()
    date_string_proper = year+month+day
    date_num = int(date_string_proper)
    return date_num

def compareDates(metadata, records, field_name_1, field_name_2, row_index_1, row_index_2=None, comparison="eq"):
    """Compare two dates. If one of the dates is blank, the comparison is assumed
    false. This choice was made because other checks identify blank fields.

    Options for 'comparison' argument:

    equal: date1 == date2
    less : date1 < date2
    more : date1 > date2
    """

    # If a second row index is not specified, assume the comparison is within the first row.
    if (row_index_2 == None):
        row_index_2 = row_index_1

    # Get row data.
    row_1 = records[row_index_1]
    row_2 = records[row_index_2]

    # Get date strings.
    date_string_1 = row_1[field_name_1]
    date_string_2 = row_2[field_name_2]

    # Get date format (e.g. YYYY-MM-DD).
    date_format_1 = metadata[field_name_1].text_validation_type
    date_format_2 = metadata[field_name_2].text_validation_type

    # Only compare dates if both are not empty:
    if (date_string_1 != "") and (date_string_2 != ""):
        # Assign variable indicating no blanks fields.
        blanks = False
        
        # Convert the dates to numbers:
        date_num_1 = dateToNum(date_string_1, date_format_1)
        date_num_2 = dateToNum(date_string_2, date_format_2)

        # Compare dates
        if (comparison == "e"):
            truth = (date_num_1 == date_num_2)
        elif (comparison == "l"):
            truth = (date_num_1 < date_num_2)
        elif (comparison == "le"):
            truth = (date_num_1 <= date_num_2)
        elif (comparison == "g"):
            truth = (date_num_1 > date_num_2)
        elif (comparison == "ge"):
            truth = (date_num_1 >= date_num_2)
        else: 
            print "ERROR IN compareDates(): Unrecognized comparison type."
    else: # If one of the dates is blank, assume relationship false.
        blanks = True
        truth = None # note: Python treats None as False.
    return truth, blanks
