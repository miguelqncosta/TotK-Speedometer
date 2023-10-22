
import json
import os
import signal
import sys
import time

import cv2
import mss.tools
import numpy as np
import pytesseract
from moviepy.editor import *
from PyQt6 import QtWidgets
from PyQt6.QtCore import QRunnable, QThreadPool

import settings
from overlay import SpeedometerOverlay

# Lists to keep historical values
speed_list = []
speed_h_list = []
speed_v_list = []


def get_coord_img(map_img, map_circle, scaling):
    polar_img = cv2.warpPolar(map_img, dsize=(
                                        map_img.shape[1]*scaling,
                                        map_img.shape[0]*scaling),
                                        center=(map_circle[0],map_circle[1]
                                    ),
                                    maxRadius=map_circle[2],
                                    flags=cv2.WARP_POLAR_LOG | cv2.INTER_CUBIC )

    polar_img = cv2.rotate(polar_img, cv2.ROTATE_90_CLOCKWISE)
    cropped_img = polar_img[int(polar_img.shape[0]*0.95):, int(polar_img.shape[1]*0.58):int(polar_img.shape[1]*0.92)]

    if settings.save_preprocessing_images:
        cv2.imwrite('images/map_polar.png', polar_img)
        cv2.imwrite('images/map_cropped.png', cropped_img)

    return cropped_img



