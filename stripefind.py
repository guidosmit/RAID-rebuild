#!/usr/bin/python
# 
# stripefind.py - Guido Smit - May 2015
# This script needs a file called params.txt, which contains output of 
# all inputblkhash.py output files	


import csv
import operator

with open('params.txt', 'rb') as csvfile:		# This script needs a file params.txt
	params = csv.reader(csvfile, delimiter=' ') 	# takes a file with all catted input files

	def getKey(item):
		return int(item[0])
 	inputsort=(sorted(params, key=getKey))		# sort csv list by input file block collumn
	
	count=0					# overall count in csv list parser
	continued=1
	continued_stripe=1	
	continued_input=1
	continued_diskcount=1			# counter for counting disks in the set

	newblockdest=inputsort[0][1]			# list of array set to first stripe offset on disks
	
	storedinputinfo=[]				# stores all input block hits for later parsing
	storedblockinfo=[]				# stores all offset info for later parsing
	storeddestblockinfo=[]


	maxarray=[]				# counter for stripesize
	maxdisks=[]				# counter for detecting #disks in the block hit set

	images_in_stripe=[]				# array for storing the disk names 
	input_in_stripe=[]				# array for storing input block offsets
	
	print len(inputsort)	
	for count in range(0, len(inputsort)-1):


		block0=inputsort[count-1]		#blockx[0]=input  blockx[1]=destblock block[2]=imagename
		block1=inputsort[count]
		block2=inputsort[count+1]
					
		
		if block2[2] == block1[2]:		# count consecutive found diskblocks 
			continued+=1
		
		else:
			maxarray.append(continued)	# n consecutive found diskblocks	
			continued=1		# reset counter

			if block2[1] == newblockdest:	# look for a new complete stripe line marker
				
				input_in_stripe.append(int(block2[0]))	# found inputblock on stripe line
				images_in_stripe.append(block1[2])	# found imagefile on strip marker
				continued_stripe+=1
				continued_input+=1
				continued_diskcount+=1	
				
			else:					# new marker stripe line found
				maxdisks.append(continued_diskcount)
				
				input_in_stripe.append(int(block2[0]))	# finish parsing last value of stripe line
				images_in_stripe.append(block1[2])
					
				storedinputinfo.append(input_in_stripe)
				storedblockinfo.append(images_in_stripe)				
				storeddestblockinfo.append(float(newblockdest))# parse the offset of the stripe line				

				continued_stripe=1			# reset some counters for new blockdetect
				images_in_stripe=[]
				input_in_stripe=[]				
				continued_diskcount=1

			newblockdest=block2[1]			# set the new stripe line to detect

raidblocksize=max(maxarray)			# max consecutive found 512-byte inputblocks/2 results in stripesize
disks=max(maxdisks)+1			# max equal stripe blocks +1 = disk count for this analysis

# print some stats like stripesize and amount of disks 
print "Found ",disks," disks in this file"
print "It seems that the blocksize used is: ",raidblocksize/2, " Kb. This is ",raidblocksize," 512-byte blocks" 

# find a suitable first block if sector that matches a starting offset closest to offset 0
fullstripesequence=raidblocksize/2*disks*1024   					
print fullstripesequence

# divide all ints in the array list by stripe size for visualizing dstripe sized datablocks v.s. the disk where they were found
for count in range (0, len(storedinputinfo)):
	for element in range (0, len(storedinputinfo[count])):
			storedinputinfo[count][element]-=raidblocksize
			storedinputinfo[count][element]/=raidblocksize


#parsing found block offsets from inputblocks and found blocks on disk next to eachother
for count in range(0, len(storedblockinfo)):
	
	if len(storedinputinfo[count])==disks-1:	# only print complete stripe lines, discard any incompletes
		print storedblockinfo[count],storeddestblockinfo[count],(storeddestblockinfo[count]*512/fullstripesequence)

