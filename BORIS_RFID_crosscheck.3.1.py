#DESCRIPTION
#this function creates a BORIS spreadsheet that assigns a most likely fishid to each 'Fish 2' pot entry event, by referencing the RFID sheet readings for the same time 
    #from a BORIS sheet of a certain date
    #and from an RFID entry sheet with a date range including that date
    #find the likely fishids for each 'Fish 2' pot entry event (a fishid with RFID entry readings that correspond to the BORIS reading)
    #removes all dates outside of the day of the BORIS video, and removes the fishid of the Tyrosinase fish (Fish 1) from being considered as a match

#PROBLEMS
    #wildly innacurate- average of 4460 seconds off between BORIS and 'closest' RFID reading times- TODO verify that 'closest' RFID times are actually closest
    #TODO- find source of time mismatch between BORIS events and 'closest' RFID events
        #issue with code? initial RFID-BORIS video start matching wrong?

#IMPORT LIBRARIES
from datetime import datetime
import pandas as pd
import numpy as np
from datetime import timedelta
import timeit

def enter_and_trim_rfid_df(RFID_filepath, RFID_filename, boris_date): #enter, compress column names, sort and remove duplicates from RFID spreadsheet
    print('READING IN RFID SHEET, CULLING TYROSINASE POT ENTRIES, AND CULLING TO TARGET DATE AND TIME...')
    rfid_pathname = RFID_filepath + RFID_filename + '.xlsx' #combine file path and file name for RFID spreadsheet
    rfid_df = pd.read_excel(rfid_pathname) #read in RFID spreadsheet as dataframe
    rfid_df.columns = rfid_df.columns.str.replace(" ","") #remove spaces from column names
    rfid_df = rfid_df[rfid_df.HEXTagID != '3D6.1D59B0793D'] #remove all RFID readings for 793D (tyrosinase) fish- it cannot correspond to a legitimate Fish 2 entry, as it is Fish 1
    rfid_df = rfid_df.drop(columns = ['DownloadTime', 'DownloadDate']) #drop columns so that sheet can drop duplicates
    rfid_df = rfid_df.drop_duplicates() #drop any duplicate values
    rfid_df = rfid_df.sort_values(by=['ScanDate', 'ScanTime']) #sort sheet by scandate and then scantime
    rfid_df = convert_to_datetime(rfid_df) #creates a ScanDateTime (datetime object) column via a separate function
    #TODO remove all rfid_df readings outside of 08:00-20:00 on target day
    date_eight = datetime.strptime((boris_date + ' 07:50:00.00'), '%Y-%m-%d %H:%M:%S.%f') #creates datetime object of 07:50AM on day of video, used to cull RFID readings before that datetime
    #^07:50:00.00 creates 10 minutes of buffer time incase the BORIS start time was as early as 07:50:00- TODO IT IS UNLIKELY TO BE THIS OFFSET- DISCUSS WITH KAREN WHAT A GOOD CUTOFF START TIME
    #TODO #TODO #TODO
    date_twenty = datetime.strptime((boris_date + ' 20:00:00.00'), '%Y-%m-%d %H:%M:%S.%f') #creates datetime object of 8PM on day of video, used to cull RFID readings after that datetime
    rfid_df = rfid_df[rfid_df.ScanDateTime >= date_eight] #removes any RFID readings before 08:00 on the target day
    rfid_df = rfid_df[rfid_df.ScanDateTime <= date_twenty] #removes any RFID readings after 20:00 on the target day
    rfid_df.to_excel(output_filepath + 'RFID OUTPUT TEST 0925.xlsx')
    return(rfid_df)

