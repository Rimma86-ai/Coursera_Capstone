#!/usr/bin/env python
# coding: utf-8

# <h1>Explore and cluster the neighborhoods in Toronto<h1>

# Before we get the data and start exploring it, let's download all the dependencies that we will need.

# In[1]:


import pandas as pd
from bs4 import BeautifulSoup
import requests
import numpy as np


# In[2]:


import numpy as np # library to handle data in a vectorized manner

import pandas as pd # library for data analsysis
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)

import json # library to handle JSON files

#!conda install -c conda-forge geopy --yes 
from geopy.geocoders import Nominatim # convert an address into latitude and longitude values

import requests # library to handle requests
from pandas.io.json import json_normalize # tranform JSON file into a pandas dataframe

# Matplotlib and associated plotting modules
import matplotlib.cm as cm
import matplotlib.colors as colors

# import k-means from clustering stage
from sklearn.cluster import KMeans


# In[3]:


#!conda install -c conda-forge folium=0.5.0 --yes 
import folium # map rendering library

print('Libraries imported.')


# <h2>1. Download and Explore Dataset<h2>

# Webscraping to Extract Postal Codes of Toronto
# 
# Parse the html data using beautiful_soup

# In[4]:


source = requests.get("https://en.wikipedia.org/wiki/List_of_postal_codes_of_Canada:_M").text
soup = BeautifulSoup(source, "html5lib")


# In[5]:


table = soup.find('table')


# After retreiving the URL and creating a Beautiful soup object
# 
# Firstly create a list
# 
# Later after finding the table and table data  create a dictionary called cell having 3 keys PostalCode, Borough and Neighborhood.
# 
# As postal code contains upto 3 characters extract that using tablerow.p.text
# 
# Next use split ,strip and replace functions for getting Borough and Neighborhood information.
# 
# Append to the list 

# In[6]:


table_contents=[]
table=soup.find('table')
for row in table.findAll('td'):
    cell = {}
    if row.span.text=='Not assigned':
        pass
    else:
        cell['Postal Code'] = row.p.text[:3]
        cell['Borough'] = (row.span.text).split('(')[0]
        cell['Neighborhood'] = (((((row.span.text).split('(')[1]).strip(')')).replace(' /',',')).replace(')',' ')).strip(' ')
        table_contents.append(cell)

        # print(table_contents)
df=pd.DataFrame(table_contents)
df['Borough']=df['Borough'].replace({'Downtown TorontoStn A PO Boxes25 The Esplanade':'Downtown Toronto Stn A',
                                             'East TorontoBusiness reply mail Processing Centre969 Eastern':'East Toronto Business',
                                             'EtobicokeNorthwest':'Etobicoke Northwest','East YorkEast Toronto':'East York/East Toronto',
                                             'MississaugaCanada Post Gateway Processing Centre':'Mississauga'})
df.head(12)


# In[7]:


df.shape


# Use a link to a csv file that has the geographical coordinates of each postal code

# In[8]:


df1 = pd.read_csv ('https://cocl.us/Geospatial_data')
df1


# Merge two datasets (df and df1) based on Postal code

# In[9]:


df2 = pd.merge(df, df1, on='Postal Code')
df2.head()


#  Let's slice the original dataframe and create a new dataframe of the Downtown Toronto.

# In[10]:


Downtown_data = df2[df2['Borough'] == 'Downtown Toronto'].reset_index(drop=True)
Downtown_data.head()


# Use geopy library to get the latitude and longitude values of Downtown Toronto

# In[11]:


address = 'Downtown Toronto'

geolocator = Nominatim(user_agent="t_explorer")
location = geolocator.geocode(address)
latitude = location.latitude
longitude = location.longitude
print('The geograpical coordinate of Downtown Toronto are {}, {}.'.format(latitude, longitude))


# Let's visualize Downtown Toronto the neighborhoods in it.

# In[12]:


# create map of Downtown Toronto using latitude and longitude values
map_downtown = folium.Map(location=[latitude, longitude], zoom_start=11)

# add markers to map
for lat, lng, label in zip(Downtown_data['Latitude'], Downtown_data['Longitude'], Downtown_data['Neighborhood']):
    label = folium.Popup(label, parse_html=True)
    folium.CircleMarker(
        [lat, lng],
        radius=5,
        popup=label,
        color='blue',
        fill=True,
        fill_color='#3186cc',
        fill_opacity=0.7,
        parse_html=False).add_to(map_downtown)  
    
map_downtown


# Next, we are going to start utilizing the Foursquare API to explore the neighborhoods and segment them.

# ### Define Foursquare Credentials and Version

# ##### Make sure that you have created a Foursquare developer account and have your credentials handy

