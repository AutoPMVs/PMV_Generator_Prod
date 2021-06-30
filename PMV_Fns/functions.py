import numpy as np
import ntpath
from os import listdir
from os.path import isfile, join
from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.video.fx.mirror_x import mirror_x
import moviepy.audio.fx.all as afx
from moviepy.audio.fx.volumex import volumex
from moviepy.editor import concatenate_videoclips, CompositeAudioClip
from moviepy.video.fx.fadein import fadein
from moviepy.video.fx.fadeout import fadeout
from PMV_Fns.IntroTitle import getIntroVid
from Classify_Model.ClassifyVideo import getVidClassifiedData
from operator import itemgetter
import pandas as pd
import random

class Video:
    def __init__(self, name, customStart, customEnd, directory):
        self.name = name
        self.customStart = customStart
        self.customEnd = customEnd
        self.directory = directory

# class VideoSections:
#     def __init__(self, name, customStart, customEnd, directory):
#         self.name = name
#         self.customStart = customStart
#         self.customEnd = customEnd
#         self.directory = directory

def properTitles(row):
    try:
        return str.title(row['Title'].replace("/", "_"))
    except AttributeError:
        return 0

def reshapeData(data, time_scale):
    reshaped = np.mean(data[:(len(data)//time_scale)*time_scale].reshape(-1,time_scale), axis=1)

    return reshaped

def getElementDiff(data):

    
#    output=[0]
#    i=1
#    while i < len(data):
#        if data[i]-data[i-1]>50:
#            output.append(data[i])
#        i=i+1
    
    differenceList = [abs(x - data[i - 1]) for i, x in enumerate(data)][1:]

    return differenceList


def getHighValues(reshaped_data, diff_data, sd_scale, nSplits, granularity):
    output=[0]
    
    timeChunks = np.array_split(diff_data, nSplits)
    j=0
    
    print('SmallerArrays: ', len(timeChunks))
    TotalLength=0
    while j < len(timeChunks):        
        data=timeChunks[j]
    
    
        max_element = np.amax(data)
        sd_element = np.std(data)
        av_element = np.mean(data)
        
        print(max_element, sd_element, av_element, (av_element+1.5*sd_element)/max_element)
        
        i=0
        result=[]
        while i< len(data):
            if data[i] >= (av_element+sd_scale*sd_element):
                result.append[i]
            i=i+1
        
        new_result = result
        
        print(new_result)
        
        i=1
        while i < len(new_result):
            if new_result[i]-new_result[i-1]>0.2/granularity:
                output.append(new_result[i]+TotalLength)
            i=i+1
        
        TotalLength=TotalLength + len(timeChunks[j])
        j=j+1
    
    return output

def getHighValues2(reshaped_data, diff_data, sd_scale, nSplits, granularity, min_length):
    output=[0]
    
    max_all = np.amax(diff_data)
    sd_all = np.std(diff_data)
    av_all= np.mean(diff_data)
    
    max_all2= np.amax(reshaped_data)
    sd_all2= np.std(reshaped_data)
    av_all2 = np.mean(reshaped_data)
    
    
    timeChunks = np.array_split(diff_data, nSplits)
    timeChunks2 = np.array_split(reshaped_data, nSplits)
    j=0
    
    print('SmallerArrays: ', len(timeChunks))
    TotalLength=0
    while j < len(timeChunks):        
        data=timeChunks[j]        
        data2=timeChunks2[j]
    
    
        max_element = np.amax(data)
        sd_element = np.std(data)
        av_element = np.mean(data)
        
        max_element2 = np.amax(data2)
        sd_element2 = np.std(data2)
        av_element2 = np.mean(data2)
        
        
#        sd_scale=2-av_element2/max_element2
        
#        print(max_element, sd_element, av_element, (av_element+sd_scale*sd_element)/max_element)
#        print(max_element2, sd_element2, av_element2, 2-av_element2/max_element2)
        
        
        result = np.where(data >= (av_element+sd_scale*sd_element))
        
        new_result = result[0].tolist()
        
#        print(new_result)
        
        i=1
        prevStopped=False
        prevDif=0
        while i < len(new_result):
#            print(new_result[i]+TotalLength, prevDif, prevStopped)
            if new_result[i]-new_result[i-1]>((min_length/granularity)-prevDif):
                output.append(new_result[i]+TotalLength)
                prevDif=0
                prevStopped=False
            else:
                prevDif=prevDif+(new_result[i]-new_result[i-1])
                prevStopped=True
            i=i+1
        
        TotalLength=TotalLength + len(timeChunks[j])
        j=j+1
    
    return output

def checkSwitch(data, max_scale, max_element, sd_element, av_element):
    if data >= max_scale * max_element:
        return True
    else:
        return False


def videoSplits(audioSplits, videos, videoData, first_data, bitrate, granularity, randomise, origVidName):
    audVidRatio = [0] * len(videos)
    clips = []

    i = 0
    while i < len(videos):
        audVidRatio[i] = (videoData[i].customEnd - videoData[i].customStart) / (len(first_data) / (granularity * (bitrate)))
        i = i + 1
    #    splitList=pd.DataFrame(columns = ['startTime', 'endTime', 'deltaTime'])
    print(len(audioSplits))
    i = 0
    while i <= len(audioSplits):
        #        splitList.loc[i]=[audioSplits[i]*audVidRatio, audioSplits[i] * audVidRatio + (audioSplits[i+1] - audioSplits[i])/10, audioSplits[i+1] - audioSplits[i]]
        deck = [k for k in range(len(videos))]
        random.shuffle(deck)
        j = 0
        while j < len(videos):
            try:
                if randomise == True:
                    iVid = deck[j]
                    print(videoData[iVid].name)  ####If Breaking, uncomment this line to find video with error!!!
                else:
                    iVid = j

                if i + len(videos) + 1 <= len(audioSplits) or len(videos) >= len(audioSplits) or videoData[iVid].name == origVidName:
                    print(videoData[iVid].name)  ####If Breaking, uncomment this line to find video with error!!!
                    clipStart = videoData[iVid].customStart + audioSplits[i + j] * audVidRatio[iVid]
                    clipEnd = clipStart + (audioSplits[i + j + 1] - audioSplits[i + j]) * granularity
                    print(i, j, iVid, i + j, 'True', clipStart, clipEnd)
                else:
                    clipEnd = videoData[iVid].customEnd
                    clipStart = clipEnd - (audioSplits[i + j + 1] - audioSplits[i + j]) * granularity
                    print(i, j, iVid, i + j, 'True', clipStart, clipEnd)
                clips.append(videos[iVid].subclip(clipStart, clipEnd))
            except:
                print('End')
                pass
            j = j + 1
        i = i + len(videos)

    print('length: ', len(clips))
    return (clips)


def getVideoSections(videoDicts, useSectionsBool):
    vidList=[]
    for vid in videoDicts:
        sectionList = []
        for section in vid["Sections"]:
            sectionList.append(vid["Sections"][section])
        if useSectionsBool==False:
            sectionList = [item for sublist in sectionList for item in sublist]
            sectionList = sorted(sectionList, key=itemgetter(0))
            sectionList = [sectionList]
        vidList.append(sectionList)
    return vidList


def videoSplitsUseClassifyModel(audioSplits, videos, videoData, songSections, granularity, randomise, origVidName, videoDicts):

    audVidRatio = [0] * len(videos)
    clips = []
    i = 0
    print(len(audioSplits))
    minSectionLength = max(audioSplits)*granularity/25
    # sectionArray1 = sectionArray[:,0]
    useSectionsBool=True
    if useSectionsBool:
        sectionArray = getSectionLengthData(videoDicts, useSectionsBool, minSectionLength)
        audioSections = getAudioSections(audioSplits, sectionArray, songSections)
        vidSections = getVideoSections(videoDicts, useSectionsBool)
    else:
        sectionArray = getSectionLengthData(videoDicts, useSectionsBool, minSectionLength)
        audioSections = [max(audioSplits)]
        vidSections = getVideoSections(videoDicts, useSectionsBool)

    vidPosition = [0]*len(videos)
    audioSectionsMusicVid = [audioSections[0] * granularity, audioSections[1] * granularity,
                            audioSections[2] * granularity, audioSections[3] * granularity]
    for vid in videoData:
        if vid.name==origVidName:
            vidSections.append([[[0, audioSectionsMusicVid[0]]], [[audioSectionsMusicVid[0], audioSectionsMusicVid[1]]], [[audioSectionsMusicVid[1], audioSectionsMusicVid[2]]], [[audioSectionsMusicVid[2], audioSectionsMusicVid[3]]]])
            audioMusicVid_np = np.array([audioSectionsMusicVid])
            # audioMusicVid_np = audioMusicVid_np.transpose()
            sectionArray = np.concatenate((sectionArray, audioMusicVid_np), axis=0)
            # sectionArray = np.append(sectionArray, audioMusicVid_np)


    iAudioSect=0
    while iAudioSect < len(audioSections):
        # print("/////////////////////////////////////")
        # print("/////////////////////////////////////")
        print("//////// Section " + str(iAudioSect) + " /////////")

        # print("/////////////////////////////////////")
        # print("/////////////////////////////////////")
        vidSectionPosition = [0] * len(videos)

        selectedVidSections = [vidSect[iAudioSect] for vidSect in vidSections]
        print(len(selectedVidSections))
        print(selectedVidSections)
        selectedVidSections2 = []
        vidRemoveList = []
        iVidRemove=0

        iSection=0
        vidStartSections = []
        vidEndSections = []
        while iSection < len(selectedVidSections):
            section = selectedVidSections[iSection]
            if len(section) > 0 and sectionArray[iSection, iAudioSect]>0:
                selectedVidSections2.append(section)
            else:
                vidRemoveList.append(iSection)
            vidStartSections.append([vidSect[0] for vidSect in section])
            vidEndSections.append([vidSect[1] for vidSect in section])
            if iAudioSect>0 and iSection<len(videoDicts):
                audVidRatio[iSection] = (sectionArray[iSection, iAudioSect]) / (audioSections[iAudioSect]-audioSections[iAudioSect-1])
            else:
                audVidRatio[iSection] = (sectionArray[iSection, iAudioSect]) / (audioSections[iAudioSect])
            iSection=iSection + 1

        # selectedVidSections = selectedVidSections2
        print(len(vidRemoveList))
        print(vidRemoveList)

        if iAudioSect==0:
            i = 0
            clipStartOffset = 0
            # print((len(first_data) / (granularity * (bitrate))))
            # print(max(audioSplits))
        else:
            i = audioSplits.index(audioSections[iAudioSect-1])
            if i == 0:
                clipStartOffset = 0
            else:
                clipStartOffset = audioSplits[i-1]
        # print(i, audioSplits.index(audioSections[iAudioSect-1]), audioSplits.index(audioSections[iAudioSect]))
        if len(vidRemoveList) == len(videos):
            print("No Available Videos")
        else:
            deckLast = 0
            while i <= audioSplits.index(audioSections[iAudioSect]): #len(audioSplits) and audioSplits[i]<=audioSections[iAudioSect]:
                deck = [k for k in range(len(videos))]
                deck = [k for k  in deck if k not in vidRemoveList]
                iAttempt=0
                random.shuffle(deck)
                while deckLast == deck[0] and iAttempt<5:
                    random.shuffle(deck)
                    iAttempt = iAttempt + 1
                deckLast = deck[len(deck)-1]
                j = 0
                while j < len(deck) and i+j<audioSplits.index(audioSections[iAudioSect]):
                    # try:
                    if randomise == True:
                        iVid = deck[j]
                    else:
                        iVid = j
                    iOffset = 0
                    if iAudioSect + 1 == len(audioSections):
                        iOffset = 1
                    if (i + len(deck) + iOffset <= len(audioSplits) or len(deck) >= len(audioSplits)) and videoData[iVid].name != origVidName:
                        # print(videoData[iVid].name)  ####If Breaking, uncomment this line to find video with error!!!
                        clipStart = (audioSplits[i + j] - clipStartOffset) * audVidRatio[iVid]
                        clipDiff = (audioSplits[i + j + 1] - audioSplits[i + j]) * granularity
                        clipEnd = clipStart + clipDiff
                        clipStart, clipEnd = getNewClipStartEnd(clipStart, clipEnd, clipDiff, vidStartSections[iVid], vidEndSections[iVid], vidSectionPosition, iVid, False)
                        print(i + j, i, j, iVid, 'Normal', clipStart, clipEnd, audioSplits[i + j], audioSplits[i + j+1], videoData[iVid].name)
                    elif videoData[iVid].name == origVidName:
                        clipStart = videoData[iVid].customStart + audioSplits[i + j] * audVidRatio[iVid]
                        clipEnd = clipStart + (audioSplits[i + j + 1] - audioSplits[i + j]) * granularity
                        print(i + j, i, j, iVid, 'Music Vid', clipStart, clipEnd, audioSplits[i + j], audioSplits[i + j+1], videoData[iVid].name)
                    else:
                        try:
                            clipDiff = (audioSplits[i + j + 1] - audioSplits[i + j]) * granularity
                            clipEnd = vidEndSections[iVid][len(vidEndSections[iVid])-1]
                            clipStart = clipEnd - clipDiff
                            print(i + j, i, j, iVid, 'Final', clipStart, clipEnd, audioSplits[i + j], audioSplits[i + j+1], videoData[iVid].name)
                        except IndexError:
                            print('End')
                            pass

                    clips.append(videos[iVid].subclip(clipStart, clipEnd))
                    # except:
                    #     print('End')
                    #     pass
                    j = j + 1
                i = i + len(deck)
        iAudioSect = iAudioSect + 1

    print(max(audioSplits))
    TotalDuration=0
    for iclip, clip in enumerate(clips):
        TotalDuration = TotalDuration + clip.duration
        print(iclip, " ", ntpath.basename(clip.filename), " ", clip.duration)
    print('length: ', len(clips), 'duration: ', TotalDuration)
    return (clips)

def getNewClipStartEnd(clipStart, clipEnd, clipDiff, vidStartSections, vidEndSections, vidSectionPosition, iVid, finalClip):

    vidDiffSections = []
    iElem = 0
    while iElem < len(vidEndSections):
        vidDiffSections.append(vidEndSections[iElem] - vidStartSections[iElem])
        iElem = iElem + 1
    vidCumDiffSections = np.cumsum(vidDiffSections)
    vidCumDiffSections = [0] + vidCumDiffSections.tolist()
    iSection = 0
    selectedSection = iSection
    while iSection < len(vidDiffSections):
        if clipStart >= vidCumDiffSections[iSection] and clipStart <= vidCumDiffSections[iSection+1]:
            selectedSection = iSection
        iSection = iSection + 1
    if selectedSection >= len(vidEndSections):
        # print(selectedSection)
        selectedSection=len(vidEndSections)-1
    clipOffset = clipStart - vidCumDiffSections[selectedSection]
    clipStartInit = clipStart
    clipEndInit = clipEnd
    clipStart = vidStartSections[selectedSection] + clipOffset
    clipEnd = clipStart + clipDiff
    clipStartSaved = clipStart
    clipEndSaved = clipEnd
    if finalClip==False:
        if clipEnd > vidEndSections[selectedSection]:
            # if clipDiff<3 and iVid==0:
                # print("WTF?")
            iAttempt = selectedSection + 1
            while iAttempt < min(selectedSection + 5, len(vidDiffSections)):
                sectStart = vidStartSections[iAttempt]
                sectEnd = vidEndSections[iAttempt]
                sectDiff = vidDiffSections[iAttempt]
                if clipStart >= sectStart and clipEnd <= sectEnd:
                    clipStart = sectStart
                    clipEnd = clipStart + clipDiff
                    break
                else:
                    clipStart = sectStart + (random.randint(0,int(sectDiff/2))/10)
                    clipEnd = clipStart + clipDiff
                    if clipStart >= sectStart and clipEnd <= sectEnd:
                        break
                # print(iAttempt)
                iAttempt = iAttempt + 1
            # print(iAttempt)
            if iAttempt==min(selectedSection + 5, len(vidDiffSections)):
                iAttempt = selectedSection - 1
                while iAttempt > max(selectedSection - 5, 0):
                    sectStart = vidStartSections[iAttempt]
                    sectEnd = vidEndSections[iAttempt]
                    sectDiff = vidDiffSections[iAttempt]
                    if clipStart >= sectStart and clipEnd <= sectEnd:
                        clipStart = sectStart
                        clipEnd = clipStart + clipDiff
                        break
                    else:
                        clipStart = sectStart + (random.randint(0, int(sectDiff / 2)) / 10)
                        clipEnd = clipStart + clipDiff
                        if clipStart >= sectStart and clipEnd <= sectEnd:
                            break
                    # print(iAttempt)
                    iAttempt = iAttempt - 1
                # print(iAttempt)
                if iAttempt == max(selectedSection - 5, 0):
                    clipStart = clipStartSaved
                    clipEnd = clipEndSaved

    # print(clipStartSaved, clipEndSaved, clipDiff)
    # print(iSection, clipOffset)
    # print(clipStart, clipEnd, clipDiff)
    # else:
    #     while clipStart < vidStartSections[vidSectionPosition[len(vidSectionPosition)]] or clipEnd > vidEndSections[vidSectionPosition[len(vidSectionPosition)]]:
    #         if clipStart < vidStartSections[vidSectionPosition[len(vidSectionPosition)]] and clipEnd > vidEndSections[vidSectionPosition[len(vidSectionPosition)]]:
    #             clipEnd = vidStartSections[vidSectionPosition[len(vidSectionPosition)]]
    #             clipStart = clipEnd - clipDiff
    return clipStart, clipEnd

def getAudioSections(audioSplits, sectionArray, songSections):
    musicLength = max(audioSplits)
    print(musicLength)

    sectionArraySumsAdjusted = []
    sectionArraySumsAdjusted.append(sectionArray[:, 0].sum())
    sectionArraySumsAdjusted.append(sectionArray[:, 1].sum())#*2)
    sectionArraySumsAdjusted.append(sectionArray[:, 2].sum())#*2)
    sectionArraySumsAdjusted.append(sectionArray[:, 3].sum())

    origLength = sectionArray.sum()
    vidLength = sum(sectionArraySumsAdjusted)

    sectionArraySumsAdjusted = [i*origLength/vidLength for i in sectionArraySumsAdjusted]

    iSection=0
    audioSection = []
    ratioTotal = 0
    missingIndexes = []
    while iSection < sectionArray.shape[1]:
        sectionRatio = sectionArraySumsAdjusted[iSection]/origLength
        ratioTotal = ratioTotal + sectionRatio
        audioValue = round(musicLength * ratioTotal,0)
        audioLstValue = min(audioSplits, key=lambda x: abs(x - audioValue))
        if audioLstValue == max(audioSplits) and iSection < sectionArray.shape[1]-1:
            audioLstValue = audioSplits[len(audioSplits)-2]
        print(sectionRatio, ratioTotal, round(musicLength * ratioTotal,0), audioLstValue)
        if iSection==0:
            audioSectionDiff = audioLstValue - 0
        else:
            audioSectionDiff = audioLstValue - audioSection[-1]
        if audioSectionDiff!=0:
            audioSection.append(audioLstValue)
        else:
            missingIndexes.append(iSection)

        iSection = iSection + 1


    audioSectionFinal = []
    audioSectionRanges = []
    audioSectionForRange = [0] + audioSection
    iSection = 1
    while iSection < len(audioSectionForRange)-1:
        if iSection < len(audioSectionForRange)-2:
            downDiff = (audioSectionForRange[iSection] - audioSectionForRange[iSection-1])/3
            upDiff = (audioSectionForRange[iSection+ 1] - audioSectionForRange[iSection])/3
        else:
            downDiff = (audioSectionForRange[iSection] - audioSectionForRange[iSection-1])/8
            upDiff = (audioSectionForRange[iSection+ 1] - audioSectionForRange[iSection])/2
        if audioSectionForRange[iSection-1]==audioSectionForRange[iSection]:
            downDiff = 0
            upDiff = 0
        audioSectionRanges.append([audioSection[iSection-1] - downDiff, audioSection[iSection-1] + upDiff])
        iSection = iSection + 1

    audioSectionRanges.append([audioSection[len(audioSection)-1], audioSection[len(audioSection)-1]])

    for iSection, section in enumerate(audioSection):
        nearestSection = find_nearest(songSections, section)
        if nearestSection>audioSectionRanges[iSection][0] and nearestSection<audioSectionRanges[iSection][1]:
            finalSection = find_nearest(audioSplits, nearestSection)
            audioSectionFinal.append(finalSection)
        else:
            audioSectionFinal.append(section)

    iSection = 0
    while iSection < len(audioSectionFinal)-1:
        if audioSectionFinal[iSection]>=audioSectionFinal[iSection+1] and audioSection[iSection]!=audioSection[iSection+1]:
            audioSectionFinal[iSection] = audioSection[iSection]
        iSection = iSection + 1
    iSection = 0
    while iSection < len(audioSectionFinal):
        if audioSectionFinal[iSection]<audioSectionFinal[iSection-1]:
            audioSectionFinal[iSection] = audioSection[iSection]
        iSection = iSection + 1

    for index in missingIndexes:
        audioSectionFinal.insert(index, audioSectionFinal[index-1])

    return audioSectionFinal

def find_nearest(array, value):
    array = np.asarray(array)
    idx = (np.abs(array - value)).argmin()
    return array[idx]

def getSectionLengthData(videoDicts, useSectionsBool, minSectionLength):

    categories = []
    sectionLengths=[]
    for vidDict in videoDicts:
        sections_list = vidDict["Sections"]
        sectionLength = getSectionLengths(sections_list, minSectionLength)
        sectionLengths.append(sectionLength)
    sectionArray = np.array(sectionLengths)

    if useSectionsBool==False:
        sectionArray = sectionArray.sum(axis=1)
        sectionArray = sectionArray.reshape(sectionArray.shape[0], -1)

    iSection = 0
    while iSection < sectionArray.shape[1]:
        iAudioSect = 0
        columnArray = sectionArray[ : ,iSection]
        columnArrayCount = np.count_nonzero(columnArray)
        if columnArrayCount<2 and sectionArray.shape[0]>2:
            while iAudioSect < sectionArray.shape[0]:
                sectionArray[iAudioSect, iSection]=0
                iAudioSect = iAudioSect + 1
        iSection = iSection + 1

    print(categories)
    return sectionArray

def getSectionLengths(sections_list, minSectionLength):
    lengthList = [] # np.array()
    for iSection, section in enumerate(sections_list):
        totalLength = 0
        for clip in sections_list[section]:
            totalLength = totalLength + clip[1]-clip[0]
        if ((totalLength<minSectionLength or (len(sections_list[section])<3) and totalLength<minSectionLength*2)) and iSection != len(sections_list)-1:
            totalLength = 0
        lengthList.append(totalLength)
    return lengthList

def getVideoData(PMV, df_Videos_All, allVideoDict):
    videosIn = list()
    videoDicts = list()
    iVids = 0
    for f in listdir(PMV.DirectoryFile_Info.vidDownloadDir):
        if isfile:
            if f.endswith(".mp4") and f.endswith(".temp.mp4") == False:
                if iVids < 120:
                    videosIn.append(f)
                    if PMV.Configuration.UseClassifyModel:
                        videoDicts.append(getVidClassifiedData(PMV.DirectoryFile_Info.vidDownloadDir + "/" + f, allVideoDict, modelStoragePath = PMV.DirectoryFile_Info.ModelStorageDir, df_Videos_All=df_Videos_All))

                iVids = iVids + 1


    videoData = list()
    for i, vid in enumerate(videosIn):
        if PMV.Configuration.UseClassifyModel:
            try:
                videoData.append(Video(name=vid, customStart=videoDicts[i]["StartEndTimes"][0], customEnd=videoDicts[i]["StartEndTimes"][1], directory=PMV.DirectoryFile_Info.vidDownloadDir))
            except:
                print(vid)
                pass
        else:
            videoData.append(Video(name=vid, customStart=0, customEnd=0, directory=PMV.DirectoryFile_Info.vidDownloadDir))
        print(vid)

    nInVids = len(videosIn)
    iOrig = 0
    origVidName = PMV.Music_Info.musicName + ".mp4"
    if PMV.Music_Info.musicVideoBool == True:
        while iOrig <= nInVids * PMV.Music_Info.musicVideoOccuranceFactor:
            videoData.append(Video(name=origVidName, customStart=0, customEnd=0, directory=PMV.DirectoryFile_Info.musicVidDir))
            iOrig = iOrig + 1

    return videoData, origVidName, videoDicts
        
def processVideoData(PMV, videoData, sampleWidth, sampleHeight, origVidName, df_videos_filtered): #, originalVidBool, df_videos_filtered, defaultStartTime, defaultEndTime):
    nVideos = len(videoData)
    videos = [0] * nVideos

    i = 0
    while i < nVideos:
        if PMV.Configuration.resize == True:
            vidTemp = VideoFileClip(videoData[i].directory + videoData[i].name).resize(width = sampleWidth) #(sampleWidth, sampleHeight))
            if PMV.Configuration.flipBool == True and videoData[i].name != origVidName:
                vidTemp2 = mirror_x(vidTemp)
            else:
                vidTemp2 = vidTemp
            videos[i] = vidTemp2
        else:
            videos[i] = VideoFileClip(PMV.DirectoryFile_Info.vidDownloadDir + videoData[i].name)

        print('name', 'duration', 'customStart', 'customEnd')

        if PMV.Music_Info.musicVideoBool == True and videoData[i].name == origVidName:
            if PMV.Music_Info.trimSong == True:
                videoData[i].customEnd = PMV.Music_Info.songEnd
                videoData[i].customStart = PMV.Music_Info.songStart
            else:
                videoData[i].customEnd = videos[i].duration
                videoData[i].customStart = 0  #
            print(videoData[i].name, videos[i].duration, videoData[i].customStart, videoData[i].customEnd, 'Original Video')
        else:
            videoName = str.title(videoData[i].name[:-4])  # + " - Pornhub.com")
            df_videos_filtered['Title Proper'] = df_videos_filtered.apply(lambda row: properTitles(row), axis=1)
            csvVideoInfo = df_videos_filtered.loc[df_videos_filtered['Title Proper'] == videoName]
            csvVideoInfo = csvVideoInfo.reset_index()
            if PMV.Configuration.UseClassifyModel==True:
                videoData[i].customEnd = videos[i].duration
                videoData[i].customStart = 0
            else:
                try:
                    customStart = csvVideoInfo.loc[0]['Start'] + 0  # Add extra break
                except:
                    customStart = PMV.Configuration.startTime

                try:
                    subtractEnd = csvVideoInfo.loc[0]['End'] + 0  # Add extra break
                except:
                    subtractEnd = PMV.Configuration.subtractEnd
                videoData[i].customEnd = videos[i].duration - subtractEnd
                videoData[i].customStart = customStart

            print(videoData[i].name, videos[i].duration, videoData[i].customStart, videoData[i].customEnd)

        i = i + 1
    return videos, videoData

def concatonateFinalVideo(PMV, clips, sampleWidth, sampleHeight, audioclip, file_out, nAttempts=3):
    for attempt in range(nAttempts):
        try:

            print('stage 1')
            finalVideo = concatenate_videoclips(clips, method='compose')
            if PMV.Configuration.cropVidBool == True:
                (w, h) = finalVideo.size
                print(PMV.Configuration.cropVidFraction, int(sampleHeight * PMV.Configuration.cropVidFraction), int((1 - PMV.Configuration.cropVidFraction) * sampleHeight), w, h)
                finalVideo = finalVideo.crop(height=int(round((1 - PMV.Configuration.cropVidFraction*2) * sampleHeight, 0)), width = w, x_center=w/2, y_center=h/2)

            print('stage 2')
            finalVideo.volumex(0)

            print('stage 3')

            # final_audio = CompositeAudioClip([finalVideo.audio.afx(volumex, 2), audioclip.afx(volumex, 0.5)])
            finalVideo2 = finalVideo.set_audio(audioclip)

            print('stage 4')
            finalVideo2a = fadeout(finalVideo2, 1, final_color=None)
            finalVideo2c = fadein(finalVideo2a, 1, initial_color=None)

            if PMV.Configuration.addIntro:
                introVideo = getIntroVid(PMV.DirectoryFile_Info.finalVidName, PMV.Configuration.cropVidFraction, sampleHeight,
                                         PMV.DirectoryFile_Info.introVidDir, PMV.Configuration.userName)
                finalVideo3 = concatenate_videoclips([introVideo, finalVideo2c], method='compose')
            else:
                finalVideo3 = finalVideo2c

            print('stage 4')
            print('stage 5')

            finalVideo3.write_videofile(file_out, threads=4, fps=30)
        except OSError as OSErrorMessage:
            print("OSError retrying - Attempt: ", attempt)
            print(OSErrorMessage)
            pass
        else:
            break
    print('stage 6')
