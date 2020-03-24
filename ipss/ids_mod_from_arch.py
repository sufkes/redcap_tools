import os
script_dir = os.path.dirname(os.path.realpath(__file__))
file_path = os.path.join(script_dir, 'ids_mod_from_arch.txt')
with open(file_path,'rb') as fh:
    ids_mod_from_arch = fh.readlines()
    ids_mod_from_arch = [id.rstrip('\n') for id in ids_mod_from_arch]
