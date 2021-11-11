from datetime import datetime
import pandas as pd
import numpy as np
from datetime import timedelta
import timeit
import matplotlib.pyplot as plt
import matplotlib.axes as axs
import matplotlib.colors as mcolors
import seaborn as sns
import xlrd
pd.options.mode.chained_assignment = None  # default='warn'

rfid_fp = 'C:/Users/karen/OneDrive/Documents/0_RESEARCH/RFID/BORIS/Bev projects/'
boris_fp = 'C:/Users/karen/OneDrive/Documents/0_RESEARCH/RFID/BORIS/Bev projects/'

boris_file_male_fem_circling = "BORIS_OutputTest_converttimes_FEMALE-MAL_CIRCLING_Bev_10-14_2021-05-02.xlsx"  #BORIS_OutputTest_WITHDIVIDEDTIMES_2021-02-09_male2.xlsx
rfid_file_male = "RFID_OutputTest_MALE_Bev_10-14_2021-05-02.xlsx" #RFID_MatchPot_2021-02-09_male.xlsx
rfid_file_female = "RFID_OutputTest_FEMALE_Bev_10-14_2021-05-02.xlsx" #RFID_MatchPot_2021-02-09_male.xlsx

bf = pd.read_excel(boris_fp + boris_file_male_fem_circling)
rfm = pd.read_excel(rfid_fp + rfid_file_male)
rff = pd.read_excel(rfid_fp + rfid_file_female)

bf.rename(columns={'Stop (s)': 'Stop', 'Start (s)': 'Start'}, inplace=True)

start_date = '2021-05-02'
end_date = '2021-05-02' #string of the year, month and date of the BORIS reading ('YYYY-MM-DD')
start_time = '10:00:00.00'
end_time = '14:00:00.00'
start = datetime.strptime((start_date + ' ' + start_time), '%Y-%m-%d %H:%M:%S.%f')
end = atetime.strptime((start_date + ' ' + start_time), '%Y-%m-%d %H:%M:%S.%f')

def minusplus(bf, minus, plus):
    start_minus = bf['Start'] - timedelta(seconds = minus)
    start_minus = start_minus.tolist()
    stop_plus = bf['Stop'] + timedelta(seconds = plus)
    stop_plus = stop_plus.tolist()
    start_stop = list(zip(start_minus, stop_plus))
    return(start_stop)

def circling(rff, sec_within):
    rff["within"] = ""
    pointer = 0
    for i in range(len(rff['ScanDateTime'])):
        min = rff['ScanDateTime'][i] - timedelta(seconds = sec_within)
        max = rff['ScanDateTime'][i] + timedelta(seconds = sec_within)
        for p in range(pointer, len(rfm['ScanDateTime'])):
            if min <= rfm['ScanDateTime'][p] <= max:
                rff['within'][i] = 1
                pointer = p
                break
            elif rfm['ScanDateTime'][p] >= max:
                rff['within'][i] = 0
                pointer = p
                break
    return(rff)

def raster(rff, bf):
    rff['yval']=0.1
    rfm['yval']=0.101
    begin = datetime.strptime(('2021-05-02 ' + '10:00:00.00'), '%Y-%m-%d %H:%M:%S.%f')
    end = datetime.strptime(('2021-05-02 ' + '14:00:00.00'), '%Y-%m-%d %H:%M:%S.%f')
    fig, ax = plt.subplots()
    plt.scatter(rff.ScanDateTime, rff.yval, c=rff.within, marker='|', s=200, cmap = mcolors.ListedColormap(["orange", "blue"]))
    plt.scatter(rfm.ScanDateTime, rfm.yval, marker='|', s=200, cmap = mcolors.ListedColormap(["green"]))
    for x_1 , x_2 in zip(bf['Start'] ,bf['Stop']):
        ax.add_patch(plt.Rectangle((x_1,0.102),x_2-x_1,0.005))
    ax.set_xlim([begin, end])
    ax.set_ylim([0.095, 0.110])
    plt.show()

def raster_rfid(rff):
    rff['yval']=0.1
    rfm['yval']=0.101
    begin = datetime.strptime(('2021-05-02 ' + '10:00:00.00'), '%Y-%m-%d %H:%M:%S.%f')
    end = datetime.strptime(('2021-05-02 ' + '14:00:00.00'), '%Y-%m-%d %H:%M:%S.%f')
    fig, ax = plt.subplots()
    plt.scatter(rff.ScanDateTime, rff.yval, c=rff.within, marker='|', s=200, cmap = mcolors.ListedColormap(["orange", "blue"]))
    plt.scatter(rfm.ScanDateTime, rfm.yval, marker='|', s=200, cmap = mcolors.ListedColormap(["green"]))
    for x_1 , x_2 in zip(bf['Start'] ,bf['Stop']):
        ax.add_patch(plt.Rectangle((x_1,0.102),x_2-x_1,0.005))
    ax.set_xlim([begin, end])
    ax.set_ylim([0.095, 0.110])
    plt.show()

def enter_and_trim_rfid_df(rfid_df, rtarget, start_dt, end_dt):
    print("ENTER and TRIM RFID")
    #rfid_df = pd.read_excel(rpathname) #read in RFID spreadsheet as dataframe
    rfid_df.columns = rfid_df.columns.str.replace(" ","") #remove spaces from column names
    rfid_df = rfid_df[rfid_df.HEXTagID == rtarget]
    unwanted_columns = ['DownloadTime', 'DownloadDate']
    for col_name in unwanted_columns:
        try:
            print(col_name)
            rfid_df.drop(columns = col_name)
        except:
            pass
            print("no column " + col_name)

    rfid_df = rfid_df[rfid_df.AntennaID != 5] #remove all rows with antenna5
    rfid_df = rfid_df.drop_duplicates() #drop any duplicate values
    rfid_df = rfid_df.sort_values(by=['ScanDate', 'ScanTime'])
    rfid_df = convert_to_datetime(rfid_df)

    rfid_df = rfid_df[ rfid_df.ScanDateTime >= start_dt]
    rfid_df = rfid_df[ rfid_df.ScanDateTime <= end_dt]
    #rfid_df.to_excel(output_filepath + 'RFID_OutputTest_FEMALE_Bev_10-14_'+ date +'.xlsx')
    return(rfid_df)

"""
rff_circ = circling(rff, 2)
raster(rff_circ, bf)
"""
"""
    for i in range(len(rf['ScanDateTime'])):
        if any(lower <= rf['ScanDateTime'][i] <= upper for (lower, upper) in start_stop_1):
            rf['within'][i] = 1
            print(str(i), ' True')
        else:
            rf['within'][i] = 0
            print(str(i), ' False')
"""
