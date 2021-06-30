import string
import os
import subprocess
import pandas as pd
import youtube_dl
import random
import _pickle as pickle
import xlrd
from moviepy.editor import VideoFileClip
import time
from Admin_Fns.allPaths import PathList
from Admin_Fns.getVideoInfoFn import exportUpdatedFile
from Admin_Fns.getVideoInfoFn import updateDF
from Admin_Fns.getMusicInfoFn import initialise
from Admin_Fns.getMusicInfoFn import getMusicInfoFn
from Admin_Fns.getMusicInfoFn import exportMusicList
pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)


def getMusic(musicName, musicVideoBool): # , artistName):
    print("Downloading Music... " + musicName)
    print(musicVideoBool)
    df_music = pd.read_csv(PathList["combinedMusicListPath"])

    print(df_music)
    musicDir = PathList["defaultMusicDownloadPath"]
    musicVidDir = PathList["defaultMusicVidDownloadPath"]


    if len(musicName)>0:
        df_music = df_music.loc[(df_music['Title'].isin([musicName]))]
        print(df_music)
    music_url = df_music['url'].tolist()

    if len(music_url) > 1:
        # df_music = df_music.loc[(df_music['Artist'].isin(artistName))]
        if musicVideoBool:
            df_music = df_music.loc[(df_music['Type'].isin(["Video"]))]
        else:
            df_music = df_music.loc[(df_music['Type'].isin(["Lyric"]))]


    music_url = df_music['url'].tolist()
    music_artist = df_music['_Artist1'].tolist()
    musicURL = music_url[0]
    music_artist = music_artist[0]

    musicFileName = getMusicFromURL(musicURL, musicDir, musicVidDir, musicVideoBool)
    
    return musicName, musicFileName, music_artist


def getMusicFromURL(musicURL, musicDir, musicVidDir, musicVideoBool):

    ydl_opts = {'outtmpl': musicDir + '%(title)s' + '.%(ext)s',
                'videoformat': "mp4",
                'format': 'best/mp4',
                'playlist': 'no'}#,
                # 'cookiefile': cookies} #'best'} #

    # if musicName == 'White Girl Pussy':
    # try:
    print('Downloading music with ydl...')
    for attempt in range(3):
        try:
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                ydl.cache.remove()
                ydl.download([musicURL])
            break
        except:
            print("Error retrying - Attempt: ", attempt)
            pass

    ydl.cache.remove()
    info_dict = ydl.extract_info(musicURL, download=False)
    musicName = ydl.prepare_filename(info_dict)
    musicName = os.path.basename(musicName)
    musicName = musicName.replace(".mp4", "")

    if musicVideoBool:
        ydl_opts = {'outtmpl': musicVidDir + '%(title)s' + '.%(ext)s',
                    'videoformat': "mp4",
                    'format': 'bestvideo/mp4',
                    'playlist': 'no'}#,
        print('Downloading video with ydl...')
        for attempt in range(3):
            try:
                with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                    ydl.cache.remove()
                    ydl.download([musicURL])
                break
            except:
                print("Error retrying - Attempt: ", attempt)
                pass
        ydl.cache.remove()
        info_dict = ydl.extract_info(musicURL, download=False)
        musicVidName = ydl.prepare_filename(info_dict)
        extension = os.path.splitext(musicVidName)[1]
        if extension != ".mp4":
            convertFile(musicVidName)

    df_MusicList, ydl_opts, uniqArtistList, knownURLs, removeStrings_List = initialise()
    if musicURL not in knownURLs:
        musicList=[]
        resultList = getMusicInfoFn(musicURL, info_dict, [], uniqArtistList, removeStrings_List)
        musicList.append(resultList)
        exportMusicList(musicList, PathList["combinedMusicListPath"], dfMusicList=df_MusicList)

    return musicName

