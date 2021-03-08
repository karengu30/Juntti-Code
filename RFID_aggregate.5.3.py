# UPDATE: version 5.3 saves output individual fishid files by month rather than in bulk
    #folder names are 'Split Fishids' -> Fishid -> month.year.xlsx
    #TODO still has yet to be updated so that aggregate_Raster(), aggregate_barplot and aggregate_export() can work with the files split by month

# method spreadsheet_update() creates/updates spreadsheets for multiple fishids at once, given a tagmanager RFID spreadsheet filename
    #output sheet names will be 'fishid_all.xlsx' (filepath of choice)- will update existing spreadsheets and make new ones for fishids with no spreadsheet
    #if length of a spreadsheet for one fishid exceeds 1 million (near limit that pandas or excel can handle), program creates a new spreadsheet (_most_recent)
    #the older dates are assigned to a spreadsheet with the filename 'fishid_dates_firstscandate_lastscandate.xlsx'
#method aggregate_raster() creates raster plots of RFID readings for given fishids over a given date range
    #only graphs RFID readings between 08:00 and 20:00
#method aggregate_barplot() creates bar plots of RFID readings for given fishids over a given date range
    #only graphs RFID readings between 08:00 and 20:00
#TODO decide whether AntennaIDs can be kept at 1,3, and 5 or need to be automated for whatever AntennaIDs are in use- discuss with Karen
#TODO adjust space between labels/axes, margin space, graph distance, etc for better-looking graphs




import numpy as np
import pandas as pd
import os
from os import path #imported to test if file exists
from datetime import datetime
from datetime import timedelta
import matplotlib.pyplot as plt
import matplotlib.axes as axs
import seaborn as sns
import xlrd
import sys


class FishAggregator: #create class
    def __init__(self, target_fishids, filenames, filepath_in, filepath_out, extra_filenames, target_start, target_end): #define class variables
        self.target_fishids = target_fishids
        self.filenames = filenames
        self.filepath_in = filepath_in
        self.filepath_out = filepath_out
        self.target_start, self.target_end = target_start, target_end
        self.extra_filenames = extra_filenames

    def build_dict_all(self): #this function reads in every new file, and compiles them into a dictionary of dataframes, so that they can
        #be used between fishids without re-loading in each time
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
        print('COMPILING SPREADSHEET FOR FISHID: ' + self.fishid + '...')
        for i in self.fishdict: #for each dataframe in the dictionary of dataframes (containing all fish, all date ranges)
            df = self.fishdict[i] #df is the dataframe at that index
            df.columns = df.columns.str.replace(" ","") #take spaces out of column names
            df_fishid = df[(df['HEXTagID'] == self.fishid)] #takes only the RFID readings for the fishid of choice
            fishlist = fishlist.append(df_fishid) #add dataframe to overall dataframe of all RFID readings for fishid
        for i in ('DownloadTime', 'DownloadDate', 'IsDuplicate'):
            if i in fishlist:
                fishlist = fishlist.drop(columns= i) #drops columns to allow duplicate RFID readings to be recognized
        print(fishlist.head(2))
        return(fishlist)



