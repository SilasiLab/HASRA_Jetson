"""
    Author: Junzheng Wu, Gavin Heidenreich
    Email: jwu220@uottawa.ca, gheidenr@uottawa.ca
    Organization: University of Ottawa (Silasi Lab)

    To increase FPS, the whole stream is divided into two parallel threads.
    And then those two threads are organized to run as a subprocess in the main.py script
    1. Sample frames from camera.
    2. Save frames into a video file.
"""
import datetime
from threading import Thread
import cv2
import time
import inspect
import ctypes
import argparse
import platform
import pickle
import os
import sys


DETECT_FLAG = False

class FPS_camera:
    def __init__(self):
        self._start = None
        self._end = None
        self._numFrames = 0

    def start(self):
        # start the timer
        self._start = datetime.datetime.now()
        return self

    def stop(self):
        # stop the timer
        self._end = datetime.datetime.now()

    def update(self):
        # increment the total number of frames examined during the
        # start and end intervals
        self._numFrames += 1

    def elapsed(self):
        # return the total number of seconds between the start and
        # end interval
        return (self._end - self._start).total_seconds()

    def fps(self):
        # compute the (approximate) frames per second
        return self._numFrames / self.elapsed()


class WebcamVideoStream:
    def __init__(self, src=0, width=640, height=360):
    # def __init__(self, src=0, width=640, height=240):

        # If you are under windows system using Dshow as backend
        if platform.system() == 'Windows':
            self.stream = cv2.VideoCapture(src, cv2.CAP_DSHOW)
            print(self.stream.isOpened())
            self.width = width
            self.height = height
            ret1 = self.stream.set(cv2.CAP_PROP_FRAME_WIDTH, 640) #640
            ret2 = self.stream.set(cv2.CAP_PROP_FRAME_HEIGHT, 360) # 360
            ret3 = self.stream.set(cv2.CAP_PROP_AUTO_EXPOSURE, 5) # was 0.25
            ret4 = self.stream.set(cv2.CAP_PROP_EXPOSURE, -7) # -5 == 2**-5 == 1/32 seconds

        # If not go next line
        else:
            # run v4l2-ctl -d /dev/video0 --list-ctrls to see list of available settings and argument ranges
            self.stream = cv2.VideoCapture(self.gstreamer_pipeline(),  cv2.CAP_GSTREAMER)
            print(self.stream.isOpened())

        (self.grabbed, self.frame) = self.stream.read()
        self.thread = None
        # initialize the variable used to indicate if the thread should
        # be stopped
        self.stopped = False
        self.flag = False
        self.FPS = FPS_camera()

    def gstreamer_pipeline(self,
            sensor_id=0,
            sensor_mode=4,
            capture_width=1280,
            capture_height=720,
            display_width=640,
            display_height=360,
            framerate=60,
            flip_method=0,
    ):
        return (
                "nvarguscamerasrc sensor-id=%d sensor-mode=%d ! "
                "video/x-raw(memory:NVMM), "
                "width=(int)%d, height=(int)%d, "
                "format=(string)NV12, framerate=(fraction)%d/1 ! "
                "nvvidconv flip-method=%d ! "
                "video/x-raw, width=(int)%d, height=(int)%d, format=(string)BGRx ! "
                "videoconvert ! "
                "video/x-raw, format=(string)BGR ! appsink"
                % (
                    sensor_id,
                    sensor_mode,
                    capture_width,
                    capture_height,
                    framerate,
                    flip_method,
                    display_width,
                    display_height,
                )
        )

    def start(self):
        # start the thread to read frames from the video stream

        self.thread = Thread(target=self.update, args=())
        self.thread.start()
        self.FPS = self.FPS.start()
        return self

    def update(self):

        # keep looping infinitely until the thread is stopped
        while True:
            # if the thread indicator variable is set, stop the thread
            if self.stopped:
                break
            self.grabbed, self.frame = self.stream.read()
            if self.grabbed:
                # got a frame
                self.FPS.update()
            else:
                # no frame
                pass

        self.stream.release()
        self.flag = True

    def read(self):
        # return the frame most recently read
        return self.frame

    def stop(self):
        # indicate that the thread should be stopped
        self.stopped = True
        self.FPS.stop()
        print("[INFO] elasped time: {:.2f}".format(self.FPS.elapsed()))
        print("[INFO] approx. FPS: {:.2f}".format(self.FPS.fps()))
        while not self.flag:
            continue
        if self.thread.is_alive():
            _async_raise(self.thread.ident, SystemExit)


