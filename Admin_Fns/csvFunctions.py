import pandas as pd
import string as stringFn
from Admin_Fns.allPaths import PathList

def title_to_cat(searchTitleTags, title, catList):
    i = 0
    while i < len(searchTitleTags):
        if str.title(searchTitleTags[i]) in str.title(title):
            catList.append(str.title(searchTitleTags[i]))
        i = i + 1

    catList = ['0' if str(x) == 'nan' else x for x in catList]
    return catList

def catSorting(categories, nCat, pornstarList, psList):
    i = 0
    catList = []

    while i < nCat:
        if i < len(categories):
            if str.title(str(categories[i])) in pornstarList:
                psList.append(str.title(categories[i]).strip())
                catList.append('0')
            else:
                try:
                    catList.append(str.title(str(categories[i])).strip())
                except:
                    print(categories[i])
                    catList.append('0')

        else:
            catList.append('0')
        i = i + 1

    catList = ['0' if str(x) == 'nan' else x for x in catList]
    catList = ['0' if str(x) == 'Nan' else x for x in catList]

    return [catList, psList]

def title_to_pornstar(pornstarList, psList, title, uploader):
    i = 0
    while i < len(pornstarList):
        if pornstarList[i] in title or pornstarList[i] in str(uploader):
            psList.append(pornstarList[i])
        i = i + 1

    return psList

def pornstar_sorting(psList, nPornstar):
    psList = list(dict.fromkeys(psList))
    psList = [x for x in psList if str(x) != 'nan']
    psList2 = []
    i = 0
    while i < nPornstar:
        if i < len(psList):
            psList2.append(psList[i])
        else:
            psList2.append('0')
        i = i + 1

    return psList2

def groupCategories(categories, includeCats, excludeCats, nCat):

    categories = ['0' if str(x) == 'nan' else x for x in categories]
    newCategories = categories
    iCat = 0
    while iCat < nCat:
        iGroup = 0
        if iCat>=len(categories):
            categories.append('0')
        while iGroup < len(includeCats):
            if categories[iCat] in includeCats[iGroup] and len(set(categories).intersection(excludeCats[iGroup])) == 0:
                newCategories.append(includeCats[iGroup][0])
            elif categories[iCat] in includeCats[iGroup] and len(set(categories).intersection(excludeCats[iGroup])) > 0:
                newCategories[iCat]='0'
            iGroup = iGroup + 1
        iCat = iCat + 1
    newCategories = list(dict.fromkeys(newCategories))
    newCats2 = []
    i=0
    while i < nCat:
        if i < len(newCategories):
            newCats2.append(newCategories[i])
        else:
            newCats2.append('0')
        i = i + 1
    return newCats2

def groupChannels(channel, includeChannels):

    groupChannel = ""
    channel = str.title(str(channel))
    iGroup = 0
    while iGroup < len(includeChannels):

        includeChannelsGroup = includeChannels[iGroup]
        includeChannelsGroupNew = []
        for chan in includeChannelsGroup:
            includeChannelsGroupNew.append(chan)
            includeChannelsGroupNew.append(str.replace(str(chan), " ", ""))
        includeChannelsGroupNew = list(dict.fromkeys(includeChannelsGroupNew))

        includeChannels[iGroup] = [str.title(str(x)) for x in includeChannelsGroupNew]
        if channel in includeChannelsGroupNew:
            # if includeChannels[iGroup][0][-5:] != "Group":
            #     includeChannels[iGroup][0] = includeChannels[iGroup][0] + " Group"
            groupChannel = includeChannelsGroupNew[0]
            break
        iGroup = iGroup + 1

    return str.title(groupChannel)

def getProxyChannel(proxyChannels, title, categories):

    proxyChannel = ""
    proxyChannelsNew = []
    for chan in proxyChannels:
        proxyChannelsNew.append(str.title(chan))
    proxyChannelsNew = list(dict.fromkeys(proxyChannelsNew))

    for iCat, cat in enumerate(categories):
        categories[iCat] = str.title(cat)

    title = str.title(title)

    for chan in proxyChannelsNew:
        if chan in categories:
            proxyChannel = chan
            break
        elif chan in title:
            proxyChannel=chan
            break

    return str.title(proxyChannel)


