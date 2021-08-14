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


# In[37]:


import glob
import pandas as pd
import numpy as np
import nltk

from nltk.corpus import stopwords
import re
import string
from nltk.stem import WordNetLemmatizer
from nltk import word_tokenize
from nltk.corpus import stopwords


# In[38]:


nltk.download('punkt') 
nltk.download('stopwords')
nltk.download('wordnet')
nltk.download('averaged_perceptron_tagger')

stop = stopwords.words('english')
stop_words_ = set(stopwords.words('english'))
wn = WordNetLemmatizer()


# In[8]:


files = sorted(glob.glob('./data/bronze/*.parquet.gz'))
files


# In[64]:


df_exp = pd.read_parquet(files[0])
df_exp.head()


# In[79]:


df_job = pd.read_parquet(files[1])
df_job.head()


# In[80]:


df_poi = pd.read_parquet(files[2])
df_poi.head()


# ## Create job corpus

# In[81]:


df_job2 = df_job.merge(df_exp, on='Applicant.ID', how='left')
df_job2.head()


# In[82]:


df_job2['Job.ID'].nunique()


# In[83]:


df_job2 = df_job2.drop_duplicates(subset='Job.ID')


# In[84]:


df_job2.info()


# In[85]:


# check the NA's
df_job2.isnull().sum()


# In[86]:


# select only required columns
cols = ['Job.ID','Title','Position', 'Company','City_x','Job.Description']
df_job2 = df_job2[cols]
df_job2.columns = ['Job.ID', 'Title', 'Position', 'Company','City','Job_Description']
df_job2.head() 


# In[87]:


# checking for the null values again.
df_job2.isnull().sum()


# In[88]:


str_cols = ['Title', 'Position', 'Company', 'City', 'Job_Description']
df_job2.loc[:, str_cols] = df_job2.loc[:, str_cols].fillna('')
df_job2.isnull().sum()


# In[89]:


# creating the jobs corpus
# combining the columns
df_job2["text"] = df_job2["Position"].map(str) + " " + df_job2["Company"] +" "+ df_job2["City"]+" "+df_job2['Job_Description'] +" "+df_job2['Title']
df_all = df_job2[['Job.ID', 'text', 'Title']]
df_all = df_all.fillna(" ")
df_all.head()


# In[90]:


def black_txt(token):
    return  token not in stop_words_ and token not in list(string.punctuation)  and len(token)>2   
  
def clean_txt(text):
  clean_text = []
  clean_text2 = []
  text = re.sub("'", "",text)
  text=re.sub("(\\d|\\W)+"," ",text) 
  text = text.replace("nbsp", "")
  clean_text = [ wn.lemmatize(word, pos="v") for word in word_tokenize(text.lower()) if black_txt(word)]
  clean_text2 = [word for word in clean_text if black_txt(word)]
  return " ".join(clean_text2)


# In[91]:


# cleaning the job corpus
df_all['text'] = df_all['text'].apply(clean_txt)
df_all.head()


# ## Applicant dataset

# In[ ]:


# let's now create the applicant corpus
df_job_view = df_job[['Applicant.ID', 'Job.ID', 'Position', 'Company','City']]
df_job_view["select_pos_com_city"] = df_job_view["Position"].map(str) + "  " + df_job_view["Company"] +"  "+ df_job_view["City"]
df_job_view['select_pos_com_city'] = df_job_view['select_pos_com_city'].map(str).apply(clean_txt)
df_job_view['select_pos_com_city'] = df_job_view['select_pos_com_city'].str.lower()
df_job_view = df_job_view[['Applicant.ID','select_pos_com_city']]


# In[93]:


df_job_view.head()


# ## Experience dataset

# In[95]:


df_exp.head(2)


# In[96]:


df_experience = df_exp[['Applicant.ID','Position.Name']].copy()
df_experience['Position.Name'] = df_experience['Position.Name'].map(str).apply(clean_txt)
df_experience =  df_experience.sort_values(by='Applicant.ID')
df_experience = df_experience.fillna(" ")
df_experience.head()


# In[97]:


# same applicant has 3 applications 100001 in single line so we need to join them
df_experience = df_experience.groupby('Applicant.ID', sort=True)['Position.Name'].apply(' '.join).reset_index()
df_experience.head(5)


# ## Position of Interest dataset

# In[98]:


df_poi = df_poi.sort_values(by='Applicant.ID')
df_poi.head()


