#!/usr/bin/env python
# -*- coding: utf-8 -*-
# To test this file, run:
# $ python ccr_cluster_1.1.py
# And then in a browser, enter the URL:
#   http://localhost:5000/cluster?InpFile=data/ccr1.csv&OutFile=ccr1.1_05.txt&NumTopic=5
import sys, time
time1 = time.time()
import Next_CCR
from gensim import corpora, models, similarities
import logging
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

from Stopwords import clean_text, clean_words
import jieba
# jieba.load_userdict("userdict.txt") # will use self-built dict.
# jieba.set_dictionary('TermFreq-utf8.txt') # did not work on 2015/10/21
# jieba.add_word('壞人');jieba.add_word('細菌'); # did not work

# The next 3 lines are required for jieba to initialize. It takes 3 to 4 seconds.
text = "This is a test.測試。"
words = jieba.lcut(clean_text(text)) # https://github.com/fxsjy/jieba
words = clean_words(words)
print("It takes %1.2f seconds to load packages"%(time.time()-time1))

from flask import Flask, request, jsonify
app = Flask(__name__)

def Maxi(doc): 
# doc= [(0, 0.2536), (1, -0.1903), (2, 0.1874), (3, -0.0720), (4, 0.1475)]
	maxi = -100000.0; i = -1
	for (j, coef) in doc:
		if maxi < abs(coef):
			maxi = abs(coef)
			i = j
	return i

def Output_to_File(dic, UserID, time2, OutFile):
    f = open(OutFile, "w")
    f.write("GroupID\tUserID\tEmail\tContent\n")
    for groupID, DocID in dic.items():
        for ID in DocID:
            (email, content) = UserID[ID]
            #f.write("%d\t%d\t%s\t%s\n" % (groupID, ID, email, content))
# Next line is for Yan to use
            f.write("%d[Θ]%d[Θ]%s[Θ]%s\n" % (groupID, ID, email, content))
        f.write("\t\t\t\n")
    f.close()
#    return jsonify ({'message':'OK'})
    return("It takes %1.2f seconds."%(time.time()-time2))

def Output_to_HTML(dic, UserID, time2):
#    out = "<p>GroupID\tUserID\tEmail\tContent<br>\n"
# Next line is for Yan to use
    out = "GroupID\tUserID\tEmail\tContent\n"
    for groupID, DocID in dic.items():
        for ID in DocID:
            (email, content) = UserID[ID]
            #out += "%d\t%d\t%s\t%s<br>\n" % (groupID, ID, email, content)
# Next line is for Yan to use
            out += "%d[Θ]%d[Θ]%s[Θ]%s\n" % (groupID, ID, email, content)
        out += "\t\t\t\n"
#        out += "\t\t\t<br>\n"
#    return jsonify ({'message':'OK'})
    return out

# Initialize the 3 variables:
(NumTopic, InpFile, OutFile) = (5, 'data/ccr1.csv', 'ccr1.1-05.txt')

# See: https://medium.com/@twilightlau94/rest-apis-with-flask-%E7%B3%BB%E5%88%97%E6%95%99%E5%AD%B8%E6%96%87-1-5405216d3166
@app.route('/cluster' , methods=['POST', 'GET'])
def cluster_by_post():
# None of the next 3 methods work!
#    WebIn = request.get_json(force=True, silent=True)
#    WebIn = request.get_data( as_text=True)
#    NumTopic = request.form['NumTopic']
    NumTopic = request.args.get('NumTopic')
    InpFile = request.args.get('InpFile')
    OutFile = request.args.get('OutFile')
    return ccr_cluster(NumTopic, InpFile, OutFile)

def ccr_cluster(NumTopic, InpFile, OutFile):
    time2 = time.time()
    NumTopic = int(NumTopic)
    nxtd = Next_CCR.Next_CCR(InFile=InpFile)
    i = 0
    texts = []; UserID = []
    for email, content in nxtd:
    	i += 1
    	UserID.append((email, content)) # append a tuple for later use
    	#print "%d : %s : %s\n" % (i, email, content)
    	words = jieba.lcut(clean_text(content)) # see https://github.com/fxsjy/jieba
    	text = clean_words(words) # 2018/09/19
    	texts.append(text)
    sys.stderr.write("There are %d documents" % i)
#    from pprint import pprint   # pretty-printer
#    pprint(texts) # [u'\u8ddf', u'\u6211', u'\u540c\u5b78', u'\u597d\u50cf'],
    dictionary = corpora.Dictionary(texts)
#    dictionary.save('./ccr.dict') # store the dictionary, for future reference
#    print(dictionary) # => Dictionary(12 unique tokens)
#   print(dictionary.token2id) #; exit()

    corpus = [dictionary.doc2bow(text) for text in texts]
    #corpora.MmCorpus.serialize('./ccr.mm', corpus) # store to disk, for later use
#   print(corpus) #; exit()

    tfidf = models.TfidfModel(corpus) # initialize a model
    corpus_tfidf = tfidf[corpus] # use the model to transform vectors
#   #for doc in corpus_tfidf:    print(doc)

    # initialize an LSI transformation
    lsi = models.LsiModel(corpus_tfidf, id2word=dictionary, num_topics=NumTopic) 
#   lsi.print_topics(NumTopic) # the above line will print the same thing using logging

    # create a double wrapper over the original corpus: bow->tfidf->fold-in-lsi
    corpus_lsi = lsi[corpus_tfidf] 
    from collections import defaultdict
    dic = defaultdict(list) # value is a list
    i=-1
    for doc in corpus_lsi: # both bow->tfidf and tfidf->lsi transformations are actually executed here, on the fly
        i += 1 # DocID
        maxi = Maxi(doc)
        dic[maxi].append(i) # append DocID to group maxi
#        print(maxi, doc)
#   dic.items()
#   exit()
    out = '' # a string to be returned to the calling URL
#    out = Output_to_File(dic, UserID, time2, OutFile)
    out += Output_to_HTML(dic, UserID, time2)
    return out

if __name__ == "__main__":
    if len(sys.argv) == 4:
        (NumTopic, InpFile, OutFile) = (sys.argv[1], sys.argv[2], sys.argv[3])
    if len(sys.argv) == 3:
        (NumTopic, InpFile) = (sys.argv[1], sys.argv[2])
    elif len(sys.argv) == 2:
        (NumTopic) = (sys.argv[1])
    else:
        pass
    #ccr_cluster(NumTopic, InpFile, OutFile)
    #print("It takes %1.2f seconds."%(time.time()-time1))
    app.run(port=5000, debug=True)
