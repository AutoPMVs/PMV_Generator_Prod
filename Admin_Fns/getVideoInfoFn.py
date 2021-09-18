from __future__ import unicode_literals
import math
import time
import requests
from bs4 import BeautifulSoup, SoupStrainer
import random
import youtube_dl
import pandas as pd
import cloudscraper
from Admin_Fns.csvFunctions import title_to_cat
from Admin_Fns.csvFunctions import catSorting
from Admin_Fns.csvFunctions import title_to_pornstar
from Admin_Fns.csvFunctions import pornstar_sorting
from Admin_Fns.csvFunctions import groupCategories
from Admin_Fns.csvFunctions import groupChannels
from Admin_Fns.csvFunctions import remove_PS_Cats
from Admin_Fns.csvFunctions import getProxyChannel
from Admin_Fns.csvFunctions import getWebsite
from Admin_Fns.allPaths import PathList
import math as m
# cookies = PathList["cookiePath"]

def groupAndSortInputs(title, id, url, tags, categories, uploader, upload_date, duration, view_count, like_count, dislike_count, ext, fps, height, width,
                       videoList, autoAssignStartTimes =True, startTimeMain=30, endTimeMain=20, pornstarList=[], searchTitleTags=[], includeGroupedChannels=[],
                       includeGroupedCats=[], excludeGroupedCats=[], knownCatList=[], proxyChannels=[], channelTimings_df=[], groupChannelTimings_df=[],
                       startList=[], endList=[], iURL=0, nCat=40, nPornstar=5,  customPornstar=[], excludeTags=[], minDuration=0, knownChannel="", errorMessage=""):
    knownCategories = knownCatList


    removePS_strings = ['Sex', 'Bo', 'Pornstar', 'Cum', 'Anal', 'Milf', 'Wife', 'Bedroom', 'Big ass', 'Cuckold',
                        'Sharing', 'Big tits', 'Cheating', 'Watching', 'Housewife', 'nan', '0', 'Bbc', 'Jordan']
    for remPS in removePS_strings:
        pornstarList = [x for x in pornstarList if x != remPS]
    # else:
    #     knownCategories = []

    if knownChannel != "":
        if str(knownChannel)!='nan':
            if uploader == "" and len(knownChannel) > 0:
                uploader = str.title(str(knownChannel))

    catList = []
    psList = []
    categories = categories + tags
    categories = list(dict.fromkeys(categories))
    # print(catList)
    # print(categories)

    catList = title_to_cat(searchTitleTags, title, catList)
    # print("Cats from title")
    # print(catList)
    catList = catList + categories + knownCategories
    # print(catList)
    sortedLists = catSorting(catList, nCat, pornstarList, psList)
    catList = sortedLists[0]
    # print(catList)

    psList = sortedLists[1]
    psList = title_to_pornstar(pornstarList, psList, title, uploader)
    psList = psList + customPornstar
    psList2 = pornstar_sorting(psList, nPornstar)
    catList = remove_PS_Cats(psList, catList)

    # print(catList)
    catList = groupCategories(catList, includeGroupedCats, excludeGroupedCats, nCat)

    # print(catList)
    groupChannel = groupChannels(uploader, includeGroupedChannels)

    if groupChannel == "":
        groupChannel = getProxyChannel(proxyChannels, title, categories)

    if duration < 300 and duration >= 120:
        startTime = 10
        endTime = 10
    elif duration < 120 and duration >= 30:
        startTime = 6
        endTime = 5
    elif duration > 10 and duration < 30:
        startTime = 1
        endTime = 1
    elif groupChannel == "Group Lets Doe It":
        startTime = 20
        endTime = 40
    elif uploader == "Dogfart Network":
        startTime = 30
        endTime = duration - (8 * 60)
        if endTime < 2:
            endTime = 2
    elif uploader == "Divine Bitches":
        startTime = 8
        endTime = 5
        if duration > 480:
            endTime = 70
    elif autoAssignStartTimes:
        try:
            timings = channelTimings_df.loc[uploader]
            startTime = timings["Start"]
            endTime = timings["End"]
        except KeyError:
            try:
                timings = groupChannelTimings_df.loc[groupChannel]
                startTime = timings["Start"]
                endTime = timings["End"]
            except KeyError:
                startTime = startTimeMain
                endTime = endTimeMain
    else:
        startTime = startTimeMain
        endTime = endTimeMain

    website = getWebsite(url)

    if len(startList) > 0:
        if math.isnan(startList[iURL]) == False:
            startTime = startList[iURL]
        if math.isnan(endList[iURL]) == False:
            endTime = endList[iURL]

    # print(catList)
    #
    # print(len(excludeTags), any(item in excludeTags for item in catList), duration)

    if (len(excludeTags)==0 or any(item in excludeTags for item in catList)==False) and (duration>minDuration or duration==0):
        videoList.append([title, id, url, startTime, endTime] + catList + psList2 + [uploader, groupChannel, website, upload_date, duration, view_count, like_count, dislike_count, ext, fps, height, width, errorMessage])
    return videoList


