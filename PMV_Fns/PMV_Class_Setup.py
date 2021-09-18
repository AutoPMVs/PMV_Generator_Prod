class PMV_Class:
    def __init__(self, DirectoryFile_Info, Configuration, Music_Info, CH_Settings, Video_Select, URL_Data):
        self.DirectoryFile_Info = DirectoryFile_Info
        self.Configuration = Configuration
        self.Music_Info = Music_Info
        self.CH_Settings = CH_Settings
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
    def __init__(self, musicName, musicType, songStart, songEnd, musicVideoBool, musicVideoOccuranceFactor, trimSong,
                 origSoundScale, origSoundFromSection):
        self.musicName = musicName
        self.musicType = musicType
        self.songStart = songStart
        self.songEnd = songEnd
        self.musicVideoBool = musicVideoBool
        self.musicVideoOccuranceFactor = musicVideoOccuranceFactor
        self.trimSong = trimSong
        self.origSoundScale = origSoundScale
        self.origSoundFromSection = origSoundFromSection


class CH_Settings:
    def __init__(self, make_CH_Vid, nSections, requiredDiff, minSections, beatSelect, animationDuration, sdfactor,
                 yPosScale, useRankMethod, rollingSections, circleSizeScale, beatEndPosScale):
        self.make_CH_Vid = make_CH_Vid
        self.nSections = nSections
        self.requiredDiff = requiredDiff
        self.minSections = minSections
        self.useRankMethod = useRankMethod
        self.rollingSections = rollingSections
        self.sdfactor = sdfactor
        self.beatSelect = beatSelect
        self.animationDuration = animationDuration
        self.yPosScale = yPosScale
        self.circleSizeScale = circleSizeScale
        self.beatEndPosScale = beatEndPosScale

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
                 cropVidFraction, resize, flipBool,
                 addIntro, userName, UseClassifyModel, sectionArray):
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
        self.sectionArray = sectionArray #"other", "cunnilingus", "titfuck", "blowjob_handjob", "sex", "finish"

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
