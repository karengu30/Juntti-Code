import numpy as np
import pandas as pd
# dir /b > files.txt
# get list of filenames in notepad, command prompt, go to file, type 'cmd' at top
inputfp = "C:/Users/karen/OneDrive/Documents/0_RESEARCH/ISH/ImageJ/08-06-2021/Slide8/"
fnblank = "Histogram of Slide2-P1C-bmid3-correct-10x_038-L-blank.csv"
#threshold(inputfp, fn, 95)
def threshold(inputfp, fn, q):
    df = pd.read_csv(inputfp+fn)
    a = np.array(df['count'])
    b = np.cumsum(a)/np.sum(a) * 100
    #q = 95
    indexbin = len(b[b <= q])
    threshold = df['bin start'][indexbin-1]
    print(fn)
    print(threshold)
    return(threshold)
#blank = threshold(inputfp, fnblank, 95)
#signal(inputfp, fnsig, blank)

fnsig = "Histogram of Slide2-P1C-bmid3-correct-10x_038-L-sig.csv"
def signal(inputfp, fn, threshold):
    df2 = pd.read_csv(inputfp+fn)
    result_index = df2['bin start'].sub(threshold).abs().idxmin() #returns index of bin closest to threshold in signal section
    df21 = df2[result_index:] #new dataframe of values after threshold bin
    #real = sum(df21['count']*df21['bin start']) / sum(df21['count']) # gives average above threshold
    total_signal = sum(df21['count']*df21['bin start'])
    total_pixel = sum(df21['count'])
    total_thresh = threshold * total_pixel
    real_diff = total_signal - total_thresh
    print(fn)
    print(total_signal)
    print(total_pixel)
    print(real_diff)
    return(real_diff)

"""
#https://stackoverflow.com/questions/22638557/using-numpy-percentile-on-binned-data
import numpy as np
a = np.array([204., 1651., 2405., 1972., 872., 1455.])
b = np.cumsum(a)/np.sum(a) * 100
q = 75
len(b[b <= q])
4       # ie bin $300,000 - $399,999
"""

# plt.bar(data['bin start'], data['count'], width=8)
# plt.axvline(2035.809, ymin=0, ymax=1500, label='pyplot vertical line', c='g')
# show()
"""
#plt.subplots(2, 2, sharex='all', sharey='all')
plt.subplot(2,1,1, sharex='all', sharey='all')
plt.bar(datablank['bin start'], data['count'], width = 7, color = 'blue')
#plt.axvline(blank, ymin=0, ymax=1500, label='pyplot vertical line', c='g')
plt.subplot(2,1,2, sharex='all', sharey='all')
plt.bar(datasig['bin start'], datasig['count'], width = 20, alpha = 0.5, color = 'orange')
plt.axvline(blank, ymin=0, ymax=1500, label='pyplot vertical line', c='g')
plt.xlabel('Pixel Intensity')
plt.ylabel('Frequency')
matplotlib.rcParams.update({'font.size': 18})
show()
"""
