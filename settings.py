
### GENERAL SETTINGS ###

# Length of the lists used to calculate the averages and maximums.
# Use the last 10 speed values to calculate the average and maximum.
avg_length = 10

# Units
## Default unit is meters per second (m/s)
units = (1, 'm/s')

## It is assumed that the map coordinates are in meters.
## If you don't like this assumption and prefer to use units per second (u/s) uncomment the line bellow.
# units = (1, 'u/s')

## To use kilometers per hour (km/h) uncomment the line bellow.
# units = (3.6, 'km/h')

## To use miles per hour (mph) uncomment the line bellow.
# units = (2.2369363, 'mph')

# Maximum valid speed in meters per second (m/s)
# Speeds above this value are considered to be from bad coordinate readings and are invalidated
max_speed = 100

# Overlay text  colors
title_color = (255, 255, 255)
text_color_ok = (255, 255, 255) # white text when the coordinates are OK
text_color_fail = (200, 200, 200) # grayed out text when the coordinates are not valid




### VIDEO MODE SETTINGS ###
# Only used when running 'python3 totk-speedometer.py -f ...'

# Read coordinates and calculate speed every x frames
# Reading every frame is very inaccurate. For better results is is best to read every 5 or 10 frames.
calc_every_x_frames = 10

# Name of the directory where the videos will be saved.
output_directory = 'totk-speedometer-videos'

# Show preview while creating the video
show_preview = False




### REAL-TIME OVERLAY SETTINGS ###
# Only used when running 'python3 totk-speedometer.py -s'

# Maximum refresh rate (times per second)
refresh_rate = 3

# Width for the real-time mode overlay
# If set to None it will be automatically adjusted to the map width
overlay_width = None




### DEBUGGING SETTINGS ###

# Save an image for each pre-processing stage to images/preprocessing/
save_preprocessing_images = False