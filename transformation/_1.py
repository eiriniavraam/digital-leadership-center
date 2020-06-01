#!/usr/bin/env python3

"""
Docstring
------------------------------------------------------------------------------
    _1.py    |    Creating a corpus and dictionary out of web search data
------------------------------------------------------------------------------

Author: Simone Santoni, simone.santoni.1@city.ac.uk

Edits:
       - created
       - last edit

Notes: the dataset contains 49,197 web-pages that have been retrieved by
       searching for the name of a company in conjunction with one or
       multiple of the following keywords:
       of the following keywords:

       + Computer Software
       + Internet of Things
       + Machine Learning
       + Robotics
       + Technology
       + Computer Science
       + Computers
       + Automation
       + Augmented Reality
       + Big Data
       + Deep Learning
       + Cloud Computing
       + Natural Language Processing
       + Pattern Recognition
       + Analytics
       + Computing

"""

# %% load libraries
# basic operations
import os
import pickle
import re
from urllib.parse import quote_plus
from sshtunnel import SSHTunnelForwarder
# load data from mongodb
import pymongo
from pymongo import MongoClient
# data analysis/management/manipulation
import numpy as np
import pandas as pd
# data visualization
import matplotlib.pyplot as plt
from matplotlib import rc
# nlp pipeline
import spacy
import en_core_web_lg
from spacy_cld import LanguageDetector
# building corpus/dictionary
import gensim
from gensim.corpora import MmCorpus, Dictionary
from gensim.models import Phrases


# %% check software versions
print("""
spaCy version : {}
Gensim version: {}
""".format(spacy.__version__, gensim.__version__))


# %% work directory
srv = '/home/simone'
prj = 'githubRepos/digital-leadership-center'
fdr = 'transformation'
wd = os.path.join(srv, prj, fdr)
os.chdir(wd)


# %% viz options
plt.style.use('seaborn-bright')
rc('font',**{'family':'serif','serif':['Computer Modern Roman']})
rc('text', usetex=True)


# %% read data

# open monog pipeline
# --+ params
mongo_host = "10.16.142.91"
mongo_db = "digitalTechs"
mongo_user = "simone"
mongo_pass = "DELL123"
# --+ server
server = SSHTunnelForwarder(
    mongo_host,
    ssh_username=mongo_user,
    ssh_password=mongo_pass,
    remote_bind_address=('127.0.0.1', 27017)
)
# --+ start server
server.start()
# --+ create client
client = MongoClient('127.0.0.1', server.local_bind_port)
# --+ target db
db = client[mongo_db]
# load the data
df = pd.DataFrame(list(db.web_contents.find()))
# --+ stop server
server.stop()
# --+ double check data have been properly loaded
df.info()


# %% clean data

# basic cleaning
# --+ get timespans
df.loc[:, 'year'] = pd.to_numeric(df['year'])
# --+ slice the data
df = df.loc[df['year'] >= 2013]
# arrange data for sequential lda
# --+ order data by year of publication
df.sort_values('year', inplace=True)
# --+ get stacks by year
data = df.groupby('year').size()
# --+ time slices
time_slices = data.values
out_f = os.path.join('.data', 'ws_time_slices.txt')
with open(out_f, 'w') as pipe:
    for item in time_slices:
        pipe.write('{}\n'.format(item))

# compute string len
df.loc[:, 'len'] = df['content'].str.len()

# visualize distribution of string len
# --+ create figure
fig, [ax0, ax1] = plt.subplots(1, 2, figsize=(6, 4), sharey=True)
# --+ data series
x = df.loc[df['len'] > 0, 'len']
n, bins, patches = ax0.hist(x, n_bins, density=True, histtype='step',
                            cumulative=True, label='Empirical')
y = ((1 / (np.sqrt(2 * np.pi) * sigma)) *
     np.exp(-0.5 * (1 / sigma * (bins - mu))**2))
y = y.cumsum()
y /= y[-1]
# --+ create PANEL --  cumulative histogram
ax0.plot(bins, y, 'k--', linewidth=1.5, label='Theoretical')
# --+ overlay a reversed cumulative histogram.
ax0.hist(x, bins=bins, density=True, histtype='step', cumulative=-1,
         label='Reversed emp.')
