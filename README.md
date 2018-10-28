# CCR_Cluster

This is the module used in https://ccr.tw/.

This version of CCR clustering code is far faster than the old one (not public).

## Preparation:
1. Get this repository to a local folder by 'git clone' or by download.
2. This module contains the following files:
```
    ccr_cluster_1.1.py : the clustering algorithm from 
                    https://radimrehurek.com/gensim/tutorial.html
    Next_CCR.py : to read next line from the input file
    Stopwords.py : to remove stopwords in the responses (language dependent)
    ReadMe.md : this file
    data/ccr1.csv : Chinese responses to be clustered
    data/ccr2.csv : simple English responses to show the clustering result
    data/ccr3.csv : example sentences from 
                    Deerwester et al. (1990): Indexing by Latent Semantic Analysis
                    http://www.cs.bham.ac.uk/~pxt/IDA/lsa_ind.pdf
                    to show the clustering result
```
3. Under the command line in that folder, install some packages by running:
```
   $ pip install jieba
   $ pip install gensim
   $ pip install flask
```

## Run the clustering Web server:
1. Under the command line, run:
   $ nohup python ccr_cluster_1.1.py &
   The above command would run the ccr_cluster_1.1.py as a Web server 
   (at port 5000) in the background process. You may then run:
```
   $ ps
```
   to see if it is running.
2. ccr_cluster_1.1.py now is waiting for a client (browser) to 
   feed in the input file and number of topics.
   So, in a browser, enter the URL (or in your PHP code, issue an URL):
   http://localhost:5000/cluster?InpFile=data/ccr2.csv&NumTopic=2
   you will get the clustered result from the HTTP response string.
   To view the clustered result, it's better to examine the source:
   view-source:http://localhost:5000/cluster?InpFile=data/ccr2.csv&NumTopic=2
3. You may change the values of InpFile and NumTopic for your need.
4. You may fetch this URL in your own program.
5. You may change the code segment in ccr_cluster_1.1.py:
```python
    #out = Output_to_File(dic, UserID, time2, OutFile)
    out += Output_to_HTML(dic, UserID, time2)
```
into:
```python
    out = Output_to_File(dic, UserID, time2, OutFile)
    out += Output_to_HTML(dic, UserID, time2)
```
to tell ccr_cluster_1.1.py to write the result to OutFile.
In this case, your URL would look like:
http://localhost:5000/cluster?InpFile=data/ccr2.csv&OutFile=ccr2_2.txt&NumTopic=2
and you'll get the result either in the OutFile or from the http response.
