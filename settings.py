
##### GENERAL SETTINGS #####

## Length of the lists used to calculate the averages and maximums.
## Use the last 10 speed values to calculate the average and maximum.
avg_length = 10


### Units
## The default unit is meters per second (m/s)
units = (1, 'm/s')

## If prefer to use units per second (u/s) uncomment the line bellow.
# units = (1, 'u/s')

## To use kilometers per hour (km/h) uncomment the line bellow.
# units = (3.6, 'km/h')

## To use miles per hour (mph) uncomment the line bellow.
# units = (2.2369363, 'mph')


## Maximum valid speed in meters per second (m/s)
## Speeds above this value are considered to be from bad coordinate readings and are invalidated
max_speed = 100


### Colors (RGB)
## Overlay background color
overlay_color = (0, 0, 0)
## Overlay background opacity (0.0 - 1.0)
overlay_opacity = 0.2

## Title color (Default: white)
title_color = (255, 255, 255)
## Text color when the coordinates are valid (Default: white)
text_color_ok = (255, 255, 255)
## Text color when the coordinates are not valid (Default: gray)
text_color_fail = (200, 200, 200)




##### VIDEO MODE SETTINGS #####
## Only used when running 'python3 totk-speedometer.py -f ...'

## Read coordinates and calculate speed every x frames
## Reading every frame is very inaccurate. For better results is is best to read every 5 or 10 frames.
calc_every_x_frames = 10

## Name of the directory where the videos will be saved.
output_directory = 'totk-speedometer-videos'

## Show preview while creating the video
show_preview = False

## Text size scale
## Default is 1.0 for m/s or u/s and 0.9 for km/h and mph
if units[1] == 'km/h' or 'mph':
    text_scale = 0.9
else:
    text_scale = 1.0




##### REAL-TIME OVERLAY SETTINGS #####
## Only used when running 'python3 totk-speedometer.py -s'

## Maximum refresh rate (times per second)
refresh_rate = 3

## Fixed offsets for overlay position
## The default overlay position is centered above the map.
## If you prefer to have the overlay in a different position change these offsets.
## Horizontal Offset: a positive value moves the overlay to the right and a negative value moves the overlay to the left.
horizontal_offset = 0
## Vertical Offset: a positive value moves the overlay up and a negative value moves the overlay down.
vertical_offset = 0

## Stylesheets
title_style = (
                'font-size: 30pt;'
                'padding-top: 1em;'
                'color: rgb'+str(title_color)+';'
            )

text_style_ok = (
                'font-size: 24pt;'
                'color: rgb'+str(text_color_ok)+';'
            )

text_style_fail = (
                'font-size: 24pt;'
                'color: rgb'+str(text_color_fail)+';'
            )

close_button_style = (
                'font-size: 24pt;'
                'color: white;'
                'background-color: none;'
                'border-style: solid;'
                'border-radius: 5px;'
                'border-width: 1px;'
                'border-color: white;'
            )




##### DEBUGGING SETTINGS #####

## Save an image for each pre-processing stage to images/preprocessing/
save_preprocessing_images = False
