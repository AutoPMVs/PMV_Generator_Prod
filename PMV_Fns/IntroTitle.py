from os import listdir
import subprocess
from os.path import isfile, join
from moviepy.audio.io.AudioFileClip import AudioFileClip
from moviepy.editor import concatenate_videoclips
from moviepy.video.VideoClip import TextClip
from moviepy.video.io.VideoFileClip import VideoFileClip
import moviepy.editor as mpe
from pydub import AudioSegment
from moviepy.video.fx.fadein import fadein
from moviepy.video.fx.fadeout import fadeout


AudioSegment.converter = r"C:/ffmpeg/bin/ffmpeg.exe"
AudioSegment.ffmpeg = r"C:/ffmpeg/bin/ffmpeg.exe"
AudioSegment.ffprobe = r"C:/ffmpeg/bin/ffprobe.exe"

def getIntroVid(vidTitle, origCropFrac, sampleHeight, introVidDir, userName):
    titleParts = [vidTitle,
                  " ",
                  "by \n " + userName]
    times = [[0, 3],
             [3, 9],
             [9, 14]]
    sizes = [50,
             30,
             80]

    introVid = VideoFileClip(introVidDir)
    (w, h) = introVid.size

    introVid = introVid.crop(height=int(round((1 - origCropFrac*2) * sampleHeight, 0)), width = w, x_center=w/2, y_center=h/2)
    clips=[]
    iPart=0
    while iPart < len(titleParts):
        title=titleParts[iPart]
        if times[iPart][1]>introVid.duration:
            times[iPart][1] = introVid.duration
        vidClip = introVid.subclip(times[iPart][0], times[iPart][1])
        text = TextClip(title, font="Amiri-Bold", fontsize=sizes[iPart], color="white", align = 'center').set_position(("center",0.3), relative=True)
        text_clip = mpe.CompositeVideoClip([vidClip, text]).set_duration(vidClip.duration)
        clips.append(text_clip)
        iPart = iPart + 1

    final_clip = concatenate_videoclips(clips, method='compose')

    final_clip1 = fadeout(final_clip, 1, final_color=None)

    final_clip2 = fadein(final_clip1, 1, initial_color=None)

    return final_clip2
