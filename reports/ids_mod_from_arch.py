with open('ids_mod_from_arch.txt','r') as fh:
    ids_mod_from_arch = fh.readlines()
    ids_mod_from_arch = [id.rstrip('\n') for id in ids_mod_from_arch]