#NEW METHOD (split_by_month_and_save) SPLITS FISHID DATAFRAMES BY MONTH FOR SAVING, SAVES IN SEPARATE FOLDERS



    def split_by_month_and_save(self, fishid_df, fishid):
        fishid_df['ScanDateConverted'] = pd.to_datetime(fishid_df.ScanDate, format = '%m/%d/%Y')
        fishid_df['ScanMonth'] = fishid_df.ScanDateConverted.dt.month
        fishid_df['ScanYear'] = fishid_df.ScanDateConverted.dt.year
        #fishid_df['YearMonth'] = (fishid_df['ScanYear']) + '.' + (fishid_df['ScanMonth'])
        print('FISHIDDFHEAD WITH MONTH AND YEAR')
        print(fishid_df.head(5))
        #fishid_df['YearMonth'] = str(str(fishid_df.ScanDateConverted.dt.year) + '.' + (str(fishid_df.ScanDateConverted.dt.month))) #creates column with YYYY.MM, zeropads months to two demicals so that they sort correctly
        years = fishid_df['ScanYear'].unique().tolist() #gets list of all yearmonths in sheet
        months = fishid_df['ScanMonth'].unique().tolist()
        folderpath = self.filepath_out + fishid #folder path for that fishid
        if not path.exists(folderpath):
            print('THERE IS NO EXISTING FOLDER FOR FISHID: ' + fishid + '. CREATING...')
            os.makedirs(folderpath)
        print('YEARS: ', years)
        print('MONTHS: ', months)
        #print('YEARMONTHS: ' + str(yearmonths))
        for y in years:
            for m in months:
                ym = str(m) + '.' + str(y)
                print('YEARMONTH: ', ym)
                fishid_yearmonth_df = fishid_df.loc[(fishid_df.ScanYear == y) & (fishid_df.ScanMonth == m)]
                if len(fishid_yearmonth_df.index) > 0:
                    output_df_pathname = folderpath + '/' + ym + '.xlsx'
                    print('OUTPUT_DF_PATHNAME: ' + output_df_pathname)
                    if not path.exists(output_df_pathname):
                        print('THERE IS NO SPREADSHEET FOR YEARMONTH: ' +  str(ym) + '. CREATING...')
                        fishid_yearmonth_df.to_excel(output_df_pathname, index= False)
                    else:
                        print('THERE IS ALREADY A SPREADSHEET FOR YEARMONTH: ' + str(ym) + ' . COMBINING OLD AND NEW SPREADSHEETS...')
                        older_fishid_yearmonth_df = pd.read_excel(output_df_pathname)
                        fishid_yearmonth_df_merged = older_fishid_yearmonth_df.append(fishid_yearmonth_df)
                        fishid_yearmonth_df_merged.to_excel(output_df_pathname, index= False)
            print('SPREADSHEETS (SPLIT BY MONTH) SAVED FOR FISHID: ' + fishid)

#TODO check_and_export is where I need to make the bulk of edits to create separate folders for each output fishid, 
#then separate year/month spreadsheets for each fishid