def preprocess_coord_img(coord_img):
    coord_img = cv2.cvtColor(coord_img,cv2.COLOR_BGR2GRAY)
    blur_img = cv2.GaussianBlur(coord_img,(5,5),0)
    avg_brightness = cv2.mean(blur_img)[0]
    beta = -2*avg_brightness-50
    contrast_img = cv2.convertScaleAbs(blur_img, alpha=3.5, beta=beta)
    ret, threshold_img = cv2.threshold(contrast_img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    erode_img = cv2.erode(threshold_img, np.ones((3,3)), iterations=1)
    dilate_img = cv2.dilate(erode_img, np.ones((3,3)), iterations=2)
    processed_img = cv2.erode(dilate_img, np.ones((3,3)), iterations=2)

    if settings.save_preprocessing_images:
        os.makedirs(os.path.join('images', 'preprocessing'), exist_ok=True)
        cv2.imwrite('images/preprocessing/1_blur_img.png', blur_img)
        cv2.imwrite('images/preprocessing/2_contrast_img.png', contrast_img)
        cv2.imwrite('images/preprocessing/3_threshold_img.png', threshold_img)
        cv2.imwrite('images/preprocessing/4_erode_img.png', erode_img)
        cv2.imwrite('images/preprocessing/5_dilate_img.png', dilate_img)
        cv2.imwrite('images/preprocessing/6_processed_img.png', processed_img)

    return processed_img



def extract_coordinates(coord_img):
    text = pytesseract.image_to_string(coord_img, config='--psm 7 --oem 3 --user-patterns coord.patterns -c tessedit_char_whitelist=" -0123456789"')
    coord_list = text.strip().replace('--', '-').split(' ')

    if '' in coord_list:
        coord_list.remove('')
    if ' ' in coord_list:
        coord_list.remove(' ')
    if '-' in coord_list:
        coord_list.remove('-')

    coord_list = [c.rstrip('-') for c in coord_list]

    try:
        if isinstance(text, str) and text != '':
            coord = [int(c) for c in coord_list]

            if len(coord) == 3:
                if (5000 > coord[0] > -5000 and 4000 > coord[1] > -4000 and 3500 > coord[2] > -3000):
                    return True, coord
    except ValueError:
        return False, coord_list

    return False, coord_list



def process_coordinates(coord, last_coord, time_delta):
    if len(coord)==3 and len(last_coord)==3 and all(isinstance(val, int) for val in coord+last_coord):

        # Use absolute coordinates if they are far enough from the map origin
        # Only accounts for the coordinates sign near the (0,0,0) position to avoid errors from miss reading the minus sign
        if abs(coord[0]) > 100 and abs(last_coord[0]) > 100:
            coord_x = abs(coord[0])
            last_coord_x = abs(last_coord[0])
        else:
            coord_x = coord[0]
            last_coord_x = last_coord[0]

        if abs(coord[1]) > 100 and abs(last_coord[1]) > 100:
            coord_y = abs(coord[1])
            last_coord_y = abs(last_coord[1])
        else:
            coord_y = coord[1]
            last_coord_y = last_coord[1]

        if abs(coord[2]) > 100 and abs(last_coord[2]) > 100:
            coord_z = abs(coord[2])
            last_coord_z = abs(last_coord[2])
        else:
            coord_z = coord[2]
            last_coord_z = last_coord[2]

        distance = np.sqrt((coord_x-last_coord_x)**2 + (coord_y-last_coord_y)**2 + (coord_z-last_coord_z)**2)
        distance_h = np.sqrt((coord_x-last_coord_x)**2 + (coord_y-last_coord_y)**2)
        distance_v = np.sqrt((coord_z-last_coord_z)**2)

        speed = distance/time_delta
        if speed <= settings.max_speed:
            speed_list.append(speed)
        if len(speed_list) > settings.avg_length:
            speed_list.pop(0)

        speed_h = distance_h/time_delta
        if speed_h <= settings.max_speed:
            speed_h_list.append(speed_h)
        if len(speed_h_list) > settings.avg_length:
            speed_h_list.pop(0)

        speed_v = distance_v/time_delta
        if speed_v <= settings.max_speed:
            speed_v_list.append(speed_v)
        if len(speed_v_list) > settings.avg_length:
            speed_v_list.pop(0)

        if len(speed_list) > 0:
            avg_speed = sum(speed_list)/len(speed_list)
            max_speed = max(speed_list)
        else:
            avg_speed = float('nan')
            max_speed = float('nan')

        if len(speed_h_list) > 0:
            avg_speed_h = sum(speed_h_list)/len(speed_h_list)
            max_speed_h = max(speed_h_list)
        else:
            avg_speed_h = float('nan')
            max_speed_h = float('nan')

        if len(speed_v_list) > 0:
            avg_speed_v = sum(speed_v_list)/len(speed_v_list)
            max_speed_v = max(speed_v_list)
        else:
            avg_speed_v = float('nan')
            max_speed_v = float('nan')

        speed_stats = {
                    'distance': {
                        'Distance': distance,
                        'Distance H': distance_h,
                        'Distance V': distance_v
                    },
                    'total': {
                        'Speed': speed,
                        'Avg': avg_speed,
                        'Max': max_speed
                    },
                    'horizontal': {
                        'Speed': speed_h,
                        'Avg': avg_speed_h,
                        'Max': max_speed_h
                    },
                    'vertical': {
                        'Speed': speed_v,
                        'Avg': avg_speed_v,
                        'Max': max_speed_v
                    }
                }

        return speed_stats



def print_stats(coord, last_coord, stats):
    print(f'Coord: {[f"{c: 05d}" for c in coord]}'
    f' - Last Coord {[f"{c: 05d}" for c in last_coord]}'
    f' - Distance: {stats["distance"]["Distance"]:8.2f} m'
    f' - Speed: {stats["total"]["Speed"]*settings.units[0]:9.2f} {settings.units[1]}'
    f' - AvgSpeed: {stats["total"]["Avg"]*settings.units[0]:5.2f} {settings.units[1]}'
    f' - Speed H: {stats["horizontal"]["Speed"]*settings.units[0]:9.2f} {settings.units[1]}'
    f' - Speed V: {stats["vertical"]["Speed"]*settings.units[0]:9.2f} {settings.units[1]}', end='')

    if not any(np.isnan(b) or b > settings.max_speed for v in stats.values() for b in v.values()):
        print()
    else:
        print(' - Invalid Coordinates!')



def add_overlay(frame, speed_stats, width, height, text_color):
    text_w_start = int(width*0.842)
    text_h_start = int(height*0.20)
    overlay_w_start = int(width*0.836)
    overlay_w_end = int(width*0.961)
    overlay_h_start = int(height*0.16)
    overlay_h_end = int(height*0.694)
    spacing = int(height/25)
    text_size = height/1500 * settings.text_scale

    bgr_text_color = text_color[::-1]
    bgr_title_color = settings.title_color[::-1]
    bgr_overlay_color = settings.overlay_color[::-1]

    overlay = frame.copy()
    cv2.rectangle(overlay, (overlay_w_start, overlay_h_start), (overlay_w_end, overlay_h_end), bgr_overlay_color, cv2.FILLED)
    cv2.addWeighted(overlay, settings.overlay_opacity, frame, 1 - settings.overlay_opacity, 0, frame)

    text_h = text_h_start
    frame = cv2.putText(frame, 'Total', (text_w_start, text_h), cv2.FONT_HERSHEY_TRIPLEX, text_size, bgr_title_color, 1, cv2.LINE_AA)
    for key,value in speed_stats['total'].items():
        text_h = text_h + spacing
        text = f'{key}: {value*settings.units[0]:.2f} {settings.units[1]}'
        frame = cv2.putText(frame, text, (text_w_start, text_h), cv2.FONT_HERSHEY_SIMPLEX, text_size, bgr_text_color, 1, cv2.LINE_AA)

    text_h = int(text_h + (1.5*spacing))
    frame = cv2.putText(frame, 'Horizontal', (text_w_start, text_h), cv2.FONT_HERSHEY_TRIPLEX, text_size, bgr_title_color, 1, cv2.LINE_AA)
    for key,value in speed_stats['horizontal'].items():
        text_h = text_h + spacing
        text = f'{key}: {value*settings.units[0]:.2f} {settings.units[1]}'
        frame = cv2.putText(frame, text, (text_w_start, text_h), cv2.FONT_HERSHEY_SIMPLEX, text_size, bgr_text_color, 1, cv2.LINE_AA)

    text_h = int(text_h + (1.5*spacing))
    frame = cv2.putText(frame, 'Vertical', (text_w_start, text_h), cv2.FONT_HERSHEY_TRIPLEX, text_size, bgr_title_color, 1, cv2.LINE_AA)
    for key,value in speed_stats['vertical'].items():
        text_h = text_h + spacing
        text = f'{key}: {value*settings.units[0]:.2f} {settings.units[1]}'
        frame = cv2.putText(frame, text, (text_w_start, text_h), cv2.FONT_HERSHEY_SIMPLEX, text_size, bgr_text_color, 1, cv2.LINE_AA)

    return frame



def export_video(video_path, fps):
    path = os.path.dirname(video_path)
    filename = os.path.basename(video_path)
    name = os.path.splitext(filename)[0]
    ext = os.path.splitext(filename)[1]
    os.makedirs(os.path.join(path, settings.output_directory), exist_ok=True)
    tmp_filename = os.path.join(path, settings.output_directory, name+'_speedometer_tmp'+ext)
    output_filename = os.path.join(path, settings.output_directory, name+'_speedometer'+ext)

    # Add audio from original video
    orig_clip = VideoFileClip(video_path)
    orig_audioclip = orig_clip.audio
    tmp_clip = VideoFileClip(tmp_filename)
    clip_with_audio = tmp_clip.set_audio(orig_audioclip)
    clip_with_audio.write_videofile(output_filename, codec='libx264', audio_codec='aac', fps=fps)
    orig_clip.close()
    tmp_clip.close()

    # Remove temporary video file
    os.remove(tmp_filename)



def export_video_with_overlay(video_path):
    print('Processing video: ' + video_path)

    video = cv2.VideoCapture(video_path)
    width  = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = video.get(cv2.CAP_PROP_FPS)
    h = int(video.get(cv2.CAP_PROP_FOURCC))
    codec = chr(h&0xff) + chr((h>>8)&0xff) + chr((h>>16)&0xff) + chr((h>>24)&0xff)

    print(f'Video - Width: {width}, Height: {height}, FPS: {fps}, Encoding: {codec}')

    path = os.path.dirname(video_path)
    filename = os.path.basename(video_path)
    name = os.path.splitext(filename)[0]
    ext = os.path.splitext(filename)[1]
    os.makedirs(os.path.join(path, settings.output_directory), exist_ok=True)
    tmp_filename = os.path.join(path, settings.output_directory, name+'_speedometer_tmp'+ext)
    tmp_video = cv2.VideoWriter(tmp_filename, cv2.VideoWriter_fourcc(*'avc1'), fps, (width, height))

    count = 0
    map_circle = None
    last_coord = None

    while video.isOpened():
        ret,frame = video.read()
        if not ret:
            break

        map_img = frame[int(height*0.71):int(height*0.96), int(width*0.829):int(width*0.97)]
        map_circle = [int(width*0.06875), int(height*0.1223), int(width*0.0641)]

        if settings.save_preprocessing_images:
            cv2.imwrite('images/map.png', map_img)

        if count > settings.calc_every_x_frames:
            coord_img = get_coord_img(map_img, map_circle, 16)
            processed_img = preprocess_coord_img(coord_img)
            ret, coord = extract_coordinates(processed_img)
            text_color = settings.text_color_fail # Set text color to gray when the coordinates are not valid

            if ret:
                if last_coord is not None:
                    tmp_speed_stats = process_coordinates(coord, last_coord, (1/fps)*count)
                    print_stats(coord, last_coord, tmp_speed_stats)

                    if not any(np.isnan(b) or b > settings.max_speed for v in tmp_speed_stats.values() for b in v.values()):
                        speed_stats = tmp_speed_stats
                        text_color = settings.text_color_ok # Set text to white when the coordinates are valid

                last_coord = coord
                count = 0
            else:
                print('Failed reading coordinates! Coord:', coord)

        count = count + 1

        if 'speed_stats' in locals() and speed_stats is not None:
            frame = add_overlay(frame, speed_stats, width, height, text_color)

        tmp_video.write(frame)

        if settings.show_preview:
            cv2.imshow('TotK Speedometer', frame)
            # Press 'q' key to quit
            if cv2.waitKey(1) & 0xFF == ord('q'):
                return

    video.release()
    tmp_video.release()
    cv2.destroyAllWindows()
    export_video(video_path, fps)



def detect_circle(map_img, height):
    img = cv2.cvtColor(map_img,cv2.COLOR_BGR2GRAY)

    circles = cv2.HoughCircles(img, cv2.HOUGH_GRADIENT, 1, (height*0.25),
                            param1=120,
                            param2=30,
                            minRadius=int(height*0.05),
                            maxRadius=int(height*0.12)
                            )

    if circles is not None:
        circles = np.uint16(np.around(circles))
        circles_img = img.copy()
        circles_img = cv2.cvtColor(circles_img, cv2.COLOR_GRAY2BGR)

        for i in circles[0,:]:
            # draw the outer circle
            cv2.circle(circles_img,(i[0],i[1]),i[2],(0,255,0),2)
            # draw the center of the circle
            cv2.circle(circles_img,(i[0],i[1]),2,(0,0,255),3)

        return circles, circles_img
    else:
        return None, None



def detect_map(monitor_number):
    with mss.mss() as sct:
        mon = sct.monitors[monitor_number]

        monitor = {
                'top': mon['top'],
                'left': mon['left'],
                'width': mon['width'],
                'height': mon['height'],
                'mon': monitor_number
            }

        sct_img = sct.grab(monitor)
        img = np.array(sct_img)
        h, w, c = img.shape
        monitor_scaling = int(w/mon['width'])

        print('Using Monitor', monitor_number, '- Geometry:',
                ' width:', mon['width'],
                ' height:', mon['height'],
                ' top:', mon['top'],
                ' left:', mon['left'],
                ' scaling:', monitor_scaling
            )

        print()
        print('Searching map position...')

        while True:
            t_start = time.time()

            sct_img = sct.grab(monitor)
            img = np.array(sct_img)
            cv2.imwrite('images/screenshot.png', img)

            circles, circles_img = detect_circle(img, h)
            if circles_img is not None:
                cv2.imwrite('images/detected_circles.png', circles_img)

            if circles is not None:
                for map_circle in circles[0]:
                    # Capture only the screen part the map occupies
                    monitor_region = {
                        'top': int(mon['top']+(map_circle[1]-map_circle[2])/monitor_scaling - 20),
                        'left': int(mon['left']+(map_circle[0]-map_circle[2])/monitor_scaling - 20),
                        'width': int(((map_circle[2]*2)/monitor_scaling) + 40),
                        'height': int(((map_circle[2]*2)/monitor_scaling) + 40),
                        'mon': monitor_number
                    }

                    sct_img = sct.grab(monitor_region)
                    map_img = np.array(sct_img)
                    cv2.imwrite('images/map.png', map_img)

                    circles, circles_img = detect_circle(map_img, h)
                    if circles_img is not None:
                        cv2.imwrite('images/detected_map_circle.png', circles_img)

                    if circles is not None:
                        if len(circles[0])==1:
                            map_circle = circles[0][0]
                            coord_img = get_coord_img(map_img, map_circle, int(8/monitor_scaling))
                            processed_img = preprocess_coord_img(coord_img)
                            ret, coord = extract_coordinates(processed_img)
                            if ret:
                                tmp_speed_stats = process_coordinates(coord, coord, 1)
                                if tmp_speed_stats is not None:
                                    print('Map position detected.')
                                    print()
                                    print('Map region',
                                            ' width:', monitor_region['width'],
                                            ' height:', monitor_region['height'],
                                            ' top:', monitor_region['top'],
                                            ' left:', monitor_region['left']
                                        )
                                    print('Map center: [', map_circle[0], ',', map_circle[1], ']  Map radius:', map_circle[2])
                                    print()
                                    map_position_cache = {'monitor_region': monitor_region,
                                                            'monitor_scaling': monitor_scaling,
                                                            'map_circle': map_circle.tolist()
                                                        }
                                    json.dump(map_position_cache, open(settings.map_position_cache_filename, 'w') )
                                    return map_circle, monitor_region, monitor_scaling

            sleep_time = (1/settings.refresh_rate)-(time.time()-t_start)
            if sleep_time > 0:
                time.sleep(sleep_time)



class SpeedometerRunnable(QRunnable):
    def __init__(self, mainwindow, monitor_region, monitor_scaling, map_circle):
        super().__init__()
        self.mainwindow = mainwindow
        self.monitor_region = monitor_region
        self.monitor_scaling = monitor_scaling
        self.map_circle = map_circle
        self.running = True
        self.finished = False

    def stop(self):
        self.running = False

    def wait(self):
        t = time.time()
        while not self.finished and (time.time() - t < 1):
            time.sleep(0.1)

    def run(self):
        last_coord = None
        last_coord_time = None
        speed_stats = None

        with mss.mss() as sct:
            while self.running:
                t_start = time.time()

                # Grab the map screenshot
                sct_img = sct.grab(self.monitor_region)

                # Save the map screenshot
                if settings.save_preprocessing_images:
                    mss.tools.to_png(sct_img.rgb, sct_img.size, output='images/map.png')

                map_img = np.array(sct_img)
                scaling = int(8/self.monitor_scaling)
                coord_img = get_coord_img(map_img, self.map_circle, scaling)
                processed_img = preprocess_coord_img(coord_img)
                ret, coord = extract_coordinates(processed_img)
                text_style = settings.text_style_fail # Set text color to gray when the coordinates are not valid

                if ret:
                    t = time.time()
                    if last_coord is not None:
                        tmp_speed_stats = process_coordinates(coord, last_coord, t-last_coord_time)
                        print_stats(coord, last_coord, tmp_speed_stats)

                        if not any(np.isnan(b) or b > settings.max_speed for v in tmp_speed_stats.values() for b in v.values()):
                            speed_stats = tmp_speed_stats
                            text_style = settings.text_style_ok # Set text to white when the coordinates are valid

                    last_coord_time = t
                    last_coord = coord
                else:
                    print('Failed reading coordinates! Coord:', coord)

                self.mainwindow.update_labels(speed_stats, text_style)

                sleep_time = (1/settings.refresh_rate)-(time.time()-t_start)
                if sleep_time > 0:
                    time.sleep(sleep_time)

                # # Uncomment this line to print the overlay refresh rate
                # print('FPS:', 1/(time.time()-t_start))

        self.finished = True



def main():
    import argparse

    parser = argparse.ArgumentParser(description='Speedometer for Zelda TotK')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-f', dest='files', metavar='file', type=str, nargs='+', help='path to video file. Accepts multiple files')
    group.add_argument('-s', dest='screen_capture', action='store_true', help='use screen capture and overlay stats')
    group.add_argument('--test', dest='test', action='store_true', help='test image pre-processing')

    group_optional = parser.add_mutually_exclusive_group(required=False)
    group_optional.add_argument('-m', '--monitor', dest='monitor', default=1, type=int, help='monitor number to capture and display the overlay')
    group_optional.add_argument('-c', '--cached-map-position', dest='cache', action='store_true', help='use the cached map position instead of searching')

    args = parser.parse_args()

    signal.signal(signal.SIGINT, signal.SIG_DFL)

    if args.files is None and args.screen_capture is False and args.test is False:
        parser.print_help()
        exit()

    print()
    print('---------- TotK Speedometer ----------')
    print()

    if args.files is not None:
        for f in args.files:
            if os.path.isfile(f):
                export_video_with_overlay(f)

    elif args.screen_capture:
        if args.cache and os.path.isfile(settings.map_position_cache_filename):
            map_position_cache = json.load(open(settings.map_position_cache_filename))
            monitor_region = map_position_cache['monitor_region']
            monitor_scaling = map_position_cache['monitor_scaling']
            map_circle = map_position_cache['map_circle']
            print('Using cached map position.')
            print()
            print('Map region',
                    ' width:', monitor_region['width'],
                    ' height:', monitor_region['height'],
                    ' top:', monitor_region['top'],
                    ' left:', monitor_region['left']
                )
            print('Map center: [', map_circle[0], ',', map_circle[1], ']  Map radius:', map_circle[2])
            print()
        else:
            map_circle, monitor_region, monitor_scaling = detect_map(args.monitor)
        app = QtWidgets.QApplication(sys.argv)
        mainwindow = SpeedometerOverlay(monitor_region['left'], monitor_region['top'], monitor_region['width'])
        mainwindow.show()
        runnable = SpeedometerRunnable(mainwindow, monitor_region, monitor_scaling, map_circle)
        mainwindow.set_runnable(runnable)
        QThreadPool.globalInstance().start(runnable)
        sys.exit(app.exec())

    elif args.test:
        map_img = cv2.imread('images/map.png')
        width = 1280
        height = 720
        map_circle = [int(width*0.06875), int(height*0.1223), int(width*0.0641)]
        coord_img = get_coord_img(map_img, map_circle, 16)
        processed_img = preprocess_coord_img(coord_img)
        ret, coord = extract_coordinates(processed_img)
        print(coord)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(0)
