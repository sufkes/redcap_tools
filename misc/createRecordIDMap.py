def getRecordIDs(def_field, records):
    record_ids = []
    for row_index in range(len(records)):
        record_id = records[row_index][def_field]
        if (not record_id in record_ids):
            record_ids.append(record_id)
    return record_ids

def createRecordIDMap(def_field, records):
    record_id_map = {}
    record_ids = getRecordIDs(def_field, records)
    for record_id in record_ids:
        record_id_map[record_id] = []
    for row_index in range(len(records)):
        record_id = records[row_index][def_field]
        record_id_map[record_id].append(row_index)
    return record_id_map
