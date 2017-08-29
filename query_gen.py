import json, re, operator
from parser.lc_quad_linked import LC_Qaud_Linked
from jerrl.jerrl import Jerrl


def prepare_dataset(ds):
	ds.load()
	ds.parse()
	return ds

if __name__ == "__main__":
	jerrl = Jerrl()
	i=0
	no_answer = 0
	ds = LC_Qaud_Linked(path = "./data/LC-QUAD/linked_answer3.json")
	tmp = []
	for qapair in prepare_dataset(ds).qapairs:
		results = jerrl.do(qapair)
		# if len(results) != 2:
		# 	continue
		# sparql = qapair.sparql
		# print qapair.question.text
		# print qapair.question_template(results)
		# print sparql.where_clause
		if qapair.answers is None or len(qapair.answers) == 0:
			no_answer += 1
		# print qapair.answers
		# print "--"
		
		i+=1
		# if i > 10:
		# 	break
	print no_answer, i