def getValsFromDict(info_dict):
    try:
        title = info_dict['title']
    except:
        title = ""

    try:
        id = info_dict['id']
    except:
        id = ""

    try:
        url = info_dict['webpage_url']
    except:
        url = ""

    try:
        tags = info_dict['tags']
    except:
        tags = [""]

    try:
        categories = info_dict['categories']
    except:
        print('get categories failed')
        categories = [""]

    try:
        uploader = info_dict['uploader']
    except:
        uploader = ""

    try:
        upload_date = info_dict['upload_date']
    except:
        upload_date = ""

    try:
        duration = info_dict['duration']
    except:
        duration = 0

    try:
        view_count = info_dict['view_count']
    except:
        view_count = 0

    try:
        like_count = info_dict['like_count']
    except:
        like_count = 0

    try:
        dislike_count = info_dict['dislike_count']
    except:
        dislike_count = 0

    try:
        ext = info_dict['ext']
    except:
        ext = ""

    try:
        fps = info_dict['fps']
    except:
        fps = 0

    try:
        height = info_dict['height']
    except:
        height = 0

    try:
        width = info_dict['width']
    except:
        width = 0
    return title, id, url, tags, categories, uploader, upload_date, duration, view_count, like_count, dislike_count, ext, fps, height, width

def setVidInfoFields():

    ### getChannelTimings ###
    pornList_df = pd.read_csv(PathList["combinedPornListPath"])
    df_KnownVideos = pornList_df

    knownURLs_List = df_KnownVideos['url'].to_list()

    minRequired=5
    countChannels = pornList_df[['_Channel', '_Channel_Group']].apply(pd.Series.value_counts)
    countChannels['Total'] = countChannels.sum(axis=1)
    countChannels = countChannels.loc[countChannels['Total']>minRequired]
    uniqChannels = pd.unique(countChannels.index.values.ravel('K'))

    pornList_df = pornList_df[pornList_df["_Channel"].isin(uniqChannels)]

    channelTimings_df = pornList_df[["Start", "End", "_Channel"]]
    channelTimings_df = channelTimings_df.groupby(by="_Channel").mean()
    channelTimings_df["Start"] = channelTimings_df["Start"].astype(int)
    channelTimings_df = channelTimings_df.sort_values(by=['End'])
    channelTimings_df["End"] = channelTimings_df["End"].astype(int)

    groupChannelTimings_df = pornList_df[["Start", "End", "_Channel_Group"]]
    groupChannelTimings_df = groupChannelTimings_df.groupby(by="_Channel_Group").mean()
    groupChannelTimings_df["Start"] = groupChannelTimings_df["Start"].astype(int)
    groupChannelTimings_df = groupChannelTimings_df.sort_values(by=['End'])
    groupChannelTimings_df["End"] = groupChannelTimings_df["End"].astype(int)

    ### Get Channel and Ps Groupings ###

    groupedCats = pd.read_excel(PathList["GroupCatPath"], sheet_name='Category Groupings')
    groupedChannels = pd.read_excel(PathList["GroupCatPath"], sheet_name='Channel Groupings')
    proxyChannels = pd.read_excel(PathList["GroupCatPath"], sheet_name='ProxyChannels')
    proxyChannels = proxyChannels["Channel"].tolist()
    nGroupVars = 28
    includeColNames = []
    excludeColNames = []
    i=0
    while i < nGroupVars:
        includeColNames.append('_Include'+str(i+1))
        excludeColNames.append('_Exclude'+str(i+1))
        i=i+1
    includeGroupedCats = groupedCats[['Group']+includeColNames].values.tolist()
    excludeGroupedCats = groupedCats[excludeColNames].values.tolist()

    includeColNamesChannel = []
    i=0
    while i < 150:
        includeColNamesChannel.append('_Include'+str(i+1))
        i=i+1
    includeGroupedChannels = groupedChannels[['Group']+includeColNamesChannel].values.tolist()

    ### Get comb list and download file ###

    dfVideoList = pd.read_csv(PathList["combinedPornListPath"])
    dfVideoList = dfVideoList.replace([0], ['0'])

    countPornstars = dfVideoList[['_Pornstar1', '_Pornstar2', '_Pornstar3', '_Pornstar4', '_Pornstar5']].apply(pd.Series.value_counts)
    countPornstars['Total'] = countPornstars.sum(axis=1)
    uniqPornstars = pd.unique(countPornstars.index.values.ravel('K'))
    # df_PornStarList = pd.read_excel(r"Porn Lists/Porn_URL_Dir.xlsx", sheet_name='PornstarCount')
    df_Pornstar = pd.read_csv(PathList["PornstarListPath"])
    pornstarListStart = df_Pornstar["Pornstar"].to_list()

    countPornstars['Pornstar'] = countPornstars.index
    outPornstars = countPornstars[['Pornstar', 'Total']]
    outPornstars.reset_index(inplace=True)
    outPornstars = outPornstars[['Pornstar', 'Total']]
    for pornstar in pornstarListStart:
        if pornstar not in countPornstars['Pornstar'].to_list():
            outPornstars = outPornstars.append(pd.DataFrame({'Pornstar': [pornstar], 'Total': [0]}),ignore_index = True)
    outPornstars.sort_values(by='Pornstar', inplace=True)
    outPornstars.to_csv(PathList["PornstarListPath"], index=False, encoding='utf-8-sig')

    i=0
    pornstarList = []
    while i < len(pornstarListStart):
        try:
            if str.title(pornstarListStart[i]) != "Pornstar":
                pornstarList.append(str.title(pornstarListStart[i]))
        except TypeError:
            pass
        i=i+1

    df_searchTitleTags = pd.read_excel(PathList["GroupCatPath"], sheet_name='SearchTitleTags')
    searchTitleTags = df_searchTitleTags['Tags'].to_list()
    searchTitleTags = searchTitleTags + proxyChannels

    return proxyChannels, pornstarList, includeGroupedChannels, includeGroupedCats, excludeGroupedCats, channelTimings_df, groupChannelTimings_df, searchTitleTags, knownURLs_List

