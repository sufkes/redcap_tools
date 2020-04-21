from exportRecords import exportRecords
import redcap # PyCap
from more_itertools import unique_everseen

def getRecordIDList(api_url, api_key):
    """Generate a list of record IDs in a REDCap project, without duplicates."""

    def_field = redcap.Project(api_url, api_key).def_field

    record_ids_all = exportRecords(api_url, api_key, fields=[def_field], quiet=True)
    record_ids_all = [r[def_field] for r in record_ids_all]
    record_ids_all = list(unique_everseen(record_ids_all))    
    return record_ids_all