def enter_boris_convert_times(boris_filepath, boris_filename, boris_date, rfid_df):
    print('LOADING BORIS SHEET AND ESTIMATING EVENT TIMES BASED ON FIRST READING OF CULLED RFID SHEET...')
    boris_pathname = boris_filepath + boris_filename + '.xlsx' #assemble file path and name for boris input sheet
    boris_df = pd.read_excel(boris_pathname) #read in BORIS spreadsheet using filepath and name
    boris_df = boris_df[boris_df.Subject != 'Fish 1'] #remove all Fish 1 rows from BORIS spreadsheet
    boris_df = boris_df[boris_df.Behavior != 'Circling'] #remove all rows where primary behavior is 'Circling'
    boris_first_entry = boris_df['Start (s)'].iloc[0] #returns first entry event (first row in 'Start (s)' for Fish 2)
    boris_df['Start (s)'] = boris_df['Start (s)'] - boris_first_entry #subtracts the initial (s) count of the first entry from every pot entry event
    boris_df['Stop (s)'] = boris_df['Stop (s)'] - boris_first_entry #subtracts the initial (s) count of the first entry from every pot exit event    
    rfid_first_entry = rfid_df.ScanDateTime.iloc[0] #get datetime value of first RFID pot event
    boris_df['Start (s)'] = rfid_first_entry + pd.to_timedelta(boris_df['Start (s)'], 's') #change BORIS entry column by adding timedelta of seconds to first RFID pot entry time
    boris_df['Stop (s)'] = rfid_first_entry + pd.to_timedelta(boris_df['Stop (s)'], 's') #change BORIS exit column by adding timedelta of seconds to first RFID pot entry time
    return(boris_df) #return the BORIS spreadsheet, now with corrected times

def match_pot_antennae(rfid_df, boris_df): #by matching the first non-tyrosinase RFID reading after the start time to the first 'Fish 2' BORIS entry for that day (BIG STRETCH), 
    print('MATCHING ANTENNAID TO POT POSITION USING ASSUMED FIRST ENTRY, AND ADDING POT POSITION TO RFID SHEET...')
    #^adds a column to rfid_df listing the pot side (same values as boris_df['Behavior']) based on each row's AntennaID- useful later for matching closest reads
    boris_first_pot = boris_df['Behavior'].iloc[0] #return 'Left Pot Entry' or 'Right Pot Entry' first pot entry event of day for Fish 2
    rfid_first_antenna = rfid_df['AntennaID'].iloc[0] #return AntennaID of first pot entry
    #^if entries were aligned correctly, boris_first_pot should be the pot containing rfid_first_antenna
    print('FISH POT ', str(boris_first_pot), ' CONTAINS ANTENNAID ', str(rfid_first_antenna))
    #preliminary step- later modify spreadsheet to either have both be in terms of pot or both in terms of antenna
# TODO add 'Pot' Column to rfid_df to for each antennaID
    pot_names = (boris_df['Behavior'].unique()).tolist() #creates a (hopefully) 2-item long list of the two 'Behaviors' (Left Pot Entry and Right Pot Entry)
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

def convert_to_datetime(df): #for a given spreadsheet, combines ScanDate and ScanTime columns into a ScanDateTime column, and makes the rows datetime objects
    print('CREATING ScanDateTime COLUMN...')
    df['DateTimeRaw'] = df['ScanDate'] + ' ' + df['ScanTime'] #combine scandate and scantime as strings
    df['ScanDateTime'] = pd.to_datetime(df.DateTimeRaw, format = '%m/%d/%Y %H:%M:%S.%f') #convert datetimeraw column into a datetime object that can be used
    return(df)

