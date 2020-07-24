from collections import Counter, defaultdict

import cv2
import numpy as np
import os
from random import sample, seed

'''
What does this class do?
1. loads video input in avi form from stereo camera
2. splits the video in 2 and pseudo-randomly samples frames between start_time and end_time.
   You can change the factor by which the sampling is fixed to prevent consecutive sampling in
   the gen_sample method.
3. sampled frames are outputted to [your project dir]/calibration_images with the naming convention; camera-[cam number]-[frame number].jpg


note1: filenames from camera may contain brackets and other characters, failing to handle for
       this will cause the load_vid method to throw an OSErr
note2: if you want to use >99 calibration images (num_cal_imgs > 99), please change zfill(2)-> zfill(3)
       in the load_vid method. I don't know if DeepLabCut can handle for this.
note3: there must be at least num_cal_imgs*3 frames within (end_time - start_time) or
       gen_sample will throw, that is a bare minimum though and should not be used

note4: make sure the lines at the bottom that instantiate this class and run its method are not commented out

params:
vid_name = r'2020-07-21_(09-02-58)_00782B1B4A02_16_2022.avi'
project_name = 'stereo_cam_test1-silasi_lab-2020-07-21-3d'
start_time = 6
end_time = 13

TODO:
'''

project_name = 'stereo_cam_test1-silasi_lab-2020-07-21-3d'
vid_name = r'2020-07-23_(11-45-24)_00783A32F484_16_2015.avi'
start_time = 11
end_time = 29


params:
vid_path = r'/home/gavin/Documents/python_projects/DLC/DeepLabCut/deeplabcut/projects/stereo_cam_test1-silasi_lab-2020-07-21-3d/2020-07-21_(09-02-58)_00782B1B4A02_16_2022.avi'
project_path = '/home/gavin/Documents/python_projects/DLC/DeepLabCut/deeplabcut/projects/stereo_cam_test1-silasi_lab-2020-07-21-3d'
start_time = 6
end_time = 13

TODO: use os.sep, needs to be added for Windows compatibility
'''

vid_path = r'/home/gavin/Documents/python_projects/DLC/DeepLabCut/deeplabcut/projects/stereo_cam_test1-silasi_lab-2020-07-21-3d/2020-07-21_(09-02-58)_00782B1B4A02_16_2022.avi'
project_path = '/home/gavin/Documents/python_projects/DLC/DeepLabCut/deeplabcut/projects/stereo_cam_test1-silasi_lab-2020-07-21-3d'
start_time = 6
end_time = 13


seed(2020)


class VidLoader:
    def __init__(self, project_name, vid_name, start_time, end_time, num_cal_imgs=300):
        self.project_name = project_name
        self.vid_name = vid_name

    def __init__(self, project_path, vid_path, start_time, end_time, num_cal_imgs=70):
        self.project_path = project_path
        self.vid_path = vid_path

        self.start_time = start_time
        self.end_time = end_time
        self.num_cal_imgs = num_cal_imgs

    # Divided sample interval by 3 so sampled frames have at least a small degree of randomness to them
    # but also aren't consecutive frames... This could be a bad idea but idk
    def gen_sample(self, fps):
        sample_range = (int(fps*self.start_time), int(fps*self.end_time))
        sample_interval = (sample_range[1] - sample_range[0]) // int((self.num_cal_imgs*3))
        return set(sample(range(sample_range[0]+1, sample_range[1]+2, sample_interval), k=self.num_cal_imgs)) # +1 and +2 cause frame indices start on 1

    def load_vid(self):
        # Playing video from file:

        cap = cv2.VideoCapture(os.getcwd() + os.sep + self.project_name + os.sep + self.vid_name)

        cap = cv2.VideoCapture(self.vid_path)

        # get height and width from opencv and print to console
        if cap.isOpened():
            w = cap.get(3) # 3 = cv2.CAP_PROP_FRAME_WIDTH
            h = cap.get(4) # 4 = cv2.CAP_PROP_FRAME_HEIGHT
            fps = cap.get(5) # 5 is FPS and returned 60 (correct)... but 7 is frame count and returned 1206fps for some reason
            print('video height and width: {}, {}'.format(h, w))

        sample_frames = self.gen_sample(fps)

        # output jpgs will be stored in [your project dir]/calibration_images
        try:
            if not os.path.exists(os.getcwd() + os.sep + self.project_name + os.sep + 'calibration_images'):
                os.makedirs(os.getcwd() + os.sep + self.project_name + os.sep + 'calibration_images')
            if not os.path.exists(self.project_path + '/calibration_images'):
                os.makedirs(self.project_path + '/calibration_images')
        except OSError:
            print ('Error: Creating directory of data')

        current_frame = 1
        sample_frame_cnt = 1
        while(True):
            # Capture frame-by-frame
            ret, frame = cap.read()

            # this logic limits cap to fps from video input, aka output will not have unecessarily high fps
            if not ret:
                break

            # h, w = frame.shape[:2]

            # # pixel coords of left cam
            # start_row, start_col = int(0), int(0)
            # end_row, end_col = int(h), int(w * .5)
            # cropped_left = frame[start_row:end_row , start_col:end_col]

            # # pixel coords of right cam
            # start_row, start_col = int(0), int(w * .5)
            # end_row, end_col = int(h), int(w)
            # cropped_right = frame[start_row:end_row , start_col:end_col]

            ###################### cropping inner ~1/3 of each 1/2 of the combined frames
            # pixel coords of left cam
            start_row, start_col = int(h//2 - h//5.5), int(w//2 - w//5.5)

            # pixel coords of left cam
            start_row, start_col = int(0), int(0)

            end_row, end_col = int(h), int(w * .5)
            cropped_left = frame[start_row:end_row , start_col:end_col]

            # pixel coords of right cam

            start_row, start_col = int(h//2 - h//5.5), int(w * .5)
            end_row, end_col = int(h), int(w//2 + w//5.5)

            start_row, start_col = int(0), int(w * .5)
            end_row, end_col = int(h), int(w)

            cropped_right = frame[start_row:end_row , start_col:end_col]

            # Saves image of the current frame in jpg file if frame # is in the sample

            if current_frame in sample_frames:

                name1 = os.getcwd() + os.sep + self.project_name + os.sep + 'calibration_images' + os.sep + 'camera-1-' + str(sample_frame_cnt).zfill(3) + '.jpg'
                cv2.imwrite(name1, cropped_left)

                name2 = os.getcwd() + os.sep + self.project_name + os.sep + 'calibration_images' + os.sep + 'camera-2-' + str(sample_frame_cnt).zfill(3) + '.jpg'

                name1 = self.project_path + '/calibration_images/' + 'camera-1-' + str(sample_frame_cnt).zfill(2) + '.jpg'
                cv2.imwrite(name1, cropped_left)

                name2 = self.project_path + '/calibration_images/' + 'camera-2-' + str(sample_frame_cnt).zfill(2) + '.jpg'

                cv2.imwrite(name2, cropped_right)
                sample_frame_cnt += 1


            # # print sth encouraging to console
            # if current_frame % 10 == 0 and current_frame != 0:
            #     print(str(current_frame / 70) + r'% done...')

            # To stop duplicate images
            current_frame += 1

        # When everything done, release the capture
        cap.release()
        cv2.destroyAllWindows()


'''
What does this class do?
1. Counts all the images in the ./[project_name]/corners dir
2. Deletes any images that don't have a pair image (i.e. deeplabcut.calibrate_cameras/opencv
   corresponding method was only able to find corners on the image from 1 of the lenses)

