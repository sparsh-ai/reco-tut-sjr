#!/usr/bin/env python
# coding: utf-8

# In[2]:


import os
project_name = "reco-tut-sjr"; branch = "main"; account = "sparsh-ai"
project_path = os.path.join('/content', project_name)

if not os.path.exists(project_path):
    get_ipython().system(u'cp /content/drive/MyDrive/mykeys.py /content')
    import mykeys
    get_ipython().system(u'rm /content/mykeys.py')
    path = "/content/" + project_name; 
    get_ipython().system(u'mkdir "{path}"')
    get_ipython().magic(u'cd "{path}"')
    import sys; sys.path.append(path)
    get_ipython().system(u'git config --global user.email "recotut@recohut.com"')
    get_ipython().system(u'git config --global user.name  "reco-tut"')
    get_ipython().system(u'git init')
    get_ipython().system(u'git remote add origin https://"{mykeys.git_token}":x-oauth-basic@github.com/"{account}"/"{project_name}".git')
    get_ipython().system(u'git pull origin "{branch}"')
    get_ipython().system(u'git checkout main')
else:
    get_ipython().magic(u'cd "{project_path}"')


# In[59]:


import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.neighbors import NearestNeighbors
import spacy


# In[55]:


# !python -m spacy download en_core_web_lg
get_ipython().system(u'ls /usr/local/lib/python3.7/dist-packages/en_core_web_lg')


# In[56]:


nlp = spacy.load('/usr/local/lib/python3.7/dist-packages/en_core_web_lg/en_core_web_lg-2.2.5')


# In[34]:


df_jobs = pd.read_pickle('./data/silver/jobs.p', compression='gzip')
df_jobs = df_jobs.reset_index(drop=True)
df_jobs.head()


# In[35]:


df_users = pd.read_pickle('./data/silver/applicants.p', compression='gzip')
df_users = df_users.reset_index(drop=True)
df_users.head()


# ## Selecting test user

# In[37]:


def get_recommendation(top, df_all, scores):
  recommendation = pd.DataFrame(columns = ['ApplicantID', 'JobID',  'title', 'score'])
  count = 0
  for i in top:
      recommendation.at[count, 'ApplicantID'] = u
      recommendation.at[count, 'JobID'] = df_all['Job.ID'][i]
      recommendation.at[count, 'title'] = df_all['Title'][i]
      recommendation.at[count, 'score'] =  scores[count]
      count += 1
  return recommendation


# In[38]:


u = 10001
index = np.where(df_users['Applicant_id'] == u)[0][0]
user_q = df_users.iloc[[index]]
user_q


# ## Model 1 - TFIDF

# In[36]:


#initializing tfidf vectorizer
##This is a technique to quantify a word in documents, 
#we generally compute a weight to each word which signifies the importance of the word in the document and corpus. 
##This method is a widely used technique in Information Retrieval and Text Mining.
tfidf_vectorizer = TfidfVectorizer()

tfidf_jobid = tfidf_vectorizer.fit_transform((df_jobs['text'])) #fitting and transforming the vector
tfidf_jobid


# Computing cosine similarity using tfidf

# In[39]:


user_tfidf = tfidf_vectorizer.transform(user_q['text'])
cos_similarity_tfidf = map(lambda x: cosine_similarity(user_tfidf, x), tfidf_jobid)
output2 = list(cos_similarity_tfidf)

top = sorted(range(len(output2)), key=lambda i: output2[i], reverse=True)[:10]
list_scores = [output2[i][0][0] for i in top]
get_recommendation(top, df_jobs, list_scores)


# ## Model 2 - CountVectorizer

# In[41]:


count_vectorizer = CountVectorizer()
count_jobid = count_vectorizer.fit_transform((df_jobs['text'])) #fitting and transforming the vector
count_jobid


# In[43]:


user_count = count_vectorizer.transform(user_q['text'])
cos_similarity_countv = map(lambda x: cosine_similarity(user_count, x),count_jobid)
output2 = list(cos_similarity_countv)

top = sorted(range(len(output2)), key=lambda i: output2[i], reverse=True)[:10]
list_scores = [output2[i][0][0] for i in top]
get_recommendation(top, df_jobs, list_scores)


# ## Model 3 - Spacy

# Transform the copurs text to the *spacy's documents* 

# In[ ]:


get_ipython().run_cell_magic(u'time', u'', u'list_docs = []\nfor i in range(len(df_jobs)):\n  doc = nlp("u\'" + df_jobs[\'text\'][i] + "\'")\n  list_docs.append((doc,i))\nprint(len(list_docs))')


# In[ ]:


def calculateSimWithSpaCy(nlp, df, user_text, n=6):
    # Calculate similarity using spaCy
    list_sim =[]
    doc1 = nlp("u'" + user_text + "'")
    for i in df.index:
      try:
            doc2 = list_docs[i][0]
            score = doc1.similarity(doc2)
            list_sim.append((doc1, doc2, list_docs[i][1],score))
      except:
        continue

    return  list_sim   


# In[ ]:


user_q.text[186]


# In[ ]:


df3 = calculateSimWithSpaCy(nlp, df_jobs, user_q.text[186], n=15)
df_recom_spacy = pd.DataFrame(df3).sort_values([3], ascending=False).head(10)
df_recom_spacy.reset_index(inplace=True)

index_spacy = df_recom_spacy[2]
list_scores = df_recom_spacy[3]


# Top recommendations using Spacy

# In[ ]:


get_recommendation(index_spacy, df_jobs, list_scores)


# ## Model 4 - KNN

# In[60]:


n_neighbors = 11
KNN = NearestNeighbors(n_neighbors, p=2)
KNN.fit(tfidf_jobid)
NNs = KNN.kneighbors(user_tfidf, return_distance=True) 


# In[61]:


NNs[0][0][1:]


# The top recommendations using KNN

# In[62]:


top = NNs[1][0][1:]
index_score = NNs[0][0][1:]

get_recommendation(top, df_jobs, index_score)

