# Parse_VSC_RFC.py by sk3tchymoos3
# This script will automatically mount an E01 single 
# disk image, mount the VSC found on disk and run 
# rfc by Harlan Carvey against all of them. 
# You can always add other commands if you so desire!
# usage: python parse_VSC_RFC.py <pathTofile.e01>

import os
import re
import sys

#declaring variables 
tempFile="/tmp/info"

#check for the E01 file
if len(sys.argv) == 1:
	print "Please prvide the E01 image to mount!"
	sys.exit()
else:
	imageFile=sys.argv[1]
	print "Using the E01 file %s" % imageFile

#first we need to mount the E01
os.system("sudo ewfmount %s /mnt/ewf >/dev/null 2>&1" % imageFile)

#lets grab the number of vss
os.system("vshadowinfo /mnt/ewf/ewf1 >> %s" % tempFile)
file = open(tempFile,"r")
for line in file:		
	if re.search("stores",line):	
		for s in line.split():
			if s.isdigit():
				number=int(s)
				print "We have %d VSS" % number

#w00t, lets mount these bad boys
print "Running vshadowmount..."
os.system("vshadowmount /mnt/ewf/ewf1 /mnt/vss >/dev/null 2>&1")
os.chdir("/mnt/vss")
#print os.getcwd()
for x in range(1,number+1):
	try:
		os.system("mount -o ro,loop,show_sys_files,streams_interface=windows vss%d /mnt/shadow_mount/vss%d >/dev/null 2>&1" % (x,x))
	except:
		print "Could not parse vss%d, skipping" % x		
		pass

#ok run your tools :D
for x in range (1,number+1):
	if os.path.exists("/mnt/shadow_mount/vss%d/Windows" % x):
		print "Executing on RecentFileCache on vss%d" % x
		os.system("perl /usr/local/bin/rfc.pl /mnt/shadow_mount/vss%d/Windows/AppCompat/Programs/RecentFileCache.bcf" % x)
	else:
		pass

#cleanup!
print "Cleaning up the mounted VSS files and temporary files..."
for x in range (1,number+1):
	try:	
		os.system("umount /mnt/shadow_mount/vss%d >> /tmp/trash" % x)
	except:
		pass
#os.system("umount /mnt/vss")
#os.system("umount /mnt/ewf")
os.system("rm -rf %s" % tempFile)
print "Thank you and have a good day :D Don't forget to unmount vss & ewf"