def convertFile(inputpath, targetFormat=".mp4", outputPath="", deleteWhenComplete=False):
    print(inputpath)
    if len(outputPath)==0:
        outputPath = os.path.split(inputpath)[0]
    outputName = os.path.splitext(os.path.split(inputpath)[1])[0]+ targetFormat
    clip = VideoFileClip(inputpath)
    if os.path.isfile(outputPath + "/" + outputName)==False:
        clip.write_videofile(outputPath + "/" + outputName)
    if deleteWhenComplete:
        os.remove(inputpath)

def getKey(x):

    inputVideoName = x["Title"]
    vidId = x["id"]

    inputVid = inputVideoName.replace(r"’", r"'")
    inputVid = inputVid.replace("&nbsp", r" ")
    printable = set(string.printable)
    inputVidIter = filter(lambda x: x in printable, inputVid)
    inputVid = "".join(inputVidIter)

    dictKey = str(inputVid) + " - " + str(vidId)

    return dictKey

def getClassifiedList(dfVideos, allVideoDict):
    dfVideos["Key"] = dfVideos.apply(lambda x: getKey(x), axis=1)

    videoDict = allVideoDict

    keyList=[]
    for key in videoDict:
        keyList.append(key)

    dfVideos = dfVideos[dfVideos["Key"].isin(keyList)]

    return dfVideos


