#!/bin/csh -f
#

# Set the output file
set psfile = "./gmt.ps"

# Start the Postscript file 
# 
psbasemap -JM6.5i -R-111.635/-108.406/23.899/26.321 -Ba1.000f1.000/a0.500f0.500NEWS:."":  -X0.75i -Y1.0i -P -K > $psfile 

# Add the Coastline and National Boundaries
# 
pscoast -K -O -J -R -B -N1 -N2 -W -Dl -A8 -G250/250/200  >> $psfile 

# Add station locations.  
# Input are longitude latitude.
#
psxy -K -O -J -R -St0.25i -G0/0/0 <<EOF >> $psfile 
-110.309 24.101 
EOF

# Add event locations.
# Input are longitude latitude.
#
psxy -O -K -J -R -W10/0/0/0  -Sc0.25i  <<EOF >> $psfile 
-109.540 25.220 
-110.461 26.087 
-110.410 26.057 
-110.501 26.119 
EOF

# End the Postscript File
# 
psxy -R -J -O /dev/null >> $psfile 