# ##### To obtain access token follow these steps.
# 
# <br>
# 
# 1.  Go to your **"App Settings"** page on the developer console of Foursquare.com   
# 2.  Set the **"Redirect URL"** under **"Web Addresses"** to [https://www.google.com](https://www.google.com?cm_mmc=Email_Newsletter-_-Developer_Ed%2BTech-_-WW_WW-_-SkillsNetwork-Courses-IBMDeveloperSkillsNetwork-DS0701EN-SkillsNetwork-21253531&cm_mmca1=000026UJ&cm_mmca2=10006555&cm_mmca3=M12345678&cvosrc=email.Newsletter.M12345678&cvo_campaign=000026UJ&cm_mmc=Email_Newsletter-_-Developer_Ed%2BTech-_-WW_WW-_-SkillsNetwork-Courses-IBMDeveloperSkillsNetwork-DS0701EN-SkillsNetwork-21253531&cm_mmca1=000026UJ&cm_mmca2=10006555&cm_mmca3=M12345678&cvosrc=email.Newsletter.M12345678&cvo_campaign=000026UJ&cm_mmc=Email_Newsletter-_-Developer_Ed%2BTech-_-WW_WW-_-SkillsNetwork-Courses-IBMDeveloperSkillsNetwork-DS0701EN-SkillsNetwork-21253531&cm_mmca1=000026UJ&cm_mmca2=10006555&cm_mmca3=M12345678&cvosrc=email.Newsletter.M12345678&cvo_campaign=000026UJ&cm_mmc=Email_Newsletter-_-Developer_Ed%2BTech-_-WW_WW-_-SkillsNetwork-Courses-IBMDeveloperSkillsNetwork-DS0701EN-SkillsNetwork-21253531&cm_mmca1=000026UJ&cm_mmca2=10006555&cm_mmca3=M12345678&cvosrc=email.Newsletter.M12345678&cvo_campaign=000026UJ&cm_mmc=Email_Newsletter-_-Developer_Ed%2BTech-_-WW_WW-_-SkillsNetwork-Courses-IBMDeveloperSkillsNetwork-DS0701EN-SkillsNetwork-21253531&cm_mmca1=000026UJ&cm_mmca2=10006555&cm_mmca3=M12345678&cvosrc=email.Newsletter.M12345678&cvo_campaign=000026UJ&cm_mmc=Email_Newsletter-_-Developer_Ed%2BTech-_-WW_WW-_-SkillsNetwork-Courses-IBMDeveloperSkillsNetwork-DS0701EN-SkillsNetwork-21253531&cm_mmca1=000026UJ&cm_mmca2=10006555&cm_mmca3=M12345678&cvosrc=email.Newsletter.M12345678&cvo_campaign=000026UJ)  
# 
# 
# 3.  Paste and enter the following url in your web browser **(replace YOUR_CLIENT_ID with your actual client id)**:  
#     [https://foursquare.com/oauth2/authenticate?client_id=YOUR_CLIENT_ID&response_type=code&redirect_uri=https://www.google.com](https://foursquare.com/oauth2/authenticate?client_id=YOUR_CLIENT_ID&response_type=code&redirect_uri=https://www.google.com&cm_mmc=Email_Newsletter-_-Developer_Ed%2BTech-_-WW_WW-_-SkillsNetwork-Courses-IBMDeveloperSkillsNetwork-DS0701EN-SkillsNetwork-21253531&cm_mmca1=000026UJ&cm_mmca2=10006555&cm_mmca3=M12345678&cvosrc=email.Newsletter.M12345678&cvo_campaign=000026UJ) 
# 
#     This should redirect you to a google page requesting permission to make the connection. 
# 4.  Accept and then look at the url of your web browser **(take note at the CODE part of the url to use in step 5)**  
#     It should look like [https://www.google.com/?code=CODE](https://www.google.com?code=CODE&cm_mmc=Email_Newsletter-_-Developer_Ed%2BTech-_-WW_WW-_-SkillsNetwork-Courses-IBMDeveloperSkillsNetwork-DS0701EN-SkillsNetwork-21253531&cm_mmca1=000026UJ&cm_mmca2=10006555&cm_mmca3=M12345678&cvosrc=email.Newsletter.M12345678&cvo_campaign=000026UJ)  
# 5.  Copy the code value from the previous step.  
#        Paste and enter the following into your web browser **(replace placeholders with actual values)**:  
#     [https://foursquare.com/oauth2/access_token?client_id=YOUR_CLIENT_ID&client_secret=YOUR_CLIENT_SECRET&grant_type=authorization_code&redirect_uri=https://www.google.com&code=CODE](https://foursquare.com/oauth2/access_token?client_id=YOUR_CLIENT_ID&client_secret=YOUR_CLIENT_SECRET&grant_type=authorization_code&redirect_uri=https://www.google.com&code=CODE&cm_mmc=Email_Newsletter-_-Developer_Ed%2BTech-_-WW_WW-_-SkillsNetwork-Courses-IBMDeveloperSkillsNetwork-DS0701EN-SkillsNetwork-21253531&cm_mmca1=000026UJ&cm_mmca2=10006555&cm_mmca3=M12345678&cvosrc=email.Newsletter.M12345678&cvo_campaign=000026UJ).  
# 6.  When you paste the link , This should lead you to a page that gives you your **access token**.
# 
# 

