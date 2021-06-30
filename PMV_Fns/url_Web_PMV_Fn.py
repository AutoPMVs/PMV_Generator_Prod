from pydub import AudioSegment
from PMV_Fns.functions import getHighValues2
from PMV_Fns.functions import getElementDiff
from PMV_Fns.functions import videoSplitsUseClassifyModel
from PMV_Fns.functions import videoSplits
from PMV_Fns.functions import getVideoData
from PMV_Fns.functions import processVideoData
from PMV_Fns.functions import concatonateFinalVideo
import time
import pandas as pd
import subprocess
from Admin_Fns.allPaths import PathList
from PMV_Fns.processMusicFile import inputMusic
from PMV_Fns.selectFunctions import filterForSelection
from PMV_Fns.selectFunctions import downloadVids
from PMV_Fns.selectFunctions import getMusic
from PMV_Fns.selectFunctions import getMusicFromURL
import os
from Classify_Model.ClassifyVideo import loadClassifyPickleFile
from Admin_Fns.getVideoInfoFn import exportUpdatedFile
from Admin_Fns.getVideoInfoFn import updateDF

beepDur = 500  # milliseconds
beepFreq = 440  # Hz

AudioSegment.converter = PathList["AudioSegmentPath"]
AudioSegment.ffmpeg = PathList["AudioSegmentPath"]
AudioSegment.ffprobe = PathList["AudioSegmentPath"]



