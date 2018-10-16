
# coding: utf-8

# In[2]:


import pandas as pd
import numpy as np
from scipy.stats import ttest_ind


# # Hypothesis Testing
# This project requires more individual learning than previous assignments - you are encouraged to check out the [pandas documentation](http://pandas.pydata.org/pandas-docs/stable/) to find functions or methods you might not have used yet, or ask questions on [Stack Overflow](http://stackoverflow.com/) and tag them as pandas and python related. And of course, the discussion forums are open for interaction with your peers and the course staff.
# 
# Definitions:
# * A _quarter_ is a specific three month period, Q1 is January through March, Q2 is April through June, Q3 is July through September, Q4 is October through December.
# * A _recession_ is defined as starting with two consecutive quarters of GDP decline, and ending with two consecutive quarters of GDP growth.
# * A _recession bottom_ is the quarter within a recession which had the lowest GDP.
# * A _university town_ is a city which has a high percentage of university students compared to the total population of the city.
# 
# **Hypothesis**: University towns have their mean housing prices less effected by recessions. Run a t-test to compare the ratio of the mean price of houses in university towns the quarter before the recession starts compared to the recession bottom. (`price_ratio=quarter_before_recession/recession_bottom`)
# 
# The following data files are available for this assignment:
# * From the [Zillow research data site](http://www.zillow.com/research/data/) there is housing data for the United States. In particular the datafile for [all homes at a city level](http://files.zillowstatic.com/research/public/City/City_Zhvi_AllHomes.csv), ```City_Zhvi_AllHomes.csv```, has median home sale prices at a fine grained level.
# * From the Wikipedia page on college towns is a list of [university towns in the United States](https://en.wikipedia.org/wiki/List_of_college_towns#College_towns_in_the_United_States) which has been copy and pasted into the file ```university_towns.txt```.
# * From Bureau of Economic Analysis, US Department of Commerce, the [GDP over time](http://www.bea.gov/national/index.htm#gdp) of the United States in current dollars (use the chained value in 2009 dollars), in quarterly intervals, in the file ```gdplev.xls```. For this assignment, only look at GDP data from the first quarter of 2000 onward.
# 
# Each function in this assignment below is worth 10%, with the exception of ```run_ttest()```, which is worth 50%.

# In[39]:


# Use this dictionary to map state names to two letter acronyms
states = {'OH': 'Ohio', 'KY': 'Kentucky', 'AS': 'American Samoa', 'NV': 'Nevada', 'WY': 'Wyoming', 'NA': 'National', 'AL': 'Alabama', 'MD': 'Maryland', 'AK': 'Alaska', 'UT': 'Utah', 'OR': 'Oregon', 'MT': 'Montana', 'IL': 'Illinois', 'TN': 'Tennessee', 'DC': 'District of Columbia', 'VT': 'Vermont', 'ID': 'Idaho', 'AR': 'Arkansas', 'ME': 'Maine', 'WA': 'Washington', 'HI': 'Hawaii', 'WI': 'Wisconsin', 'MI': 'Michigan', 'IN': 'Indiana', 'NJ': 'New Jersey', 'AZ': 'Arizona', 'GU': 'Guam', 'MS': 'Mississippi', 'PR': 'Puerto Rico', 'NC': 'North Carolina', 'TX': 'Texas', 'SD': 'South Dakota', 'MP': 'Northern Mariana Islands', 'IA': 'Iowa', 'MO': 'Missouri', 'CT': 'Connecticut', 'WV': 'West Virginia', 'SC': 'South Carolina', 'LA': 'Louisiana', 'KS': 'Kansas', 'NY': 'New York', 'NE': 'Nebraska', 'OK': 'Oklahoma', 'FL': 'Florida', 'CA': 'California', 'CO': 'Colorado', 'PA': 'Pennsylvania', 'DE': 'Delaware', 'NM': 'New Mexico', 'RI': 'Rhode Island', 'MN': 'Minnesota', 'VI': 'Virgin Islands', 'NH': 'New Hampshire', 'MA': 'Massachusetts', 'GA': 'Georgia', 'ND': 'North Dakota', 'VA': 'Virginia'}


# In[41]:


def get_list_of_university_towns():
    '''Returns a DataFrame of towns and the states they are in from the 
    university_towns.txt list. The format of the DataFrame should be:
    DataFrame( [ ["Michigan", "Ann Arbor"], ["Michigan", "Yipsilanti"] ], 
    columns=["State", "RegionName"]  )
    
    The following cleaning needs to be done:

    1. For "State", removing characters from "[" to the end.
    2. For "RegionName", when applicable, removing every character from " (" to the end.
    3. Depending on how you read the data, you may need to remove newline character '\n'. '''
    
    state_town = []
    with open('university_towns.txt') as file:
        for line in file:
            thisline = line[:-1]
            if thisline[-6:] == '[edit]':
                state = thisline[:-6]
            elif '(' in line:
                town = thisline[:thisline.index('(')-1]
                state_town.append([state, town])
            else:
                town = thisline
                state_town.append([state, town])
    df = pd.DataFrame(state_town,columns = ['State','RegionName'])
    
    return df


# In[56]:


def get_recession_start():
    '''Returns the year and quarter of the recession start time as a 
    string value in a format such as 2005q3'''
    
    gdp = pd.read_excel('gdplev.xls',skiprows = 219)
    gdp = gdp[['1999q4',12323.3]]
    gdp = gdp.rename(columns={'1999q4':'Quarter',12323.3:'Billions'})
    
    decrease = list()
    for i in range(0,gdp.shape[0]-2):
        if gdp['Billions'][i] > gdp['Billions'][i+1] and gdp['Billions'][i+1] > gdp['Billions'][i+2]:
            decrease.append(gdp['Quarter'][i-1])                            
    return decrease[2]
get_recession_start()


# In[53]:


def get_recession_end():
    '''Returns the year and quarter of the recession end time as a 
    string value in a format such as 2005q3'''
    
    gdp = pd.read_excel('gdplev.xls',skiprows = 219)
    gdp = gdp[['1999q4',12323.3]]
    gdp = gdp.rename(columns={'1999q4':'Quarter',12323.3:'Billions'})
    
    start = get_recession_start()
    increase = list()
    for i in range(gdp.index[gdp['Quarter']==start][0],gdp.shape[0]-2):
        if gdp['Billions'][i] < gdp['Billions'][i+1] and gdp['Billions'][i+1] < gdp['Billions'][i+2]:
            increase.append(gdp['Quarter'][i+2])                            
    return increase[0]


# In[47]:


def get_recession_bottom():
    '''Returns the year and quarter of the recession bottom time as a 
    string value in a format such as 2005q3'''
    
    gdp = pd.read_excel('gdplev.xls',skiprows = 219)
    gdp = gdp[['1999q4',12323.3]]
    gdp = gdp.rename(columns={'1999q4':'Quarter',12323.3:'Billions'})
    
    start = get_recession_start()
    end = get_recession_end()
    
    temp = 1e6
    for i in range(gdp.index[gdp['Quarter']==start][0],gdp.index[gdp['Quarter']==end][0]):
        if gdp['Billions'][i] < temp:
            temp = gdp['Billions'][i]
            bottom = gdp['Quarter'][i]
    
    return bottom


# In[8]:


def convert_housing_data_to_quarters():
    '''Converts the housing data to quarters and returns it as mean 
    values in a dataframe. This dataframe should be a dataframe with
    columns for 2000q1 through 2016q3, and should have a multi-index
    in the shape of ["State","RegionName"].
    
    Note: Quarters are defined in the assignment description, they are
    not arbitrary three month periods.
    
    The resulting dataframe should have 67 columns, and 10,730 rows.
    '''
    
    houses = pd.read_csv('City_Zhvi_AllHomes.csv')
    for i in range(2000, 2017):
        if i == 2016:
            houses[str(i) + 'q1'] = houses[[str(i)+'-01',str(i)+'-02',str(i)+'-03']].mean(axis=1)
            houses[str(i) + 'q2'] = houses[[str(i)+'-04',str(i)+'-05',str(i)+'-06']].mean(axis=1)
            houses[str(i) + 'q3'] = houses[[str(i)+'-07',str(i)+'-08']].mean(axis=1)
        else:
            houses[str(i) + 'q1'] = houses[[str(i)+'-01',str(i)+'-02',str(i)+'-03']].mean(axis=1)
            houses[str(i) + 'q2'] = houses[[str(i)+'-04',str(i)+'-05',str(i)+'-06']].mean(axis=1)
            houses[str(i) + 'q3'] = houses[[str(i)+'-07',str(i)+'-08',str(i)+'-09']].mean(axis=1)
            houses[str(i) + 'q4'] = houses[[str(i)+'-10',str(i)+'-11',str(i)+'-12']].mean(axis=1)
    
    houses = houses.drop(houses.columns[[0]+list(range(3,251))],axis = 1)
    #houses = houses.replace({'State':states})
    houses = houses.set_index(['State','RegionName'])

    return houses


# In[49]:


def run_ttest():
    '''First creates new data showing the decline or growth of housing prices
    between the recession start and the recession bottom. Then runs a ttest
    comparing the university town values to the non-university towns values, 
    return whether the alternative hypothesis (that the two groups are the same)
    is true or not as well as the p-value of the confidence. 
    
    Return the tuple (different, p, better) where different=True if the t-test is
    True at a p<0.01 (we reject the null hypothesis), or different=False if 
    otherwise (we cannot reject the null hypothesis). The variable p should
    be equal to the exact p value returned from scipy.stats.ttest_ind(). The
    value for better should be either "university town" or "non-university town"
    depending on which has a lower mean price ratio (which is equivilent to a
    reduced market loss).'''
    
    towns = get_list_of_university_towns()
    start = get_recession_start()
    bottom = get_recession_bottom()
    houses = convert_housing_data_to_quarters()
    houses = houses.reset_index()
    houses['Diff'] = houses[start] - houses[bottom]
    houses = houses[['State','RegionName',start, bottom, 'Diff']]
    
    df = pd.merge(houses, towns, how = 'inner', on = ['State','RegionName'])
    df['UniversityTown'] = True
    result = pd.merge(houses, df, how = 'outer', on = ['State','RegionName',start,bottom,'Diff'])
    result['UniversityTown'] = result['UniversityTown'].fillna(False)
    
    university_town = result[result['UniversityTown']==True]
    non_university_town = result[result['UniversityTown']==False]
    
    t,p = ttest_ind(university_town['Diff'].dropna(),non_university_town['Diff'].dropna())
    different = True if p < 0.01 else False
    better = 'university town' if university_town['Diff'].mean() < non_university_town['Diff'].mean() else 'non-university town'
    
    
    return different, p, better