# In[13]:


CLIENT_ID = 'UPR0W3TF11EDJ40A1SI41GSJ1ALBGGAMADUFXFB22CGJMJJK' # your Foursquare ID
CLIENT_SECRET = '0WDT12HOHT2AM0ZNM23PGKRJPRLBEUUAVCAI2CGF4LNX1MOL' # your Foursquare Secret
VERSION = '20180604' # Foursquare API version
ACCESS_TOKEN = 'ADA44SZQAXVEN2COKKH5JSS3FCLJWQYJQWZUDXJE55O5X3N2' 
LIMIT = 100 # A default Foursquare API limit value

print('Your credentails:')
print('CLIENT_ID: ' + CLIENT_ID)
print('CLIENT_SECRET:' + CLIENT_SECRET)


# <h2> 2. Explore Neighborhoods in Downtown Toronto<h2>

# Let's get venues that are in Downtown Toronto within a radius of 500 meters.

# In[14]:


def getNearbyVenues(names, latitudes, longitudes, radius=500):
    
    venues_list=[]
    for name, lat, lng in zip(names, latitudes, longitudes):
        print(name)
            
        # create the API request URL
        url = 'https://api.foursquare.com/v2/venues/explore?&client_id={}&client_secret={}&v={}&ll={},{}&radius={}&limit={}'.format(
            CLIENT_ID, 
            CLIENT_SECRET, 
            VERSION, 
            lat, 
            lng, 
            radius, 
            LIMIT)
            
        # make the GET request
        results = requests.get(url).json()["response"]['groups'][0]['items']
        
        # return only relevant information for each nearby venue
        venues_list.append([(
            name, 
            lat, 
            lng, 
            v['venue']['name'], 
            v['venue']['location']['lat'], 
            v['venue']['location']['lng'],  
            v['venue']['categories'][0]['name']) for v in results])

    nearby_venues = pd.DataFrame([item for venue_list in venues_list for item in venue_list])
    nearby_venues.columns = ['Neighborhood', 
                  'Neighborhood Latitude', 
                  'Neighborhood Longitude', 
                  'Venue', 
                  'Venue Latitude', 
                  'Venue Longitude', 
                  'Venue Category']
    
    return(nearby_venues)


# In[15]:


downtown_venues = getNearbyVenues(names=Downtown_data['Neighborhood'],
                                   latitudes=Downtown_data['Latitude'],
                                   longitudes=Downtown_data['Longitude']
                                  )


# Let's check the size of the resulting dataframe

# In[16]:


print(downtown_venues.shape)
downtown_venues.head()


# Let's check how many venues were returned for each neighborhood

# In[17]:


downtown_venues.groupby('Neighborhood').count()


# Let's find out how many unique categories can be curated from all the returned venues

# In[18]:


print('There are {} uniques categories.'.format(len(downtown_venues['Venue Category'].unique())))


# <h2>3. Analyze Each Neighborhood<h2>

# In[19]:


# one hot encoding
downtown_onehot = pd.get_dummies(downtown_venues[['Venue Category']], prefix="", prefix_sep="")

# add neighborhood column back to dataframe
downtown_onehot['Neighborhood'] = downtown_venues['Neighborhood'] 

# move neighborhood column to the first column
fixed_columns = [downtown_onehot.columns[-1]] + list(downtown_onehot.columns[:-1])
downtown_onehot = downtown_onehot[fixed_columns]

downtown_onehot.head()


# And let's examine the new dataframe size.

# In[20]:


downtown_onehot.shape


# Next, let's group rows by neighborhood and by taking the mean of the frequency of occurrence of each category

# In[21]:


downtown_grouped = downtown_onehot.groupby('Neighborhood').mean().reset_index()
downtown_grouped.head()


# Let's confirm the new size

# In[22]:


downtown_grouped.shape


# Let's print each neighborhood along with the top 5 most common venues

# In[23]:


num_top_venues = 5

for hood in downtown_grouped['Neighborhood']:
    print("----"+hood+"----")
    temp = downtown_grouped[downtown_grouped['Neighborhood'] == hood].T.reset_index()
    temp.columns = ['venue','freq']
    temp = temp.iloc[1:]
    temp['freq'] = temp['freq'].astype(float)
    temp = temp.round({'freq': 2})
    print(temp.sort_values('freq', ascending=False).reset_index(drop=True).head(num_top_venues))
    print('\n')


