#PROBLEMS
    #takes about 12 minutes to verify one BORIS sheet
    #large inaccuracies in matching times- average of 80 seconds off between BORIS and 'closest' RFID reading times- TODO verify that 'closest' RFID times are actually closest
    #sometimes IDs 'Fish 2' as 3D6.1D59B0793D, which is the Tyr- fish, and would be flagged as 'Fish 1' in BORIS- probably linked to disparity in matching times
    #TODO- find source of time mismatch between BORIS events and 'closest' RFID events- issue with code?

#DESCRIPTION
#this function creates a BORIS spreadsheet that assigns a most likely fishid to each 'Fish 2' pot entry event, by referencing the RFID sheet readings for the same time
    #from a BORIS sheet of a certain date
    #and from an RFID entry sheet with a date range including that date
    #find the likely fishids for each 'Fish 2' pot entry event (a fishid with RFID entry readings that correspond to the BORIS reading)

#IMPORT LIBRARIES
from datetime import datetime
import pandas as pd
import numpy as np
from datetime import timedelta
import timeit

def enter_and_trim_rfid_df(RFID_filepath, RFID_filename): #enter, compress column names, sort and remove duplicates from RFID spreadsheet
    rfid_pathname = RFID_filepath + RFID_filename + '.xlsx' #combine file path and file name for RFID spreadsheet
    rfid_df = pd.read_excel(rfid_pathname) #read in RFID spreadsheet as dataframe
    rfid_df.columns = rfid_df.columns.str.replace(" ","") #remove spaces from column names
    rfid_df = rfid_df.drop(columns = ['DownloadTime', 'DownloadDate']) #drop columns so that sheet can drop duplicates
    rfid_df = rfid_df.drop_duplicates() #drop any duplicate values
    rfid_df = rfid_df.sort_values(by=['ScanDate', 'ScanTime']) #sort sheet by scandate and then scantime
    rfid_df = convert_to_datetime(rfid_df) #creates a ScanDateTime (datetime object) column via a separate function
    rfid_df.to_excel(output_filepath + 'RFID OUTPUT TEST 0925.xlsx')
    return(rfid_df)

def enter_boris_df_get_times(boris_filepath, boris_filename, boris_video_length, boris_date): #function of all the commands to read in boris spreadsheet and get video start time
    boris_pathname = boris_filepath + boris_filename + '.xlsx' #assemble file path and name for boris input sheet
    boris_df = pd.read_excel(boris_pathname) #read in boris output spreadsheet as a dataframe
    boris_datetime = boris_date + ' 20:00:00.00' #create string of video date and end time (20:00 unless otherwise specified)
    video_end = datetime.strptime(boris_datetime, '%Y-%m-%d %H:%M:%S.%f') #convert the end time of the video (20:00:00.0 on chosen date) to a datetime object
    h,m,s = boris_video_length.split(':') #splits video length string into h,m,s for conversion in following line
    boris_video_length = (int(timedelta(hours=int(h),minutes=int(m),seconds=int(s)).total_seconds())) #converts video length str to int of seconds
    boris_video_start_time = video_end - timedelta(seconds= boris_video_length) #finds time of video start
    return(boris_video_start_time, boris_df) #return start time and dataframe

def match_boris_fishid(rfid_df, boris_df, boris_video_start_time, boris_start, boris_end): #finds middle of start and end times, and closes RFID reading to that time
    boris_middle = round(((boris_start + boris_end)/2), 2) #finds 'middle' time between start-pot entry and end-pot entry. Rounds to 2 decimal places
    event_time = boris_video_start_time + timedelta(seconds= boris_middle) #calculate actual event time by adding number of seconds of event time to actual time of video start
    print('EVENT TIME: ', str(event_time))
    closest_index, closest_datetime = get_index_of_nearest_time(rfid_df, event_time) #apply function to find index of closest reading to event_time
    result_fishid = rfid_df['HEXTagID'].iloc[closest_index] #use index to find the fishid at that index/datetime- this is the likely identity of the fish that created the BORIS readings
    print('RESULT FISHID: ', result_fishid)
    time_offset = abs((event_time - closest_datetime).total_seconds()) #find abs() of difference between BORIS event_time and closest available RFID reading
    return(result_fishid, event_time, closest_datetime, time_offset) #return the four values

