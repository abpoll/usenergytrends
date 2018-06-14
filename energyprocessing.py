#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 19 19:04:00 2018

@author: Adam
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import openpyxl
import os

"""
Methods for printing out table for the states
"""

def percent(s):
    '''
    changes float series to % string
    '''
    columns = ['1990ProportionOfTotalConsumption', 
               '2015ProportionOfTotalConsumption', 
               'DifferenceOfProportion']
    if(s.name in(columns)):
        s = s.astype(str) + '%'
    
    

def highlight_max(s):
    '''
    highlight the maximum in a Series yellow.
    '''
    columns = ['1990ProportionOfTotalConsumption', 
               '2015ProportionOfTotalConsumption', 
               'DifferenceOfProportion']
    
    if(s.name in(columns)):
        s = s.apply(lambda x: x[:-1]).astype(float)
    
    is_max = s == s.max()
    return ['background-color: yellow' if v else '' for v in is_max]
   


def color_negative_red(val):
    """
    Takes a scalar and returns a string with
    the css property `'color: red'` for negative
    strings, black otherwise.
    """
    color = 'black'
    if(type(val) != str):
        color = 'red' if val < 0 else 'black'
    return 'color: %s' % color

def make_cons_table(cons_total, codes, msn, pop):
    temp = cons_total[cons_total.MSN == msn]

    #Can store a string as the mapping of temp code description & unit
    #This can be the title of the table that gets printed, plot, etc. 
    
    ##Getting the factor change
    base = temp[temp.Year == 1990].set_index("StateCode")["Data"]
    new = temp[temp.Year == 2015].set_index("StateCode")["Data"]
    
    #Add column for 1990 and 2015 consumption, and FactorChange
    test_df = pd.concat({'1990':base, '2015':new,
                         'FactorChange':new/base}, axis=1)
    #make StateCode a column
    test_df = test_df.reset_index()
    
    #merge population with test_df
    test_df = test_df.merge(pop.reset_index(), how='left', on = 'StateCode',
                            suffixes=['', '_pop'])
    
    #Add columns for consumption as proportion of total in base, comp, and change of these
    #Total is based on last 3 digits of code. Match that string to get the total into its own sub frame
    tot_cons = 'TETCB'
    temp_tot = cons_total[cons_total.MSN == tot_cons]
    
    base_tot = temp_tot[temp_tot.Year == 1990].set_index("StateCode")["Data"]
    new_tot = temp_tot[temp_tot.Year == 2015].set_index("StateCode")["Data"]
    
    test_df['1990ProportionOfTotalConsumption'] = 100 * (base/base_tot).values
    test_df['2015ProportionOfTotalConsumption'] = 100 * (new/new_tot).values
    test_df['DifferenceOfProportion'] = (test_df['2015ProportionOfTotalConsumption'] - 
                                         test_df['1990ProportionOfTotalConsumption']).values
    
    #Add columns for per capita in each year
    test_df['1990ConsumptionPerCapita'] = (test_df['1990']/test_df['1990_pop'].values)
    test_df['2015ConsumptionPerCapita'] = (test_df['2015']/test_df['2015_pop'].values)

    #Add columns for change in per capita over the time
    test_df['ChangeConsumptionPerCapita'] = (test_df['2015ConsumptionPerCapita'] - 
                                             test_df['1990ConsumptionPerCapita'])
    #test_df['PercChangePerCapita'] = (test_df.NewPerCapita - test_df.BasePerCapita)/test_df.BasePerCapita * 100
    
    ##US is index 43. Want to move to bottom of data frame
    target_row = test_df.iloc[[43],:]
    test_df = test_df.drop(test_df.index[43]).append(target_row)
    
    
    return test_df

def plot_cons_table(consumption, msn):
    
    ##Want to format the consumption table more
    #highlight max in each column for starters
    #better float handling
    
    dest = "./consumption_tables/" + codes.loc['TETCB'].to_string(index=False).replace("\n", "_") + "/"
    csv = ".csv"
    
    if not os.path.exists(dest):
        os.makedirs(dest, exist_ok=True)
    
    title = (codes.loc[msn].to_string(index=False)).replace("\n", "_")


    consumption.to_csv(dest+title+csv, float_format='%g')
    
    consumption['1990ProportionOfTotalConsumption'] = consumption['1990ProportionOfTotalConsumption'].astype(str) + '%'
    consumption['2015ProportionOfTotalConsumption'] = consumption['2015ProportionOfTotalConsumption'].astype(str) + '%'
    consumption['DifferenceOfProportion'] = consumption['DifferenceOfProportion'].astype(str) + '%'
    
    
    ##might turn into method for writing out the tables this way
    consumption.style.\
    applymap(color_negative_red).\
    apply(highlight_max).\
    to_excel(dest+title+'.xlsx', engine='openpyxl')
    
    
    
