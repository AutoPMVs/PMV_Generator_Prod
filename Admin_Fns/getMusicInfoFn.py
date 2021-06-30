from __future__ import unicode_literals
import random
import youtube_dl
import pandas as pd
from Admin_Fns.csvFunctions import getArtistList
from Admin_Fns.csvFunctions import reformatTitle
from Admin_Fns.allPaths import PathList
cookies = r"C:\Users\vince\Downloads\cookies.txt"

def splitURL(x):
    x2 = x.split("&", 1)[0]
    return x2

def initialise():
    df_All_Artists = pd.read_csv(PathList["ArtistListPath"])
    df_RemoveStrings = pd.read_excel(PathList["MusicDirPath"], sheet_name='Remove Strings')
    df_MusicList = pd.read_csv(PathList["combinedMusicListPath"])

    knownURLs = df_MusicList["url"].to_list()
    uniqArtists = pd.unique(df_All_Artists['Artist'].values.ravel('K'))
    removeStrings_List = df_RemoveStrings['Strings'].to_list()

    i = 0
    uniqArtistList = []
    while i < len(uniqArtists):
        try:
            uniqArtistList.append(str.title(uniqArtists[i]))
        except TypeError:
            pass
        i = i + 1

    removeStrings_List.sort(key=len, reverse=True)
    uniqArtistList.sort(key=len, reverse=True)

    uniqArtistListEdit = []
    for artist in uniqArtistList:
        if len(artist) < 6:
            uniqArtistListEdit.append(" " + artist)
            uniqArtistListEdit.append(artist + " ")
        else:
            uniqArtistListEdit.append(artist)

    ydl_opts = {'outtmpl': r'/test.%(ext)s',
                # r'C:/Users/vince/Pictures/Python/PMV_Generator/TempVids/%(title)s.%(ext)s',
                'format': 'bestaudio/best',
                'simulate': True,
                'dump_single_json': True,
                'writeinfojson': True}


    return df_MusicList, ydl_opts, uniqArtistList, knownURLs, removeStrings_List

def exportMusicList(musicList, outputPath, nArtist=5, dfMusicList=pd.DataFrame()):
    columnList = ['Name', 'Title']
    i = 0
    while i < nArtist:
        columnList.append('_Artist' + str(i + 1))
        i = i + 1
    columnList = columnList + ['url', 'Type', 'Lyric', 'Video', 'Christmas', 'Live', 'Remix', 'Cover', 'id', 'Start',
                               'End', 'Uploader', 'Duration']
    dfMusicListOut = pd.DataFrame(musicList, columns=columnList)
    # dfMusicListOut.columns = [columnList]

    if dfMusicList.shape[0]>0:
        dfMusicListColumns = dfMusicList.columns
        dfMusicListColumns = [col for col in dfMusicListColumns if "Unnamed:" not in col]
        dfMusicList = dfMusicList[dfMusicListColumns]
        dfMusicListOut = pd.concat([dfMusicList, dfMusicListOut], ignore_index=True, sort=False)
        dfMusicListOut = dfMusicListOut.drop_duplicates(subset=['url'], keep='first')
        dfMusicListOut.sort_values(by=['_Artist1', 'Title'], inplace=True)

    dfMusicListOut = dfMusicListOut.fillna('')
    dfMusicListOut = dfMusicListOut.replace('nan', '')
    dfMusicListOut = dfMusicListOut.replace('na', '')
    print(dfMusicListOut)
    dfMusicListOut.to_csv(outputPath, index=False, encoding='utf-8-sig')

def getMusicInfoFn(line, info_dict, knownArtists, uniqArtistList, removeStrings_List, title="", videoBool=0, lyricBool=1, christmasBool=0, liveBool=0, remixBool=0, startTime=0, endTime=0):

    try:

        try:
            title = str.title(str(info_dict['title']))
        except:
            title = ""

        try:
            id = info_dict['id'].replace("=","")
        except:
            id = ""

        try:
            if "&" in line:
                url = info_dict['webpage_url'].split("&", 1)[0]
            else:
                url = info_dict['webpage_url']
        except:
            if "&" in line:
                url = line.split("&", 1)[0]
            else:
                url = line

        try:
            uploader = str.title(str(info_dict['uploader']))
        except:
            uploader = ""

        try:
            duration = info_dict['duration']
        except:
            duration = ""

        name = title

        artistList = getArtistList(uniqArtistList, knownArtists, title, uploader)
        artistList.sort(key=len, reverse=True)
        title = reformatTitle(removeStrings_List, title, artistList)

        remix = 0
        video = 0
        lyric = 0
        cover = 0
        christmas = 0
        live = 0
        type = "Lyric"
        if "Remix" in str.title(name):
            remix = 1
        if "Lyric" in str.title(name):
            lyric = 1
        if ("Video" in str.title(name) and lyric == 0) or ('Official Video' in str.title(name) or 'Official Music Video' in str.title(name)) and ('Lyric' not in str.title(name) and 'Vertical' not in str.title(name)):
            type = "Video"
            video = 1
        else:
            lyric = 1
        if "Cover" in str.title(name):
            cover = 1
        if "Christmas" in str.title(name) or "Santa" in str.title(name) or "Winter" in str.title(
                name) or "Snow" in str.title(name) or "Xmas" in str.title(name):
            christmas = 1

        if videoBool == 1:
            video = 1
            lyric = 0
        if lyricBool == 1:
            video = 0
            lyric = 1
        if christmasBool == 1:
            christmas = 1
        if liveBool == 1:
            live = 1
        if remixBool == 1:
            remix = 1

        return [name, title] + artistList + [url, type, lyric, video, christmas, live, remix, cover, id, startTime, endTime, uploader, duration]

    except youtube_dl.utils.DownloadError or TypeError:

        print("Error adding manual details")
        print('')

        url = line
        # title = df_download.loc[iURL]['Title']
        uploader = "unknown"
        id = ""
        duration = 0
        print(url, title)

        name = title

        artistList = getArtistList(uniqArtistList, knownArtists, title, uploader)
        artistList.sort(key=len, reverse=True)
        title = reformatTitle(removeStrings_List, title, artistList)

        remix = 0
        video = 0
        lyric = 0
        cover = 0
        christmas = 0
        live = 0
        type = "Lyric"
        if "Remix" in str.title(name):
            remix = 1
        if "Lyric" in str.title(name):
            lyric = 1
        if "Video" in str.title(name) and lyric == 0:
            type = "Video"
            video = 1
        else:
            lyric = 1
        if "Cover" in str.title(name):
            cover = 1
        if "Christmas" in str.title(name) or "Santa" in str.title(name) or "Winter" in str.title(
                name) or "Snow" in str.title(name) or "Xmas" in str.title(name):
            christmas = 1

        return [name, title] + artistList + [url, type, lyric, video, christmas, live, remix, cover, id, startTime,endTime, uploader, duration]
        pass