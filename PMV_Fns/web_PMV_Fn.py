from PMV_Fns.functions import getVideoData
from PMV_Fns.functions import processVideoData
from PMV_Fns.functions import concatonateFinalVideo
from pydub import AudioSegment
from PMV_Fns.functions import getHighValues2
from PMV_Fns.functions import getElementDiff
from PMV_Fns.functions import videoSplits
from PMV_Fns.selectFunctions import getCustom
from PMV_Fns.selectFunctions import getMusic
from Admin_Fns.allPaths import PathList
from PMV_Fns.processMusicFile import inputMusic

beepDur = 500  # milliseconds
beepFreq = 440  # Hz

class Video:
    def __init__(self, name, customStart, customEnd, directory):
        self.name = name
        self.customStart = customStart
        self.customEnd = customEnd
        self.directory = directory
# sampleWidth = 1280  # 360#
# sampleHeight = 720  # 640#

AudioSegment.converter = PathList["AudioSegmentPath"]
AudioSegment.ffmpeg = PathList["AudioSegmentPath"]
AudioSegment.ffprobe = PathList["AudioSegmentPath"]





def genPMVs(PMV, sampleHeight, sampleWidth, df_Videos_All):

    musicDir = getMusic(PMV.Music_Info.musicName, PMV.Music_Info.musicType)

    # downloadVids(selectedVidUrls, selectDir=PMV.outputDir, number=PMV.number)

    df_videos_filtered = getCustom(df_Videos_All, includeCategories = PMV.Video_Select.includeCategories, includePornstars = PMV.Video_Select.includePornstars,
                             includeChannels = PMV.Video_Select.includeChannels, excludeCategories = PMV.Video_Select.excludeCategories,
                             excludePornstars = PMV.Video_Select.excludePornstars, excludeChannels=PMV.Video_Select.excludeChannels,
                             orCategories=PMV.Video_Select.orCategories, orPornstars=PMV.Video_Select.orPornstars,
                             outputDir=PMV.DirectoryFile_Info.vidDownloadDir, number=PMV.Configuration.videoNumber,
                             maxDuration=PMV.Configuration.maxVidLength, minDuration=PMV.Configuration.minVidLength)

    print(AudioSegment.ffmpeg)
    mp3_dir = PMV.DirectoryFile_Info.musicDir + PMV.Music_Info.musicName + '.mp4'

    file_out = PMV.DirectoryFile_Info.finalVidDir + PMV.DirectoryFile_Info.finalVidName + '.mp4' #  filetypeout
    print(mp3_dir)
    reshaped_data, first_data, audioclip, ratio, bitrate = inputMusic(mp3_dir, trimSong=PMV.Music_Info.trimSong, songStart=PMV.Music_Info.songStart, songEnd=PMV.Music_Info.songEnd, granularity=PMV.Configuration.granularity)
    diff_data = getElementDiff(reshaped_data)

    result = getHighValues2(reshaped_data, diff_data, PMV.Configuration.sd_scale, PMV.Configuration.nSplits, PMV.Configuration.granularity, PMV.Configuration.min_length)

    print('List of Indices of maximum element :', len(result))
    result.append(len(first_data) / ratio)

    videoData, origVidName = getVideoData(PMV, df_Videos_All)
    videos = processVideoData(PMV, videoData, sampleWidth, sampleHeight, origVidName, df_videos_filtered)
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

    # winsound.Beep(beepFreq, beepDur)
    print('Finished!')


        # except OSError:
        #     print("Error - retrying - Attempt: ", bigAttempt)
        #     pass
        # else:
        #     break