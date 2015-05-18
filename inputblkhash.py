#!/usr/bin/python
# inputblkhash.py - Guid Smit - May 2015
# Usage: inputblkhash <inputfile> <image file>  > <results> 
import md5
import os
import multiprocessing as mp
import sys

# Arguments

sectorsize=512
sect_multiplier=10000  # tweak this for performance

inputfile=sys.argv[1]
file=sys.argv[2]

################### hash inputfile ##############
hasharray=[]
f = open(inputfile, 'rb')
fsize = os.path.getsize(inputfile)
inputblocks = fsize/sectorsize
seek=0

for inphash in range (0, inputblocks):
	f.seek(seek)  
  	buf = f.read(sectorsize)	
	
	hash_block_offset=0
	
	m = md5.new()
	m.update(buf[hash_block_offset:hash_block_offset+sectorsize])
	m.digest()
	hasharray.append (m.hexdigest())
	hash_block_offset = hash_block_offset + sectorsize
	seek=seek+sectorsize
f.close

################## Hash & compare block ################
def search_block(seek, workload, output):
	
#	print 'Seek', seek
	limit_seek=seek+workload
	
	f = open(file, 'rb')
	loop=1
	skip=seek	
	while loop == 1:
		f.seek(skip)  
  		buf = f.read(sectorsize*sect_multiplier)	
		hash_block_offset=0

		for x in range(0, sect_multiplier):
	
			m = md5.new()
			m.update(buf[hash_block_offset:hash_block_offset+sectorsize])
			m.digest()
			hex = m.hexdigest()
		
			try:
				indx = hasharray.index(hex)
				output.put(indx)
				output.put((skip+hash_block_offset)/sectorsize)				
								
				print indx,
				print ((skip+hash_block_offset)/sectorsize),
				print file 
			except ValueError: indx=None
		
		
			hash_block_offset = hash_block_offset + sectorsize
	
		skip=skip+sectorsize*sect_multiplier	
		#print skip
		if skip > limit_seek: loop = 0
	f.close

############### Divide total image into number of CPU's ################
cpus = mp.cpu_count()
fsize = os.path.getsize(file)
workload=(fsize/cpus/sectorsize)*sectorsize

output = mp.Queue()

############### set up all threads with their own offsets to analyze #######

processes = [mp.Process(target=search_block, args=(x*workload, workload, output)) for x in range(0,cpus-1)]

# Run processes
for p in processes:
    p.start()

# Exit the completed processes
for p in processes:
    p.join()