def horizontal_state_charts(cons):
    fig, ax = plt.subplots(nrows=2, ncols=2, figsize=(10,10))
    
    rep_rep = cons[cons.POL_GROUP == 'REP_REP']
    rep_rep = rep_rep[rep_rep.DifferenceOfProportion > rep_rep.DifferenceOfProportion.quantile(.75)].append(cons[cons.StateCode == 'US'])
    
    rep_dem = cons[cons.POL_GROUP == 'REP_DEM'].append(cons[cons.StateCode == 'US'])
    
    dem_rep = cons[cons.POL_GROUP == 'DEM_REP'].append(cons[cons.StateCode == 'US'])
    dem_rep = dem_rep[dem_rep.DifferenceOfProportion > dem_rep.DifferenceOfProportion.quantile(.75)].append(cons[cons.StateCode == 'US'])
    
    dem_dem = cons[cons.POL_GROUP == 'DEM_DEM'].append(cons[cons.StateCode == 'US'])
    dem_dem = dem_dem[dem_dem.DifferenceOfProportion > dem_dem.DifferenceOfProportion.quantile(.75)].append(cons[cons.StateCode == 'US'])
    
    width = .25
    
    pos_rep_rep = list(range(len(rep_rep)))
    
    ax[0,0].barh(pos_rep_rep,
                 rep_rep['1990ProportionOfTotalConsumption'],
                 width,
                 alpha=.5,
                 color='#EE3224')
    ax[0,0].barh([p + width for p in pos_rep_rep],
                  rep_rep['2015ProportionOfTotalConsumption'],
                  width,
                  alpha=.5,
                  color='#F78F1E')
    ax[0,0].set_ylabel('States')
    
    ax[0,0].set_title('1992 and 2016 Rep')
  
    ax[0,0].set_yticks([p + .5 * width for p in pos_rep_rep])
    
    ax[0,0].set_yticklabels(rep_rep['StateCode'])
    
    ax[0,0].set_ylim([min(pos_rep_rep)-width, max(pos_rep_rep)+width*4])
    ax[0,0].set_xlim([0, 100])
    
    pos_dem_dem = list(range(len(dem_dem)))
    
    ax[1,1].barh(pos_dem_dem,
                 dem_dem['1990ProportionOfTotalConsumption'],
                 width,
                 alpha=.5,
                 color='#EE3224')
    ax[1,1].barh([p + width for p in pos_dem_dem],
                  dem_dem['2015ProportionOfTotalConsumption'],
                  width,
                  alpha=.5,
                  color='#F78F1E')
    ax[1,1].set_ylabel('States')
    
    ax[1,1].set_title('1992 and 2016 Dem')
  
    ax[1,1].set_yticks([p + .5 * width for p in pos_dem_dem])
    
    ax[1,1].set_yticklabels(dem_dem['StateCode'])
    
    ax[1,1].set_ylim([min(pos_dem_dem)-width, max(pos_dem_dem)+width*4])
    ax[1,1].set_xlim([0, 100])
    
    pos_dem_rep = list(range(len(dem_rep)))
    
    ax[1,0].barh(pos_dem_rep,
                 dem_rep['1990ProportionOfTotalConsumption'],
                 width,
                 alpha=.5,
                 color='#EE3224')
    ax[1,0].barh([p + width for p in pos_dem_rep],
                  dem_rep['2015ProportionOfTotalConsumption'],
                  width,
                  alpha=.5,
                  color='#F78F1E')
    ax[1,0].set_ylabel('States')
    
    ax[1,0].set_title('1992 Dem, 2016 Rep')
  
    ax[1,0].set_yticks([p + .5 * width for p in pos_dem_rep])
    
    ax[1,0].set_yticklabels(dem_rep['StateCode'])
    
    ax[1,0].set_ylim([min(pos_dem_rep)-width, max(pos_dem_rep)+width*4])
    ax[1,0].set_xlim([0, 100])
 
    pos_rep_dem = list(range(len(rep_dem)))
    
    ax[0,1].barh(pos_rep_dem,
                 rep_dem['1990ProportionOfTotalConsumption'],
                 width,
                 alpha=.5,
                 color='#EE3224')
    ax[0,1].barh([p + width for p in pos_rep_dem],
                  rep_dem['2015ProportionOfTotalConsumption'],
                  width,
                  alpha=.5,
                  color='#F78F1E')
    ax[0,1].set_ylabel('States')
    
    ax[0,1].set_title('1992 Rep, 2016 Dem')
  
    ax[0,1].set_yticks([p + .5 * width for p in pos_rep_dem])
    
    ax[0,1].set_yticklabels(rep_dem['StateCode'])
    
    
    ax[0,1].set_ylim([min(pos_rep_dem)-width, max(pos_rep_dem)+width*4])
    ax[0,1].set_xlim([0, 100])
    ax[0,1].legend(loc='upper right')
    
    ax[0,1].legend(['1990', '2015'], loc='upper right')
    plt.suptitle('Top Renewable Energy Proportion of Total Consumption Shifters',
                 fontsize=14)
    
