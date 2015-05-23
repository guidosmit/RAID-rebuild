#!/usr/bin/python
# stripe2vol.py - Guido Smit - May 2015
# change disk image order, data block offsets and parity size before running 

import sys
import os 

# append the disk image names according to the found disk order
disk=[]
disk.append('PLACEHOLDER FOR ZERO OFFSET CONFUSION')
disk.append('DISK1.dd')
disk.append('DISK2.dd')
disk.append('DISK3.dd')
disk.append('DISK4.dd')
disk.append('DISK5.dd')

# This is the datablock ordering reference table. 0 marks new stripe
datablocks=[1,2,3,4,0,5,1,2,3,0,4,5,1,2,0,3,4,5,1,0,2,3,4,5,0]   #  Left synchronous 5 disk

######## Use one of the following orders for Left async/sync layouts:  ################
#datablocks=[1,2,3,4,0,1,2,3,5,0,1,2,4,5,0,1,3,4,5,0,2,3,4,5,0]   #  Left Asynchronous 5 disk

#datablocks=[1,2,3,0,4,1,2,0,3,4,1,0,2,3,4,0]  #  Left synchronous 4 disk
#datablocks=[1,2,3,0,1,2,4,0,1,3,4,0,2,3,4,0]  #  Left Asynchronous 4 disk

#datablocks=[1,2,0,1,3,0,2,3,0]   #  Left Synchronous 3 disk
#datablocks=[1,2,0,1,3,0,2,3,0]   #  Left Asynchronous 3 disk
#######################################################################################

# change stripe size here
stripesize=128*512

# set output file
outputfile='output.dd'
of=open(outputfile, 'w')

# calculate total stripe sequences by filesize of image
statinfo = os.stat(disk[1])
stripecounttotal=(statinfo.st_size/stripesize)     	

# start parsing closest to 0
stripeline=0*512

for stripecount in range(0, stripecounttotal):
	
	countblksequence=0
		

	while (countblksequence<len(datablocks)):
		
		readdisk=datablocks[countblksequence] 		
			
		if readdisk==0:				# test for a new line marker
			stripeline+=stripesize
			
		else:
			f = open(disk[readdisk],'rb')	# else read a new datablock and write
			f.seek(stripeline)
                	read = f.read(stripesize)
			of.write(read)
			f.close
	
		countblksequence+=1

of.close