def getInfoDict(line):
    selectDir = r'E:/Pics/System Images/Vid/Videos/1 - To be sorted/'
    ydl_opts = {'outtmpl': "",
                'format': 'best[height>720]',
                'simulate': True,
                'dump_single_json': True,
                'writeinfojson': True}

    iAttempt = 0
    errorMessage=''
    if line == "":
        iAttempt = 7
    info_dict = dict()
    print("Getting Video Info")
    while iAttempt <= 6:
        print(iAttempt)
        if iAttempt <3:
            try:
                with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                    info_dict = ydl.extract_info(line, download=False)
                break
            except Exception as e:
                # print(str(e))
                if "PornHub said:" in str(e) or "HTTP Error 410: Gone" in str(e) or "ERROR: Unable to extract encoded url" in str(e):
                    errorMessage=str(e)
                    info_dict=dict()
                    print("Error - Video Removed")
                    break
                elif "ERROR: requested format not available" == str(e):
                    iAttempt = 2
                pass
        if iAttempt >= 3 and iAttempt <6:
            try:
                ydl_opts = {'outtmpl': "",
                            'format': 'best',
                            'simulate': True,
                            'dump_single_json': True,
                            'writeinfojson': True}
                # print("Error retrying - Attempt: ", iAttempt)
                with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                    info_dict = ydl.extract_info(line, download=False)
                break
            except Exception as e:
                print(str(e))
                if "PornHub said:" in str(e) or "HTTP Error 410: Gone" in str(e) or "ERROR: Unable to extract encoded url" in str(e):
                    errorMessage=str(e)
                    info_dict=dict()
                    # print("Error - Video Removed")
                    break
                elif "ERROR: requested format not available" == str(e):
                    iAttempt = 5
                pass
        elif iAttempt == 6:
            try:
                ydl_opts = {'outtmpl': "",
                            'format': 'best',
                            'simulate': True,
                            'dump_single_json': True,
                            'writeinfojson': True}
                # print("Error retrying - Attempt: ", iAttempt)
                with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                    info_dict = ydl.extract_info(line, download=False)
                break
            except Exception as e:
                # print(str(e))
                errorMessage=str(e)
                info_dict=dict()
                pass
        iAttempt = iAttempt + 1
    return info_dict, errorMessage