# In[99]:


df_poi = df_poi.drop('Updated.At', 1)
df_poi = df_poi.drop('Created.At', 1)

#cleaning the text
df_poi['Position.Of.Interest']=df_poi['Position.Of.Interest'].map(str).apply(clean_txt)
df_poi = df_poi.fillna(" ")
df_poi = df_poi.groupby('Applicant.ID', sort=True)['Position.Of.Interest'].apply(' '.join).reset_index()

df_poi.head()


# ## Creating the final user dataset by merging all the users datasets
# 
# Merging `df_job_view`, `df_experience`, and `df_poi` datasets

# In[100]:


df_jobs_exp = df_job_view.merge(df_experience, left_on='Applicant.ID', right_on='Applicant.ID', how='outer')
df_jobs_exp = df_jobs_exp.fillna(' ')
df_jobs_exp = df_jobs_exp.sort_values(by='Applicant.ID')
df_jobs_exp.head()


# In[101]:


df_jobs_exp_poi = df_jobs_exp.merge(df_poi, left_on='Applicant.ID', right_on='Applicant.ID', how='outer')
df_jobs_exp_poi = df_jobs_exp_poi.fillna(' ')
df_jobs_exp_poi = df_jobs_exp_poi.sort_values(by='Applicant.ID')
df_jobs_exp_poi.head()


# In[ ]:


# combining all the columns
df_jobs_exp_poi["text"] = df_jobs_exp_poi["select_pos_com_city"].map(str) + df_jobs_exp_poi["Position.Name"] +" "+ df_jobs_exp_poi["Position.Of.Interest"]
df_final_person = df_jobs_exp_poi[['Applicant.ID','text']]
df_final_person.columns = ['Applicant_id','text']
df_final_person.loc[:, 'text'] = df_final_person.loc[:, 'text'].apply(clean_txt)


# In[106]:


df_final_person.head()


# ## Exporting the processed datasets

# In[107]:


get_ipython().system(u'mkdir ./data/silver')
df_all.to_pickle('./data/silver/jobs.p', compression='gzip')
df_final_person.to_pickle('./data/silver/applicants.p', compression='gzip')


# ## Versioning

# In[108]:


get_ipython().system(u'git status')


# In[109]:


get_ipython().system(u"git add . && git commit -m 'commit' && git push origin main")


# ## Extras - Wordcloud

# In[114]:


from PIL import Image
import matplotlib.pyplot as plt
from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator


# In[111]:


bunch_text = " ".join(text for text in df_all.tail(10000).text)


# In[112]:


stopwords = set(STOPWORDS)
wordcloud = WordCloud(stopwords=stopwords, background_color="white", colormap= "magma").generate(bunch_text)


# In[115]:


plt.figure(figsize=[11,11])
plt.imshow(wordcloud, interpolation="sinc")
plt.axis("off")
plt.show()


# In[116]:


get_ipython().system(u'wget -q --show-progress -O ./docs/img1.png https://microventures.com/wp-content/uploads/team-1697987_640.png')


# In[117]:


img = Image.open("./docs/img1.png").convert('RGBA')
x = np.array(img)
r, g, b, a = np.rollaxis(x, axis = -1)
r[a == 0] = 255
g[a == 0] = 255
b[a == 0] = 255
x = np.dstack([r, g, b, a])
img = Image.fromarray(x, 'RGBA')


# In[118]:


thresh = 200
fn = lambda x : 255 if x <= thresh else 0
wf_mask = img.convert('L').point(fn, mode='1')
wf_mask = np.array(wf_mask)


# In[119]:


def transform_format(val):
    if val == 0:
        return 255
    else:
        return val


# In[120]:


transformed_wf_mask = np.ndarray((wf_mask.shape[0],wf_mask.shape[1]), np.int32)

for i in range(len(wf_mask)):
    transformed_wf_mask[i] = list(map(transform_format, wf_mask[i]))


# In[121]:


wc = WordCloud(background_color="white", mask=transformed_wf_mask,
               stopwords=stopwords, contour_width=.1, contour_color='black')

# Generate a wordcloud
wc.generate(bunch_text)

# show
plt.figure(figsize=[20,10])
plt.imshow(wc, interpolation="sinc")
plt.axis("off")
plt.show()


# ## Versioning

# In[122]:


get_ipython().system(u'git status')


# In[123]:


get_ipython().system(u"git add . && git commit -m 'commit' && git push origin main")

