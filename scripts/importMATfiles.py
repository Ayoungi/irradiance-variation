import matplotlib
import numpy as np
import matplotlib.pyplot as plt
import csv
import exifread
import bisect
import datetime
from scipy import interpolate
from matplotlib.dates import DateFormatter
import scipy.io as sio

def importMATfiles(dict_file,year_number):

	dict_list = list(dict_file.values())
	for i,item in enumerate(dict_list):
		if type(item) is np.ndarray:
			mymatrix = dict_list[i]

	day_array = mymatrix[:,0]
	hour_array = mymatrix[:,1]
	minute_array = mymatrix[:,2]
	solar_rad_array = mymatrix[:,4]
	pwv_array = mymatrix[:,12]

	timestamps = []

	for i,day in enumerate(day_array):
		mydate = datetime.datetime(year_number, 1, 1) + datetime.timedelta(day - 1)
		myyear = mydate.year
		mymonth = mydate.month
		myday = mydate.day
		timestamps.append(datetime.datetime(year_number,mymonth,myday,int(hour_array[i]),int(minute_array[i]),0))

	return(timestamps,solar_rad_array,pwv_array)


