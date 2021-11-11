#method spreadsheet_update() creates/updates spreadsheets for multiple fishids at once, given a tagmanager RFID spreadsheet filename
    #output sheet names will be 'fishid_all.xlsx' (filepath of choice)- will update existing spreadsheets and make new ones for fishids with no spreadsheet
#method aggregate_raster() creates raster plots of RFID readings for given fishids over a given date range
    #only graphs RFID readings between 08:00 and 20:00
#method aggregate_barplot() creates bar plots of RFID readings for given fishids over a given date range
    #only graphs RFID readings between 08:00 and 20:00
#TODO decide whether AntennaIDs can be kept at 1,3, and 5 or need to be automated for whatever AntennaIDs are in use- discuss with Karen
#TODO adjust space between labels/axes, margin space, graph distance, etc for better-looking graphs

import numpy as np
import pandas as pd
from os import path #imported to test if file exists
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.axes as axs
import seaborn as sns
import xlrd
import matplotlib.dates as mdates
from matplotlib.dates import DateFormatter


class FishAggregator: #create class
    def __init__(self, target_fishids, filenames, filepath_in, filepath_out): #define class variables
        print("INIT")
        self.target_fishids = target_fishids
        self.filenames = filenames
        self.filepath_in = filepath_in
        self.filepath_out = filepath_out
        self.target_start, self.target_end = target_start, target_end


    def build_dict_all(self): #this function reads in every new file, and compiles them into a dictionary of dataframes, so that they can
        #be used between fishids without re-loading in each time
        print("build dict all")
        fishdict = {} #create dictionary
        for i in self.filenames: #for every filename
            pathname = self.filepath_in + i + '.xlsx' #combines file and path for reading in
            new_file = pd.read_excel(pathname) #loads in new excel as a dataframe
            fishdict[i] = new_file #adds the dataframe to the fishdictionary under the index of its filename
            print('READING IN FILE: ' + i + '...')
        print('FISHDICTIONARY LOADED')
        return(fishdict)


    def fishid_from_dict(self): #compiles dataframe of all RFID readings for a given fishid, across all dates
        fishlist = pd.DataFrame() #create empty dataframe to hold the fishid readins from each individual dataframe
        #print('COMPILING SPREADSHEET FOR FISHID: ' + self.fishid + '...')
        for i in self.fishdict: #for each dataframe in the dictionary of dataframes (containing all fish, all date ranges)
            df = self.fishdict[i] #df is the dataframe at that index
            df.columns = df.columns.str.replace(" ","") #take spaces out of column names
            df_fishid = df[(df['HEXTagID'] == self.fishid)] #takes only the RFID readings for the fishid of choice
            fishlist = fishlist.append(df_fishid) #add dataframe to overall dataframe of all RFID readings for fishid
        #fishlist = fishlist.drop(columns= ['DownloadTime', 'DownloadDate'])
        try:
            fishlist = fishlist.drop(columns= ['IsDuplicate']) #drops columns to allow duplicate RFID readings to be recognized
        except:
            pass
        print(fishlist.head(2))
        return(fishlist)

    def check_and_export(self): #this function checks whether the fishid already has a saved spreadsheet
        pathname = self.filepath_out + self.fishid + '_alldates.xlsx' #combines name and filepath to test if there is already a sheet for the fishid
        print('CHECKING FOR EXISTING FILENAMES: ' + pathname + '...')
        if path.exists(pathname): #if there is already a spreadsheet with that filename...
            previous_file = pd.read_excel(pathname) #read in that spreadsheet as a dataframe
            print('THERE IS ALREADY A SHEET FOR FISHID: ' + self.fishid)
            output_file = previous_file.append(self.fishlist) #adds new list to end of existing list
            output_file = output_file.drop_duplicates() #removes any overlap readings from the old and new file.
            add_length = len(output_file.index) - len(previous_file.index) #calculate how many RFID rows are being added to spreadsheet
        else: #if there is no previous spreadsheet...
            print('THERE IS NO PREVIOUS SHEET FOR FISHID: ' + self.fishid)
            output_file = self.fishlist #no previous sheet exists, so the sheet in python becomes the output file
            output_file = output_file.drop_duplicates() #removes any overlap readings from the old and new file.
            add_length = len(output_file.index) #calculate how many RFID rows are being added in new spreadsheet
        output_file = output_file.sort_values(by=['ScanDate', 'ScanTime']) #sort sheet by scandate and then scantime
        print('ADDING ' + str(add_length) + ' RFID READINGS TO SPREADSHEET FOR ' + self.fishid + '...')
        self.fishid_fishdict[self.fishid] = output_file #add the dataframe to dataframe dictionary of fishids (1 entry per fishid, over all dates)
        output_file.to_excel(pathname, index= False) #export to folder
        print(self.fishid + ' SPREADSHEET SAVED') #appends to existing dataframe (or not), and exports to folder by running check_and_export


    def update_spreadsheets(self): #updates spreadsheets with new RFID readings for all fishids in list
        print("update_spreadsheets")
        self.fishdict = self.build_dict_all() #gets aggregate dataframe of inputs for fishid by running fishname_cycler
        self.fishid_fishdict = {} #creates dataframe dictionary to hold dataframes of each fishid, so that they don't have to be re-read in for graphing
        for i in self.target_fishids: #for every fishid in the list...
            self.fishid = i #that fishid becomes self.fishid
            self.fishlist = self.fishid_from_dict() #compiles spreadsheet of all new reads for that fishid
            self.check_and_export() #updates (or creates new) spreadsheet for that fishid
        print('SPREADSHEETS UPDATED FOR FISHIDS: ' + str(self.target_fishids))

    def convert_date(self, input_date): #function converts a string of text into a readable date format (requires mm/dd/yyyy input)
        output_date = datetime.strptime(input_date, '%m/%d/%Y') #converts input date (string) into a datetime function
        return(output_date)

    def aggregate_fishids_by_date(self): #combines RFID readings for fishids of your choice, between dates of your choice, into one dataframe-
        #sets this dataframe as self.fishids_aggregated_by_date, callable in other methods
        self.fishid_fishdict = {} #create empty dictionary to hold spreadsheets for all target fishids
        for i in self.target_fishids: #for each target fishid...
            pathname = self.filepath_out + i + '_alldates.xlsx' #combines name and filepath to test if there is already a sheet for the fishid
        #print('CHECKING FOR EXISTING FILENAMES: ' + pathname + '...')
            if path.exists(pathname): #if there is already a spreadsheet with that filename...
                previous_file = pd.read_excel(pathname) #read in that spreadsheet as a dataframe
                print('THERE IS ALREADY A SHEET FOR FISHID: ' + i)
                self.fishid_fishdict[i] = previous_file #insert the spreadsheet for that fishid into the dataframe dictionary
            else:
                print('THERE IS NO SHEET FOR FISHID: ' + i)
                self.fishlist = self.fishid_from_dict()  #????
                self.fishlist[i] = pd.DataFrame() #insert empty dataframe as place in dictionary- TODO does this work when there are no reads?
        df_for_graphing = pd.DataFrame() #create empty dataframe to hold all fishids for the date range
        target_start, target_end = self.convert_date(self.target_start), self.convert_date(self.target_end) #convert start and end dates into datetime objects
        for i in self.target_fishids: #for each target fishid...
            fishid_fishlist = self.fishid_fishdict[i] #pull out the dataframe in the dictionary of dataframes for that fishid
            culled_fishlist = fishid_fishlist[(fishid_fishlist['ScanDate'].apply(self.convert_date) >= target_start) & (fishid_fishlist['ScanDate'].apply(self.convert_date) < target_end)]
            #^for that fishid dataframe, pulls out only the RFID readings for the daterange between target_start and target_end
            df_for_graphing = df_for_graphing.append(culled_fishlist) #add it to the dataframe of all fishids for that date range
        self.fishids_aggregated_by_date = df_for_graphing #self.fishids_aggregated_by_date can now be used in different methods within the class
        print('GENERATED COMBINED DATAFRAME FOR FISHIDS:' + str(self.target_fishids) + ' BETWEEN DATES: ' + self.target_start + ' - ' + self.target_end) #prints that dataframe for fishids and dates has been created

    def convert_time(self, input_time): #converts a value from a string into a datetime (time) object
        output_time = datetime.strptime(input_time, '%H:%M:%S.%f')
        return(output_time)

    def select_hours(self, input_sheet, start_time, end_time): #culls a sheet to only a certain range of hours
        input_sheet['TimeConverted'] = input_sheet['ScanTime'].apply(self.convert_time) #make a new column of datetime time objects for scantime
        input_sheet = input_sheet[(input_sheet['TimeConverted'] <= self.convert_time(end_time)) & (input_sheet['TimeConverted'] >= self.convert_time(start_time))] #cull spreadsheet to just readings between target times
        return(input_sheet)

    def generate_raster(self, raster_start, raster_end): #given a set list of target fishids readings between a start date and end date,
        #this function generates a figure containing one raster plot for each AntennaID, with all target fish, between those dates
        #this function culls so that only times between 08:00 and 20:00 are shown
        #instructions for including AntennaID5 are commented out
        self.raster_start = raster_start
        self.raster_end = raster_end
        df = self.fishids_aggregated_by_date #load dataframe of all fishids for the chosen date range
        df = self.convert_to_datetime(df) #add column of datetime objects for ScanDateTime
        df = self.select_hours(df, self.raster_start, self.raster_end) #culls dataframe to just readings between 08:00 and 20:00 (does not include 20:00)
        df.to_excel(self.filepath_out + 'justchecking.xlsx')
        df_antennaid_1 = df[df.AntennaID == 1] #sort all RFId reads from AntennaID1 into one dataframe
        df_antennaid_3 = df[df.AntennaID == 3] #sort all RFId reads from AntennaID3 into one dataframe
        #df_antennaid_5 = df[df.AntennaID == 5]
        print('SHEETS SORTED BY ANTENNA ID- RFID READS FOR ANTENNAID 1: ' + str(len(df_antennaid_1.index)) + ' RFID READS FOR ANTENNAID 3: ' + str(len(df_antennaid_3.index)))
        #fig, (ax1, ax2, ax3) = plt.subplots(3)
        fig, (ax1, ax2) = plt.subplots(2, figsize=(18,7)) #makes 2 stacked subplots in one image, image size is 18x8 inches
        fig.suptitle('RFID readings for fishids: ' + str(self.target_fishids) + ' between dates: ' + self.target_start + ' - ' + self.target_end) #creates title for figure, noting fishid and dates
        sns.scatterplot(x= df_antennaid_1.ScanDateTime, y= df_antennaid_1.HEXTagID, data= df_antennaid_1, marker = '|', hue = df_antennaid_1.HEXTagID, s = 100, ax= ax1) #creates raster plot for AntennaID1
        sns.scatterplot(x= df_antennaid_3.ScanDateTime, y= df_antennaid_3.HEXTagID, data= df_antennaid_3, marker = '|', hue = df_antennaid_3.HEXTagID, s = 100, ax= ax2) #creates raster plot for AntennaID3
        ax1.title.set_text('AntennaID 1') #subtitle
        ax2.title.set_text('AntennaID 3') #subtitle
        #sns.scatterplot(x= df_antennaid_5.ScanDateTime, y= df_antennaid_5.HEXTagID, data= df_antennaid_5, marker = '|', hue = df_antennaid_5.HEXTagID, s = 100, ax= ax3)
        plt.subplots_adjust(bottom=0.2, hspace=0.5) #creates space at bottom of figure and between plots
        plt.show() #display plots- TODO save plots as image file



    def convert_to_datetime(self, df): #for a given spreadsheet, combines ScanDate and ScanTime columns into a ScanDateTime column, and makes the rows datetime objects
        df['DateTimeRaw'] = df['ScanDate'] + ' ' + df['ScanTime'] #combine scandate and scantime as strings
        df['ScanDateTime'] = pd.to_datetime(df.DateTimeRaw, format = '%m/%d/%Y %H:%M:%S.%f') #convert datetimeraw column into a datetime object that can be used
        return(df)

    def create_bargraph(self, hour_start, hour_end): #from a dataframe of RFID readings for a group of target fishids between a target daterange, produces a bargraph of RFID counts binned by hour
        print('CREATING BARGRAPH FOR FISHIDS: ' + str(self.target_fishids) + ' FOR TARGET DATES: ' + target_start + ' - ' + target_end + '...')
        df = self.fishids_aggregated_by_date #reads in the aggregated df of target fishids in the target daterange
        df = self.convert_to_datetime(df) #creates a column of datetime objects for the RFID reading (df['ScanDateTime'])
        df['ScanDateTimeShort'] = df['ScanDateTime'].values.astype('datetime64[h]') #cuts the datetime column to just month, day and hour
        possible = pd.date_range(self.target_start, self.target_end, freq='h') #creates list of all datetimes between start dayhour and end dayhour
        possible = possible[:-1] #removes the first hour of end date (output will not include any hour in end date)
        possible_culled = [] #create empty list to hold possible all hours (including those with 0 entries) that will be in bar graph
        for i in possible: #adds hours between 08:00 and 20:00 to a new series, then makes that series into 'possible'
            if ((i.hour <= hour_end) and (i.hour >= hour_start)): #if the hour is between 08:00 and 20:00...  CHANGED FROM if ((i.hour <= 19) and (i.hour >= 8)):
                possible_culled.append(i) #add that hour to the list of hours to be included in the binned graph
        df_tograph = pd.DataFrame(possible_culled, columns= ['possible_culled']) #create empty dataframe- first column is list of all possible datehours to be graphed, column name is possible_culled
                                                #^will contain columns with the RFID frequency for each datehour in possible_culled for each target fishid
        for i in self.target_fishids: #for each fishid in the list of target fishids...
            #TODO create a df holding only readings for that fishid
            df_target_fishid = df[df['HEXTagID'] == i] #creates dataframe holding only RFID readings for that individual target fishid
            #TODO for each fishid df, get list of frequencies for each datehour in possible[], and add it as a column as df_tograph[fishid]
            df_tograph[i] = self.get_fishid_occurences_for_datehour_range(df_target_fishid, possible_culled) #adds that fishid's RFID frequency list (for each datehour in possible_culled) as a column to the tograph dataframe
            #TODO ^ will df_tograph[i] (meant to name the column after that fishid string) work?
        #TODO once df of RFID counts for each fishid for possible_culled is created, make graph
        #fig, ax = plt.subplots(1, figsize=(18,7)) #makes 2 stacked subplots in one image, image size is 18x8 inches
        #x_vals = df_tograph['possible_culled'] #x values are all the datehours in possible_culled
        #y_vals = df_tograph[self.target_fishids] #y values are all the frequencies of RFID readings for the possible_culled datehours, for each fish
        fig, ax = plt.subplots(figsize=(18,7))
        df_tograph.plot(x='possible_culled', y=self.target_fishids, kind='bar', width= self.barwidth, ax=ax)
        #fig.autofmt_xdate()
        ax.set_xticklabels(labels= df_tograph.possible_culled, rotation=55, ha='right')
        ax.xaxis.set_major_locator(mdates.WeekdayLocator(interval=1))
        #ax.set_ylim([0,500])
        #ax.set_xlim([datetime.strptime(self.target_start, '%m/%d/%Y'), datetime.strptime(self.target_end, '%m/%d/%Y')])
        plt.title('RFID readings for fishids: ' + str(self.target_fishids) + ' between dates: ' + self.target_start + ' - ' + self.target_end) #creates title for figure, noting fishid and dates
        plt.xlabel('Date and Time (H)')
        plt.ylabel('RFID Readings')
        plt.tight_layout()
        plt.subplots_adjust(left= 0.05)
        plt.show()


    def get_fishid_occurences_for_datehour_range(self, fishid_df, possible_datehours): #given a df of RFID readings for only one target fishid, and a list of datehours to be graphed, returns a list of that fishid's RFID counts for each datehour to be graphed
        freqlist = [] #empty list to hold the RFID frequencies for each datehour (including 0 if there are none for the datehour)
        for i in possible_datehours: #for each datehour in the list of all datehours between the start and end dates and between 08:00 and 20:00...
            if (i in fishid_df['ScanDateTimeShort'].values): #if the df for the input fishid contains that datehour...
                freqlist.append(fishid_df['ScanDateTimeShort'].value_counts()[i]) #return the number of RFID readings for that datehour
            else: #if there are no RFID readings for that datehour...
                freqlist.append(0) #add 0 to the list of frequencies
        return(freqlist) #return the list of frequencies,
                        #^which will line up with list of frequencies for all other fishids because all are structure around the list of possible datehours



