#!/usr/bin/env python
# coding: utf-8

# In[1]:


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


# In[3]:


import glob
import pandas as pd


# In[4]:


files = glob.glob('./data/bronze/*.csv')
files


# In[5]:


df1 = pd.read_csv(files[0])
df1.head()


# In[6]:


df1.info()


# In[7]:


df1.to_parquet('./data/bronze/experience.parquet.gz', compression='gzip')


# In[8]:


df2 = pd.read_csv(files[1])
df2.head()


# In[9]:


df2.info()


# In[10]:


df2.to_parquet('./data/bronze/job_views.parquet.gz', compression='gzip')


# In[11]:


df3 = pd.read_csv(files[2])
df3.head()


# In[12]:


df3.info()


# In[13]:


df3.to_parquet('./data/bronze/poi.parquet.gz', compression='gzip')


# In[14]:


get_ipython().system(u'cd ./data/bronze && zip -m raw_csv.zip ./*.csv')


# In[ ]:


get_ipython().system(u'git status')


# In[ ]:


get_ipython().system(u"git add . && git commit -m 'ADD notebooks' && git push origin main")