def getVidInfoFn(urls, startTimeMain, endTimeMain, titles=[], startList=[], endList=[], knownCatList=[], knownPornstar=[], knownChannel=[], autoAssignStartTimes=True, excludeTags=[], minDuration=0, removeKnown=True, exportData=True, overwrite=False, knownTitles_List=[]):
    time.sleep(1)
    proxyChannels, pornstarList, includeGroupedChannels, includeGroupedCats, excludeGroupedCats, channelTimings_df, groupChannelTimings_df, searchTitleTags, knownURLs_List = setVidInfoFields()
    if removeKnown:
        # knownUrls = [url for url in urls if url in knownURLs_List]
        # df_videos = pd.read_csv(PathList["combinedPornListPath"])
        # for url in knownUrls:
        #     df_videos = updateDF(df_videos, url)
        #     iAttempt = 0
        #     while iAttempt < 5:
        #         try:
        #             exportUpdatedFile(df_videos, PathList["combinedPornListPath"])
        #             break
        #         except:
        #             print("File unavailable. Attempt ", iAttempt)
        #             time.sleep(10)
        #             pass
        #         iAttempt = iAttempt + 1
        urls = [url.split("?pl=")[0] for url in urls]


        urls = [url for url in urls if url not in knownURLs_List]
        urls = [url for url in urls if url != ""]
    if len(knownCatList)==0:
        knownCatList = [[]] * len(urls)
    if len(knownPornstar)==0:
        knownPornstar = [[]] * len(urls)
    if len(knownChannel)==0:
        knownChannel = [[]] * len(urls)
    if len(titles)==0:
        titles = [[]] * len(urls)


    nCat = 40
    nPornstar = 5
    breakcsv = 500


    iURL = 0
    ErrorCount = 0
    videoList = []
    while iURL < len(urls):
        # try:
        # knownPornstar=knownPornstarSaved
        info_dict=dict()
        print(str(iURL) + ' Out Of ' + str(len(urls)))
        line = urls[iURL]
        line = line.replace('http://', 'https://')

        foundPornstars = knownPornstar[iURL][:]
        print(knownPornstar[iURL])

        info_dict, errorMessage = getInfoDict(line)

        title, id, url, tags, categories, uploader, upload_date, duration, view_count, like_count, dislike_count, ext, fps, height, width = getValsFromDict(info_dict)

        if 'youporn' not in url and 'videos.trendyporn.com' not in url and len(errorMessage)==0:
            line, categories, uploader, foundPornstars = getMoreCatandChannel(url, categories, uploader, foundPornstars, pornstarList)
        print(url)
        print(categories + tags)
        print(uploader)
        print(knownPornstar[iURL])
        try:
            knownChan = knownChannel[iURL][:]
        except:
            knownChan=knownChannel

        try:
            if m.isnan(knownChan[iURL]):
                knownChan = uploader
        except:
            pass

        if title not in knownTitles_List:
            videoList = groupAndSortInputs(title, id, url, tags, categories, uploader, upload_date, duration, view_count, like_count, dislike_count, ext, fps, height, width,
                       videoList, autoAssignStartTimes=autoAssignStartTimes, startTimeMain=startTimeMain, endTimeMain=endTimeMain, pornstarList=pornstarList, searchTitleTags=searchTitleTags, includeGroupedChannels=includeGroupedChannels,
                       includeGroupedCats=includeGroupedCats, excludeGroupedCats=excludeGroupedCats, knownCatList=knownCatList[iURL][:], proxyChannels=proxyChannels, channelTimings_df=channelTimings_df,
                       groupChannelTimings_df=groupChannelTimings_df, startList=startList, endList=endList, iURL=iURL, nCat=nCat, nPornstar=nPornstar,  customPornstar=foundPornstars, excludeTags=excludeTags,
                        minDuration=minDuration, knownChannel=knownChan, errorMessage=errorMessage)
        # except Exception as e:
        #     ErrorCount = ErrorCount + 1
        #     print('')
        #     print(e)
        #     print('Error ' + str(ErrorCount))
        #     print('')
        #     pass

        if(iURL%breakcsv==0 and iURL>0):
            if len(videoList)>0:
                exportVideoList(videoList, nCat, nPornstar, iURL, (len(urls)), overwrite=overwrite)
            time.sleep(10)

        iURL = iURL + 1

    print('Total Errors ' + str(ErrorCount))
    if len(videoList) > 0 and exportData:
        exportVideoList(videoList, nCat, nPornstar, iURL, exportData=exportData, overwrite=overwrite)
    elif exportData==False:
        return exportVideoList(videoList, nCat, nPornstar, iURL, exportData=exportData)

