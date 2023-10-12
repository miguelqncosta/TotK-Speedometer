
### GENERAL SETTINGS ###

# Read corrdinates and calculate speed every x frames
# Reading every frame is very incacurate. For better results is is best to read every 5 or 10 frames.
calc_every_x_frames = 10

# Length of the lists used to calculate the averages and maximums.
# Use the last 10 speed values to calculate the average and maximum.
avg_length = 10


# Text overlay colors
title_color = (255, 255, 255)
text_color_ok = (255, 255, 255) # white text when the coordinates are OK
text_color_fail = (200, 200, 200) # grayed out text when the coordinates are not valid



### VIDEO MODE SETTINGS ###
# Only used when running 'python3 totk-speedometer.py -f ...'

# Name of the directory where the videos will be saved.
output_directory = 'totk-speedometer-videos'

# Show preview while creating the video
show_preview = False



### REAL-TIME OVERLAY SETTINGS ###
# Only used when running 'python3 totk-speedometer.py -s'

# Position for the real-time mode overlay
# 0,0 is the top left corner of the screen
overlay_vertical_pos = 500
overlay_horizontal_pos = 2150
overlay_width = 300
overlay_height = 400



### DEBUGGING SETTINGS ###

# Save an image for each pre-processing stage to images/preprocessing/
save_preprocessing_images = False