def find_nearest_time_and_fishid(event_time, rfid_df): #find index of closest RFID time to an individual BORIS-derived event_time
    #print('EVENT TIME IS DATETIME OBJECT: ', str(isinstance(event_time, datetime)))
    #print(event_time)
    #print('INNER LOOP: FIND_NEAREST_TIME_AND_FISHID...')
    #TODO subtract time from every cell in column
    #print('INNER LOOP: SUBTRACTING event_time FROM ALL rfid_df CELLS IN [ScanDateTime]...')
    rfid_df['ScanDateTimeSubtracted'] = (rfid_df['ScanDateTime'] - event_time).dt.seconds #subtracts event_time from all RFID reading times, converts to seconds, converts to numeric
    #print('RFID_DF[ScanDateTime]:')
    #print(rfid_df.head(5))
    #print('RFID_DF[ScanDateTimeSubtracted]:')
    #print(rfid_df['ScanDateTimeSubtracted'].head(5))
    #^VSCode is giving warning message with this method- change if it seems to be causing a problem.
    #print('INNER LOOP: TAKING ABSOLUTE VALUE AND FINDING INDEX OF MINIMUM VALUE AFTER SUBTRACTION...')
    result_index = rfid_df['ScanDateTimeSubtracted'].abs().idxmin()
    #result_index = rfid_df['ScanDateTime'].sub(event_time).total_seconds().abs().idxmin() #returns index of row in rfid_df that is closest to event_time- TODO very likely will haveo to adjust to the fact that mine are datetimes and not values
    #print('RESULT INDEX: ', str(result_index))
    #print('RESULT INDEX DISCREPANCY: ', str(rfid_df.loc[result_index, 'ScanDateTimeSubtracted']))
    #explanation on codereview: https://codereview.stackexchange.com/questions/204549/lookup-closest-value-in-pandas-dataframe
    nearest_datetime = rfid_df.loc[result_index, 'ScanDateTime'] #gives the ScanDateTime (nearest RFID reading datetime to the chosen BORIS entry time) based on previously found index of nearest RFID time
    #print('NEAREST DATETIME: ', str(nearest_datetime))
    result_fishid = rfid_df.loc[result_index, 'HEXTagID'] #gives the corresponding fishid for the nearest RFID ScanDateTime to the chosen BORIS entry time
    #print('RESULT FISHID: ', result_fishid)
    return(nearest_datetime, result_fishid) #return the closest datetime and the corresponding fishid


def sort_by_behavior(df): #sorts rfid_df or boris_df into two dataframes, one for each pot/AntennaID
    print('SORTING SPREADSHEET BY LEFT/RIGHT POT BEHAVIOR...')
    left_pot_df = df[df.Behavior == 'Left pot occupied'] #left_pot_df only contains rows for which df.Behavior is the left pot (inferred for rfid_df)
    right_pot_df = df[df.Behavior == 'Right pot occupied'] #right_pot_df only contains rows for which df.Behavior is the right pot (inferred for rfid_df)
    return(left_pot_df, right_pot_df) #return the new, split dataframes

def add_nearest_time_and_fishid(boris_side_df, rfid_side_df): #gets closest times in RFID sheet for each BORIS time (pot entry, not exit, not middle) #TODO DISCUSS WHAT PART OF THE ENTRY-EXIT STRETCH WE WANT TO TARGET!!!!!
    #print('FINDING NEAREST RFID READING AND CORRESPONDING FISHID FOR EACH BORIS POT ENTRY EVENT...')
    #print('BORIS SIDE DF INDEX: ', str(boris_side_df.index))
    for row_index in boris_side_df.index: #for each row in the BORIS sheet for one pot...
        #print('ROW INDEX: ', str(row_index))
        boris_event_time = boris_side_df.loc[row_index, 'Start (s)'] #set boris_event_time as the 'Start (s)'  time for that row
        #print('BORIS EVENT TIME OUTER: ')
        #print(boris_event_time)
        #if .iloc doesn't work, stackoverflow has alternate solution: https://stackoverflow.com/questions/28754603/indexing-pandas-data-frames-integer-rows-named-columns
        boris_side_df.loc[row_index, 'RFIDScanDateTime'], boris_side_df.loc[row_index, 'HEXTagID'] = find_nearest_time_and_fishid(boris_event_time, rfid_side_df)
        #^uses 'nearest_time_and_fishid()' function to return a closest RFID datetime and corresponding fishid for each BORIS start time
    return(boris_side_df) #returns the fully edited BORIS sheet for one pot, with added 'RFIDScanDateTime' and 'HEXTagID' columns

