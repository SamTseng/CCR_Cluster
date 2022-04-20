#!/usr/bin/env python
# -*- coding: utf-8 -*-
# On 2019/01/21
#   1. Copy ccr_cluster_1.1.py to ccr_cluster_1.2.py
#   2. Edit ccr_cluster_1.2.py to add cluster descriptors for each cluster.
#   3. Then follow the README.md to run the test.
# To test this file, run:
# $ python ccr_cluster_1.2.py
# And then in a browser, enter the URL:
#   http://localhost:5000/cluster?InpFile=data/ccr1.csv&OutFile=ccr1.1_05.txt&NumTopic=5
import sys, time
time1 = time.time()
from collections import defaultdict
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
#	if maxi < 0.15: i = -1
	return i

def Output_to_File(dic, CluDes, UserID, time2, OutFile):
    f = open(OutFile, "w")
    f.write("GroupID\tUserID\tEmail\tContent\n")
    for groupID, DocID in dic.items():
        if groupID in CluDes:
            f.write("%d\t%s\t\t\n"%(groupID, CluDes[groupID]))
        else:
            f.write("%d\t\t\t\n"%groupID)
        for ID in DocID:
            (email, content) = UserID[ID]
            #f.write("%d\t%d\t%s\t%s\n" % (groupID, ID, email, content))
# Next line is for Yan to use
            f.write("%d[Θ]%d[Θ]%s[Θ]%s\n" % (groupID, ID, email, content))
        f.write("\t\t\t\n")
    f.close()
#    return jsonify ({'message':'OK'})
    return("It takes %1.2f seconds."%(time.time()-time2))

def Output_to_HTML(dic, CluDes, UserID, time2):
#    out = "<p>GroupID\tUserID\tEmail\tContent<br>\n"
# Next line is for Yan to use
    out = "GroupID\tUserID\tEmail\tContent\n"
    for groupID, DocID in dic.items():
        if groupID in CluDes:
            out += "%d\t%s\t\t\n"%(groupID, CluDes[groupID])
        else:
            out += "%d\t\t\t\n"%groupID
        for ID in DocID:
            (email, content) = UserID[ID]
            #out += "%d\t%d\t%s\t%s<br>\n" % (groupID, ID, email, content)
# Next line is for Yan to use
            out += "%d[Θ]%d[Θ]%s[Θ]%s\n" % (groupID, ID, email, content)
        out += "\t\t\t\n"
#        out += "\t\t\t<br>\n"
#    return jsonify ({'message':'OK'})
    return out

def RemoveLowHighFrequencyTerms(texts):
    frequency = defaultdict(int)
    for text in texts:
        for term in text:
            frequency[term] += 1
    DF_max = int(0.7 * len(texts))
    texts = [[token for token in text 
                if frequency[token] > 1 and frequency[token] < DF_max]
             for text in texts]
    return texts

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

def LSI(corpus, dictionary, NumTopic):
	tfidf = models.TfidfModel(corpus) # step 1 -- initialize a model
	corpus_tfidf = tfidf[corpus] # step 2 -- use the model to transform vectors
#	for doc in corpus_tfidf:    print(doc)
	# initialize an LSI transformation
	lsi = models.LsiModel(corpus_tfidf, id2word=dictionary, num_topics=NumTopic) 
##	lsi.print_topics(NumTopic) # the above line will print the same thing using logging
	# create a double wrapper over the original corpus: bow->tfidf->fold-in-lsi
	corpus_lsi = lsi[corpus_tfidf] 
#	for doc in corpus_lsi: print doc # both bow->tfidf and tfidf->lsi transformations are actually executed here, on the fly
#	lsi.print_topics(NumTopic) # same as using logging
	return lsi, corpus_lsi

# LDA leads to unstable clusters. So do not use LDA
def LDA(corpus, dictionary, NumTopic):
#	lda = models.ldamodel.LdaModel(corpus, id2word=dictionary, num_topics=NumTopic, passes=5)
	lda = models.LdaModel(corpus, id2word=dictionary, num_topics=NumTopic, passes=5)
	corpus_lda = lda[corpus] # infer topic distributions on the same corpus
#	lda.show_topics(num_topics=NumTopic) #, num_words=10, log=False, formatted=True)
# The following segment does print out topic distribution 
#	i=0 # for the given document bow, as a list of 
#	for bow in corpus: # (topic_id, topic_probability) 2-tuples
#		print i, lda.get_document_topics(bow)
#		i+=1
	return lda, corpus_lda

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
        # see https://github.com/fxsjy/jieba
        words = jieba.lcut(clean_text(content), cut_all=False) 
    	#words = jieba.lcut(clean_text(content), cut_all=True) 
    	#words = jieba.lcut_for_search(clean_text(content)) 
        text = clean_words(words) # 2018/09/19
        texts.append(text)
    sys.stderr.write("There are %d documents" % i)
    texts = RemoveLowHighFrequencyTerms(texts)
#    from pprint import pprint   # pretty-printer
#    pprint(texts) # [u'\u8ddf', u'\u6211', u'\u540c\u5b78', u'\u597d\u50cf'],
    dictionary = corpora.Dictionary(texts)
#    dictionary.save('./ccr.dict') # store the dictionary, for future reference
#    print(dictionary) # => Dictionary(12 unique tokens)
#   print(dictionary.token2id) #; exit()

    corpus = [dictionary.doc2bow(text) for text in texts]
    #corpora.MmCorpus.serialize('./ccr.mm', corpus) # store to disk, for later use
#   print(corpus) #; exit()


# After we have dictionary and corpus, now build the model
    model, corpus_model = LSI(corpus, dictionary, NumTopic)
#    corpus_model = LDA(corpus, dictionary, NumTopic) # do not use this
    TP = model.show_topics(num_topics=NumTopic, num_words=5)
    #return("TP:"+str(TP)); exit()
    CluDes = {k:GT(v) for (k, v) in TP}

    dic = defaultdict(list) # value is a list
    for i, doc in enumerate(corpus_model): 
    # both bow->tfidf and tfidf->lsi transformations are actually executed here, on the fly
        maxi = Maxi(doc)
        dic[maxi].append(i) # append DocID to group maxi
#        print(maxi, doc)
#   dic.items()
#   exit()

    out = '' # a string to be returned to the calling URL
#    out = Output_to_File(dic, CluDes, UserID, time2, OutFile)
    out += Output_to_HTML(dic, CluDes, UserID, time2)
    return out

def GT(vts): # vts : '1.000*"thank" + 0.000*"good" + 0.000*"morn"'
    T = []
    for vt in vts.split(' + '):
        (v, t) = vt.split('*')
        if float(v)>0.01:  T.append(t)
    return ', '.join(T)


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