#set variables
#all_fishids = ['3D6.1D59B07986', '3D6.1D59B07981', '3D6.1D59B0796C', '3D6.1D59B07978','3D6.1D59B0793D','3D6.1D599FDD2C',
#                '3D6.1D599FDD53','3D6.1D599FDD2A','3D6.1D599FDD3F','3D6.1D599FDD07','3D6.1D599FDD27','3D6.1D599FDD31']
                #^this list doesn't get used in the script- just contains all the fishids for easy copying and pasting
all_fishids = ['3D6.1D59B07986','3D6.1D599FDD2A','3D6.1D599FDD27','3D6.1D599FDD31',  '3D6.1D59B07956', '3D6.1D59B07953', '3D6.1D59B0794C', '3D6.1D59B07940', '3D6.1D59B07974', '3D6.1D59B0794E', '3D6.1D59B0794A','3D6.1D59B07944', '3D6.1D59B047', '3D6.1D59B07932']
filenames = ['11-10-2021_tagmanager_all']
                #^list of new spreadsheet filenames to be added (updating spreadsheets)
filepath_in = 'C:/Users/karen/OneDrive/Documents/0_RESEARCH/RFID/'
                #^shared filepath of files to be read in (assumes they are in same folder) (updating spreadsheets)
filepath_out = 'C:/Users/karen/OneDrive/Documents/0_RESEARCH/RFID/ExportedData/'
                #^filepath of destination for aggregate sheet (updating spreadsheets) (plotting)