# axes
ax0.set_xlabel("Text corpus length (characters)")
ax0.set_ylabel("u'$Pr(x = x_{i}$)")
ax0.set_xticks(np.arange(5, 10, 1))
ax0.set_yticks(np.arange(_min, _max, 0.02))
# reference line
#ax0.ax0vline(x=11, ymin=0, ymax0=1, color='r')
# grid
ax0.grid(True, ls='--', axis='y', which='major')
# --+ hide all spines while preserving ticks
ax0.spines['right'].set_visible(False)
ax0.spines['top'].set_visible(False)
ax0.spines['bottom'].set_visible(False)
ax0.spines['left'].set_visible(False)
ax0.yaxis.set_ticks_position('left')
ax0.xaxis.set_ticks_position('bottom')
ax0.yaxis.set_ticks_position('left')
ax0.xaxis.set_ticks_position('bottom')
# -- textbox
ax0.text(5, 0.51, u'$A$', fontsize=13)
# --+ PANEL B
# --+ plot data
ax1.plot(x1, y1, marker='o', color='k', ls='')
# axes
ax1.set_xlabel("Number of topics retained")
ax1.set_xticks(np.arange(10, 35, 5))
# grid
ax1.grid(True, ls='--', axis='y', which='major')
# --+ hide all spines while preserving ticks
ax1.spines['right'].set_visible(False)
ax1.spines['top'].set_visible(False)
ax1.spines['bottom'].set_visible(False)
ax1.spines['left'].set_visible(False)
#ax1.yaxis.set_ticks_position('left')
#ax1.xaxis.set_ticks_position('bottom')
#ax1.yaxis.set_ticks_position('left')
#ax1.xaxis.set_ticks_position('bottom')
# --+ textbox
ax0.text(10, 0.51, u'$B$', fontsize=13)
# --+ write plot to file
out_f = os.path.join('analysis', 'topicModeling', '.output', '_1.pdf')
plt.savefig(out_f,
            transparent=True,
            bbox_inches='tight',
            pad_inches=0)



print("""
      Mean: {}
      SD  : {}
      Min : {}
      Max : {}
      """.format(np.mean(df.len).round(2),
                 np.std(df.len).round(2),
                 np.min(df.len),
                 np.max(df.len)))

# remove returns and tabulates
df.loc[:, 'content'] = df['content'].str.replace('\n', ' ')
df.loc[:, 'content'] = df['content'].str.replace('\t', ' ')
df.loc[:, 'content'] = df['content'].str.replace('|', ' ')
df.loc[:, 'content'] = df['content'].str.replace('―', ' ')
df.loc[:, 'content'] = df['content'].str.replace('--', ' ')
df.loc[:, 'content'] = df['content'].str.replace('---', ' ')

# prepare list to pass through spacy
docs = [article.strip().lower() for article in df.content]


# %% NLP pipeline

# load pipeline
nlp = spacy.load('en_core_web_lg', disable=['parser', 'tagger', 'ner'])

# specifiy max len
nlp.max_length = 5000000

# expand on spaCy's stopwords
# --+ my stopwrods
my_stopwords = ['\x1c',
                'ft', 'wsj', 'time', 'sec',
                'say', 'says', 'said',
                'mr.', 'mister', 'mr', 'miss', 'ms',
                'inc']
# --+ expand on spacy's stopwords
for stopword in my_stopwords:
    nlp.vocab[stopword].is_stop = True

# filter-out non-en pages
language_detector = LanguageDetector()
nlp.add_pipe(language_detector)

# tokenize text conditional on english text
docs_tokens = []
docs_ln = []

for _id, doc in zip(df._id, docs):
    doc = nlp(doc)
    ln = doc._.languages
    docs_ln.append([_id, ln])
    if ('en' in ln):
        if doc._.language_scores['en'] > 0.95:
            tmp_tokens = [token.lemma_ for token in doc
                          if not token.is_stop
                          and not token.is_punct
                          and not token.like_num
                          and not token.like_url
                          and not token.like_email
                          and not token.is_currency
                          and not token.is_oov]
            docs_tokens.append([_id, tmp_tokens])
        else:
            pass
    else:
        pass


# take into account bi- and tri-grams

# --+ get rid of common terms
common_terms = [u'of', u'with', u'without', u'and', u'or', u'the', u'a',
                u'not', 'be', u'to', u'this', u'who', u'in']

# --+ fing phrases as bigrams
bigram = Phrases(docs_tokens,
                 min_count=50,
                 threshold=5,
                 max_vocab_size=50000,
                 common_terms=common_terms)
# --+ fing phrases as trigrams
trigram = Phrases(bigram[docs_tokens],
                  min_count=50,
                  threshold=5,
                  max_vocab_size=50000,
                  common_terms=common_terms)

# uncomment if a tri-grammed, tokenized document is preferred
docs_phrased = [bigram[line] for line in docs_tokens]
#docs_phrased = [trigram[bigram[line]] for line in docs_tokens]

# check outcome of nlp pipeline
print('''
=============================================================================
published article: {}

=============================================================================
tokenized article: {}

=============================================================================
tri-grammed tokenized article: {}

'''.format(docs[1],
           docs_tokens[1],
           docs_phrased[1]))


# %% get corpus & dictionary to use for further nlp analysis

# get dictionary and write it to a file
pr_dictionary = Dictionary(docs_phrased)
pr_dictionary.save('.data/pr_dictionary.dict')

# get corpus and write it to a file
pr_corpus = [pr_dictionary.doc2bow(doc) for doc in docs_phrased]

out_f = ('.data/pr_corpus.mm')
MmCorpus.serialize(out_f, pr_corpus)
mm = MmCorpus(out_f)  # `mm` document stream now has random access
