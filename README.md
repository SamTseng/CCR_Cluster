# CCR_Cluster

This is the module used in https://ccr.tw/.

This version of CCR clustering code is far faster than the old one (not public).

## Preparation:
1. Get this repository to a local folder by 'git clone' or by download.
2. This module contains the following files:
```
    ccr_cluster_1.1.py : the clustering algorithm based on LSI from 
                    https://radimrehurek.com/gensim/tutorial.html.
    Next_CCR.py : to read next line from the input file.
    Stopwords.py : to remove stopwords in the responses (language dependent).
    ReadMe.md : this file.
    data/ccr1.csv : Chinese responses to be clustered.
    data/ccr2.csv : simple English responses to show the clustering result.
    data/ccr3.csv : example sentences from 
                    Deerwester et al. (1990): Indexing by Latent Semantic Analysis
                    http://www.cs.bham.ac.uk/~pxt/IDA/lsa_ind.pdf
                    to show the clustering result.
```
3. Under the command line in that folder, install some packages by running:
```
   $ pip install jieba
   $ pip install nltk
   $ pip install gensim
   $ pip install flask
```

## Run the clustering Web server:
1. Under the command line, run:
```
   $ nohup python ccr_cluster_1.1.py &
```
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
   and you will get the clustered result from the HTTP response string.

   To view the clustered result, it's better to examine the source:
   view-source:http://localhost:5000/cluster?InpFile=data/ccr2.csv&NumTopic=2

3. You may change the values of InpFile and NumTopic for your need.
4. You may fetch the above URL in your own (say, PHP) program to get the clustered result.
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

## Examples:
After running: 
```
$ python ccr_cluster_1.1.py
```
you can view the result in chrome browser with the URLs:

1. view-source:http://localhost:5000/cluster?InpFile=data/ccr2.csv&NumTopic=2 

The result would look like:
```
GroupID	UserID	Email	 Content
1       0 john@gmail.com Good morning
1       1 kent@gmail.com Good afternoon
1       2 Mary@gmail.com Morning has broken

0       3 sosa@gmail.com Thank you
0       4 mike@gmail.com Thank you very much
0       6 bill@gmail.com Many thanks

-1      5 andy@gmail.com Much appreciated
```
The value -1 in GourpID means that the corresponding texts are outliers.
In the case, the 'Much' term is removed before clustering because it is in the stopword list.

2. view-source:http://localhost:5000/cluster?InpFile=data/ccr3.csv&NumTopic=2

The result would look like:
```
GroupID	UserID	Email	Content
1       0 john@gmail.com Human machine interface for lab abc computer applications
1       1 kent@gmail.com A survey of user opinion of computer system response time
1       2 Mary@gmail.com The EPS user interface management system
1       3 boby@gmail.com System and human system engineering testing of EPS
1       4 mike@gmail.com Relation of user perceived response time to error measurement

0       5 andy@gmail.com The generation of random binary unordered trees
0       6 bill@gmail.com The intersection graph of paths in trees
0       7 neil@gmail.com Graph minors IV Widths of trees and well quasi ordering
0       8 greg@gmail.com Graph minors A survey
```
The above result is the same as that at: https://radimrehurek.com/gensim/tut2.html