# *******************************

    def update_spreadsheets(self): #updates spreadsheets with new RFID readings for all fishids in list
        self.fishdict = self.build_dict_all() #gets aggregate dataframe of inputs for fishid by running fishname_cycler
        self.fishid_fishdict = {} #creates dataframe dictionary to hold dataframes of each fishid, so that they don't have to be re-read in for graphing
        for i in self.target_fishids: #for every fishid in the list...
            self.fishid = i #that fishid becomes self.fishid
            self.fishlist = self.fishid_from_dict() #compiles spreadsheet of all new reads for that fishid
            self.split_by_month_and_save(self.fishlist, i) #updates (or creates new) spreadsheet for that fishid
        print('SPREADSHEETS UPDATED FOR FISHIDS: ' + str(self.target_fishids))

    def convert_date(self, input_date): #function converts a string of text into a readable date format (requires mm.dd.yyyy input)
        input_date = str(input_date)
        output_date = datetime.strptime(input_date, '%m/%d/%Y') #converts input date (string) into a datetime function
        return(output_date)
    
    def aggregate_fishids_by_date(self): #combines RFID readings for fishids of your choice, between dates of your choice, into one dataframe- 
        #sets this dataframe as self.fishids_aggregated_by_date, callable in other methods
        self.fishid_fishdict = {} #create empty dictionary to hold spreadsheets for all target fishids
        for i in self.target_fishids: #for each target fishid...
            pathname = self.filepath_out + i + '_most_recent.xlsx' #combines name and filepath to test if there is already a sheet for the fishid
        #print('CHECKING FOR 
        # EXISTING FILENAMES: ' + pathname + '...')
            if path.exists(pathname): #if there is already a spreadsheet with that filename...
                previous_file = pd.read_excel(pathname) #read in that spreadsheet as a dataframe
                print('THERE IS ALREADY A SHEET FOR FISHID: ' + i)
                self.fishid_fishdict[i] = previous_file #insert the spreadsheet for that fishid into the dataframe dictionary
            else:
                print('THERE IS NO SHEET FOR FISHID: ' + i)
                self.fishlist[i] = pd.DataFrame() #insert empty dataframe as place in dictionary- TODO does this work when there are no reads?
        if len(self.extra_filenames) > 0:
            for j in self.extra_filenames: #for each extra file (if those are needed given the date range and fishids in question)...
                pathname = self.filepath_out + j + '.xlsx' #create pathname... (no need to add any words to the actual filename)
                if path.exists(pathname) == False: #the file should already exist if it is being specifically written in- if it does not...
                    print('ERROR: THE PATHNAME: ' + pathname + 'DOES NOT EXIST- RECHECK THAT FILENAME WAS ENTERED CORRECTLY') #recheck that filename and filepath exist
                else: #if the extra file exists (as it should if it has been entered/called for)...
                    print('READING IN EXTRA FILE: ' + j) 
                    previous_file = pd.read_excel(pathname) #read in the extra spreadsheet file
                    self.fishid_fishdict[j] = previous_file #add the extra spreadsheet file to the dictionary of spreadsheets for each of the selected fishids accross the daterange
                    #self.fishid_fishdict will then contain spreadsheets for every fishid (including extra, older files if needed based on date range)
        print('FISHID FISHDICTIONARY: ')
        print(self.fishid_fishdict)
        df_for_graphing = pd.DataFrame() #create empty dataframe to hold all fishids for the date range
        target_start, target_end = self.convert_date(self.target_start), self.convert_date(self.target_end) #convert start and end dates into datetime objects
        fishids_and_extra_files = self.target_fishids + self.extra_filenames #all initial fishids, and the extra files for fishids whose RFID read spreadsheets exceeded one million rows
        for i in fishids_and_extra_files: #for each target fishid/file...
            fishid_fishlist = self.fishid_fishdict[i] #pull out the dataframe in the dictionary of dataframes for that fishid
            print('CONVERTING AND CULLING TIMES FOR FISHID: ', i)
            culled_fishlist = fishid_fishlist[(fishid_fishlist['ScanDate'].apply(self.convert_date) >= target_start) & (fishid_fishlist['ScanDate'].apply(self.convert_date) <= target_end)]
            print('CULLED FISHLIST HEAD FOR FISHID: ' + str(i) + ': ')
            print(culled_fishlist.head(10))
            #^for that fishid dataframe, pulls out only the RFID readings for the daterange between target_start and target_end
            df_for_graphing = df_for_graphing.append(culled_fishlist) #add it to the dataframe of all fishids for that date range
        df_for_graphing = df_for_graphing.sort_values(by=['ScanDate', 'ScanTime'])
        self.fishids_aggregated_by_date = df_for_graphing #self.fishids_aggregated_by_date can now be used in different methods within the class
        print('AGGREGATED: HEAD: ')
        print(df_for_graphing.head(10))
        print('AGGREGATED: TAIL: ')
        print(df_for_graphing.tail(10))
        print('GENERATED COMBINED DATAFRAME FOR FISHIDS:' + str(self.target_fishids) + ' BETWEEN DATES: ' + self.target_start + ' - ' + self.target_end) #prints that dataframe for fishids and dates has been created

    def convert_time(self, input_time): #converts a value from a string into a datetime (time) object
        output_time = datetime.strptime(input_time, '%H:%M:%S.%f')
        return(output_time)

    def select_hours(self, input_sheet, start_time, end_time): #culls a sheet to only a certain range of hours
        input_sheet['TimeConverted'] = input_sheet['ScanTime'].apply(self.convert_time) #make a new column of datetime time objects for scantime
        input_sheet = input_sheet[(input_sheet['TimeConverted'] <= self.convert_time(end_time)) & (input_sheet['TimeConverted'] >= self.convert_time(start_time))] #cull spreadsheet to just readings between target times
        return(input_sheet)

    def generate_raster(self): #given a set list of target fishids readings between a start date and end date,
        #this function generates a figure containing one raster plot for each AntennaID, with all target fish, between those dates
        #this function culls so that only times between 08:00 and 20:00 are shown
        #instructions for including AntennaID5 are commented out
        df = self.fishids_aggregated_by_date #load dataframe of all fishids for the chosen date range
        df = self.convert_to_datetime(df) #add column of datetime objects for ScanDateTime
        df = self.select_hours(df, '08:00:00.00', '20:00:00.00') #culls dataframe to just readings between 08:00 and 20:00 (does not include 20:00)
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
        plotname = str(self.target_fishids) + '_' + str(self.target_start).replace('/','.') + '-' + str(self.target_end).replace('/','.') + '_raster.png'
        pathname = '/Users/johnmerlo-coyne/Desktop/Juntti Lab Stuff/RFID Project/Figures/' + plotname
        plt.savefig(pathname)
        plt.show() #display plots- TODO save plots as image file
        
    def convert_to_datetime(self, df): #for a given spreadsheet, combines ScanDate and ScanTime columns into a ScanDateTime column, and makes the rows datetime objects
        df['DateTimeRaw'] = df['ScanDate'] + ' ' + df['ScanTime'] #combine scandate and scantime as strings
        df['ScanDateTime'] = pd.to_datetime(df.DateTimeRaw, format = '%m/%d/%Y %H:%M:%S.%f') #convert datetimeraw column into a datetime object that can be used
        return(df)

    def create_bargraph(self): #from a dataframe of RFID readings for a group of target fishids between a target daterange, produces a bargraph of RFID counts binned by hour
        print('CREATING BARGRAPH FOR FISHIDS: ' + str(self.target_fishids) + ' FOR TARGET DATES: ' + target_start + ' - ' + target_end + '...')
        df = self.fishids_aggregated_by_date #reads in the aggregated df of target fishids in the target daterange
        df = self.convert_to_datetime(df) #creates a column of datetime objects for the RFID reading (df['ScanDateTime'])
        df['ScanDateTimeShort'] = df['ScanDateTime'].values.astype('datetime64[h]') #cuts the datetime column to just month, day and hour
        start_date, raw_end_date = self.convert_date(self.target_start), self.convert_date(self.target_end)
        end_date = raw_end_date + timedelta(days=1)
        possible = pd.date_range(start_date, end_date, freq='h') #creates list of all datetimes between start dayhour and end dayhour
        possible = possible[:-1] #removes the first hour of end date (output will not include any hour in end date)
        possible_culled = [] #create empty list to hold possible all hours (including those with 0 entries) that will be in bar graph
        for i in possible: #adds hours between 08:00 and 20:00 to a new series, then makes that series into 'possible'
            if ((i.hour <= 19) and (i.hour >= 8)): #if the hour is between 08:00 and 20:00...
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
        #ax.set_xticklabels(labels= df_tograph.possible_culled, rotation=55, ha='right')
        plt.title('RFID readings for fishids: ' + str(self.target_fishids) + ' between dates: ' + self.target_start + ' - ' + self.target_end) #creates title for figure, noting fishid and dates
        plt.xlabel('Date and Time (H)')
        plt.ylabel('RFID Readings')
        plt.tight_layout()
        plt.subplots_adjust(left= 0.05)
        plotname = str(self.target_fishids) + '_' + str(self.target_start).replace('/','.') + '-' + str(self.target_end).replace('/','.') + '_bar.png'
        pathname = '/Users/johnmerlo-coyne/Desktop/Juntti Lab Stuff/RFID Project/Figures/' + plotname 
        plt.savefig(pathname)
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
all_fishids = ['3D6.1D59B07986', '3D6.1D59B07981', '3D6.1D59B0796C','3D6.1D59B0793D','3D6.1D599FDD2C', '3D6.1D59B07978',
                '3D6.1D599FDD53','3D6.1D599FDD2A','3D6.1D599FDD3F','3D6.1D599FDD07','3D6.1D599FDD27','3D6.1D599FDD31'] 
                #^this list doesn't get used in the script- just contains all the fishids for easy copying and pasting