def getMoreCatandChannel(url, categories, uploader, pornstars, pornstarList):
    headers = {"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36"}

    # s = requests.session()
    # source_code = s.get(url)
    # soup = BeautifulSoup(source_code.content, "html.parser")
    # s.cookies.clear()

    scraper = cloudscraper.create_scraper(browser={'browser': 'firefox', 'platform': 'windows'})
    source_code = scraper.get(url) #headers=headers)
    soup = BeautifulSoup(source_code.content, 'html.parser')

    newPornstars = []

    url_out = ""
    if len(categories)==1 and categories[0]=="":
        categories = []
    appendBool=False
    for link in soup.find_all('a'):
        if 'spankbang.com' in url:
            # print(str(link))
            if '<a href="/category/' in str(link) or '<a href="/tag/' in str(link):
                categories.append(str(link.contents[0]))
            if '<a class="ul" href="/profile/' in str(link) and uploader=="":
                uploader = link.attrs['href'].replace('/profile/', '')
            if '<a href="/' in str(link) and '/pornstar/' in str(link):
                newPornstars.append(str(link.contents[0]))
        # elif 'youporn.com' in url:
        #     print(str(link))
        #     if 'mp4' in str(link) and '202009' in str(link):
        #         url_out = str(link.contents[0])
        #     if '<a class="button bubble-button gray' in str(link) and 'data-espnode="pornstar_tag" href="/pornstar' in str(link):
        #         newPornstars.append(str(link.contents[0]))
        #     if '<a class="button bubble-button pink' in str(link) and 'data-espnode="' in str(link) and '_tag" href="/' in str(link):
        #         categories.append(str(link.contents[0]))
        elif 'xvideos.com' in url:
            if '<a class="btn btn-default" href="/tags/' in str(link) and 'All tags' not in str(link):
                categories.append(str(link.contents[0]))
            if '<a class="btn btn-default label profile" href="/pornstars/' in str(link):
                newPornstars.append(str(link.contents[0].contents[0]))
            if '<a class="btn btn-default label main uploader-tag' in str(link):
                uploader = str(link.contents[0].contents[0])
        elif 'pervclips.com' in url:
            if '<a class="link" href="https://www.pervclips.com/tube/tags/' in str(link):
                categories.append(str(link.contents[0]))
            if '<a class="text link" href="https://www.pervclips.com/tube/pornstars/' in str(link):
                newPornstars.append(str(link.contents[0]))
            if '<a class="member" href="https://www.pervclips.com/tube/members/' in str(link):
                uploader = str(link.contents[0])
        elif 'redtube.com' in url:
            if '<a class="item video_carousel_item video_carousel_category" href="/redtube/' in str(link) or '<a class="item video_carousel_item video_carousel_tag' in str(link):
                categories.append(str(link.contents[0]).strip('\n').strip())
            if '<a class="tm_pornstar_link pornstar_link js_mpop js-pop" href="/pornstar/' in str(link) and appendBool==False: # in str(link) and '<a class="ps_info_name js_mpop js-pop" href="/pornstar' in str(link):
                newPornstars.append(str(link.attrs['href']).replace('/pornstar/','').replace('+',' '))
            if '<a class="share_icon_wrapper share_twitter lazy" data-bg=' in str(link):
                appendBool=True
            if '<a class="video-infobox-link" href="/channels/' in str(link):
                uploader = str(link.contents[0])
        elif 'eporner.com' in url:
            if ('<a href="/cat/' in str(link) or '<a href="/search' in str(link)) and '/cat/all/' not in str(link) and appendBool:
                categories.append(str(link.contents[0]))
            if '<a href="/pornstar' in str(link) and appendBool:
                newPornstars.append(str(link.contents[0]))
            if '<a href="/profile/' in str(link) and appendBool==False:
                appendBool=True
                uploader = str(link.contents[0])
        elif 'anysex.com' in url:
            if '<a href="https://anysex.com/tags/' in str(link) or '<a href="https://anysex.com/categories/' in str(link):
                categories.append(str(link.contents[0]))
            if '<a href="https://anysex.com/models/' in str(link):
                newPornstars.append(str(link.contents[0]))
            if '<a href="https://anysex.com/channels/' in str(link):
                uploader = str(link.contents[1].attrs['content'])
        elif 'gotporn.com' in url:
            if '<a href="https://www.gotporn.com/categories' in str(link) and 'Porn categories' not in str(link):
                categories.append(str(link.contents[0]).strip('\n'))
            if '<a href="https://www.gotporn.com/users/' in str(link):
                uploader = str(link.contents[0])
        elif 'pornhub.com' in url:
            if '<a class="pstar-list-btn js-mxp"' in str(link):
                pornstars.append(str(link.attrs['data-mxptext']).strip('\n'))

    if len(newPornstars)>0:
        i=0
        while i < len(newPornstars):
            if newPornstars[i] in pornstarList:
                pornstars.append(newPornstars[i])
            i = i + 1

    if len(url_out)==0:
        url_out = url
    return url_out, categories, uploader, pornstars

