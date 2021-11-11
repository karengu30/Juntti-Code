
#IMPORT LIBRARIES
from datetime import datetime
import pandas as pd
import numpy as np
from datetime import timedelta
import timeit
import matplotlib.pyplot as plt
import matplotlib.axes as axs
import seaborn as sns
import xlrd

class CrossCheck:
    def __init__(self, boris_filename, boris_filepath, RFID_filename, RFID_filepath, output_filepath, date, start_time, end_time, RFIDtarget, BORIStarget):
        self.bfilename = boris_filename
        self.bfilepath = boris_filepath
        self.rfilename = RFID_filename
        self.rfilepath = RFID_filepath
        self.output_filepath = output_filepath
        self.date = date # '2021-02-09'
        self.start_time = start_time # "10:00:00.00"
        self.end_time = end_time   # "12:00:00.00"
        self.rtarget = RFIDtarget # HEX Tag of fish
        self.btarget = BORIStarget # BORIS subject "Male 1" "Females"

        ## easier
        self.rpathname = RFID_filepath + RFID_filename + '.xlsx'
        self.bpathname = boris_filepath + boris_filename + '.xlsx'
        self.start_dt = datetime.strptime((self.date + ' ' + self.start_time), '%Y-%m-%d %H:%M:%S.%f') #creates datetime object to cull RFID readings before that datetime
        self.end_dt = datetime.strptime((self.date + ' ' + self.end_time), '%Y-%m-%d %H:%M:%S.%f')

    def enter_and_trim_rfid_df(self):
        print("ENTER and TRIM RFID")
        self.rfid_df = pd.read_excel(self.rpathname) #read in RFID spreadsheet as dataframe
        self.rfid_df.columns = self.rfid_df.columns.str.replace(" ","") #remove spaces from column names
        self.rfid_df = self.rfid_df[self.rfid_df.HEXTagID == self.rtarget]
        unwanted_columns = ['DownloadTime', 'DownloadDate']
        for col_name in unwanted_columns:
            try:
                print(col_name)
                self.rfid_df.drop(columns = col_name)
            except:
                pass
                print("no column " + col_name)

        self.rfid_df = self.rfid_df[self.rfid_df.AntennaID != 5] #remove all rows with antenna5
        self.rfid_df = self.rfid_df.drop_duplicates() #drop any duplicate values
        self.rfid_df = self.rfid_df.sort_values(by=['ScanDate', 'ScanTime'])
        self.rfid_df = self.convert_to_datetime(self.rfid_df)

        self.rfid_df = self.rfid_df[self.rfid_df.ScanDateTime >= self.start_dt]
        self.rfid_df = self.rfid_df[self.rfid_df.ScanDateTime <= self.end_dt]

        self.rfid_df.to_excel(output_filepath + 'RFID_OutputTest_FEMALE_AQ_08-14_'+ date +'.xlsx')
        return(self.rfid_df)

    def enter_and_trim_boris_df(self, keep_behaviors): # EVENTUALLY USE KEEP BEHAVIORS TO EXCLUDE UNWANTED BEHAVIORS
        print('LOADING BORIS SHEET AND ESTIMATING EVENT TIMES')
        self.boris_df = pd.read_excel(self.bpathname)
        self.boris_df = self.boris_df.loc[self.boris_df['Behavior'].isin(keep_behaviors)]
        self.boris_df = self.boris_df[self.boris_df.Subject == self.btarget]
        #self.boris_df.to_excel(output_filepath + 'BORIS_OutputTest_WITHDIVIDEDTIMES_'+ date +'.xlsx')
        return(self.boris_df)

    def boris_convert_times(self, boris_first_acutaltime):
        print("CONVERTING BORIS TIMES")
        self.boris_first_entry = self.boris_df['Start (s)'].iloc[0]  #returns first entry event (first row in 'Start (s)' for Fish 2)
        self.boris_first_actualtime = boris_first_acutaltime
        self.boris_df['Start (s)'] = self.boris_df['Start (s)'] - self.boris_first_entry #subtracts the initial (s) count of the first entry from every pot entry event
        self.boris_df['Stop (s)'] = self.boris_df['Stop (s)'] - self.boris_first_entry #subtracts the initial (s) count of the first entry from every pot exit event
        #self.rfid_first_entry = self.rfid_df.ScanDateTime.iloc[0] #get datetime value of first RFID pot event
        self.boris_df['Start (s)'] = self.boris_first_actualtime + pd.to_timedelta(self.boris_df['Start (s)'], 's') #change BORIS entry column by adding timedelta of seconds to first RFID pot entry time
        self.boris_df['Stop (s)'] = self.boris_first_actualtime + pd.to_timedelta(self.boris_df['Stop (s)'], 's') #change BORIS exit column by adding timedelta of seconds to first RFID pot entry time
        self.boris_df.to_excel(output_filepath + 'BORIS_OutputTest_circling_converttimes_new'+ date +'.xlsx')
        return(self.boris_df)

    def boris_convert_times_new(self, video_beginning):
        print("NEW BORIS TIME CONVERSION")
        self.video_beginning = video_beginning
        self.boris_df['Start (s)'] = self.video_beginning + pd.to_timedelta(self.boris_df['Start (s)'], unit='s') #change BORIS entry column by adding timedelta of seconds to first RFID pot entry time
        self.boris_df['Stop (s)'] = self.video_beginning + pd.to_timedelta(self.boris_df['Stop (s)'], unit='s')
        self.boris_df.to_excel(output_filepath + 'BORIS_OutputTest_converttimes_FEMALE_AQ_08-14' + date +'.xlsx')
        return(self.boris_df)

    def match_pot_antennae(self, boris_df, rfid_df):
        print("Matching pot antenna")
        boris_first_pot = boris_df['Behavior'].iloc[0] #return 'Left Pot Entry' or 'Right Pot Entry' first pot entry event of day for Fish 2
        rfid_first_antenna = rfid_df['AntennaID'].iloc[0] #return AntennaID of first pot entry
        print('FISH POT ', str(boris_first_pot), ' CONTAINS ANTENNAID ', str(rfid_first_antenna))
        pot_names = (boris_df['Behavior'].unique()).tolist()
        if len(pot_names) > 2: #if there are more than two pot names/behaviors in the BORIS sheet...
            print('Behaviors: ', str(pot_names))
            raise ValueError('Wrong number of pot positions/behavior types') #raise an error
        antenna_ids = (rfid_df['AntennaID'].unique()).tolist() #creates a (hopefully) 2-item long list of the two AntennaIDs in the RFID sheet
        print('ANTENNA IDS: match_pot_antennae: ', str(antenna_ids))
        if len(antenna_ids) > 2: #if there are more than 2 AntennaIDs in the RFID sheet...
            print('AntennaIDs: ', str(antenna_ids))
            raise ValueError('Wrong number of AntennaIDs') #raise a value error- it will be impossible to match pots to antennae if this is the case
        else:
            pot_names.remove(boris_first_pot)
            boris_second_pot = pot_names[0]
            #print('BORIS SECOND POT: ', str(boris_second_pot))
            antenna_ids.remove(rfid_first_antenna)
            rfid_second_antenna = antenna_ids[0]
            print('FISH POT ', str(boris_second_pot), ' CONTAINS ', str(rfid_second_antenna))
            #TODO might need to create an empty 'PotSide' column before filling it in lines below
            rfid_df.loc[rfid_df.AntennaID == rfid_first_antenna, 'Behavior'] = boris_first_pot #for rfid_df rows where 'AntennaID' is the first antenna, add a column value of the first pot under 'Potside'
            rfid_df.loc[rfid_df.AntennaID == rfid_second_antenna, 'Behavior'] = boris_second_pot #for rfid_df rows where 'AntennaID' is the second antenna, add a column value of the second antenna under 'PotSide'
            #^the two lines above (based on assumption that first non-793D RFID reading after 07:50 matches first BORIS 'Fish 2' pot entry event),
            #add a column to rfid_df listing the inferred pot side based on the existing AntennaID in the RFID row
            return(rfid_df)

    #def convert_pot_antennae(self):


    def sort_by_behavior(self, df):
        print('SORTING SPREADSHEET BY LEFT/RIGHT POT BEHAVIOR...')
        left_pot_df = df[df.Behavior == 'Left pot occupied'] #left_pot_df only contains rows for which df.Behavior is the left pot (inferred for rfid_df)
        right_pot_df = df[df.Behavior == 'Right pot occupied'] #right_pot_df only contains rows for which df.Behavior is the right pot (inferred for rfid_df)
        return(left_pot_df, right_pot_df) #return the new, split dataframes


    def convert_to_datetime(self, df):
        print('CREATING ScanDateTime COLUMN...')
        df['DateTimeRaw'] = df['ScanDate'] + ' ' + df['ScanTime'] #combine scandate and scantime as strings
        df['ScanDateTime'] = pd.to_datetime(df.DateTimeRaw, format = '%m/%d/%Y %H:%M:%S.%f') #convert datetimeraw column into a datetime object that can be used
        return(df)

    def generate_raster(self, raster_start, raster_end, rfid_trimmed_matched): #given a set list of target fishids readings between a start date and end date,
        #this function generates a figure containing one raster plot for each AntennaID, with all target fish, between those dates
        #this function culls so that only times between 08:00 and 20:00 are shown
        #instructions for including AntennaID5 are commented out
        self.raster_start = raster_start
        self.raster_end = raster_end
        #df = self.fishids_aggregated_by_date #load dataframe of all fishids for the chosen date range
        #df = self.convert_to_datetime(df) #add column of datetime objects for ScanDateTime
        #df = self.select_hours(df, self.raster_start, self.raster_end) #culls dataframe to just readings between 08:00 and 20:00 (does not include 20:00)
        #df.to_excel(self.filepath_out + 'justchecking.xlsx')
        #df_antennaid_1 = df[df.AntennaID == 1] #sort all RFId reads from AntennaID1 into one dataframe
        #df_antennaid_3 = df[df.AntennaID == 3] #sort all RFId reads from AntennaID3 into one dataframe
        #df_antennaid_5 = df[df.AntennaID == 5]
        rfid_left_pot_df, rfid_right_pot_df = self.sort_by_behavior(rfid_trimmed_matched)

        print('SHEETS SORTED BY ANTENNA ID- RFID READS FOR LEFT POT: ' + str(len(rfid_left_pot_df.index)) + ' RFID READS FOR RIGHT POT: ' + str(len(rfid_right_pot_df.index)))
        #fig, (ax1, ax2, ax3) = plt.subplots(3)
        fig, (ax1, ax2) = plt.subplots(2, figsize=(18,7)) #makes 2 stacked subplots in one image, image size is 18x8 inches
        fig.suptitle('Raster for fishids: ' + str(self.rtarget) + ' Date: ' + self.date + ' Time: ' + self.start_time + ' - '+self.end_time) #creates title for figure, noting fishid and dates
        sns.scatterplot(x= rfid_left_pot_df.ScanDateTime, y= rfid_left_pot_df.HEXTagID, data= rfid_left_pot_df, marker = '|', hue = rfid_left_pot_df.HEXTagID, s = 100, ax= ax1) #creates raster plot for AntennaID1
        sns.scatterplot(x= rfid_right_pot_df.ScanDateTime, y= rfid_right_pot_df.HEXTagID, data= rfid_right_pot_df, marker = '|', hue = rfid_right_pot_df.HEXTagID, s = 100, ax= ax2) #creates raster plot for AntennaID3
        ax1.title.set_text('RFID Left Pot') #subtitle
        ax2.title.set_text('RFID Right Pot') #subtitle
        #sns.scatterplot(x= df_antennaid_5.ScanDateTime, y= df_antennaid_5.HEXTagID, data= df_antennaid_5, marker = '|', hue = df_antennaid_5.HEXTagID, s = 100, ax= ax3)
        plt.subplots_adjust(bottom=0.2, hspace=0.5) #creates space at bottom of figure and between plots
        plt.show() #display plots- TODO save plots as image file