all_tagmanager_files = ['09-25-2020_tagmanager','10-02-2020_tagmanager', '10-08-2020_tagmanager', '10-23-2020_tagmanager', '11-06-2020_tagmanager',
                        '12-4-2020_3', '12-18-2020_tagmanager', '01-25-2021_tagmanager', '02082021_tagmanager_ALL', '02-11-2021_tagmanager_all'] 
                        #^this list includes the file names of all tagmanager files to date- only use whole thing when creating all new fishids from scratch
filepath_in = '/Users/johnmerlo-coyne/Desktop/Juntti Lab Stuff/RFID Project/tagmanager/' 
                #^shared filepath of files to be read in (assumes they are in same folder) (updating spreadsheets)
filepath_out = '/Users/johnmerlo-coyne/Desktop/Juntti Lab Stuff/RFID Project/Split FishIDs/' 
                #^filepath of destination for aggregate sheet (updating spreadsheets) (plotting)
tagmanager_files_for_update = ['12-18-2020_tagmanager', '10-02-2020_tagmanager']
    # list of tagmanager filenames to be used for updating spreadsheets
    # must be a list, even when only updating with one file

target_start, target_end = '10/11/2020', '10/18/2020' #DATE FORMAT: 'mm.dd.yyyy' for graphing, etc- what dates should the program act on (plotting)
input_target_fishids = ['3D6.1D59B07978'] #list of fishids to be targeted (plotting)
#DON'T FORGET TO INPUT ANY EXTRA (NOT 'MOST RECENT') FILES FOR ANY NEEDED FISHIDS
input_extra_filenames = [] #list of any fishid filenames that are not 'most recent'- if there is a fishid spreadsheet that was cut off at 1 million rows and renamed,
                            #and that fishid is one of the targets, include it here- do not include '.xlsx'