def filterForSelection(df_videos_all, includeCategories = [], includePornstars = [],
                       includeChannels = [], excludeCategories = [], excludePornstars = [],
                       excludeChannels = [],  orCategories = True, orPornstars = True,
                       number = 10, minDuration = 60, maxDuration = 1200, returnDataframe = False,
                       classifiedOnly = False, allVideoDict=None):
    if allVideoDict==None:
        allVideoDict=dict()

    df_videos_all = df_videos_all[pd.notnull(df_videos_all['Title'])]

    df_videos_all['Duration'] = df_videos_all['Duration'].fillna((minDuration+maxDuration)/2)

    df_videos_all = df_videos_all[df_videos_all['Duration'] > minDuration]
    df_videos_all = df_videos_all[df_videos_all['Duration'] < maxDuration]
    df_videos = df_videos_all

    if len(includeCategories)>0:
        if orCategories == True:
            df_videos = df_videos.loc[(df_videos['_Cat1'].isin(includeCategories)) | (df_videos['_Cat2'].isin(includeCategories)) | (df_videos['_Cat3'].isin(includeCategories)) | (df_videos['_Cat4'].isin(includeCategories)) | (df_videos['_Cat5'].isin(includeCategories)) | (df_videos['_Cat6'].isin(includeCategories)) | (df_videos['_Cat7'].isin(includeCategories)) | (df_videos['_Cat8'].isin(includeCategories)) | (df_videos['_Cat9'].isin(includeCategories)) | (df_videos['_Cat10'].isin(includeCategories)) | (df_videos['_Cat11'].isin(includeCategories)) | (df_videos['_Cat12'].isin(includeCategories)) | (df_videos['_Cat13'].isin(includeCategories)) | (df_videos['_Cat14'].isin(includeCategories)) | (df_videos['_Cat15'].isin(includeCategories)) | (df_videos['_Cat16'].isin(includeCategories)) | (df_videos['_Cat17'].isin(includeCategories)) | (df_videos['_Cat18'].isin(includeCategories)) | (df_videos['_Cat19'].isin(includeCategories)) | (df_videos['_Cat20'].isin(includeCategories)) | (df_videos['_Cat21'].isin(includeCategories)) | (df_videos['_Cat22'].isin(includeCategories)) | (df_videos['_Cat23'].isin(includeCategories)) | (df_videos['_Cat24'].isin(includeCategories)) | (df_videos['_Cat25'].isin(includeCategories)) | (df_videos['_Cat26'].isin(includeCategories)) | (df_videos['_Cat27'].isin(includeCategories)) | (df_videos['_Cat28'].isin(includeCategories)) | (df_videos['_Cat29'].isin(includeCategories)) | (df_videos['_Cat30'].isin(includeCategories)) | (df_videos['_Cat31'].isin(includeCategories)) | (df_videos['_Cat32'].isin(includeCategories)) | (df_videos['_Cat33'].isin(includeCategories)) | (df_videos['_Cat34'].isin(includeCategories)) | (df_videos['_Cat35'].isin(includeCategories)) | (df_videos['_Cat36'].isin(includeCategories)) | (df_videos['_Cat37'].isin(includeCategories)) | (df_videos['_Cat38'].isin(includeCategories)) | (df_videos['_Cat39'].isin(includeCategories)) | (df_videos['_Cat40'].isin(includeCategories))]
            # df_videos = df_videos.loc[(df_videos[catList].isin(includeCategories))]
        else:
            for cat in includeCategories:
                df_videos = df_videos.loc[(df_videos['_Cat1'].isin([cat])) | (df_videos['_Cat2'].isin([cat])) | (df_videos['_Cat3'].isin([cat])) | (df_videos['_Cat4'].isin([cat])) | (df_videos['_Cat5'].isin([cat])) | (df_videos['_Cat6'].isin([cat])) | (df_videos['_Cat7'].isin([cat])) | (df_videos['_Cat8'].isin([cat])) | (df_videos['_Cat9'].isin([cat])) | (df_videos['_Cat10'].isin([cat])) | (df_videos['_Cat11'].isin([cat])) | (df_videos['_Cat12'].isin([cat])) | (df_videos['_Cat13'].isin([cat])) | (df_videos['_Cat14'].isin([cat])) | (df_videos['_Cat15'].isin([cat])) | (df_videos['_Cat16'].isin([cat])) | (df_videos['_Cat17'].isin([cat])) | (df_videos['_Cat18'].isin([cat])) | (df_videos['_Cat19'].isin([cat])) | (df_videos['_Cat20'].isin([cat])) | (df_videos['_Cat21'].isin([cat])) | (df_videos['_Cat22'].isin([cat])) | (df_videos['_Cat23'].isin([cat])) | (df_videos['_Cat24'].isin([cat])) | (df_videos['_Cat25'].isin([cat])) | (df_videos['_Cat26'].isin([cat])) | (df_videos['_Cat27'].isin([cat])) | (df_videos['_Cat28'].isin([cat])) | (df_videos['_Cat29'].isin([cat])) | (df_videos['_Cat30'].isin([cat])) | (df_videos['_Cat31'].isin([cat])) | (df_videos['_Cat32'].isin([cat])) | (df_videos['_Cat33'].isin([cat])) | (df_videos['_Cat34'].isin([cat])) | (df_videos['_Cat35'].isin([cat])) | (df_videos['_Cat36'].isin([cat])) | (df_videos['_Cat37'].isin([cat])) | (df_videos['_Cat38'].isin([cat])) | (df_videos['_Cat39'].isin([cat])) | (df_videos['_Cat40'].isin([cat]))]

    if len(excludeCategories)>0:
        df_videos = df_videos.loc[(~df_videos['_Cat1'].isin(excludeCategories)) & (~df_videos['_Cat2'].isin(excludeCategories)) & (~df_videos['_Cat3'].isin(excludeCategories)) & (~df_videos['_Cat4'].isin(excludeCategories)) & (~df_videos['_Cat5'].isin(excludeCategories)) & (~df_videos['_Cat6'].isin(excludeCategories)) & (~df_videos['_Cat7'].isin(excludeCategories)) & (~df_videos['_Cat8'].isin(excludeCategories)) & (~df_videos['_Cat9'].isin(excludeCategories)) & (~df_videos['_Cat10'].isin(excludeCategories)) & (~df_videos['_Cat11'].isin(excludeCategories)) & (~df_videos['_Cat12'].isin(excludeCategories)) & (~df_videos['_Cat13'].isin(excludeCategories)) & (~df_videos['_Cat14'].isin(excludeCategories)) & (~df_videos['_Cat15'].isin(excludeCategories)) & (~df_videos['_Cat16'].isin(excludeCategories)) & (~df_videos['_Cat17'].isin(excludeCategories)) & (~df_videos['_Cat18'].isin(excludeCategories)) & (~df_videos['_Cat19'].isin(excludeCategories)) & (~df_videos['_Cat20'].isin(excludeCategories)) & (~df_videos['_Cat21'].isin(excludeCategories)) & (~df_videos['_Cat22'].isin(excludeCategories)) & (~df_videos['_Cat23'].isin(excludeCategories)) & (~df_videos['_Cat24'].isin(excludeCategories)) & (~df_videos['_Cat25'].isin(excludeCategories)) & (~df_videos['_Cat26'].isin(excludeCategories)) & (~df_videos['_Cat27'].isin(excludeCategories)) & (~df_videos['_Cat28'].isin(excludeCategories)) & (~df_videos['_Cat29'].isin(excludeCategories)) & (~df_videos['_Cat30'].isin(excludeCategories)) & (~df_videos['_Cat31'].isin(excludeCategories)) & (~df_videos['_Cat32'].isin(excludeCategories)) & (~df_videos['_Cat33'].isin(excludeCategories)) & (~df_videos['_Cat34'].isin(excludeCategories)) & (~df_videos['_Cat35'].isin(excludeCategories)) & (~df_videos['_Cat36'].isin(excludeCategories)) & (~df_videos['_Cat37'].isin(excludeCategories)) & (~df_videos['_Cat38'].isin(excludeCategories)) & (~df_videos['_Cat39'].isin(excludeCategories)) & (~df_videos['_Cat40'].isin(excludeCategories))]

    if len(includePornstars)>0:
        if orPornstars == True:
            df_videos = df_videos.loc[(df_videos['_Pornstar1'].isin(includePornstars)) | (df_videos['_Pornstar2'].isin(includePornstars)) | (df_videos['_Pornstar3'].isin(includePornstars)) | (df_videos['_Pornstar4'].isin(includePornstars)) | (df_videos['_Pornstar5'].isin(includePornstars))]
        else:
            for pornstar in includePornstars:
                df_videos = df_videos.loc[(df_videos['_Pornstar1'].isin([pornstar])) | (df_videos['_Pornstar2'].isin([pornstar])) | (df_videos['_Pornstar3'].isin([pornstar])) | (df_videos['_Pornstar4'].isin([pornstar])) | (df_videos['_Pornstar5'].isin([pornstar]))]

    if len(excludePornstars)>0:
        df_videos = df_videos.loc[(~df_videos['_Pornstar1'].isin(excludePornstars)) & (~df_videos['_Pornstar2'].isin(excludePornstars)) & (~df_videos['_Pornstar3'].isin(excludePornstars)) & (~df_videos['_Pornstar4'].isin(excludePornstars)) & (~df_videos['_Pornstar5'].isin(excludePornstars))]

    if len(includeChannels)>0:
            df_videos = df_videos.loc[(df_videos['_Channel'].isin(includeChannels)) | (df_videos['_Channel_Group'].isin(includeChannels))]

    if len(excludeChannels)>0:
        df_videos = df_videos.loc[(~df_videos['_Channel'].isin(excludeChannels)) & (~df_videos['_Channel_Group'].isin(excludeChannels))]

    if classifiedOnly:
        df_videos = getClassifiedList(df_videos, allVideoDict)

    if number>df_videos.shape[0]:
        number = df_videos.shape[0]
    df_videos_filtered = df_videos.sample(number)
    selectedVids = df_videos_filtered

    selectedVidUrls = selectedVids['url'].tolist()

    if returnDataframe:
        return df_videos
    else:
        return selectedVidUrls