def exportVideoList(videoList, nCat=40, nPornstar=5, iURL=0, maxURL=0, exportData=True, overwrite=False):
    if iURL==0:
        iURL = len(videoList)
    if maxURL==0:
        maxURL = iURL

    columnList = ['Title', 'id', 'url', 'Start', 'End']
    i=0
    while i < nCat:
        columnList.append('_Cat' + str(i+1))
        i=i+1
    i=0

    while i < nPornstar:
        columnList.append('_Pornstar' + str(i+1))
        i=i+1

    columnList = columnList + ['_Channel', '_Channel_Group', 'Website', 'UploadDate', 'Duration', 'nViews', 'nLikes', 'nDislikes', 'Extension', 'FPS', 'Height', 'Width', "Error"]

    dfVideoListOut = pd.DataFrame(videoList, columns=columnList)

    if exportData:
        if overwrite:
            df_videos = pd.read_csv(PathList["combinedPornListPath"])
            df_videos = pd.concat([df_videos, dfVideoListOut])
            iAttempt = 0
            while iAttempt < 5:
                try:
                    exportUpdatedFile(df_videos, PathList["combinedPornListPath"])
                    break
                except:
                    print("File unavailable. Attempt ", iAttempt)
                    time.sleep(10)
                    pass
                iAttempt = iAttempt + 1
        else:
            dfVideoListOut = dfVideoListOut.fillna('')
            dfVideoListOut = dfVideoListOut.replace('nan', '')
            dfVideoListOut = dfVideoListOut.replace('0', '')
            dfVideoListOut = dfVideoListOut.replace('na', '')
            dfVideoListOut = dfVideoListOut.replace(' 0', '')
            dfVideoListOut = dfVideoListOut.replace(0, '')
            dfVideoListOut.to_csv(PathList["DataListOutPath"] + r"/output" + str(iURL) + '_' + str(maxURL) + '_' + str(time.time()) + ".csv")
    else:
        return dfVideoListOut


def getValsFromDf(row, nPornstar, nCat):

    pornstarList = []
    iPornstar=0
    while iPornstar < nPornstar:
        pornstarList.append("_Pornstar" + str(iPornstar+1))
        iPornstar=iPornstar+1

    categoryList = []
    iCat=0
    while iCat < nCat:
        categoryList.append("_Cat" + str(iCat+1))
        iCat=iCat+1

    title = row["Title"].values[0]
    id = row["id"].values[0]
    url = row["url"].values[0]
    start = row["Start"].values[0]
    end = row["End"].values[0]
    pornstars = row[pornstarList].values[0].tolist()
    categories = row[categoryList].values[0].tolist()
    channel = row["_Channel"].values[0]
    channelGroup = row["_Channel_Group"].values[0]
    website = row["Website"].values[0]
    upload_date = row["UploadDate"].values[0]
    duration = row["Duration"].values[0]
    view_count = row["nViews"].values[0]
    like_count = row["nLikes"].values[0]
    dislike_count = row["nDislikes"].values[0]
    ext = row["Extension"].values[0]
    fps = row["FPS"].values[0]
    height = row["Height"].values[0]
    width = row["Width"].values[0]

    return title, id, url, start, end, pornstars, categories, channel, channelGroup, website, upload_date, duration, view_count, like_count, dislike_count, ext, fps, height, width

