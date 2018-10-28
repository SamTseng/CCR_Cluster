#/usr/bin/env python
# -*- coding: utf-8 -*-
# Written by Sam Tseng on 2015/09/02
# This program takes me 2 hours to code and it works!
# On 2015/10/21 rewrite from /Users/sam/data_exp/Corpora/word2vec/NextDoc.py 

import sys, re

class Next_CCR():
	'''
	Given a file containing multiple documents in CSV format, 
	return a document each time nextdoc() is called.
	So far this class is only for the download CSV format from CCR
	'''
	def __init__(self, InFile='ccr1.csv', delimiter='\n'):
		self.fn = InFile
		self.delimiter = delimiter
		try:
			self.fh = open(InFile)
		except IOError:
			sys.stderr.write("Cannot read file:'%s'" % InFile)
#		(self.isTitle, self.did, self.dtitle, self.content) = (0, '', '', '')
		(self.email, self.content) = ('', '')

	def __iter__(self):
		for line in self.fh.readlines():
			LI = line.split("\",\"") # "姓名","學號","信箱","回答的問題"
			if len(LI) < 4 : 
				LI = line.split("\t") # on 2015/12/03
				if len(LI) < 4: continue
			m = re.search(r'@(\w|\d)+\.(\w|\d)+', LI[2])
			if m:
				yield (LI[2], LI[3].rstrip("\",\n"))
			else:
				sys.stderr.write( "invalide email: '%s'" % line)
		
if __name__ == "__main__":
	'''
	import Next_CCR
	nxtd = Next_CCR.NextDoc(InFile='data/ccr1.csv')
	for email, content in nxtd:
		print("%d : %s : %s\n" % (i, email, content))
	'''
	nxtd = Next_CCR(InFile='data/ccr1.csv')
	i = 1
	for email, content in nxtd:
#		print"%d : %s : %s" % (i, email, content) # 2018/09/19
		print("%d : %s : %s" % (i, email, content)) # 2018/09/19
		i+=1