def convert_to_datetime(df): #for a given spreadsheet, combines ScanDate and ScanTime columns into a ScanDateTime column, and makes the rows datetime objects
    df['DateTimeRaw'] = df['ScanDate'] + ' ' + df['ScanTime'] #combine scandate and scantime as strings
    df['ScanDateTime'] = pd.to_datetime(df.DateTimeRaw, format = '%m/%d/%Y %H:%M:%S.%f') #convert datetimeraw column into a datetime object that can be used
    return(df)

def nearest(items, pivot): #from stackoverflow- finds closest time to a given input time (pivot) in a list of datetimes (items)
    return min(items, key=lambda x: abs(x - pivot))

def get_index_of_nearest_time(df, event_time): #find index of closest time to event_time in the RFID dataframe (df)
    print('FINDING INDEX OF CLOSEST TIME TO event_time...')
    datetime_list = df['ScanDateTime'].tolist() #convert RFID datetime columns to a list
    closest_datetime = nearest(datetime_list, event_time) #apply nearest() function (find closest time to event_time)
    print('CLOSEST DATETIME: ', str(closest_datetime))
    closest_index = datetime_list.index(closest_datetime) #find index of closest time to event_time
    return(closest_index, closest_datetime)

#COMMAND LINES CALLING MAIN FUNCTIONS
def BORIS_RFID_crosscheck_inner(boris_filename, boris_filepath, boris_date, boris_video_length, RFID_filepath, RFID_filename, output_filepath):
    rfid_df = enter_and_trim_rfid_df(RFID_filepath, RFID_filename) #enter, compress column names, sort and remove duplicates from RFID spreadsheet
    boris_video_start_time, boris_df = enter_boris_df_get_times(boris_filepath, boris_filename, boris_video_length, boris_date) #get start time and dataframe for boris readings
    print('BORIS VIDEO START TIME: ', boris_video_start_time)
    indexNames = boris_df[boris_df['Subject'] == 'Fish 1'].index #finds all indices of rows with 'Fish 1' (to drop)
    boris_df.drop(indexNames , inplace=True) #drops all rows with 'Fish 1' as subject
    #PERFORMING OPERATION FOR EACH FISH 2
    print(boris_df)
    print('BORIS INDEX: ', boris_df.index)
    for i in boris_df.index:
        print('ITERATING THROUGH INDEX ROW: ', i)
        boris_df.at[i, 'HEXTagID'], boris_df.at[i, 'EventTime'], boris_df.at[i, 'ClosestDatetime'], boris_df.at[i, 'TimeOffset(s)']  = match_boris_fishid(rfid_df, boris_df, boris_video_start_time, boris_df.at[i, 'Start (s)'], boris_df.at[i, 'Stop (s)']) #for every row in the boris sheet
    #OUTPUT EDITED BORIS SHEET
    print(boris_df.head(10))
    output_filename = ('BORIS: ' + boris_filename + ' checked against RFID: ' + RFID_filename) 
    output_pathname = (output_filepath + output_filename + '.xlsx')
    boris_df.to_excel(output_pathname)

#INPUTS
boris_filename = '9.14.20_aggregated' #file name of the boris spreadsheet to be read in
boris_filepath = '/Users/johnmerlo-coyne/Desktop/Juntti Lab Stuff/RFID Project/BORIS Output Sheets/9.14.2020/' #filepath of the boris spreadsheet to be read in
boris_date = '2020-09-14' #string of the year, month and date of the BORIS reading ('YYYY-MM-DD')
boris_video_length = '11:55:00' #string of the video length ('HH:MM:SS')- can be found by looking at video length in lab drive
RFID_filepath = '/Users/johnmerlo-coyne/Desktop/Juntti Lab Stuff/RFID Project/tagmanager/' #enter common filepath for RFID tagmanager files (for convenience)
RFID_filename = '09-25-2020_tagmanager' #enter filename and filepath (and .xlsx) of RFID spreadsheet with a daterange containing the date in question
output_filepath = '/Users/johnmerlo-coyne/Desktop/Juntti Lab Stuff/RFID Project/BORIS-RFID Fishid Verification/' #this can stay the same between uses- filepath for where you want the file to go

def BORIS_RFID_crosscheck():
    BORIS_RFID_crosscheck_inner(boris_filename, boris_filepath, boris_date, boris_video_length, RFID_filepath, RFID_filename, output_filepath)

#BORIS_RFID_crosscheck()
print('START TIME:', datetime.now())
BORIS_RFID_crosscheck()
print('BORIS_RFID_crosscheck done!')
print('END TIME:', datetime.now())
print('DONE')



