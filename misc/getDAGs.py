def getDAGs(records):
    dags_used = False
    if (len(records) == 0):
        dags_used = False
        dags = []
    else:
        for row_index in range(len(records)):
            try: # Check if DAG keys exist.
                records[row_index]["redcap_data_access_group"]
                dags_used = True
                break # Stop looking once a single DAG key is found.
            except KeyError: 
                dags_used = False
                dags = None
        if (dags_used):
            dags = []
            for row_index in range(len(records)):
                dag = records[row_index]["redcap_data_access_group"].strip()
                if (not dag in dags): # Append DAG to list of DAGs if it is not already added.
                    dags.append(dag)
            if (len(dags) == 0): # If DAG key exists but no DAGs were found.
                dags = None
            else:
                dags = sorted(dags)

    return dags_used, dags
