class PMV_Class:
    def __init__(self, DirectoryFile_Info, Configuration, Music_Info, Video_Select, URL_Data):
        self.DirectoryFile_Info = DirectoryFile_Info
        self.Configuration = Configuration
        self.Music_Info = Music_Info
        self.Video_Select = Video_Select
        self.URL_Data = URL_Data
class URL_Data:
    def __init__(self, videoURLs, musicURL):
        self.videoURLs = videoURLs
        self.musicURL = musicURL
class SectionClass:
    def __init__(self, videoURLs, musicURL):
        self.videoURLs = videoURLs
        self.musicURL = musicURL
class Music_Info:
    def __init__(self, musicName, musicType, songStart, songEnd,
                 musicVideoBool, musicVideoOccuranceFactor, trimSong):
        self.musicName = musicName
        self.musicType = musicType
        self.songStart = songStart
        self.songEnd = songEnd
        self.musicVideoBool = musicVideoBool
        self.musicVideoOccuranceFactor = musicVideoOccuranceFactor
        self.trimSong = trimSong

class DirectoryFile_Info:
    def __init__(self, finalVidName, vidDownloadDir, pythonDir, introVidDir,
                 musicDir, musicVidDir, musicFilePath, finalVidDir, ModelStorageDir):
        self.finalVidName = finalVidName
        self.vidDownloadDir = vidDownloadDir
        self.pythonDir = pythonDir
        self.introVidDir = introVidDir
        self.musicDir = musicDir
        self.musicVidDir = musicVidDir
        self.musicFilePath = musicFilePath
        self.finalVidDir = finalVidDir
        self.ModelStorageDir = ModelStorageDir

class Configuration:
    def __init__(self, startEndTime, sd_scale, nSplits, randomise, granularity,
                 min_length, videoNumber, minVidLength, maxVidLength, cropVidBool,
                 cropVidFraction, resize, flipBool, addIntro, userName, UseClassifyModel):
        self.startTime = startEndTime[0]
        self.subtractEnd = startEndTime[1]
        self.sd_scale = sd_scale
        self.nSplits = nSplits
        self.randomise = randomise
        self.granularity = granularity
        self.min_length = min_length
        self.videoNumber = videoNumber
        self.minVidLength = minVidLength
        self.maxVidLength = maxVidLength
        self.cropVidBool = cropVidBool
        self.cropVidFraction = cropVidFraction
        self.resize = resize
        self.flipBool = flipBool
        self.addIntro = addIntro
        self.userName = userName
        self.UseClassifyModel = UseClassifyModel

class Video_Select:
    def __init__(self, includeChannels, includeCategories, includePornstars, excludeCategories,
                 excludePornstars, excludeChannels, includeSelectNumber, excludeSelectNumber,
                 orCategories, orPornstars, classifiedOnly):
        self.includeChannels = includeChannels
        self.includeCategories = includeCategories
        self.includePornstars = includePornstars
        self.includeSelectNumber = includeSelectNumber
        self.excludeCategories = [x for x in excludeCategories if x not in includeCategories]
        self.excludePornstars = [x for x in excludePornstars if x not in includePornstars]
        self.excludeChannels = [x for x in excludeChannels if x not in includeChannels]
        self.excludeSelectNumber = excludeSelectNumber
        self.orCategories =orCategories
        self.orPornstars = orPornstars
        self.classifiedOnly = classifiedOnly