"""
Read in the SEDS data
"""
state_cons = pd.read_csv("./data/Complete_SEDS.csv")


"""
Format the data into total consumption and total final consumption 
based on Butane units
Going forward, Final End Use not considered
"""
#total consumption rows, butane units only
state_cons_total = state_cons[state_cons.MSN.str.contains("TCB$")]
#state_cons_total.to_csv("./data/Complete_SEDS.csv") overwrote original file

#total final consumption rows, butane units only
#state_final_cons_total = state_cons[state_cons.MSN.str.contains("TXB$")]

#1990 and 2015 only for consumption comparisons
sct = state_cons_total[(state_cons_total.Year == 1990) | (state_cons_total.Year == 2015)]
#sfct = state_final_cons_total[(state_final_cons_total.Year == 1990) | (state_final_cons_total.Year == 2015)]

#REMOVE DC
sct = sct[~sct.StateCode.str.contains("DC")] #From 3380 to 3315
#sfct = sfct[~sfct.StateCode.str.contains("DC")] #From 2392 to 2346


"""
Merge the code descriptions to MSN codes
"""
##Map MSN to its full phrase
codes = pd.read_csv("./data/Codes_and_Descriptions.csv", header =9)[['MSN', 'Description', 'Unit']]
codes = codes[pd.notnull(codes.MSN)]
codes = codes[codes.MSN.str.contains("TCB$")]


sct = pd.merge(sct, codes, on = 'MSN')
#sfct = pd.merge(sfct, codes, on = 'MSN')

codes = codes.set_index('MSN')


"""
Merge population data 
"""

pop = pd.read_csv("./data/SEDSPopulation.csv")
pop = pop[~pd.isnull(pop.State)]

#Remove DC
pop = pop[~pop.State.str.contains("District of Columbia")] 

#Rename to StateCode for merging
pop = pop.rename(columns = {'State': 'StateCode'})
pop = pop.set_index("StateCode")

#Keep 1990 and 2015 years
pop = pop[['1990', '2015']]

#Get to correct units (was recorded in 1000s)
pop = pop * 1000



"""
Codes of interest for table outputs
BMTCB (biomass)
CLTCB (Coal)
ESTCB (electricity total consumption i.e., sold)
FFTCB (Fossil fuels)
GETCB (Geothermal)
HYTCB (Hydropower)
NGTCB (Natural gas including supplemental gaseous fuels)
PATCB (all petroleum)
RETCB (Renewable)
SOTCB (Solar)
TETCB (Total)
WYTCB (Wind)

Create list of these and print out tables
"""
codes_output = ('BMTCB', 'CLTCB', 'ESTCB', 'FFTCB', 'GETCB', 'HYTCB', 
                'NGTCB', 'PATCB', 'RETCB', 'SOTCB', 'WYTCB')

for c in codes_output:
   temp =  make_cons_table(sct, codes, c, pop)
   plot_cons_table(temp, c)


"""
Exploration analysis using a sample code
Note: Why is some proportion greater than 100??? 
"""

temp = make_cons_table(sct, codes, 'FFTCB', pop)
bound = temp.DifferenceOfProportion.abs().describe()['75%']
temp = temp[temp.DifferenceOfProportion.abs() >= bound]
temp = temp.reindex(temp.DifferenceOfProportion.abs().sort_values(ascending=False).index)


#temp.reindex(temp.DifferenceOfProportion.abs().sort_values(ascending=False).index)
#temp.DifferenceOfProportion.abs().describe()


"""
For renewable RETCB, make composition charts
First, add political data field that says Rep-Rep, Rep-Dem, etc. as a category
Then, for each category, we get an x-axis, with the stacked bar composed of %renewable 1990, %renewable2015
One issue with this is the actual making of the plot. I don't know how to have plot-tick groups
What I mean by this is that %1990 and %2015 is a stacked bar with 1-% on top
How do I repeat these labels so we have 8 of them, and they're grouped into 4 categories? 
Better idea - different plot for each group since there will be a lot of state names
And, it might be so crowded that for each group there should be a cutoff of states shown. 
Maybe, if size >= 4, choose top 25% shifters and display
If < 4, show all
"""