# Let's put that into a pandas dataframe

# In[24]:


#First, let's write a function to sort the venues in descending order.
def return_most_common_venues(row, num_top_venues):
    row_categories = row.iloc[1:]
    row_categories_sorted = row_categories.sort_values(ascending=False)
    
    return row_categories_sorted.index.values[0:num_top_venues]


# Now let's create the new dataframe and display the top 10 venues for each neighborhood.

# In[25]:


num_top_venues = 10

indicators = ['st', 'nd', 'rd']

# create columns according to number of top venues
columns = ['Neighborhood']
for ind in np.arange(num_top_venues):
    try:
        columns.append('{}{} Most Common Venue'.format(ind+1, indicators[ind]))
    except:
        columns.append('{}th Most Common Venue'.format(ind+1))

# create a new dataframe
neighborhoods_venues_sorted = pd.DataFrame(columns=columns)
neighborhoods_venues_sorted['Neighborhood'] = downtown_grouped['Neighborhood']

for ind in np.arange(downtown_grouped.shape[0]):
    neighborhoods_venues_sorted.iloc[ind, 1:] = return_most_common_venues(downtown_grouped.iloc[ind, :], num_top_venues)

neighborhoods_venues_sorted.head()


# <h2>4. Cluster Neighborhoods<h2>

# In[26]:


pip install --user --upgrade numpy


# Run k-means to cluster the neighborhood into 5 clusters.

# In[80]:


# import k-means from clustering stage
from sklearn.cluster import KMeans

# set number of clusters
kclusters = 4

downtown_grouped_clustering = downtown_grouped.drop('Neighborhood', 1)

# run k-means clustering
kmeans = KMeans(n_clusters=kclusters, random_state=0).fit(downtown_grouped_clustering)

# check cluster labels generated for each row in the dataframe
kmeans.labels_[0:10] 


# Let's create a new dataframe that includes the cluster as well as the top 10 venues for each neighborhood.

# In[81]:


# add clustering labels
#neighborhoods_venues_sorted.insert(0, 'Cluster', kmeans.labels_)# comment this line after first run otherwise it will give an error that inserted columns name already exist
downtown_merged = Downtown_data
# merge downtown_grouped with downtown_data to add latitude/longitude for each neighborhood
downtown_merged = downtown_merged.join(neighborhoods_venues_sorted.set_index('Neighborhood'), on='Neighborhood')
downtown_merged.head() # check the last columns!
downtown_merged_1=downtown_merged.drop(['Cluster Labels','cluster Labels'], axis = 1)# if you did not run several times line#2 then you can skip this line
downtown_merged_1


# Finally, let's visualize the resulting clusters

# In[82]:


# create map
map_clusters = folium.Map(location=[latitude, longitude], zoom_start=11)

# set color scheme for the clusters
x = np.arange(kclusters)
ys = [i + x + (i*x)**2 for i in range(kclusters)]
colors_array = cm.rainbow(np.linspace(0, 1, len(ys)))
rainbow = [colors.rgb2hex(i) for i in colors_array]

# add markers to the map
markers_colors = []
for lat, lon, poi, cluster in zip(downtown_merged_1['Latitude'], downtown_merged_1['Longitude'], downtown_merged_1['Neighborhood'], downtown_merged_1['Cluster']):
    label = folium.Popup(str(poi) + ' Cluster ' + str(cluster), parse_html=True)
    folium.CircleMarker(
        [lat, lon],
        radius=5,
        popup=label,
        color=rainbow[cluster-1],
        fill=True,
        fill_color=rainbow[cluster-1],
        fill_opacity=0.7).add_to(map_clusters)
       
map_clusters


# <h2>5. Examine Clusters<h2>

# Examine each cluster and determine the discriminating venue categories that distinguish each cluster.

# Cluster 1

# In[86]:


downtown_merged_1.loc[downtown_merged_1['Cluster'] == 0, downtown_merged_1.columns[[1] + list(range(4, downtown_merged_1.shape[1]))]]


# Cluster 2

# In[87]:


downtown_merged_1.loc[downtown_merged_1['Cluster'] == 1, downtown_merged_1.columns[[1] + list(range(4, downtown_merged_1.shape[1]))]]


# Cluster 3

# In[88]:


downtown_merged_1.loc[downtown_merged_1['Cluster'] == 2, downtown_merged_1.columns[[1] + list(range(4, downtown_merged_1.shape[1]))]]


# Cluster 4

# In[89]:


downtown_merged_1.loc[downtown_merged_1['Cluster'] == 3, downtown_merged_1.columns[[1] + list(range(4, downtown_merged_1.shape[1]))]]