fishobject = FishAggregator(input_target_fishids, tagmanager_files_for_update, filepath_in, filepath_out, input_extra_filenames, target_start, target_end)  #sets variables for class

def spreadsheet_update(): #updates RFID spreadsheets for all fishids
    #^be sure to set filenames, filepath_in and filepath_out to what you need them to be 
    fishobject.target_fishids = ['3D6.1D59B07986', '3D6.1D59B07981', '3D6.1D59B0796C','3D6.1D59B0793D','3D6.1D599FDD2C', '3D6.1D59B07978'] #sets target fishids to all fishids
    fishobject.update_spreadsheets() #updates spreadsheets
    print('SPREADSHEETS UPDATED FOR ' + str(fishobject.target_fishids) + ' USING TAGMANAGER SHEETS ' + str(fishobject.filenames))

def aggregate_raster(): #creates raster plots for fishids and date ranges of choice (set target_fishids, target_start, and target_end)
    try:
        fishobject.fishids_aggregated_by_date
    except AttributeError:
        fishobject.target_fishids = input_target_fishids
        fishobject.aggregate_fishids_by_date()
    else:
        print('AGGREGATED FISHID SHEET HAS ALREADY BEEN CREATED')
    fishobject.generate_raster() #generates raster plot from dataframe
    print('RASTER PLOTS CREATED FOR ' + str(fishobject.target_fishids) + ' IN DATE RANGE: ' + fishobject.target_start + ' - ' + fishobject.target_end)

def aggregate_barplot():
    try:
        fishobject.fishids_aggregated_by_date
    except AttributeError:
        fishobject.target_fishids = input_target_fishids
        fishobject.aggregate_fishids_by_date()
    else:
        print('AGGREGATED FISHID SHEET HAS ALREADY BEEN CREATED')
    fishobject.barwidth = 1
    fishobject.create_bargraph()
    print('BARPLOT CREATED FOR ' + str(fishobject.target_fishids) + ' IN DATE RANGE: ' + fishobject.target_start + ' - ' + fishobject.target_end)

def aggregate_export():
    fishobject.target_fishids = input_target_fishids
    fishobject.aggregate_fishids_by_date()
    if len(fishobject.fishids_aggregated_by_date.index) == 0:
        print('AGGREGATED SPREADSHEET IS EMPTY- CHECK THAT TARGET DATES AND FISHIDS ARE CORRECT')
        sys.exit()
    else:
        export_filepath = '/Users/johnmerlo-coyne/Desktop/Juntti Lab Stuff/RFID Project/Aggregated FishIDs/'
        export_filename = ('Aggregated RFID_' + str(input_target_fishids) + ' ' + fishobject.target_start.replace('/','.') + '-' + fishobject.target_end.replace('/','.') + '.xlsx')
        export_pathname = export_filepath + export_filename
        fishobject.fishids_aggregated_by_date.to_excel(export_pathname)
        print('AGGREGATE SPREADSHEET FOR: ' + str(input_target_fishids) + ' BETWEEN ' + target_start + ' - ' + target_end + 'SAVED')

spreadsheet_update()
#aggregate_barplot()
#aggregate_raster()
#aggregate_export()

