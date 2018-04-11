library(tidyverse)
library(stringr)

cons <- read.csv("/Users/Adam/usenergytrends/data/use_US.csv")
state_cons <- read.csv("/Users/Adam/usenergytrends/data/Complete_SEDS.csv")

#total consumption rows, butane units only
state_total_cons <- state_cons[grepl("TC", state_cons$MSN),]
state_total_consb <- state_total_cons[grepl("B", state_total_cons$MSN), ]

#total final consumption rows, butane units only
state_total_fcons <- state_cons[grepl("TX", state_cons$MSN),]
state_total_fconsb <- state_total_fcons[grepl("B", state_total_fcons$MSN), ]

#1990 and 2015 only for comparisons
stc_comp <- state_total_consb[grepl("1990|2015", state_total_consb$Year), ]
stfc_comp <- state_total_fconsb[grepl("1990|2015", state_total_fconsb$Year), ]

#REMOVE DC, per Prof. instructions
stc_comp <- stc_comp[stc_comp$StateCode != 'DC',]
stfc_comp <- stfc_comp[stfc_comp$StateCode != 'DC',]

##Map MSN to its full phrase
codes <- read.csv("/Users/Adam/usenergytrends/data/Codes_and_Descriptions.csv", skip =9)
codes <- select(codes, MSN, Description, Unit)
codes <- codes[grepl("TC|TX", codes$MSN),]
codes <- codes[grepl("B", codes$MSN),] #57 codes to go through
rownames(codes) <- NULL
#paste((codes %>% filter(MSN == 'TETCB'))$Description) 
#use this for 'mapping' the msn code for plotting, tables, etc

#percent change function
pct <- function(x) {diff(x)/x[1:length(diff(x))] * 100}

## Function to get df of states with % change from year to year for given MSN ##
#The data frame input is in EIA format for energy consumption data. 
#A specific value for MSN is given along with the df
#Then, for given years in the df for each state
#a % change is calculated and stored for each row
#The final df will be state-years-%change
states.perc.change <- function(cons_frame, msn){
  
  ##Store change in total consumption for each code in a df for normalizing later
  normalize <- cons_frame[str_sub(cons_frame$MSN, 1, 3) == 'TET',]
  normalize <- normalize %>% group_by(StateCode) %>% summarize(Change = diff(Data))
  
  #hold the string list of states and US
  states <- as.character(unique(cons_frame$StateCode)) 
  
  #subset the MSN values of interest from the dataframe
  msn_frame <- subset(cons_frame,grepl(msn, as.character(cons_frame$MSN)))
  years <- msn_frame %>% distinct(Year)
  
  #Create the string MSN-BaseYr-CompYr
  comp <- paste(as.character(years[,1][1]), as.character(years[,1][2]), sep="-")
  msn <- codes$Description[codes$MSN == msn]
  comp <- paste(msn, comp, sep=" ")
  #Get perc. change for each state
  perc_change <- msn_frame %>% group_by(StateCode) %>% summarize(PercentChange = pct(Data))
  #Get diff. for each state
  change <- msn_frame %>% group_by(StateCode) %>% summarize(Change = diff(Data))
  
  #Join together
  perc_changes <- merge(perc_change, change)
  
  #Rename and finalize data structure
  rename(perc_changes, Location=StateCode)
  perc_changes <- perc_changes %>% rowwise() %>% mutate(Comparison=comp)
  
  #Move US to bottom of df for later use
  top = perc_changes[-grep("US", as.character(perc_changes$StateCode)),]
  bottom = perc_changes[grep("US", as.character(perc_changes$StateCode)),]
  perc_changes <- rbind(top, bottom)
  
  return(perc_changes)
}


#Method review
#states.perc.change(stc_comp, 'WYTCB') %>% filter(!is.nan(PercChange), is.finite(PercChange))
#Only 5 States, and US as whole have non 0 1990 wind value
#Need to divide into categories - Perc. Change, Growth (maybe a log scale of growth), and No Progress
#So a column can also be returned in above method that returns the diff

#filter(!is.finite(PercentChange), !is.nan(PercentChange)) relative growth states
#filter(is.nan(PercentChange)) non mover states

##Function that takes in the states data frame of PercentChange, Change, Comparison
#and writes a figure for %changers and relative changers (and a string for non changers)
#to a file (ie MSN_1990_2015 will be folder where MSN will be fuly written out and
#files will be titled appropriately)
states.change.plots <- function(change_frame){
  changers <- change_frame %>% filter(!is.nan(PercentChange))
  zero_nochange <- change_frame %>% filter(is.nan(PercentChange))
  
  movers_x <- which(is.finite(changers$PercentChange))
  movers_y <- changers[movers_x,]$PercentChange
  
  #Print out the list of states w/ 0 cons. in base and comp. year
  cat(cat("The Following States have 0 Consumption in 1990 and 2015: "), 
      cat(as.character(t2$StateCode), sep=", "))
  
  logChange = log2(changers$Change)
  #figure out how to plot by index while still printing state code so 
  #US is all the way at the right. Or, color it differently for now. 
  ggplot(changers, aes(x=StateCode, y = logChange)) + geom_col()
  
  #Title should come from the Comparison entry 
}