def makePornstarList(videoList, publishNewList):

    removePS_strings = ['Sex', 'Bo', 'Pornstar', 'cum', 'anal', 'milf', 'wife', 'bedroom', 'big ass', 'cuckold',
                        'sharing', 'big tits', 'cheating', 'watching', 'housewife', 'nan', '0', 'Bbc', 'Jordan']

    countPornstars = videoList[['_Pornstar1', '_Pornstar2', '_Pornstar3', '_Pornstar4', '_Pornstar5']].apply(pd.Series.value_counts)
    countPornstars['Total'] = countPornstars.sum(axis=1)
    uniqPornstars = pd.unique(countPornstars.index.values.ravel('K'))

    df_Pornstar = pd.read_csv(PathList["PornstarListPath"])
    df_Pornstar['Pornstar'] = df_Pornstar['Pornstar'].fillna("")
    pornstarListStart = df_Pornstar["Pornstar"].to_list()

    for remPS in removePS_strings:
        pornstarListStart = [str(ps) for ps in pornstarListStart if str(ps) != remPS]

    pornstarListStart = [str.title(ps) for ps in pornstarListStart]
    uniqPornstars = uniqPornstars.tolist()
    uniqPornstars = [str.title(ps) for ps in uniqPornstars]

    listPornstar = uniqPornstars + pornstarListStart

    print(len(uniqPornstars))
    print(len(pornstarListStart))
    listPornstar = list(dict.fromkeys(listPornstar))
    print(len(uniqPornstars))

    for remPS in removePS_strings:
        listPornstar = [str(ps) for ps in listPornstar if str(ps) != remPS]

    countPornstars['Pornstar'] = countPornstars.index
    outPornstars = countPornstars[['Pornstar', 'Total']]
    outPornstars.reset_index(inplace=True)
    outPornstars = outPornstars[['Pornstar', 'Total']]
    for pornstar in listPornstar:
        if str.title(pornstar) not in countPornstars['Pornstar'].to_list():
            outPornstars = outPornstars.append(pd.DataFrame({'Pornstar': [pornstar], 'Total': [0]}),ignore_index = True)
    outPornstars.sort_values(by='Pornstar', inplace=True)
    if publishNewList:
        if outPornstars.shape[0]>0:
            outPornstars.to_csv(PathList["PornstarListPath"], index=False, encoding='utf-8-sig')
        else:
            print("Pornstar List length = 0 \n Not overwriting")
    return listPornstar

def makeCategoryList(nCat, videoList, publishNewList):
    allCatColumnList = []
    i = 0
    while i < nCat:
        allCatColumnList.append('_Cat' + str(i + 1))
        i = i + 1

    countCategories = videoList[allCatColumnList].apply(pd.Series.value_counts)
    countCategories['Total'] = countCategories.sum(axis=1)
    uniqCategories = pd.unique(countCategories.index.values.ravel('K'))
    countCategories['Category'] = countCategories.index
    if publishNewList:
        countCategories[['Category', 'Total']].to_csv(PathList["CategoryListPath"], index=False, encoding='utf-8-sig')

    allCatList = uniqCategories.tolist()
    allCatList = [cat for cat in allCatList if str(cat) != 'nan']
    allCatList = [cat for cat in allCatList if str(cat) != '0']

    return allCatList

def makeArtistList(videoList, publishNewList):
    countArtists = videoList[['_Artist1', '_Artist2', '_Artist3', '_Artist4', '_Artist5']].apply(pd.Series.value_counts)
    countArtists['Total'] = countArtists.sum(axis=1)
    uniqArtists = pd.unique(countArtists.index.values.ravel('K'))

    df_Artist = pd.read_csv(PathList["ArtistListPath"])
    artistListStart = df_Artist["Artist"].to_list()

    artistListStart = [str.title(ps) for ps in artistListStart]
    uniqArtists = uniqArtists.tolist()
    uniqArtists = [str.title(ps) for ps in uniqArtists]

    listArtist = uniqArtists + artistListStart

    print(len(uniqArtists))
    print(len(artistListStart))
    listArtist = list(dict.fromkeys(listArtist))
    print(len(uniqArtists))

    listArtist = [str(art) for art in listArtist if str(art) != 'nan']
    listArtist = [str(art) for art in listArtist if str(art) != '0']

    countArtists['Artist'] = countArtists.index
    outArtists = countArtists[['Artist', 'Total']]
    outArtists.reset_index(inplace=True)
    outArtists = outArtists[['Artist', 'Total']]
    for artist in listArtist:
        if str.title(artist) not in countArtists['Artist'].to_list():
            outArtists = outArtists.append(pd.DataFrame({'Artist': [artist], 'Total': [0]}),ignore_index = True)
    outArtists.sort_values(by='Artist', inplace=True)
    if publishNewList:
        outArtists.to_csv(PathList["ArtistListPath"], index=False, encoding='utf-8-sig')
    return listArtist

