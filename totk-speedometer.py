
import os
import sys
import time

import cv2
import numpy as np
import pytesseract
from moviepy.editor import *
from mss import mss
import mss.tools
from PyQt6 import QtWidgets
from PyQt6.QtGui import QScreen
from PyQt6.QtCore import QRunnable, QThreadPool

from overlay import SpeedometerOverlay
import settings

# Lists to keep historical values
speed_list = []
speed_h_list = []
speed_v_list = []


def detect_circle(map_image, width, height):
    img = cv2.cvtColor(map_image,cv2.COLOR_BGR2GRAY)

    circles = cv2.HoughCircles(img, cv2.HOUGH_GRADIENT, 1, (height*0.2),
                            param1=80,
                            param2=60,
                            minRadius=int(height*0.07),
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



def extract_coordinates(map_img, map_circle):
    map_img = cv2.cvtColor(map_img,cv2.COLOR_BGR2GRAY)

    scaling = 16

    polar_image = cv2.warpPolar(map_img, dsize=(
                                        map_img.shape[1]*scaling,
                                        map_img.shape[0]*scaling),
                                        center=(map_circle[0],map_circle[1]
                                    ),
                                    maxRadius=map_circle[2],
                                    flags=cv2.WARP_POLAR_LOG | cv2.INTER_LANCZOS4 )

    polar_image = cv2.rotate(polar_image, cv2.ROTATE_90_CLOCKWISE)
    # cv2.imwrite('images/polar_map.png', polar_image)

    # Cropping an image
    cropped_img = polar_image[int(polar_image.shape[0]*0.95):, int(polar_image.shape[1]*0.58):int(polar_image.shape[1]*0.92)]
    # cv2.imwrite('images/cropped_img.png', cropped_img)

    blur_img = cv2.GaussianBlur(cropped_img,(5,5),0)
    # cv2.imwrite('images/blur_img.png', blur_img)

    contrast_img = cv2.convertScaleAbs(blur_img, alpha=3, beta=-250)
    # cv2.imwrite('images/contrast_img.png', contrast_img)

    ret3,threshold_img = cv2.threshold(blur_img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    # cv2.imwrite('images/threshold_img.png', threshold_img)

    kernel = np.ones((3,3), np.uint8)
    erode_img = cv2.erode(threshold_img, kernel, iterations=1)
    # cv2.imwrite('images/erode_img.png', erode_img)
    dilate_img = cv2.dilate(erode_img, kernel, iterations=2)
    # cv2.imwrite('images/dilate_img.png', dilate_img)
    processed_img = cv2.erode(dilate_img, kernel, iterations=1)
    # cv2.imwrite('images/processed_img.png', processed_img)

    text = pytesseract.image_to_string(processed_img, config='--psm 7 -c tessedit_char_whitelist=" -0123456789"')
    try:
        if isinstance(text, str) and text != '':
            coord = [int(c) for c in text.strip().split(' ')]
            if not (4000 > coord[0] > -4000 and 5000 > coord[1] > -4000 and 3400 > coord[2] > -3000):
                coord = None
        else:
            coord = None
    except:
        coord = None

    return coord



def process_coordinates(coord, last_coord, time_delta):
    if len(coord)==3 and len(last_coord)==3 and all(isinstance(val, int) for val in coord+last_coord):
        distance = np.sqrt((coord[0]-last_coord[0])**2 + (coord[1]-last_coord[1])**2 + (coord[2]-last_coord[2])**2)
        distance_h = np.sqrt((coord[0]-last_coord[0])**2 + (coord[1]-last_coord[1])**2)
        distance_v = np.sqrt((coord[2]-last_coord[2])**2)

        speed = distance/time_delta
        if speed >= 100:
            speed = float('nan')
        else:
            speed_list.append(speed)
            if len(speed_list) > settings.avg_every_x_meas:
                speed_list.pop(0)

        speed_h = distance_h/time_delta
        if speed_h >= 100:
            speed_h = float('nan')
        else:
            speed_h_list.append(speed_h)
            if len(speed_h_list) > settings.avg_every_x_meas:
                speed_h_list.pop(0)

        speed_v = distance_v/time_delta
        if speed_v >= 100:
            speed_v = float('nan')
        else:
            speed_v_list.append(speed_v)
            if len(speed_v_list) > settings.avg_every_x_meas:
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

        results = {
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

        return results



def export_video_with_overlay(video_path):
    print('Processing video: ' + video_path)

    video = cv2.VideoCapture(video_path)
    width  = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = int(video.get(cv2.CAP_PROP_FPS))
    h = int(video.get(cv2.CAP_PROP_FOURCC))
    codec = chr(h&0xff) + chr((h>>8)&0xff) + chr((h>>16)&0xff) + chr((h>>24)&0xff)

    print(f'Video - Width: {width}, Height: {height}, FPS: {fps}, Enconding: {codec}')

    path = os.path.dirname(video_path)
    filename = os.path.basename(video_path)
    name = os.path.splitext(filename)[0]
    ext = os.path.splitext(filename)[1]
    os.makedirs(os.path.join(path, settings.output_directory), exist_ok=True)
    tmp_filename = os.path.join(path, settings.output_directory, name+'_speedometer_tmp'+ext)
    output_filename = os.path.join(path, settings.output_directory, name+'_speedometer'+ext)
    video_output = cv2.VideoWriter(tmp_filename, cv2.VideoWriter_fourcc(*'avc1'), fps, (width, height))

    count = 0
    map_circle = None
    last_coord = None

    while video.isOpened():
        ret,frame = video.read()
        if ret:
            map_image = frame[int(height*0.71):int(height*0.96), int(width*0.829):int(width*0.97)]
            # cv2.imwrite('images/map.png', map_image)

            map_circle = [int(width*0.06875), int(height*0.1223), int(width*0.0641)]

            if count > settings.calc_every_x_frames:
                coord = extract_coordinates(map_image, map_circle)
                if coord is not None:
                    if last_coord is None:
                        last_coord = coord
                        count = 0
                    else:
                        tmp_results = process_coordinates(coord, last_coord, (1/fps)*count)
                        if tmp_results is not None:
                            print(f'Coord: {[f"{c:5}" for c in coord]}'
                            f' - Last Coord {[f"{c:5}" for c in last_coord]}'
                            f' - Distance: {tmp_results["distance"]["Distance"]:6.2f} m'
                            f' - Speed: {tmp_results["total"]["Speed"]:5.2f} m/s'
                            f' - AvgSpeed: {tmp_results["total"]["Avg"]:5.2f} m/s'
                            f' - Speed H: {tmp_results["horizontal"]["Speed"]:5.2f} m/s'
                            f' - Speed V: {tmp_results["vertical"]["Speed"]:5.2f} m/s')

                            last_coord = coord
                            count = 0

                            if not any(np.isnan(b) for v in tmp_results.values() for b in v.values()):
                                results = tmp_results
                                text_color = (255, 255, 255)
                            else:
                                text_color = (210, 210, 210) # gray out text when the coordinates are not valid

            count = count + 1

            if 'results' in locals() and results is not None:
                text_w_start = int(width*0.842)
                text_h_start = int(height*0.20)
                overlay_w_start = int(width*0.836)
                overlay_w_end = int(width*0.961)
                overlay_h_start = int(height*0.16)
                overlay_h_end = int(height*0.694)
                spacing = int(height/25)
                text_size = height/1500

                alpha = 0.25
                overlay = frame.copy()
                cv2.rectangle(overlay, (overlay_w_start, overlay_h_start), (overlay_w_end, overlay_h_end), (0,0,0), cv2.FILLED)
                cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)

                text_h = text_h_start
                frame = cv2.putText(frame, 'Total', (text_w_start, text_h), cv2.FONT_HERSHEY_TRIPLEX, text_size, text_color, 1, cv2.LINE_AA)
                for key,value in results['total'].items():
                    text_h = text_h + spacing
                    text = f'{key}: {value:.2f} m/s'
                    frame = cv2.putText(frame, text, (text_w_start, text_h), cv2.FONT_HERSHEY_SIMPLEX, text_size, text_color, 1, cv2.LINE_AA)

                text_h = int(text_h + (1.5*spacing))
                frame = cv2.putText(frame, 'Horizontal', (text_w_start, text_h), cv2.FONT_HERSHEY_TRIPLEX, text_size, text_color, 1, cv2.LINE_AA)
                for key,value in results['horizontal'].items():
                    text_h = text_h + spacing
                    text = f'{key}: {value:.2f} m/s'
                    frame = cv2.putText(frame, text, (text_w_start, text_h), cv2.FONT_HERSHEY_SIMPLEX, text_size, text_color, 1, cv2.LINE_AA)

                text_h = int(text_h + (1.5*spacing))
                frame = cv2.putText(frame, 'Vertical', (text_w_start, text_h), cv2.FONT_HERSHEY_TRIPLEX, text_size, text_color, 1, cv2.LINE_AA)
                for key,value in results['vertical'].items():
                    text_h = text_h + spacing
                    text = f'{key}: {value:.2f} m/s'
                    frame = cv2.putText(frame, text, (text_w_start, text_h), cv2.FONT_HERSHEY_SIMPLEX, text_size, text_color, 1, cv2.LINE_AA)

            video_output.write(frame)

            # # Uncomment these lines to see a live preview of the video with the speedometer stats
            # cv2.imshow('TotK Speedometer', frame)
            # # Hold 'q' key to quit
            # if cv2.waitKey(1) & 0xFF == ord('q'):
            #     return
        else:
            break

    video.release()
    video_output.release()
    cv2.destroyAllWindows()

    # Add audio from original video
    orig_clip = VideoFileClip(video_path)
    orig_audioclip = orig_clip.audio
    clip = VideoFileClip(tmp_filename)
    clip_with_audio = clip.set_audio(orig_audioclip)
    clip_with_audio.write_videofile(output_filename, audio_codec='aac')
    orig_clip.close()
    clip.close()

    # Remove temporary video file
    os.remove(tmp_filename)


def detect_map(monitor_number):
    with mss.mss() as sct:
        mon = sct.monitors[monitor_number]

        monitor = {
                'top': mon['top'],
                'left': mon['left'],
                'width': mon['width'],
                'height': mon['height'],
                'mon': monitor_number,
            }

        print('Trying to detect map position...')

        while True:
            sct_img = sct.grab(monitor)
            img = np.array(sct_img)
            # cv2.imwrite('images/screenshot.png', img)

            h, w, c = img.shape
            if mon['width']*2 == w:
                scaling = 2
            else:
                scaling = 1

            circles, circles_img = detect_circle(img, w, h)
            if circles_img is not None:
                cv2.imwrite('images/detected-circles.png', circles_img)

            if circles is not None:
                if len(circles[0])==1:
                    map_circle = circles[0][0]

                    # Capture only the screen part the map occupies
                    monitor_region = {
                        'top': mon['top']+(map_circle[1]-map_circle[2])/scaling - 20,
                        'left': mon['left']+(map_circle[0]-map_circle[2])/scaling - 20,
                        'width': ((map_circle[2]*2)/scaling) + 40,
                        'height': ((map_circle[2]*2)/scaling) + 40,
                        'mon': monitor_number,
                    }

                    sct_img = sct.grab(monitor_region)
                    img = np.array(sct_img)
                    cv2.imwrite('images/map.png', img)

                    circles, circles_img = detect_circle(img, w, h)
                    if circles_img is not None:
                        cv2.imwrite('images/detected-map-circles.png', circles_img)

                    if circles is not None:
                        if len(circles[0])==1:
                            map_circle = circles[0][0]
                            coord = extract_coordinates(img, map_circle)
                            if coord is not None:
                                tmp_results = process_coordinates(coord, coord, 1)
                                if tmp_results is not None:
                                    print('\rMap position detected.                                         ')
                                    return map_circle, monitor_region
                        else:
                            print('\rCould not detect map circle. Too many circles were found.      ', end='')
                    else:
                        print('\rMap circle could not be found.                                 ', end='')
                else:
                    print('\rCould not detect map position. Too many positions were found.  ', end='')
            else:
                print('\rMap position could not be detected.                            ', end='')



class SpeedometerRunnable(QRunnable):
    def __init__(self, mainwindow, monitor_sct, map_circle):
        super().__init__()
        self.mainwindow = mainwindow
        self.monitor_sct = monitor_sct
        self.map_circle = map_circle
        self.running = True

    def stop(self):
        self.running = False

    def run(self):
        last_coord = None
        last_coord_time = None

        with mss.mss() as sct:
            while self.running:
                # Grab the map screenshot
                sct_img = sct.grab(self.monitor_sct)

                # Save the map screenshot
                mss.tools.to_png(sct_img.rgb, sct_img.size, output='images/map.png')

                # Get raw pixels from the screen, save it to a Numpy array
                img = np.array(sct_img)

                coord = extract_coordinates(img, self.map_circle)
                if coord is not None:
                    if last_coord is None:
                        last_coord = coord
                        last_coord_time = time.time()
                    else:
                        t = time.time()
                        results = process_coordinates(coord, last_coord, t-last_coord_time)

                        if results is not None:
                            print(f'Coord: {[f"{c:5}" for c in coord]}'
                            f' - Last Coord {[f"{c:5}" for c in last_coord]}'
                            f' - Distance: {results["distance"]["Distance"]:6.2f} m'
                            f' - Speed: {results["total"]["Speed"]:5.2f} m/s'
                            f' - AvgSpeed: {results["total"]["Avg"]:5.2f} m/s'
                            f' - Speed H: {results["horizontal"]["Speed"]:5.2f} m/s'
                            f' - Speed V: {results["vertical"]["Speed"]:5.2f} m/s')

                            last_coord_time = t
                            last_coord = coord

                            if not any(np.isnan(b) for v in results.values() for b in v.values()):
                                self.mainwindow.update_labels(results)
                                time.sleep(0.01)



def main():
    import argparse

    parser = argparse.ArgumentParser(description='Speedometer for Zelda TotK')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-f', dest='files', metavar='file', type=str, nargs='+', help='path to video file. Accepts multiple files')
    group.add_argument('-s', '--screen', dest='screen', action='store_true', help='use screen capture and overlay stats')
    parser.add_argument('-m', dest='monitor', default=1, type=int, help='monitor number to capture and display the overlay.')
    args = parser.parse_args()

    parser.add_argument('file', type=argparse.FileType('r'), nargs='+')

    if args.files is None and args.screen is None:
        parser.print_help()
        exit()

    if args.files is not None:
        for f in args.files:
            export_video_with_overlay(f)
    elif args.screen is not None:
        map_circle, monitor_sct = detect_map(args.monitor)
        app = QtWidgets.QApplication(sys.argv)
        mainwindow = SpeedometerOverlay()
        monitors = QScreen.virtualSiblings(mainwindow.screen())
        monitor = monitors[args.monitor-1].availableGeometry()
        mainwindow.move(monitor.left() + settings.overlay_horizontal_pos, monitor.top() + settings.overlay_vertical_pos)
        mainwindow.show()
        runnable = SpeedometerRunnable(mainwindow, monitor_sct, map_circle)
        QThreadPool.globalInstance().start(runnable)
        sys.exit(app.exec())


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(0)
