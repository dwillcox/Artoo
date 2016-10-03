import sys
import os

# Converts all pdf files passed on the command line to png

if len(sys.argv)==1:
	exit()

fl = sys.argv[1:]

for f in fl:
	fb = f[:-4]
	os.system('gs -o ' + fb + '.png -sDEVICE=png16m  ' + 
			'-dLastPage=1  -r300 ' + fb + '.pdf')
