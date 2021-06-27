import tensorflow as tf
import cv2
import numpy as np
import os
import argparse

parser = argparse.ArgumentParser(description='Miles Deep program for filtering 18+ content')
parser.add_argument('-vp','--video_path', help='Input video path', required=True)
parser.add_argument('-ovp','--outvideo_path', help='output video path', default='output.mp4')
parser.add_argument('-c','--ctg_in', help="Categories you want to save,categories:['blowjob_handjob', 'cunnilingus', 'other', 'sex_back', 'sex_front', 'titfuck'], if you want to use multiple then add with comma like sex_back,sex_front", default='other')
parser.add_argument('-x','--sexual', help="This edits out all the non-sexual scenes from input video", action='store_true')
parser.add_argument('-ss','--skip_s', help='Skip seconds to remove the small flickering in categories if appear do to false classification, (default:3)',type=int, default=3)
parsed = parser.parse_args()

def process(img):
	img = cv2.resize(img, (224, 224))
	img = img.astype("float32")
	img -= mean_image
	return img

def ranges(nums):
    nums = sorted(set(nums))
    gaps = [[s, e] for s, e in zip(nums, nums[1:]) if s+1 < e]
    edges = iter(nums[:1] + sum(gaps, []) + nums[-1:])
    return list(zip(edges, edges))

def video_to_img(video_name):
    print('Video Loading Started...')
    x = []
    vidcap = cv2.VideoCapture(video_name)
    fps = vidcap.get(cv2.CAP_PROP_FPS)
    total_number_of_frames=vidcap.get(cv2.CAP_PROP_FRAME_COUNT)
    success,image = vidcap.read()
    count = 0
    success=True
    while success:
        success,image = vidcap.read()
        if success:
            x.append(process(image))
            success,image = vidcap.read()
            if count%100==0:
                print('Process No. of frames:',count*2)
            count += 1
        else:
            break
    Frame_reading_fps=fps/(total_number_of_frames/len(x))
    return np.array(x),Frame_reading_fps

categories = {'0':"blowjob_handjob", '1':"cunnilingus", '2':"other", '3':"sex_back", '4':"sex_front", '5':"titfuck"}

print("Loading model")
mean_image = np.load("model/mean.npy")
model = tf.keras.models.load_model('model/weights.h5')
x,Frame_reading_fps=video_to_img(parsed.video_path)

print("Model Prediction Started...")
preds = model.predict(x)
y = preds.argmax(axis=-1)
ystr=y.astype(str)

for i in range(len(categories)):
    ystr[ystr==str(i)]=categories[str(i)]
for g in parsed.ctg_in.split(','):
    if g not in categories.values():
        print('"'+g +'" category not exists in ',categories.values())

if parsed.sexual:
    data = np.where(ystr!='other')[0]
else:
    data=np.hstack([np.where(ystr==cate)[0] for cate in parsed.ctg_in.split(',')])

if len(data)==0:
    print('Not found this category in video')
else:
    data1 = ranges(np.unique(data/Frame_reading_fps).astype(int))
    data1=np.array(data1)
    Croped_save_points=data1[np.where((data1[:,1]-data1[:,0])>parsed.skip_s)[0]]
    crop_time='+'.join(["between(t,"+str(st1)+","+str(st2)+")" for st1,st2 in Croped_save_points])
    vidp="select='"+crop_time+"',setpts=N/FRAME_RATE/TB"
    audp="aselect='"+crop_time+"',asetpts=N/SR/TB"
    os.system("ffmpeg -i {} -vf {} -af {} -y {}".format(parsed.video_path,vidp,audp,parsed.outvideo_path))