def downloadVids(selectedVidUrls, outputDir):
    print("Downloading Videos..")

    # deck = [k for k in range(len(selectedVidUrls))]
    # random.shuffle(deck)
    #
    # if number < len(deck):
    #     lenDeck = number
    # else:
    #     lenDeck = len(deck)
    # i = 0
    # while i < lenDeck:
    #     time.sleep(2)
    #     line = selectedVidUrls[deck[i]]
    #     print(line)
    #     subprocess.call([PathList["pythonPath"], PathList["downloadVidPath"], selectDir, line])
    #     i = i + 1

    for line in selectedVidUrls:
        time.sleep(2)
        # line = selectedVidUrls[deck[i]]

        print(line)
        df_videos = pd.read_csv(PathList["combinedPornListPath"])
        df_videos = updateDF(df_videos, line)
        iAttempt = 0
        while iAttempt<5:
            try:
                exportUpdatedFile(df_videos, PathList["combinedPornListPath"])
                break
            except:
                print("File unavailable. Attempt ", iAttempt)
                time.sleep(10)
                pass
            iAttempt = iAttempt +1
        subprocess.call([PathList["pythonPath"], PathList["downloadVidPath"], outputDir, line])


# def getCustom(df_videos_all, includeCategories = [], includePornstars = [], includeChannels = [], excludeCategories = [], excludePornstars = [], excludeChannels = [],  orCategories = True, orPornstars = True, outputDir = 'Videos1', number = 10, minDuration = 60, maxDuration = 1200):
#     print("Downloading Videos..")
#
#     df_videos_all = df_videos_all[pd.notnull(df_videos_all['Title'])]
#
#     df_videos_all['Duration'] = df_videos_all['Duration'].fillna((minDuration+maxDuration)/2)
#
#     df_videos_all = df_videos_all[df_videos_all['Duration'] > minDuration]
#     df_videos_all = df_videos_all[df_videos_all['Duration'] < maxDuration]
#     df_videos = df_videos_all
#
#     if len(includeCategories) > 0:
#         if orCategories == True:
#             df_videos = df_videos.loc[(df_videos['_Cat1'].isin(includeCategories)) | (df_videos['_Cat2'].isin(includeCategories)) | (df_videos['_Cat3'].isin(includeCategories)) | (df_videos['_Cat4'].isin(includeCategories)) | (df_videos['_Cat5'].isin(includeCategories)) | (df_videos['_Cat6'].isin(includeCategories)) | (df_videos['_Cat7'].isin(includeCategories)) | (df_videos['_Cat8'].isin(includeCategories)) | (df_videos['_Cat9'].isin(includeCategories)) | (df_videos['_Cat10'].isin(includeCategories)) | (df_videos['_Cat11'].isin(includeCategories)) | (df_videos['_Cat12'].isin(includeCategories)) | (df_videos['_Cat13'].isin(includeCategories)) | (df_videos['_Cat14'].isin(includeCategories)) | (df_videos['_Cat15'].isin(includeCategories)) | (df_videos['_Cat16'].isin(includeCategories)) | (df_videos['_Cat17'].isin(includeCategories)) | (df_videos['_Cat18'].isin(includeCategories)) | (df_videos['_Cat19'].isin(includeCategories)) | (df_videos['_Cat20'].isin(includeCategories)) | (
#                 df_videos['_Cat21'].isin(includeCategories)) | (df_videos['_Cat22'].isin(includeCategories)) | (df_videos['_Cat23'].isin(includeCategories)) | (df_videos['_Cat24'].isin(includeCategories)) | (df_videos['_Cat25'].isin(includeCategories)) | (df_videos['_Cat26'].isin(includeCategories)) | (df_videos['_Cat27'].isin(includeCategories)) | (df_videos['_Cat28'].isin(includeCategories)) | (df_videos['_Cat29'].isin(includeCategories)) | (df_videos['_Cat30'].isin(includeCategories)) | (df_videos['_Cat31'].isin(includeCategories)) | (df_videos['_Cat32'].isin(includeCategories)) | (df_videos['_Cat33'].isin(includeCategories)) | (df_videos['_Cat34'].isin(includeCategories)) | (df_videos['_Cat35'].isin(includeCategories)) | (df_videos['_Cat36'].isin(includeCategories)) | (df_videos['_Cat37'].isin(includeCategories)) | (df_videos['_Cat38'].isin(includeCategories)) | (df_videos['_Cat39'].isin(includeCategories)) | (df_videos['_Cat40'].isin(includeCategories))]
#             # df_videos = df_videos.loc[(df_videos[catList].isin(includeCategories))]
#         else:
#             for cat in includeCategories:
#                 df_videos = df_videos.loc[
#                     (df_videos['_Cat1'].isin([cat])) | (df_videos['_Cat2'].isin([cat])) | (df_videos['_Cat3'].isin([cat])) | (df_videos['_Cat4'].isin([cat])) | (df_videos['_Cat5'].isin([cat])) | (df_videos['_Cat6'].isin([cat])) | (df_videos['_Cat7'].isin([cat])) | (df_videos['_Cat8'].isin([cat])) | (df_videos['_Cat9'].isin([cat])) | (df_videos['_Cat10'].isin([cat])) | (df_videos['_Cat11'].isin([cat])) | (df_videos['_Cat12'].isin([cat])) | (df_videos['_Cat13'].isin([cat])) | (df_videos['_Cat14'].isin([cat])) | (df_videos['_Cat15'].isin([cat])) | (df_videos['_Cat16'].isin([cat])) | (df_videos['_Cat17'].isin([cat])) | (df_videos['_Cat18'].isin([cat])) | (df_videos['_Cat19'].isin([cat])) | (df_videos['_Cat20'].isin([cat])) | (df_videos['_Cat21'].isin([cat])) | (df_videos['_Cat22'].isin([cat])) | (df_videos['_Cat23'].isin([cat])) | (df_videos['_Cat24'].isin([cat])) | (df_videos['_Cat25'].isin([cat])) | (df_videos['_Cat26'].isin([cat])) | (df_videos['_Cat27'].isin([cat])) | (
#                         df_videos['_Cat28'].isin([cat])) | (df_videos['_Cat29'].isin([cat])) | (df_videos['_Cat30'].isin([cat])) | (df_videos['_Cat31'].isin([cat])) | (df_videos['_Cat32'].isin([cat])) | (df_videos['_Cat33'].isin([cat])) | (df_videos['_Cat34'].isin([cat])) | (df_videos['_Cat35'].isin([cat])) | (df_videos['_Cat36'].isin([cat])) | (df_videos['_Cat37'].isin([cat])) | (df_videos['_Cat38'].isin([cat])) | (df_videos['_Cat39'].isin([cat])) | (df_videos['_Cat40'].isin([cat]))]
#
#     if len(excludeCategories) > 0:
#         df_videos = df_videos.loc[
#             (~df_videos['_Cat1'].isin(excludeCategories)) & (~df_videos['_Cat2'].isin(excludeCategories)) & (~df_videos['_Cat3'].isin(excludeCategories)) & (~df_videos['_Cat4'].isin(excludeCategories)) & (~df_videos['_Cat5'].isin(excludeCategories)) & (~df_videos['_Cat6'].isin(excludeCategories)) & (~df_videos['_Cat7'].isin(excludeCategories)) & (~df_videos['_Cat8'].isin(excludeCategories)) & (~df_videos['_Cat9'].isin(excludeCategories)) & (~df_videos['_Cat10'].isin(excludeCategories)) & (~df_videos['_Cat11'].isin(excludeCategories)) & (~df_videos['_Cat12'].isin(excludeCategories)) & (~df_videos['_Cat13'].isin(excludeCategories)) & (~df_videos['_Cat14'].isin(excludeCategories)) & (~df_videos['_Cat15'].isin(excludeCategories)) & (~df_videos['_Cat16'].isin(excludeCategories)) & (~df_videos['_Cat17'].isin(excludeCategories)) & (~df_videos['_Cat18'].isin(excludeCategories)) & (~df_videos['_Cat19'].isin(excludeCategories)) & (~df_videos['_Cat20'].isin(excludeCategories)) & (
#                 ~df_videos['_Cat21'].isin(excludeCategories)) & (~df_videos['_Cat22'].isin(excludeCategories)) & (~df_videos['_Cat23'].isin(excludeCategories)) & (~df_videos['_Cat24'].isin(excludeCategories)) & (~df_videos['_Cat25'].isin(excludeCategories)) & (~df_videos['_Cat26'].isin(excludeCategories)) & (~df_videos['_Cat27'].isin(excludeCategories)) & (~df_videos['_Cat28'].isin(excludeCategories)) & (~df_videos['_Cat29'].isin(excludeCategories)) & (~df_videos['_Cat30'].isin(excludeCategories)) & (~df_videos['_Cat31'].isin(excludeCategories)) & (~df_videos['_Cat32'].isin(excludeCategories)) & (~df_videos['_Cat33'].isin(excludeCategories)) & (~df_videos['_Cat34'].isin(excludeCategories)) & (~df_videos['_Cat35'].isin(excludeCategories)) & (~df_videos['_Cat36'].isin(excludeCategories)) & (~df_videos['_Cat37'].isin(excludeCategories)) & (~df_videos['_Cat38'].isin(excludeCategories)) & (~df_videos['_Cat39'].isin(excludeCategories)) & (~df_videos['_Cat40'].isin(excludeCategories))]
#
#     if len(includePornstars) > 0:
#         if orPornstars == True:
#             df_videos = df_videos.loc[(df_videos['_Pornstar1'].isin(includePornstars)) | (df_videos['_Pornstar2'].isin(includePornstars)) | (df_videos['_Pornstar3'].isin(includePornstars)) | (df_videos['_Pornstar4'].isin(includePornstars)) | (df_videos['_Pornstar5'].isin(includePornstars))]
#         else:
#             for pornstar in includePornstars:
#                 df_videos = df_videos.loc[(df_videos['_Pornstar1'].isin([pornstar])) | (df_videos['_Pornstar2'].isin([pornstar])) | (df_videos['_Pornstar3'].isin([pornstar])) | (df_videos['_Pornstar4'].isin([pornstar])) | (df_videos['_Pornstar5'].isin([pornstar]))]
#     # print(df_videos)
#
#     if len(excludePornstars) > 0:
#         df_videos = df_videos.loc[(~df_videos['_Pornstar1'].isin(excludePornstars)) & (~df_videos['_Pornstar2'].isin(excludePornstars)) & (~df_videos['_Pornstar3'].isin(excludePornstars)) & (~df_videos['_Pornstar4'].isin(excludePornstars)) & (~df_videos['_Pornstar5'].isin(excludePornstars))]
#
#     if len(includeChannels) > 0:
#         df_videos = df_videos.loc[(df_videos['_Channel'].isin(includeChannels)) | (df_videos['_Channel_Group'].isin(includeChannels))]
#     # print(df_videos)
#
#     if len(excludeChannels) > 0:
#         df_videos = df_videos.loc[(~df_videos['_Channel'].isin(excludeChannels)) & (~df_videos['_Channel_Group'].isin(excludeChannels))]
#
#     selectedVids = df_videos
#     # print(selectedVids)
#
#     selectedVidUrls = selectedVids['url'].tolist()
#
#     deck = [k for k in range(len(selectedVidUrls))]
#     random.shuffle(deck)
#
#     if number < len(deck):
#         lenDeck = number
#     else:
#         lenDeck = len(deck)
#     i = 0
#     while i < lenDeck:
#         time.sleep(2)
#         line = selectedVidUrls[deck[i]]
#
#         print(line)
#         df_videos = pd.read_csv(PathList["combinedPornListPath"])
#         df_videos = updateDF(df_videos, line)
#         iAttempt = 0
#         while iAttempt<5:
#             try:
#                 exportUpdatedFile(df_videos, PathList["combinedPornListPath"])
#                 break
#             except:
#                 print("File unavailable. Attempt ", iAttempt)
#                 time.sleep(10)
#                 pass
#             iAttempt = iAttempt +1
#         subprocess.call([PathList["pythonPath"], PathList["downloadVidPath"], outputDir, line])
#         i = i + 1
#
#     return df_videos_all