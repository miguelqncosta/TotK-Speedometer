
### GENERAL SETTINGS ###

# Length of the lists used to calculate the averages and maximums.
# Use the last 10 speed values to calculate the average and maximum.
avg_length = 10

# Maximum valid speed in m/s
# Speeds above this value are considered to be from bad coordinate readings and are invalidated
max_speed = 100



### VIDEO MODE SETTINGS ###
# Only used when running 'python3 totk-speedometer.py -f ...'

# Read coordinates and calculate speed every x frames
# Reading every frame is very inaccurate. For better results is is best to read every 5 or 10 frames.
calc_every_x_frames = 10

# Name of the directory where the videos will be saved.
output_directory = 'totk-speedometer-videos'

# Show preview while creating the video
show_preview = False

# Text overlay colors
title_color = (255, 255, 255)
text_color_ok = (255, 255, 255) # white text when the coordinates are OK
text_color_fail = (200, 200, 200) # grayed out text when the coordinates are not valid



### REAL-TIME OVERLAY SETTINGS ###
# Only used when running 'python3 totk-speedometer.py -s'

# Width for the real-time mode overlay
# If set to None it will be automatically adjusted to the map width
overlay_width = None



### DEBUGGING SETTINGS ###

# Save an image for each pre-processing stage to images/preprocessing/
save_preprocessing_images = False