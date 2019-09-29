def modifyRecords(records):
    """This script takes all of the records exported from IPSS version 3, and returns the same records 
    modified to match the format of """
    
    for row in records:
        #### Patient information
        
        # originalipss___1 -> originalipss
        old_key = 'originalipss___1'
        new_key = 'originalipss'
        if (row[old_key] == '1'):
            new_val = '1'
        elif (row[old_key] == '0'):
            new_val = '0' # Assume blank is 'no' in this special case.
        if (not new_key in row): # * * * factor this section?
            row[new_key] = new_val
            del row[old_key]
        else:
            print "ERROR: new_key already exists in records. Pick a different name."
            
    return
