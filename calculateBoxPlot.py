# Import all libraries
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import csv
import exifread
import bisect
import datetime
from scipy import interpolate
import scipy.io as sio
from tempfile import TemporaryFile
import os
from glob import glob

# User defined functions
from scripts.SG_solarmodel import *
from scripts.importMATfiles import *
from scripts.nearest import *
from scripts.normalize_array import *


# MAT file containing the PWV and weather station values
test = sio.loadmat('./input/data/PWV_SR/PWV_2015from_WS_3_withGradient.mat')


# Import the MAT files
print ('Importing MAT files')
(timestamps,solar_rad_array,pwv_array) = importMATfiles(test,2015)
print ('MAT file are imported')


# Data cleaning
find_index = np.where( pwv_array != 0 ) #PWV values cannot be zero
new_pwv = pwv_array[find_index[0]]
new_solar = solar_rad_array[find_index[0]]
new_datetime = [timestamps[i] for i in find_index[0]]
print ('Data cleaned.')


# Calculate the clear sky radiation
print ('Computing solar radiation data.')
latitude = 1.3429943	# Latitude and longitude of our weather station.
longitude = 103.6810899
clear_sky_rad = []
for date_part in new_datetime:
	novi_date_part = date_part - datetime.timedelta(hours=7) # Because this program is tested in Dublin, Ireland
	CSR = SG_model(novi_date_part)
	clear_sky_rad.append(CSR)

clear_sky_rad = np.array(clear_sky_rad)
diff_solar_rad = np.abs(clear_sky_rad-new_solar)



# Considering only daytime observations, because there is no significance for solar radiation at night.
dayonly_time = []
dayonly_index = []

for i,p_time in enumerate(new_datetime):    
	item_year = p_time.year
	item_month = p_time.month
	item_day = p_time.day
	item_hour = p_time.hour
	item_minute = p_time.minute
	item_second = p_time.second
	start_time = datetime.datetime(int(item_year),int(item_month),int(item_day),8,0,0)
	end_time = datetime.datetime(int(item_year),int(item_month),int(item_day),18,0,0)      
	if p_time > start_time and p_time<end_time :
		dayonly_time.append(p_time)
		dayonly_index.append(i)
		
		
dayonly_index = np.array(dayonly_index)        
dayonly_pwv = new_pwv[dayonly_index]
dayonly_solar = new_solar[dayonly_index]
dayonly_diff_solar = diff_solar_rad[dayonly_index]



# Import the cloud coverage data files that were generated from Dev et al. approach
start_dir = './input/data/processed_cloud_coverage/2015/' # coverage files 
dirs = os.listdir( start_dir)
coverage_files = []
for text_file in dirs:
	if '.txt' in text_file:
		coverage_files.append(text_file)
coverage_files = sorted(coverage_files)        
print ('Coverage files imported.')


# Common timestamps between PWV, CRE and cloud coverage.
common_timestamps = []
PWV_points = []
CRE_points = []
COV_points = []
	
# Checking each files one-by-one
for file_number, cov_file in enumerate(coverage_files):    
	print ('---------------------------------')
	
	# ### Read the generated data
	cov_file = start_dir + cov_file
	print (cov_file)
	
	# read the finalised HDR file
	with open(cov_file) as f: #f is a file header
		reader = csv.reader(f, delimiter=",")
		d = list(reader) # d is a list of list here.
		total_rows = len(d)

	img_date = []
	img_time = []
	img_coverage = np.zeros(total_rows-1)
	img_datetimes = []
	
	# variable i starts from 1 so that header is skipped
	for i in range(1,total_rows):
		date_item = d[i][1]
		time_item = d[i][2]
		coverage_item = d[i][3]

		img_date.append(date_item)
		img_time.append(time_item)
		img_coverage[i-1] = coverage_item
		
		YY = int(date_item[0:4])
		MON = int(date_item[5:7])
		DD = int(date_item[8:10])
		HH = int(time_item[0:2])
		MM = int(time_item[3:5])
		SS = int(time_item[6:8])
		sw = datetime.datetime(YY,MON,DD,HH,MM,SS)
		img_datetimes.append(sw)      
		

	
	# Check wrt to image datapoints.
	for i,check_time in enumerate(img_datetimes):
		
		(time_found,diff_ts) = nearest(check_time,dayonly_time)
	
		if np.abs(diff_ts)<150:
			common_timestamps.append(check_time)
			COV_points.append(img_coverage[i])
		
			# Check the corresponding index of WS data
			i2 = dayonly_time.index(time_found)
			PWV_points.append(dayonly_pwv[i2])
			CRE_points.append(dayonly_diff_solar[i2])			  
		
		
PWV_points = np.array(PWV_points)
CRE_points = np.array(CRE_points)
COV_points = np.array(COV_points)
COV_points = 100*COV_points


# Normalizing
CRE_points = normalize_array(CRE_points)
COV_points = normalize_array(COV_points)


# Combined box plot.
NO_OF_BINS = 20   # Just note that 100/NO_OF_BINS should be an integer number
box1 = [[] for _ in range(0,5)]

for i,item in enumerate(PWV_points):
	if item<=45:
		whichBin = 0
	elif item>45 and item<=55:
		whichBin = 1
	elif item>55 and item<=60:
		whichBin = 2
	elif item>60 and item<=65:
		whichBin = 3
	elif item>65:
		whichBin = 4        
	box1[whichBin].append(CRE_points[i])
	
	
box2 = [[] for _ in range(0,5)]

for i,item in enumerate(PWV_points):
	if item<=45:
		whichBin = 0
	elif item>45 and item<=55:
		whichBin = 1
	elif item>55 and item<=60:
		whichBin = 2
	elif item>60 and item<=65:
		whichBin = 3
	elif item>65:
		whichBin = 4        
	box2[whichBin].append(COV_points[i])    
	



# Saving the numpys
outfile = TemporaryFile()
np.savez('./results/boxinfo', box1=box1, box2=box2)


labelList =['<45', '45-55', '55-60', '60-65', '>65']

fig, ax = plt.subplots()
bp1 = ax.boxplot(box1, positions = [1, 2, 3, 4, 5], widths = 0.2, sym='r+', whis=2)
print (bp1.keys())
plt.setp(bp1['boxes'], color='red') 
plt.setp(bp1['fliers'], color='red') 
plt.setp(bp1['caps'], color='red') 
plt.setp(bp1['medians'], color='red') 
plt.setp(bp1['whiskers'], color='red') 

ax2 = ax.twinx()
bp2 = ax2.boxplot(box2, positions = [1.3, 2.3, 3.3, 4.3, 5.3], widths = 0.2,  sym='b+', whis=2)
plt.setp(bp2['boxes'], color='blue') 
plt.setp(bp2['fliers'], color='blue') 
plt.setp(bp2['caps'], color='blue') 
plt.setp(bp2['medians'], color='blue') 
plt.setp(bp2['whiskers'], color='blue') 

ax.set_xticklabels(['<45', '45-55', '55-60', '60-65', '>65'])
ax.set_xticks([1.15, 2.15, 3.15, 4.15, 5.15])

ax.set_ylabel('Cloud radiative effect [Watt/m2]', fontsize=13, color='r')
ax.set_xlabel('PWV from GPS', fontsize=14)
ax2.set_ylabel('Cloud coverage from sky cameras', fontsize=13, color='b')

ax.grid(True)
plt.savefig('./results/boxplot.pdf', bbox_inches='tight')