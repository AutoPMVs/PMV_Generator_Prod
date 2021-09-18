import pandas as pd
import numpy as np
import math as m
from moviepy.audio.io.AudioFileClip import AudioFileClip
import matplotlib.pyplot as plt
import datetime
from pydub import AudioSegment
from Admin_Fns.allPaths import PathList

AudioSegment.converter = PathList["AudioSegmentPath"]
AudioSegment.ffmpeg = PathList["AudioSegmentPath"]
AudioSegment.ffprobe = PathList["AudioSegmentPath"]

def reshapeData(data, time_scale):
    reshaped = np.mean(data[:(len(data)//time_scale)*time_scale].reshape(-1,time_scale), axis=1)

    return reshaped

def compute_similarity_matrix_slow(chroma):
    """Slow but straightforward way to compute time time similarity matrix"""
    num_samples = chroma.shape[1]
    time_time_similarity = np.zeros((num_samples, num_samples))
    for i in range(num_samples):
        for j in range(num_samples):
            # For every pair of samples, check similarity
            time_time_similarity[i, j] = 1 - (
                np.linalg.norm(chroma[:, i] - chroma[:, j]) / m.sqrt(12))

    return time_time_similarity

def getMusicRatio(sound, granularity):
    tenSecs = 10 * 1000
    first_10_seconds = sound[:tenSecs]
    ten_data = first_10_seconds._data

    first_ten_data = np.fromstring(ten_data, dtype=np.int16)
    new_ten_data = np.absolute(first_ten_data)
    bitrate = len(new_ten_data) / 10  # raw data to 1 s
    print(bitrate)
    ratio = int(round(bitrate * granularity, 0))
    return ratio, bitrate

def getRawData(sound):
    sound_data = sound._data
    first_data = np.fromstring(sound_data, dtype=np.int16)
    raw_data = np.absolute(first_data)
    print(len(first_data), len(raw_data))
    return raw_data, first_data

def getStartEndTrim(sound):
    granularity=0.25

    ratio, bitrate = getMusicRatio(sound, granularity)
    raw_data, first_data = getRawData(sound)
    reshaped_data = reshapeData(raw_data, ratio)

    df_music = pd.DataFrame(reshaped_data.tolist(), columns=["audio"])
    df_music["audio"] = df_music["audio"] / df_music["audio"].max()
    list_Score = df_music["audio"].to_list()

    diffRequiredMin = 0.018
    diffRequiredMax = 1.01
    jTotal = round(30/granularity,0)
    iScore = 0
    firstChange = 0
    while iScore < len(list_Score):
        j=0
        AllTrue=0
        while j<jTotal:
            if diffRequiredMin<list_Score[iScore+j]<diffRequiredMax:
                AllTrue = AllTrue+1
            j=j+1
        if AllTrue==jTotal:
            firstChange = iScore
            break
        iScore = iScore + 1

    iScore = len(list_Score)-1
    lastChange = len(list_Score)-1
    while iScore >= 0:
        j=0
        AllTrue=0
        while j<jTotal:
            if diffRequiredMin<list_Score[iScore-j]<diffRequiredMax:
                AllTrue = AllTrue+1
            j=j+1
        if AllTrue==jTotal:
            lastChange = iScore-1
            break
        iScore = iScore - 1

    print("Music Trim (f)", firstChange, lastChange)
    print("Music Trim (s)", firstChange*granularity, lastChange*granularity)
    # plt.plot(list_Score)
    # plt.show()
    return firstChange*granularity, lastChange*granularity

def inputMusic(mp3_dir, autoTrimSong=True, songStart=0, songEnd=0, granularity=0.05, plotCharts = False, nSections = 1, requiredDiff=20, minSections=8):
    audioclip = AudioFileClip(mp3_dir)
    sound = AudioSegment.from_file(mp3_dir, 'mp4')

    if songStart > 0 or songEnd > 0:
        sound = sound[songStart * 1000:songEnd * 1000]
        audioclip = audioclip.subclip(songStart, songEnd)

    ratio, bitrate = getMusicRatio(sound, granularity)
    raw_data, first_data = getRawData(sound)
    reshaped_data = reshapeData(raw_data, ratio)

    if autoTrimSong:
        try:
            songStart, songEnd = getStartEndTrim(sound)
        except IndexError:
            songStart = 0
            songEnd = audioclip.duration
        print("Music Trim", songStart, songEnd)
        sound = sound[songStart * 1000:songEnd * 1000]
        audioclip = audioclip.subclip(songStart, songEnd)
        raw_data, first_data = getRawData(sound)
        reshaped_data = reshapeData(raw_data, ratio)

    # musicDataDiff2, points, selectedDiffs, selectedDiffsIndex = getMusicSections(reshaped_data, granularity, nSections, requiredDiff)
    mvAv = 5

    print(mvAv)
    selectedDiffsIndex = getMediaSectionsSplit(reshaped_data, nSections, mvAv, granularity, plotCharts, requiredDiff, minSections)

    # if plotCharts:
    #     ax = plt.subplot(1, 1, 1)
    #     ax.plot(reshaped_data)
    #     # plt.plot(musicDataDiff2)
    #     ax.plot(selectedDiffsIndex, points, "or")
    #     plt.show()
    #
    #     ax2 = plt.subplot(1, 1, 1)
    #     ax2.plot(musicDataDiff2)
    #     # plt.plot(musicDataDiff2)
    #     ax2.plot(selectedDiffsIndex, selectedDiffs, "or")
    #     plt.show()

    return reshaped_data, first_data, audioclip, ratio, bitrate, songStart, songEnd, selectedDiffsIndex

def moving_average(x, w):
    avNumpy = np.convolve(x, np.ones(w), 'valid')/w
    fillArray = np.zeros(w-1)
    combinedNumpy = np.concatenate((fillArray, avNumpy))
    return combinedNumpy

def checkIfNearInArray(valueIndex, value, selectedDiffsIndex, selectedDiffs, tolerance):
    for iSelectedDiff, selectedDiff in enumerate(selectedDiffs):
        index = selectedDiffsIndex[iSelectedDiff]
        difference = abs(index-valueIndex)
        if difference<tolerance:
            if selectedDiff>value:
                outPosition = iSelectedDiff
                outIndex = index
                outDiff = selectedDiff
                return outPosition, outIndex, outDiff
            else:
                outPosition = iSelectedDiff
                outIndex = valueIndex
                outDiff = value
                return outPosition, outIndex, outDiff
        # else:
    outPosition = len(selectedDiffs)-1
    outIndex = valueIndex
    outDiff = value
    return outPosition, outIndex, outDiff

def getMusicSections(musicData, granularity, nSections = 6, requiredDiffSeconds=250):
    mvAv = 50
    musicDataDiffAv = moving_average(musicData, mvAv)
    musicDataDiff = musicData - musicDataDiffAv
    # musicDataDiff = np.diff(musicData)
    musicDataDiff2 = musicDataDiff*musicDataDiff

    selectedDiffs = [0]*nSections
    selectedDiffsIndex = [0]*nSections
    for iDiff, diff in enumerate(musicDataDiff2):
        if diff>min(selectedDiffs) and iDiff>mvAv:
            outPosition, outIndex, outDiff = checkIfNearInArray(iDiff, diff, selectedDiffsIndex, selectedDiffs, int(requiredDiffSeconds/granularity))
            # iDiff, diff, overwriteBool = checkIfNearInArray(iDiff, diff, selectedDiffsIndex, selectedDiffs, 50)
            selectedDiffs[outPosition] = outDiff
            selectedDiffs.sort(reverse=True)
            for iSelectedDiff, selectedDiff in enumerate(selectedDiffs):
                selection = np.where(musicDataDiff2 == selectedDiff)
                try:
                    point = selection[0][0]
                except:
                    # print(selection)
                    continue
                    # pass
                selectedDiffsIndex[iSelectedDiff] = point

    # selectedDiffsIndex = []
    # for selectedDiff in selectedDiffs:
    #     point = np.where(musicDataDiff2 == selectedDiff)[0][0]
    #     selectedDiffsIndex.append(point)

    points=[]
    for index in selectedDiffsIndex:
        points.append(musicData[index])


    return musicDataDiff2, points, selectedDiffs, selectedDiffsIndex

def getMediaSectionsSplit(reshaped_data, nSections, mvAv, granularity, plotCharts, requiredDiff, minSections):

    iSection = 0
    startIndex = 0
    selectedDiffsIndex = []
    musicDataDiffAvDiff = []
    musicDataDiffAvBack = []
    musicDataDiffAvBackLonger = []
    musicDataDiffAvBackDeltas = []
    minLineList = []
    maxLineList = []
    while iSection < nSections:
        print(iSection)
        reshaped_data_select = reshaped_data[startIndex:startIndex + int(len(reshaped_data)/nSections)]
        selectedDiffsIndex_section, musicDataDiffAvDiff_section, musicDataDiffAvBack_section, musicDataDiffAvBackLonger_section, musicDataDiffAvBackDeltas_section, meanDiff, sdDiff = getMediaSections(reshaped_data_select, 3, mvAv, granularity, minSections)

        selectedDiffsIndex_section = [x+startIndex for x in selectedDiffsIndex_section]

        selectedDiffsIndex = selectedDiffsIndex + selectedDiffsIndex_section
        musicDataDiffAvDiff = musicDataDiffAvDiff + musicDataDiffAvDiff_section.tolist()
        musicDataDiffAvBack = musicDataDiffAvBack + musicDataDiffAvBack_section.tolist()
        musicDataDiffAvBackLonger = musicDataDiffAvBackLonger + musicDataDiffAvBackLonger_section.tolist()
        musicDataDiffAvBackDeltas = musicDataDiffAvBackDeltas + musicDataDiffAvBackDeltas_section.tolist()

        minLineList = minLineList + [meanDiff - sdDiff for i in musicDataDiffAvDiff_section.tolist()]
        maxLineList = maxLineList + [meanDiff + sdDiff for i in musicDataDiffAvDiff_section.tolist()]

        startIndex = startIndex + int(len(reshaped_data)/nSections)
        iSection = iSection + 1


    # print(selectedDiffsIndex)
    newSectionsIndex = list(dict.fromkeys(selectedDiffsIndex))
    newSectionsIndexFiltered = []
    i=1
    while i < len(newSectionsIndex):
        if newSectionsIndex[i]-newSectionsIndex[i-1]>int(requiredDiff/granularity):
            newSectionsIndexFiltered.append(newSectionsIndex[i])
        elif i == 0:
            newSectionsIndexFiltered.append(newSectionsIndex[i])
        i = i + 1

    if plotCharts:
        plt.plot(musicDataDiffAvDiff)
        plt.plot(musicDataDiffAvBack)
        plt.plot(musicDataDiffAvBackLonger)
        plt.plot(musicDataDiffAvBackDeltas)
        for i in newSectionsIndexFiltered:
            plt.axvline(x=i)
        plt.plot(minLineList)
        plt.plot(maxLineList)
        # plt.axhline(y=meanDiff + sdDiff)
        # plt.axhline(y=meanDiff - sdDiff)
        plt.show()



    return newSectionsIndexFiltered


def getMediaSections(reshaped_data, minLength, mvAv, granularity, minSections):
    # print(mvAv, minLength)
    mvAv = int(mvAv / granularity)
    minLength = minLength / granularity

    musicDataDiffAvBack = moving_average(reshaped_data, mvAv)
    musicDataDiffAvBackDeltas = np.concatenate((np.zeros(1), np.diff(musicDataDiffAvBack)))
    # musicDataDiffAvBackDeltasAv = moving_average(musicDataDiffAvBackDeltas, 3)
    musicDataDiffAvBackLonger = moving_average(musicDataDiffAvBack, int(mvAv/2))
    musicDataDiffAvBackLongest = moving_average(musicDataDiffAvBack, int(mvAv*2))

    musicDataDiffAvDiffInit = musicDataDiffAvBack - musicDataDiffAvBackLongest
    musicDataDiffAvDiff = musicDataDiffAvBack - musicDataDiffAvBackLonger

    meanDiff = 0  # musicDataDiffAvDiff.mean()
    sdDiff = musicDataDiffAvDiffInit.std()*1.2

    newSectionsIndex = []

    # print(meanDiff, sdDiff, len(musicDataDiffAvDiff), 0)
    while len(newSectionsIndex)<minSections:
        print(len(newSectionsIndex), sdDiff)
        newSectionsIndex = []
        allowNew = True
        iDiff = 0
        # print(meanDiff, sdDiff, len(musicDataDiffAvDiff), len(newSectionsIndex))
        while iDiff < len(musicDataDiffAvDiff):
            diff = musicDataDiffAvDiffInit[iDiff]
            if diff > meanDiff + sdDiff or diff < meanDiff - sdDiff:
                if allowNew:
                    if len(newSectionsIndex) > 0:
                        if iDiff - newSectionsIndex[-1] > minLength:
                            newDiff = goBackToCrossingPoint(musicDataDiffAvDiff, musicDataDiffAvBackDeltas, iDiff, granularity, sdDiff)
                            newSectionsIndex.append(newDiff)
                            # print(newDiff * granularity)
                    else:
                        newDiff = goBackToCrossingPoint(musicDataDiffAvDiff, musicDataDiffAvBackDeltas, iDiff, granularity, sdDiff)
                        # print(newDiff * granularity)
                        newSectionsIndex.append(newDiff)
                allowNew = False
            else:
                allowNew = True
            iDiff = iDiff + 1
        sdDiff = sdDiff * 0.9

    return newSectionsIndex, musicDataDiffAvDiff, musicDataDiffAvBack, musicDataDiffAvBackLonger, musicDataDiffAvBackDeltas, meanDiff, sdDiff

def goBackToCrossingPoint(musicDataDiffAvDiff, musicDataDiffAvBackDeltasAv, iDiff, granularity, sdDiff):
    sdRatio = 0.25
    backSecondsSearch = 30
    iBackVal = iDiff
    dataValueStart = musicDataDiffAvDiff[iDiff]
    dataValueStartSign = dataValueStart/abs(dataValueStart)
    newDiff = iDiff
    while iBackVal>max(0, iDiff-int(backSecondsSearch/granularity)):
        dataValue = musicDataDiffAvDiff[iBackVal]
        dataValueSign = dataValue/abs(dataValue)
        if (dataValueStartSign != dataValueSign): # or (dataValue<abs(sdDiff*sdRatio) and dataValue>-abs(sdDiff*sdRatio)):
            newDiff = iBackVal
            break
        iBackVal = iBackVal - 1
    # if newDiff==iDiff:
    #     while iBackVal>max(0, iDiff-int(backSecondsSearch/granularity)):
    #         dataValue = musicDataDiffAvDiff[iBackVal]
    #         if dataValue<abs(sdDiff*sdRatio) and dataValue>-abs(sdDiff*sdRatio):
    #             newDiff = iBackVal
    #             break
    #         iBackVal = iBackVal - 1
    return newDiff



# music_dir = r"E:\Python Main\PycharmProjects\PMV_Generator_Git\Resources\TempMusic\Forever Now.mp4"
# music_dir2 = r"C:\Users\vince\Pictures\Python\PMV_Generator_Git\Resources\TempMusic\Green Day - Too Dumb to Die (HQ).mp4"
# music_dir3 = r"C:\Users\vince\Pictures\Python\PMV_Generator_Git\Resources\TempMusic\'Dance Monkey' - Tones and I (Cover by First to Eleven).mp4"
# music_dir4 = r"C:\Users\vince\Pictures\Python\PMV_Generator_Git\Resources\NewPMVs\Lexi Anne Garza PMV - Waves Robin Schulz Remix Radio Edit - Mr Probz - AutoPMVs.mp4"
# music_dir5 = r"C:\Users\vince\Pictures\Python\PMV_Generator_Git\Resources\NewPMVs\Maryana Rose PMV - Crush Crush Crush - Paramore - AutoPMVs.mp4"
# music_dir6 = r"C:\Users\vince\Pictures\Python\PMV_Generator_Git\Resources\TempMusic\She Keeps Me up - Nickelback Lyrics.mp4"
# music_dir7 = r"C:\Users\vince\Pictures\Python\PMV_Generator_Git\Resources\TempMusic\7 Rings.mp4"
# musicFile = music_dir
# reshaped_data, first_data, audioclip, ratio, bitrate, songStart, songEnd, selectedDiffsIndex = inputMusic(musicFile, granularity=0.1, trimSong=False, plotCharts=True)
# musicData = inputMusic(musicFile, granularity=0.25)
# getRepeatedSections(musicData)
#
# musicDataDiff2, selectedDiffs, selectedDiffsIndex = getMusicSections(musicData, granularity=0.1)
# ax = plt.subplot(1, 1, 1)
# ax.plot(musicDataDiff2)
# # plt.plot(musicDataDiff2)
# ax.plot(selectedDiffsIndex, selectedDiffs, "or")
# plt.show()

# print(musicData)


#
# time1=datetime.datetime.now()
# chroma, a, b, _ = pychorus.create_chroma(musicFile)
# plt.imshow(chroma)
# plt.show()
# time_time_similarity = compute_similarity_matrix_slow(chroma)
# time2=datetime.datetime.now()
# print(time2-time1)
#
# plt.imshow(time_time_similarity)
# plt.show()