keep_subjects = []
#keep_behaviors = ['Left pot occupied', 'Right pot occupied']
keep_behaviors = ['Pot occupied']

boris_filename = 'BORIS_20210919_1230-1430_AggregatedEvents_AQ' #file name of the boris spreadsheet to be read in
boris_filepath = 'C:/Users/karen/OneDrive/Documents/0_RESEARCH/RFID/BORIS/AQ projects/2021-09-19 AQ/' #filepath of the boris spreadsheet to be read in
#boris_video_length = '11:55:00' #string of the video length ('HH:MM:SS')- can be found by looking at video length in lab drive
RFID_filepath = 'C:/Users/karen/OneDrive/Documents/0_RESEARCH/RFID/' #enter common filepath for RFID tagmanager files (for convenience)
RFID_filename = '09-20-2021_tagmanager_all' #enter filename and filepath (and .xlsx) of RFID spreadsheet with a daterange containing the date in question
output_filepath = 'C:/Users/karen/OneDrive/Documents/0_RESEARCH/RFID/BORIS/AQ projects/2021-09-19 AQ/' #this can stay the same between uses- filepath for where you want the file to go
date = '2021-09-19' #string of the year, month and date of the BORIS reading ('YYYY-MM-DD')
start_time = '12:30:25.00'
end_time = '14:30:00.00'
RFIDtarget = '3D6.1D59B07932' #3D6.1D599FDD07
BORIStarget = 'Male 1' #Females
#RFIDtarget = '3D6.1D59B07974'
#BORIStarget = 'Females'
video_beginning = datetime.strptime(('2021-09-19 ' + '12:30:25.00'), '%Y-%m-%d %H:%M:%S.%f')

cc = CrossCheck(boris_filename, boris_filepath, RFID_filename, RFID_filepath, output_filepath, date, start_time, end_time, RFIDtarget, BORIStarget)

"""
keep_behaviors = ['Pot occupied']   #['Circling'] ['Pot occupied']
x = cc.enter_and_trim_boris_df(keep_behaviors)
x = cc.boris_convert_times_new(video_beginning)
y = cc.enter_and_trim_rfid_df()
# go to colored_raster_07-21-2021.py
# use the outputted files to input into colored raster
# some issue with antennae id stuff

"""

#rfid_trimmed_matched_filepath = output_filepath + 'RFID_MatchPot_2021-02-09.xlsx'
#rfid_trimmed_matched = pd.read_excel(rfid_trimmed_matched_filepath)
#boris_converted_fp = output_filepath + 'BORIS_OutputTest_converttimes_2021-02-09.xlsx'
#boris_converted = pd.read_excel(boris_converted_fp)

#https://stackoverflow.com/questions/47727339/plot-start-end-time-slots-matplotlib-python
