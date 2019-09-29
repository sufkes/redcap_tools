def createDAGRecordMap(def_field, records, record_id_map, dags_used, dags):
    """This function creates a dictionary with information about each data access group, including 
    the records in the DAG and the number of records in the DAG."""

    if (dags_used) and (len(dags) > 0):
        dag_record_map = {} # dict with dag names as keys
        for dag in dags:
            dag_record_map[dag] = {}
            dag_record_map[dag]["record_ids"] = [] # list of records that are in the DAG

        for record_id, record_row_indices in record_id_map.iteritems(): # put each record ID in the dict for the current DAG.
            record_row_index = record_row_indices[0] # the first row corresponding to the current record ID
            record_dag = records[record_row_index]["redcap_data_access_group"]
            dag_record_map[record_dag]["record_ids"].append(record_id)
        
        for dag in dags:
            dag_record_map[dag]["num_records"] = len(dag_record_map[dag]["record_ids"])
    else:
        dag_record_map = None
    return dag_record_map