#COMMAND LINE CALLING MAIN FUNCTIONS
def boris_rfid_crosscheck_inner(boris_filename, boris_filepath, boris_date, RFID_filepath, RFID_filename, output_filepath):
    rfid_df = enter_and_trim_rfid_df(RFID_filepath, RFID_filename, boris_date) #returns RFID dataframe, 793D removed, culled to times between 07:50 and 20:00 on target date,
    #^removes duplicate readings and sorts by ScanDateTime
    boris_df = enter_boris_convert_times(boris_filepath, boris_filename, boris_date, rfid_df) #returns BORIS dataframe, Fish 1 removed, 'Circling' behavior removed, 
    #^and times converted from (s) to DateTime by assuming that first BORIS reading corresponds to first non-793D RFID read after 07:50 AM
    rfid_df = match_pot_antennae(rfid_df, boris_df) #modify rfid_df to contain column showing pot side (same values as boris_df['Behavior']) based on RFID AntennaID
    #print(rfid_df)
    rfid_left_pot_df, rfid_right_pot_df = sort_by_behavior(rfid_df) #sorts rfid_df into two sheets, one for each pot side/antennaid (under 'Behavior')
    boris_left_pot_df, boris_right_pot_df = sort_by_behavior(boris_df) #sorts boris_df into two sheets, one for each pot side (under 'Behavior')
    if len(boris_left_pot_df.index) >= 1: #if the BORIS sheet for the left pot has any entry events...
        #print('BORIS LEFT POT INDEX: ', str(len(boris_left_pot_df.index)))
        boris_left_pot_df = add_nearest_time_and_fishid(boris_left_pot_df, rfid_left_pot_df) #find the corresponding closest RFID reading and fishid from the (presumed) left pot RFID sheet
    if len(boris_right_pot_df.index) >= 1: #if the BORIS sheet for the right pot has any entry events...
        #print('BORIS RIGHT POT INDEX: ', str(len(boris_right_pot_df.index)))
        boris_right_pot_df = add_nearest_time_and_fishid(boris_right_pot_df, rfid_right_pot_df) #find the corresponding closest RFID reading and fishid from the (presumed) right pot RFID sheet
    #^edit BORIS sheet for each pot to include columns with closest RFID reading time and likely fishid of Fish 2
    boris_recombined = pd.concat([boris_left_pot_df, boris_right_pot_df], ignore_index= True) #combines separate pot dataframes back into one- TODO verify that pd.concat() is appropriate command here
    boris_recombined = boris_recombined.sort_values(by= 'Start (s)') #sort recombined BORIS sheet by the 'Start (s)' column (pot entry start)
    boris_recombined['Disparity (s)'] = abs((boris_recombined['Start (s)'] - boris_recombined['RFIDScanDateTime']).astype('timedelta64[s]')) #create column showing absolute difference (in seconds, absolute value), between each BORIS entry time and closest derived RFID time
    print('MEAN TIME BETWEEN BORIS POT ENTRY AND CLOSEST DETECTED RFID TIME: ', str(boris_recombined['Disparity (s)'].mean()), ' seconds')
    print('MAXIMUM TIME BETWEEN BORIS POT ENTRY AND CLOSEST DETECTED RFID TIME: ', str(boris_recombined['Disparity (s)'].max()), ' seconds')
    output_pathname = output_filepath + boris_filename + '_referencedagainst_' + RFID_filename + '.xlsx'
    boris_recombined.to_excel(output_pathname)
    print('DONE')

#INPUTS
boris_filename = '9.14.20_aggregated' #file name of the boris spreadsheet to be read in
boris_filepath = '/Users/johnmerlo-coyne/Desktop/Juntti Lab Stuff/RFID Project/BORIS Output Sheets/9.14.2020/' #filepath of the boris spreadsheet to be read in
boris_date = '2020-09-14' #string of the year, month and date of the BORIS reading ('YYYY-MM-DD')
boris_video_length = '11:55:00' #string of the video length ('HH:MM:SS')- can be found by looking at video length in lab drive
RFID_filepath = '/Users/johnmerlo-coyne/Desktop/Juntti Lab Stuff/RFID Project/tagmanager/' #enter common filepath for RFID tagmanager files (for convenience)
RFID_filename = '09-25-2020_tagmanager' #enter filename and filepath (and .xlsx) of RFID spreadsheet with a daterange containing the date in question
output_filepath = '/Users/johnmerlo-coyne/Desktop/Juntti Lab Stuff/RFID Project/BORIS-RFID Fishid Verification/' #this can stay the same between uses- filepath for where you want the file to go

def BORIS_RFID_crosscheck():
    boris_rfid_crosscheck_inner(boris_filename, boris_filepath, boris_date, RFID_filepath, RFID_filename, output_filepath)

#BORIS_RFID_crosscheck()
print('START TIME:', datetime.now())
BORIS_RFID_crosscheck()
print('BORIS_RFID_crosscheck done!')
print('END TIME:', datetime.now())
print('DONE')

