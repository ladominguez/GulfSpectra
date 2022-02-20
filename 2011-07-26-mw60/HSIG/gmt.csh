#!/bin/csh -f
#

# Set the output file
set psfile = "./gmt.ps"

# Start the Postscript file 
# 
psbasemap -JM6.5i -R-113.388/-107.101/24.697/29.413 -Ba2.000f2.000/a1.000f1.000NEWS:."":  -X0.75i -Y1.0i -P -K > $psfile 

# Add the Coastline and National Boundaries
# 
pscoast -K -O -J -R -B -N1 -N2 -W -Dl -A30 -G250/250/200  >> $psfile 

# Add station locations.  
# Input are longitude latitude.
#
psxy -K -O -J -R -St0.25i -G0/0/0 <<EOF >> $psfile 
-110.949 29.020 
EOF

# Add event locations.
# Input are longitude latitude.
#
psxy -O -K -J -R -W10/0/0/0  -Sc0.25i  <<EOF >> $psfile 
-109.540 25.090 
EOF

# End the Postscript File
# 
psxy -R -J -O /dev/null >> $psfile 