def genPMVs(PMV, sampleHeight, sampleWidth, df_Video_Data):

    if len(PMV.URL_Data.musicURL)>0:
        musicName = getMusicFromURL(PMV.URL_Data.musicURL, PMV.DirectoryFile_Info.musicDir, PMV.DirectoryFile_Info.musicVidDir, PMV.Music_Info.musicVideoBool)
        artistName=""
        musicFileName = musicName
    elif PMV.DirectoryFile_Info.musicFilePath != "":
        musicTitle = os.path.basename(PMV.DirectoryFile_Info.musicFilePath).replace(".mp4", "")
        PMV.DirectoryFile_Info.customMusicDir = PMV.DirectoryFile_Info.musicFilePath.replace(
            os.path.basename(PMV.DirectoryFile_Info.musicFilePath), "")
        PMV.DirectoryFile_Info.customMusicVidDir = PMV.DirectoryFile_Info.customMusicDir
        musicName = musicTitle
        musicFileName = musicTitle
        artistName = ""
    else:
        musicName, musicFileName, artistName = getMusic(PMV.Music_Info.musicName, PMV.Music_Info.musicVideoBool)


    PMV.Music_Info.musicName = musicFileName

    if PMV.Configuration.UseClassifyModel:
        allVideoDict = loadClassifyPickleFile(PMV.DirectoryFile_Info.ModelStorageDir)
    else:
        allVideoDict = dict()

    if len(PMV.URL_Data.videoURLs) > 0:
        downloadVids(PMV.URL_Data.videoURLs, outputDir=PMV.DirectoryFile_Info.vidDownloadDir)
    else:
        selectedVidUrls = filterForSelection(df_Video_Data, includeCategories=PMV.Video_Select.includeCategories, includePornstars=PMV.Video_Select.includePornstars,
                                             includeChannels=PMV.Video_Select.includeChannels, excludeCategories=PMV.Video_Select.excludeCategories,
                                             excludePornstars=PMV.Video_Select.excludePornstars, excludeChannels=PMV.Video_Select.excludeChannels,
                                             orCategories=PMV.Video_Select.orCategories, orPornstars=PMV.Video_Select.orPornstars,
                                             number=PMV.Configuration.videoNumber, maxDuration=PMV.Configuration.maxVidLength,
                                             minDuration=PMV.Configuration.minVidLength, returnDataframe = False,
                                             classifiedOnly=PMV.Video_Select.classifiedOnly, allVideoDict=allVideoDict)
        downloadVids(selectedVidUrls, outputDir=PMV.DirectoryFile_Info.vidDownloadDir)

        # df_videos_filtered = getCustom(df_Video_Data, includeCategories=PMV.Video_Select.includeCategories, includePornstars=PMV.Video_Select.includePornstars,
        #                                includeChannels=PMV.Video_Select.includeChannels, excludeCategories=PMV.Video_Select.excludeCategories,
        #                                excludePornstars=PMV.Video_Select.excludePornstars, excludeChannels=PMV.Video_Select.excludeChannels,
        #                                orCategories=PMV.Video_Select.orCategories, orPornstars=PMV.Video_Select.orPornstars,
        #                                outputDir=PMV.DirectoryFile_Info.vidDownloadDir, number=PMV.Configuration.videoNumber,
        #                                maxDuration=PMV.Configuration.maxVidLength, minDuration=PMV.Configuration.minVidLength)


    print(AudioSegment.ffmpeg)

    ################################
    mp3_dir = PMV.DirectoryFile_Info.musicDir + PMV.Music_Info.musicName + '.mp4' # PMV.musicType
    ###############################

    if len(PMV.DirectoryFile_Info.finalVidName) == 0:
        PMV.DirectoryFile_Info.finalVidName = " ".join(PMV.Video_Select.includePornstars + PMV.Video_Select.includeChannels + PMV.Video_Select.includeCategories) + ' PMV - ' + musicName
        if len(artistName)>0:
            PMV.DirectoryFile_Info.finalVidName = PMV.DirectoryFile_Info.finalVidName + ' - ' + artistName
        if len(PMV.Configuration.userName) > 0 and PMV.Configuration.userName not in PMV.DirectoryFile_Info.finalVidName:
            PMV.DirectoryFile_Info.finalVidName = PMV.DirectoryFile_Info.finalVidName + ' - ' + PMV.Configuration.userName

    file_out = PMV.DirectoryFile_Info.finalVidDir + PMV.DirectoryFile_Info.finalVidName + '.mp4' #  filetypeout
    print(mp3_dir)
    mp3_dir = mp3_dir.replace('"', "'")
    mp3_dir = mp3_dir.replace('||', "_")

    reshaped_data, first_data, audioclip, ratio, bitrate, songStart, songEnd, songSections = inputMusic(mp3_dir, trimSong=PMV.Music_Info.trimSong, songStart=PMV.Music_Info.songStart, songEnd=PMV.Music_Info.songEnd, granularity=PMV.Configuration.granularity)
    PMV.Music_Info.songStart = songStart
    PMV.Music_Info.songEnd = songEnd
    diff_data = getElementDiff(reshaped_data)
    result = getHighValues2(reshaped_data, diff_data, PMV.Configuration.sd_scale, PMV.Configuration.nSplits, PMV.Configuration.granularity, PMV.Configuration.min_length)

    print('List of Indices of maximum element :', len(result))
    result.append(len(first_data) / ratio)

    videoData, origVidName, videoDicts = getVideoData(PMV, df_Video_Data, allVideoDict)
    videos, videoData = processVideoData(PMV, videoData, sampleWidth, sampleHeight, origVidName, df_Video_Data) #, PMV.Music_Info.musicVideoBool, selectedVids, PMV.Configuration.startTime, PMV.Configuration.subtractEnd)
    if PMV.Configuration.UseClassifyModel:
        clips = videoSplitsUseClassifyModel(result, videos, videoData, songSections,
                                            PMV.Configuration.granularity, PMV.Configuration.randomise, origVidName, videoDicts)
    else:
        clips = videoSplits(result, videos, videoData, first_data, bitrate, PMV.Configuration.granularity, PMV.Configuration.randomise, origVidName)
    concatonateFinalVideo(PMV, clips, sampleWidth, sampleHeight, audioclip, file_out, nAttempts = 3)

    i = 0
    while i < len(videos):
        videos[i].reader.close()
        del videos[i].reader
        del videos[i]
        i = i + 1

    del audioclip.reader
    del audioclip

    print('Finished!')