def getVidsFromPage(url, excludeTags_List, knownURLs_List=[], brokenLinks=[], df_AutoChannels=pd.DataFrame(), iChannel=0, OldAttemptedURLs=[], useBrokenLinks=False):
    print(url)
    source_code = requests.get(url)
    soup = BeautifulSoup(source_code.content, 'lxml')
    links = []
    selected_links = []
    linkBrokenCount = 0
    linkBroken = False
    select = False
    for link in soup.find_all('a'):
        # print(str(link))
        # if r'<a class="subTitle" href="/gifs?o=tr">Top Rated Gifs</a>' == str(link) and linkBroken == False:
        if r'<i class="mr"></i>Most Recent' in str(link) and linkBroken == False:
            select = True
        if r'<a href="/support"> technical support </a>' == str(link):
            linkBrokenCount = linkBrokenCount + 1
        if r'<a href="/"><span>Return to Home Page</span></a>' == str(link):
            linkBrokenCount = linkBrokenCount + 1
        if linkBrokenCount == 2:
            select = False
            linkBroken = True
        if r'<a class="" href="/view_video' in str(link) and select and linkBroken == False:
            Title = link.attrs['title']
            if any(substring in Title for substring in excludeTags_List) == False:
                selected_links.append("https://www.pornhub.com" + str(link.attrs['href']))
        links.append(str(link).replace('http://', 'https://'))

    print("Vids Found:", len(selected_links))
    # selected_links = [url for url in selected_links if url not in OldAttemptedURLs]
    # selected_links = [url for url in selected_links if url not in knownURLs_List]

    if isinstance(selected_links, str):
        selected_links = [selected_links]

    if useBrokenLinks:
        if linkBroken:
            brokenLinks.append([df_AutoChannels.iloc[iChannel]['Name'], url])
        return selected_links, brokenLinks
    else:
        return selected_links


def exportUpdatedFile(df_videos, fileOut):
    dfVideoListOut = df_videos.fillna('')
    for col in dfVideoListOut.columns:
        if "Pornstar" in col:
            removePS_strings = ['Sex', 'Bo', 'Pornstar', 'Cum', 'Anal', 'Milf', 'Wife', 'Bedroom', 'Big ass', 'Cuckold',
                                'Sharing', 'Big tits', 'Cheating', 'Watching', 'Housewife', 'nan', '0', 'Bbc', 'Jordan']
            for remPS in removePS_strings:
                dfVideoListOut[col] = dfVideoListOut[col].replace(remPS, '')
        elif "Unnamed" in col:
            dfVideoListOut.drop(columns=col, inplace=True)
    dfVideoListOut = dfVideoListOut.replace('nan', '')
    dfVideoListOut["_Channel"] = dfVideoListOut["_Channel"].replace('#NAME?', '')
    dfVideoListOut = dfVideoListOut.replace('0', '')
    dfVideoListOut = dfVideoListOut.replace('na', '')
    dfVideoListOut = dfVideoListOut.replace(' 0', '')
    dfVideoListOut = dfVideoListOut.replace(0, '')
    dfVideoListOut = dfVideoListOut.drop_duplicates(subset=['id'], keep='first')
    dfVideoListOut.sort_values(['_Channel', 'Title'], inplace=True)
    dfVideoListOut.reset_index(inplace=True, drop=True)
    dfVideoListOut.to_csv(fileOut)

def updateDF(df_videos, url):
    print(url)
    knownUrlList = df_videos['url'].to_list()
    if url in knownUrlList:
        print(df_videos[df_videos['url']==url])
        title, id, url, start, end, pornstars, categories, channel, channelGroup, website, upload_date, duration, view_count, like_count, dislike_count, ext, fps, height, width = getValsFromDf(df_videos[df_videos['url']==url], 5, 40)
        result_df = getVidInfoFn([url], start, end, titles=[title], startList=[start], endList=[end], knownCatList=[categories], knownPornstar=[pornstars], knownChannel=[channel], autoAssignStartTimes=False, excludeTags=[], minDuration=0, removeKnown=False, exportData=False)
        ErrorMessage = result_df["Error"].values[0]
        if len(ErrorMessage)>0:
            result_df = df_videos[df_videos['url']==url]
            result_df["Error"] = ErrorMessage
        df_videos = df_videos[df_videos['url'] != url]
        df_videos = pd.concat([df_videos, result_df])
        print(result_df)
    return df_videos