#renewable cons_table store
ren = make_cons_table(sct, codes, 'RETCB', pop)

#read in 92 and 16 election data
elec_92 = pd.read_csv("./data/92Election.csv")
elec_16 = pd.read_csv("./data/16Election.csv")

#Process data to add Rep/Dem labels
elec_92.loc[elec_92.EV_D.isnull(), '90POL'] = 'REP'
elec_92.loc[~elec_92.EV_D.isnull(), '90POL'] = 'DEM'

elec_16.loc[elec_16.EV_D.isnull(), '15POL'] = 'REP'
elec_16.loc[~elec_16.EV_D.isnull(), '15POL'] = 'DEM'

#Make elec df
elec = elec_92[['STATE', '90POL']].merge(elec_16[['STATE', '15POL']], 
                                          on='STATE', how='inner')

#Update cons_table with political data
ren = ren.merge(elec, left_on='StateCode', right_on='STATE', how='left').drop(columns=['STATE'])

#Add category column
ren.loc[(ren['90POL'] == 'REP') & (ren['15POL'] == 'REP'), 'POL_GROUP'] = 'REP_REP'
ren.loc[(ren['90POL'] == 'DEM') & (ren['15POL'] == 'REP'), 'POL_GROUP'] = 'DEM_REP'
ren.loc[(ren['90POL'] == 'REP') & (ren['15POL'] == 'DEM'), 'POL_GROUP'] = 'REP_DEM'
ren.loc[(ren['90POL'] == 'DEM') & (ren['15POL'] == 'DEM'), 'POL_GROUP'] = 'DEM_DEM'

#As a note, the REP_DEM group has only 1 state. The others >= 4, so can 
#do top 25% of largest shifters for plotting

#Plotting is going to be tricky. Have to think about best way to do this
temp = ren[ren.POL_GROUP == 'REP_REP']
#bound = temp.DifferenceOfProportion.abs().describe()['75%']
#temp = temp[temp.DifferenceOfProportion.abs() >= bound]

# Setting the positions and width for the bars
pos = list(range(len(temp))) 
width = 0.25 
    
# Plotting the bars
fig, ax = plt.subplots(figsize=(5,8))

# Create a bar with 1990 data,
# in position pos,
plt.barh(pos, 
        #using df['pre_score'] data,
        temp['1990ProportionOfTotalConsumption'], 
        # of width
        width, 
        # with alpha 0.5
        alpha=0.5, 
        # with color
        color='#EE3224', 
        
        ) 

# Create a bar with 2015 data,
# in position pos + some width buffer,
plt.barh([p + width for p in pos], 
        #using df['mid_score'] data,
        temp['2015ProportionOfTotalConsumption'],
        # of width
        width, 
        # with alpha 0.5
        alpha=0.5, 
        # with color
        color='#F78F1E', 
       
        )

# Set the y axis label
ax.set_ylabel('States')

# Set the chart's title
ax.set_title('1992 Republican & 2016 Republican Renewable Energy Proportion of Total Energy Consumption')

# Set the position of the x ticks
ax.set_yticks([p + .5 * width for p in pos])

# Set the labels for the x ticks
ax.set_yticklabels(temp['StateCode'])

# Setting the x-axis and y-axis limits
plt.ylim(min(pos)-width, max(pos)+width*4)
plt.xlim([0, 100])

# Adding the legend and showing the plot
plt.legend(['1990', '2015'], loc='upper right')
plt.grid()
plt.show()


##Review and implement for all energy types
import seaborn as sns

cons = ren.copy()


lim = abs(cons[cons.StateCode=='US'].DifferenceOfProportion).iloc[0]

temp = cons[abs(cons.DifferenceOfProportion) > lim]
temp_out = cons[abs(cons.DifferenceOfProportion) < lim]


fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(10,10))

palette ={"DEM_DEM":"blue","DEM_REP":"lightblue","REP_DEM":"palevioletred", "REP_REP":"red"}

sns.barplot(ax=ax[0],x="DifferenceOfProportion", y="StateCode", hue="POL_GROUP", data=temp, 
                 palette=palette, hue_order=['DEM_DEM', 'DEM_REP', 'REP_DEM', 'REP_REP'],
                 dodge=False).set_title("Big Shifters")
                 

sns.barplot(ax=ax[1],x="DifferenceOfProportion", y="StateCode", hue="POL_GROUP", data=temp_out, 
                 palette = palette, hue_order=['DEM_DEM', 'DEM_REP', 'REP_DEM', 'REP_REP'],
                 dodge=False).set_title("Small Shifters")
      