class Recoder():
    def __init__(self, savePath='test.avi', show=False, vs=None):
        self.width = 640
        self.height = 360
        self.fourcc = cv2.VideoWriter_fourcc(*'MJPG')
        self.fps = 60
        self.writer = cv2.VideoWriter(savePath, self.fourcc, self.fps, (640, 360), False)
        self.stopped = False
        self.FPS = FPS_camera()
        self.vs = vs
        self.thread = None
        self.show = show
        self.flag = False
        self.process = None

    def recording(self):
        self.FPS = self.FPS.start()
        time_str = str(time.time())
        start_time = datetime.datetime.now()
        global DETECT_FLAG

        h = 480
        w = 1280
        cnt = 0
        prevTime = 0
        while True:
            time_iter_start = datetime.datetime.now()
            if self.stopped:
                break

            curTime = time.time() #
            sec = curTime - prevTime #
            prevTime = curTime #

            fps = 1/(sec) #

            msg = "FPS : %0.1f" % fps #

            frame = self.vs.read()	
            cnt += 1
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            if not self.show:
                self.writer.write(gray)
            if DETECT_FLAG or cnt % 30 == 0:
                cv2.imwrite("detection_frame.jpg", gray)
                DETECT_FLAG = False
            self.FPS.update()

            if self.show:
                cv2.imshow(time_str, gray)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    cv2.destroyAllWindows()
                    break
            time_iter_end = datetime.datetime.now()
            iteration = float((time_iter_end - time_iter_start).microseconds) * 1e-6
            time.sleep(max((1.0 / self.fps - iteration), 0))

        self.writer.release()
        self.vs.stream.release()
        cv2.waitKey(1)
        cv2.destroyAllWindows()
        cv2.waitKey(1)

        self.flag = True

    def start(self):
        self.thread = Thread(target=self.recording, args=())
        self.thread.start()
        return self

    def stop(self):
        self.FPS.stop()
        print("[INFO] elasped time: {:.2f}".format(self.FPS.elapsed()))
        print("[INFO] approx. FPS: {:.2f}".format(self.FPS.fps()))
        self.stopped = True

        while not self.flag:
            continue
        if self.thread.is_alive():
            _async_raise(self.thread.ident, SystemExit)


def _async_raise(tid, exctype):
    '''Raises an exception in the threads with id tid'''
    if not inspect.isclass(exctype):
        raise TypeError("Only types can be raised (not instances)")
    res = ctypes.pythonapi.PyThreadState_SetAsyncExc(ctypes.c_long(tid),
                                                     ctypes.py_object(exctype))
    if res == 0:
        raise ValueError("invalid thread id")
    elif res != 1:
        # "if it returns a number greater than one, you're in trouble,
        # and you should call it again with exc=NULL to revert the effect"
        ctypes.pythonapi.PyThreadState_SetAsyncExc(ctypes.c_long(tid), None)
        raise SystemError("PyThreadState_SetAsyncExc failed")

def record_main(camera_src, video_path, show=False):
    print("[INFO] sampling THREADED frames from webcam...")
    vs = WebcamVideoStream(src=camera_src).start()
    r = Recoder(savePath=video_path, vs=vs, show=show).start()

    while True:

        signal = input()
        if signal == "stop":
            vs.stop()
            r.stop()
            break
        else:
            global DETECT_FLAG
            DETECT_FLAG = True

if __name__ == '__main__':
    DEBUG = False
    print(sys.version_info)

    if not DEBUG:
        parser = argparse.ArgumentParser()
        parser.add_argument('--c', help='an integer for the camer index', dest='camera_index')
        parser.add_argument('--p', help='a string', dest='video_path')
        parser.add_argument('--t', help='test', dest='test', default='False')
        args = parser.parse_args()
        camera_index = args.camera_index
        video_path = args.video_path
        test = args.test
        if test == "True":
            # record_main(int(camera_index), video_path, show=True)
            record_main('/dev/video0', video_path, show=True)

        else:
            record_main('/dev/video0', video_path, show=False)
            # record_main(int(camera_index), video_path, show=False)


    else:
        # record_main(0, '1.avi', show=True)
        record_main('/dev/video0', '1.avi', show=False)