target_start, target_end = '10/25/2021', '11/09/2021'  #for graphing, etc- what dates should the program act on (plotting)
                # if only looking at one day (raster), input date of and then one day after '05/03/2021' '05/04/2021' to look at 05/03/2021
#input_target_fishids = ['3D6.1D599FDD07'] #list of fishids to be targeted (plotting)
input_target_fishids = ['3D6.1D59B07940', '3D6.1D59B07947','3D6.1D59B07932']
#, '3D6.1D599FDD53', '3D6.1D599FDD07'
new_males = ['3D6.1D59B07932', '3D6.1D59B07947']
female_fish = ['3D6.1D59B07978', '3D6.1D59B07981', '3D6.1D599FDD07', '3D6.1D599FDD27', '3D6.1D599FDD2A', '3D6.1D599FDD31', '3D6.1D599FDD53']
new_females = ['3D6.1D59B07956', '3D6.1D59B07953', '3D6.1D59B0794C', '3D6.1D59B07940', '3D6.1D59B07974', '3D6.1D59B0794E', '3D6.1D59B0794A','3D6.1D59B07944']
fishobject = FishAggregator(input_target_fishids, filenames, filepath_in, filepath_out)  #sets variables for class
fem_round1 = ['3D6.1D59B0796C', '3D6.1D59B07981', '3D6.1D59B07978']
mal_round1 = ['3D6.1D59B07986', '3D6.1D59B0793D']

def spreadsheet_update(): #updates RFID spreadsheets for all fishids
    #^be sure to set filenames, filepath_in and filepath_out to what you need them to be
    fishobject.target_fishids = all_fishids #sets target fishids to all fishids
    fishobject.update_spreadsheets() #updates spreadsheets

def aggregate_raster(raster_start, raster_end): #creates raster plots for fishids and date ranges of choice (set target_fishids, target_start, and target_end)
    #input raster start end as '09:00:00.00' or '20:00:00.00'
    fishobject.target_fishids = input_target_fishids
    fishobject.aggregate_fishids_by_date() #creates one dataframe holding readings for all target fishids between the two target dates
    fishobject.generate_raster(raster_start, raster_end) #generates raster plot from dataframe

def aggregate_barplot(hourstart, hourend):
    #aggregate_barplot(9,20)
    fishobject.target_fishids = input_target_fishids
    fishobject.aggregate_fishids_by_date()
    fishobject.barwidth = 1
    fishobject.create_bargraph(hourstart, hourend)

#spreadsheet_update()
#aggregate_raster('10:00:00.00', '12:00:00.00')
#aggregate_barplot()
"""
for fish in female_fish:
    input_target_fishids = [fish]
    aggregate_barplot()
"""