note1: the delete_frames method must be called after the deeplabcut.calibrate_cameras/corresponding
       opencv method has been called
note2: make sure that the lines at the bottom to instantiate this class and call its method arent commmented out
note3: (IMPORTANT) make sure you go over the images after deleting the singles to delete the
       incorrectly labeled corners (and their pairs)

'''


class del_single_frames:
    def __init__(self, project_name):
        self.project_name = project_name
        self.corners = os.getcwd() + os.sep + project_name + os.sep + 'corners'
        self.singles = []
        self.frame_nums = []
        self.d = defaultdict(list)

    def del_corner_singles(self):
        for f in os.listdir(self.corners):
            self.frame_nums.append(f[9:12])
            self.d[f[9:12]].append(f[7])

        c = Counter(self.frame_nums)

        # add frame number of frames that are single to list
        for k, v in c.items():
            if v == 1:
                self.singles.append(k)

        # delete all frames from corners dir that are in the singles list
        for s in self.singles:
            file2remove = self.corners + os.sep + 'camera-' + str(self.d[s][0]) + '-' + s + '_corner.jpg'
            print('deleted: {}'.format(file2remove))
            os.remove(file2remove)
        
        return

    def del_no_corner_images(self):
        cornered_image_names = set()
        del_cnt = 0

        for f in os.listdir(self.corners):
            f = f.replace('_corner', '')
            cornered_image_names.add(f)
            print(f)

        for f in os.listdir(self.project_name + os.sep + 'calibration_images'):
            if f not in cornered_image_names:
                os.remove(self.project_name + os.sep + 'calibration_images' + os.sep + f)
                del_cnt += 1
        
        print('deleted {} images from ./[project_name]/calibration_images'.format(del_cnt))

        return

dsf = del_single_frames(project_name)
dsf.del_corner_singles()
dsf.del_no_corner_images()

# v = VidLoader(project_name, vid_name, start_time, end_time)
# v.load_vid()

v = VidLoader(project_path, vid_path, start_time, end_time)
v.load_vid()