def makeChannelList(videoList, publishNewList):
    countChannels = videoList[['_Channel']].apply(pd.Series.value_counts)
    countChannels['Total'] = countChannels.sum(axis=1)
    countChannels['Channel'] = countChannels.index
    uniqChannels = pd.unique(countChannels.index.values.ravel('K'))
    if publishNewList:
        countChannels[['Channel', 'Total']].to_csv(PathList["ChannelListPath"], index=False, encoding='utf-8-sig')
    return uniqChannels.tolist()

def remove_PS_Cats(psList, catList):
    psList = list(dict.fromkeys(psList))
    psList = [x for x in psList if str(x) != 'nan']
    for ps in psList:
        for cat in catList:
            if cat in ps:
                catList.remove(cat)
                print("Removed: " + cat)
    return catList

def getArtistList(artistList, selectedArtistList, title, uploader):
    tags=[]
    i=0

    selectedArtistList = [cat for cat in selectedArtistList if str(cat) != 'nan']

    removeStrings_ShortList = ["-", ".", "/", "!", '&']

    for string in removeStrings_ShortList:
        title = title.replace(string, " ")
        title = title.replace("    ", " ")
        title = title.replace("   ", " ")
        title = title.replace("  ", " ")

    while i < len(artistList):
        if (artistList[i] in title or artistList[i] in str(uploader) or artistList[i] in tags):
            if len(selectedArtistList)>0:
                for selectedArtist in selectedArtistList:
                    if artistList[i] not in str(selectedArtist):
                        if title.startswith(artistList[i] + " "):
                            selectedArtistList.append(artistList[i].strip())
                        elif title.endswith(" " + artistList[i]):
                            selectedArtistList.append(artistList[i].strip())
                        elif " " + artistList[i] + " " in title or " " + artistList[i] + "," in title or " " + artistList[i] + "-" in title:
                            selectedArtistList.append(artistList[i].strip())

            else:
                selectedArtistList.append(artistList[i].strip())
        i = i + 1
    selectedArtistList = [cat for cat in selectedArtistList if str(cat) != 'nan']
    selectedArtistList = [cat for cat in selectedArtistList if str(cat) != '0']

    if len(selectedArtistList)>1 and "Queen" in selectedArtistList:
        selectedArtistList.remove("Queen")

    if len(selectedArtistList) < 5:
        while len(selectedArtistList) < 5:
            selectedArtistList.append('')
    elif len(selectedArtistList) > 5:
        selectedArtistList = selectedArtistList[:5]

    return selectedArtistList

def reformatTitle(removeStrings_List, Title, KnownArtists):

    Title = str.title(Title)

    if "Back In Black" in Title:
        print(Title)

    for string in removeStrings_List:
        Title = Title.replace(string, " ")

    Title = Title.replace("     ", " ")
    Title = Title.replace("    ", " ")
    Title = Title.replace("   ", " ")
    Title = Title.replace("  ", " ")

    for artist in KnownArtists:
        if len(artist)>0:
            artist = str.title(artist)
            Title = Title.replace("By " + artist, " ")
            Title = Title.replace("With " + artist, " ")
            Title = Title.replace("The " + artist, " ")
            Title = Title.replace(artist, " ")


    Title = Title.replace("     ", " ")
    Title = Title.replace("    ", " ")
    Title = Title.replace("   ", " ")
    Title = Title.replace("  ", " ")
    Title = Title.replace("The The", "The")

    Title = Title.strip()
    if len(Title)>3:
        if Title[-3:]=="The":
            Title = Title[:-3]
    if len(Title)>2:
        if Title[-2:]=="By":
            Title = Title[:-2]
    if len(Title)>3:
        if Title[-3:]=="The":
            Title = Title[:-3]
    if len(Title)>2:
        if Title[-2:]=="By":
            Title = Title[:-2]
    return stringFn.capwords(Title)

def getWebsite(url):
    url = url.replace("https://", "")
    url = url.replace("http://", "")
    url = url.replace("www.", "")
    url = url.split(".")[0]
    return str.title(url)
