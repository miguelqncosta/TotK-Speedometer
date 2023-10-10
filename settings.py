
# Read corrdinates and calculate speed every x frames
# Reading every frame is very incacurate. For better results is is best to read every 5 or 10 frames.
calc_every_x_frames = 10


# Lenght of the lists used to calculate the averages and maximums.
# 2*30/10 = 6 this means the last 6 speed values are used to calculate the average and maximum.
# At 30 FPS this corresponds to 2 seconds although it can be more if the speedometer is having dificulties reading the coordinates which can make it skips some frames.
avg_every_x_meas = 2*30/calc_every_x_frames


# Name of the directory where the videos will be saved.
output_directory = 'totk-speedometer-videos'


# Position for the real-time mode overlay
# Only used when running 'python totk-speedometer.py -s'
# 0,0 is the top left corner of the screen
overlay_vertical_pos = 500
overlay_horizontal_pos = 2150
overlay_width = 300
overlay_height = 400
