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
    test_df = test_df.shift(-1)
    test_df.iloc[-1] = target_row.squeeze()
    test_df = test_df.drop(test_df.index[42])
    
    
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
