import json, re, operator
from parser.lc_quad_linked import LC_Qaud_Linked
from jerrl.jerrl import Jerrl


def prepare_dataset(ds):
	ds.load()
	ds.parse()
	return ds

if __name__ == "__main__":
	jerrl = Jerrl()
	for qapair in prepare_dataset(LC_Qaud_Linked()).qapairs:
		print jerrl.do(qapair)
		break
	
