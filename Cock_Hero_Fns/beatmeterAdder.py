from moviepy.audio.io.AudioFileClip import AudioFileClip
from pydub import AudioSegment
from PMV_Fns.processMusicFile import inputMusic
from Admin_Fns.allPaths import PathList
import moviepy.editor as mpe
import librosa, librosa.display
from moviepy.editor import ImageClip, CompositeVideoClip, CompositeAudioClip
from Admin_Fns.allPaths import PathList
import os
from moviepy.video.io.VideoFileClip import VideoFileClip
import random

AudioSegment.converter = PathList["AudioSegmentPath"]
AudioSegment.ffmpeg = PathList["AudioSegmentPath"]
AudioSegment.ffprobe = PathList["AudioSegmentPath"]

def movingImage(t, start_x, end_x, startTime, endTime):
    duration = endTime-startTime
    gradient = (end_x - start_x)/(duration)
    pos = start_x + gradient * t
    return pos


def addBeatMeter(background_clip, selectedDiffsIndex, reshaped_data, inputFile, granularity, beatSelect, cropMusicStart=0,
                 cropMusicDuration=0, animationDuration=4, sdfactor=0.5, yPosScale=0.9, useRankMethod=True, rollingSections=5,
                 circleSizeScale=0.02, beatEndPosScale=0.25):
    beatOptions = ["beat", "boop", "thump", "basspunch"]

    selectedDiffsIndex.sort()
    selectedDiffsIndex.append(reshaped_data.size)
    print(selectedDiffsIndex)

    if cropMusicStart==0 and cropMusicDuration==0:
        samples, sample_rate = librosa.load(inputFile)
    else:
        samples, sample_rate = librosa.load(inputFile, offset=cropMusicStart, duration=cropMusicDuration)

    factor = sample_rate / (1 / granularity)

    reshapedDataMean = reshaped_data.mean()
    reshapedDataSD = reshaped_data.std()

    sectionList = []
    sectionStartBPMList = []
    sectionsMeanList = []

    iSection = 0
    while iSection < len(selectedDiffsIndex):
        if iSection == 0:
            startIndex = 0
        else:
            startIndex = int(selectedDiffsIndex[iSection - 1])
        endIndex = int(selectedDiffsIndex[iSection])
        samples_section = samples[int(startIndex * factor):int(endIndex * factor)]
        sectionList.append(samples_section)
        audioSectionMean = reshaped_data[startIndex:endIndex].mean()
        sectionsMeanList.append(audioSectionMean)
        iSection = iSection + 1

    # audioSectionsAllMean = reshapedDataMean # np.array(sectionsMeanList).mean() #
    # audioSectionsAllStDev = reshapedDataSD # np.array(sectionsMeanList).std() #
    # sectionsRank = [sorted(sectionsMeanList).index(x) for x in sectionsMeanList]

    iSection = 0
    while iSection < len(selectedDiffsIndex):

        iSectionStartMean = max(0, iSection - rollingSections)
        iSectionEndMean = min(len(selectedDiffsIndex)-1, iSection + rollingSections)

        startIndex = int(selectedDiffsIndex[iSectionStartMean])
        endIndex = int(selectedDiffsIndex[iSectionEndMean])

        if useRankMethod:
            audioSectionsAllMean = reshaped_data[startIndex:endIndex].mean()

            sectionsMeanListToRank = sectionsMeanList[iSectionStartMean:iSectionEndMean+1]
            sectionsRank = [sorted(sectionsMeanListToRank).index(x) for x in sectionsMeanListToRank]
            print(iSectionStartMean, iSectionEndMean, iSection, iSection - iSectionStartMean, len(sectionsRank))

            if sectionsRank[iSection-iSectionStartMean]>len(sectionsRank)*0.9:
                startBPM = 240
            elif sectionsRank[iSection-iSectionStartMean]>len(sectionsRank)*0.75:
                startBPM = 180
            elif sectionsRank[iSection-iSectionStartMean]>len(sectionsRank)*0.6:
                startBPM = 120
            elif sectionsRank[iSection-iSectionStartMean]>len(sectionsRank)*0.45:
                startBPM = 120
            elif sectionsRank[iSection-iSectionStartMean]>len(sectionsRank)*0.3:
                startBPM = 60
            elif sectionsRank[iSection-iSectionStartMean]>len(sectionsRank)*0.15:
                startBPM = 60
            else:
                startBPM = 30
            print(sectionsRank[iSection-iSectionStartMean], sectionsMeanList[iSection], audioSectionsAllMean, startBPM)

        else:
            audioSectionsAllMean = reshaped_data[startIndex:endIndex].mean()
            audioSectionsAllStDev = reshaped_data[startIndex:endIndex].std()

            if sectionsMeanList[iSection] > audioSectionsAllMean + audioSectionsAllStDev * 2.5 * sdfactor:
                startBPM = 240
            elif sectionsMeanList[iSection] > audioSectionsAllMean + audioSectionsAllStDev * 1.5 * sdfactor:
                startBPM = 180
            elif sectionsMeanList[iSection] > audioSectionsAllMean + audioSectionsAllStDev * 0.5 * sdfactor:
                startBPM = 120
            elif sectionsMeanList[iSection] > audioSectionsAllMean - audioSectionsAllStDev * 0.5 * sdfactor:
                startBPM = 60
            elif sectionsMeanList[iSection] > audioSectionsAllMean - audioSectionsAllStDev * 1.5 * sdfactor:
                startBPM = 60
            elif sectionsMeanList[iSection] > audioSectionsAllMean - audioSectionsAllStDev * 2.5 * sdfactor:
                startBPM = 30
            elif sectionsMeanList[iSection] > audioSectionsAllMean - audioSectionsAllStDev * 3.5 * sdfactor:
                startBPM = 30
            elif sectionsMeanList[iSection] > audioSectionsAllMean - audioSectionsAllStDev * 5 * sdfactor:
                startBPM = 30
            elif iSection == 0:
                startBPM = 30
            elif iSection == len(sectionsMeanList):
                startBPM = 60
            else:
                startBPM = 0

            print(sectionsMeanList[iSection], audioSectionsAllMean, startBPM)

        sectionStartBPMList.append(startBPM)

        iSection = iSection + 1

    offset = 0
    allBeatsList = []
    iSection = 0
    while iSection < len(sectionList):
        samples_section = sectionList[iSection]
        startBPM = sectionStartBPMList[iSection]
        if startBPM > 0:
            tempo, beat_times = librosa.beat.beat_track(samples_section, sr=sample_rate, start_bpm=startBPM, units='time', trim=False)
            print(iSection, startBPM, offset / sample_rate, (offset + samples_section.size) / sample_rate, tempo)

            beat_times = beat_times.tolist()

            iBeat = 0
            while iBeat < len(beat_times):
                beat_times[iBeat] = beat_times[iBeat] + offset / sample_rate
                iBeat = iBeat + 1

            allBeatsList = allBeatsList + beat_times
        else:
            print(iSection, startBPM, 0, 0, 0)
        offset = offset + samples_section.size
        iSection = iSection + 1

    beat_times = allBeatsList

    iBeat = 0
    while iBeat < len(beat_times):
        if iBeat == 0:
            print(beat_times[iBeat], "\t", 0)
        else:
            print(beat_times[iBeat], "\t", beat_times[iBeat] - beat_times[iBeat - 1])
        iBeat = iBeat + 1

    w, h = background_clip.size
    print(w, h)
    circleSize = int(w * circleSizeScale)
    through = 200
    stiffness = 10

    circle_clip = ImageClip(PathList["cockHeroPath"] + 'Images\circle.png').resize(height=circleSize)  # , col1=1,col2=0, blur=4))
    circle_clip = circle_clip.fx(mpe.vfx.mask_color, color=[84, 220, 60], thr=through, s=stiffness)

    end_circle_clip = ImageClip(PathList["cockHeroPath"] + 'Images\end_circle.png').resize(height=circleSize)  # , col1=1,col2=0, blur=4))

    square_clip = ImageClip(PathList["cockHeroPath"] + 'Images\square.png').resize(height=circleSize)

    if beatSelect not in beatOptions:
        beatRand = random.randint(0, len(beatOptions) - 1)
        beataudioclip = AudioFileClip(PathList["cockHeroPath"] + "Sound/" + beatOptions[beatRand] + ".mp3")
    else:
        beataudioclip = AudioFileClip(PathList["cockHeroPath"] + "Sound/" + beatSelect + ".mp3")

    vidDuration = background_clip.duration

    yPos = background_clip.h * yPosScale
    xPos_start = background_clip.w
    xPos_end = int(background_clip.w * beatEndPosScale)
    composite_clip = background_clip
    circleClips = []
    end_circle_clip = end_circle_clip.fx(mpe.vfx.mask_color, color=[84, 220, 60], thr=through, s=stiffness).set_pos((xPos_end, yPos)).set_start(0).set_duration(vidDuration)

    square_clip = square_clip.resize((background_clip.w, square_clip.h)).set_pos((0, yPos)).set_start(0).set_duration(vidDuration).set_opacity(.75)

    circleClips.append(end_circle_clip)
    circleClips.append(square_clip)
    audioClips = []

    for beat in beat_times:
        if beat > 5:  # and beat<15:
            startTime = max(0, beat - animationDuration)
            circle_clip_beat = circle_clip
            endTime = beat
            # print("///////////", startTime, endTime, "///////////////")
            circle_clip_file = circle_clip_beat.set_pos(lambda t: (movingImage(t, xPos_start, xPos_end, startTime, endTime), yPos)).set_start(startTime).set_duration(endTime - startTime)
            circleClips.append(circle_clip_file)
            audioClips.append(beataudioclip.set_start(beat))
    composite_clip = CompositeVideoClip([background_clip] + circleClips + [end_circle_clip]).set_duration(
        vidDuration)

    final_audio = CompositeAudioClip([composite_clip.audio] + audioClips)
    finalVideo = composite_clip.set_audio(final_audio)

    return finalVideo


def makeCockHero(inputFile, file_out, t_start, t_end, granularity, beatSelect, beatSpeed, nSections, requiredDiff,
                 minSections, sdfactor, yPosScale, useRankMethod, rollingSections, circleSizeScale, beatEndPosScale):

    reshaped_data, first_data, audioclip, ratio, bitrate, songStart, songEnd, selectedDiffsIndex = inputMusic(inputFile, songStart=t_start, songEnd=t_end, granularity=granularity, plotCharts=False, nSections = nSections, requiredDiff=requiredDiff, minSections=minSections, autoTrimSong=False)

    background_clip = VideoFileClip(inputFile)
    if t_start>0 and t_end>0:
        background_clip = background_clip.subclip(t_start, t_end)

    finalVideo = addBeatMeter(background_clip, selectedDiffsIndex, reshaped_data, inputFile, granularity, beatSelect,
                              cropMusicStart=t_start, cropMusicDuration=t_end-t_start, animationDuration=beatSpeed,
                              sdfactor=sdfactor, yPosScale=yPosScale, useRankMethod=useRankMethod, rollingSections=rollingSections,
                              circleSizeScale=circleSizeScale, beatEndPosScale=beatEndPosScale)

    finalVideo.write_videofile(file_out, threads=4, fps=30)
