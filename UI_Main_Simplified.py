import os
import webbrowser
import pandas as pd
import wx
from wx.lib.masked import *
import wx.lib.agw.floatspin as FS
from threading import Thread
from pydub import AudioSegment
from PMV_Fns.url_Web_PMV_Fn import genPMVs
from PMV_Fns.selectFunctions import filterForSelection
from Admin_Fns.allPaths import PathList
# from PMV_Fns.PMV_Class_Setup import PMV_Class
from PMV_Fns.PMV_Class_Setup import URL_Data
from PMV_Fns.PMV_Class_Setup import Video_Select
from PMV_Fns.PMV_Class_Setup import Configuration
from PMV_Fns.PMV_Class_Setup import DirectoryFile_Info
from PMV_Fns.PMV_Class_Setup import Music_Info
from PMV_Fns.PMV_Class_Setup import SectionClass
from Classify_Model.ClassifyVideo import ImageClass

from Admin_Fns.UI_ProfileManager import loadDefaultProfile
from Admin_Fns.UI_ProfileManager import removeProfile
from Admin_Fns.UI_ProfileManager import addNewProfile
from Admin_Fns.UI_ProfileManager import loadProfile

###### Optional ######
from Admin_Fns.addNewVideos import getVidInfo
######################


beepDur = 500  # milliseconds
beepFreq = 440  # Hz

sampleWidth = 1280  # 360#
sampleHeight = 720  # 640#

AudioSegment.converter = PathList["AudioSegmentPath"]
AudioSegment.ffmpeg = PathList["AudioSegmentPath"]
AudioSegment.ffprobe = PathList["AudioSegmentPath"]
df_Video_Data = [0]


class PMV_Class(Thread):
    def __init__(self, DirectoryFile_Info, Configuration, Video_Select, URL_Data, Music_Info):
        self.DirectoryFile_Info = DirectoryFile_Info
        self.Configuration = Configuration
        self.Music_Info = Music_Info
        self.Video_Select = Video_Select
        self.URL_Data = URL_Data

        Thread.__init__(self)
        self.start()


    def run(self):
        """Run Worker Thread."""
        # This is the code executing in the new thread.

        ###### Optional ######
        # try:
        getVidInfo(self)
        # except:
        #     pass
        ######################
        genPMVs(self, sampleHeight, sampleWidth, df_Video_Data[0])

pythonDir = PathList["pythonPath"] ########## Put your python.exe directory here - e.g. C:/User/.../python.exe ###############
dot = "."
iProject = 0


class MyFrame(wx.Frame):
    def __init__(self):
        super().__init__(None, -1, title='PMV Editor (Public Release) v1.1', pos=wx.DefaultPosition)#, size=(900, 800))
        self.Maximize(False)
        self.Maximize(True)
        self.panel = wx.Panel(self)
        self.mainSizer = wx.BoxSizer(wx.VERTICAL)

        profileOptions, self.profileList = loadDefaultProfile()

        self.minVidLength=profileOptions["Min Vid Length"]
        self.maxVidLength=profileOptions["Max Vid Length"]

        self.resetVideoList(None)
        self.recountCategories(None)

        ### Predfined Variables
        projectDir = os.getcwd()
        self.musicListOriginal = pd.read_csv(PathList["combinedMusicListPath"])
        self.musicList = self.musicListOriginal
        self.musicList["Artist"] = self.musicList.apply(lambda x: self.joinArtistsFn(x), axis=1)
        self.musicList["Index"] = self.musicList.index.astype(str)
        self.musicList["Summary"] = self.musicList.apply(lambda x: self.joinSummaryMusicString(x), axis=1)
        self.musicList = self.musicList.sort_values(by="Summary", ascending=True)
        self.musicList = self.musicList["Summary"].to_list()

        self.customVidDir = profileOptions["defaultVideoDownloadPath"]
        self.customMusicDir = profileOptions["defaultMusicDownloadPath"]
        self.customMusicVidDir = profileOptions["defaultMusicVidDownloadPath"]
        self.customOutputDir = profileOptions["defaultNewPMVsPath"]
        self.introVidName = profileOptions["introVideoPath"]
        self.username = profileOptions["Username"] #'AutoPMVs' ########## Change this to own username if desired ##########
        self.musicName = ""
        self.musicArtist = ""
        self.musicFilePath = ""
        print(self.customVidDir)

        spacing = 2

        #######################
        ######### Menu Bar
        #######################

        self.frame_menubar = wx.MenuBar()

        self.file_menu = wx.Menu()
        self.file_menu.Append(2, "&Source Vids Folder", "Select Input Video Directory")
        self.file_menu.Append(3, "&Music File", "Select Input Music Directory")
        self.file_menu.Append(4, "&Output Folder", "Select Output PMV Directory")
        self.file_menu.AppendSeparator()
        self.file_menu.Append(5, "&Make PMV", "Make PMV")
        self.Bind(wx.EVT_MENU, self.OnOpenVid, id=2)
        self.Bind(wx.EVT_MENU, self.OnOpenMusicFile, id=3)
        self.Bind(wx.EVT_MENU, self.OnOpenOutput, id=4)
        self.Bind(wx.EVT_MENU, self.onMakePMV, id=5)
        self.frame_menubar.Append(self.file_menu, "File")

        self.edit_menu = wx.Menu()
        self.edit_menu.Append(1, "&Refresh Video Selections", "Reset the video selections back to none")
        self.Bind(wx.EVT_MENU, self.resetAll, id=1)
        self.frame_menubar.Append(self.edit_menu, "Edit")

        self.view_menu = wx.Menu()
        self.view_menu.Append(6, "&Really Simplify View (No URLs)", "Simplify View to Only Key Options")
        self.view_menu.Append(7, "&Simplify View", "Simplify View to Only Key Options")
        self.view_menu.Append(8, "&Advance View", "Advanced View to See All Options")
        self.Bind(wx.EVT_MENU, self.reallySimplifyView, id=6)
        self.Bind(wx.EVT_MENU, self.simplifyView, id=7)
        self.Bind(wx.EVT_MENU, self.advancedView, id=8)
        self.frame_menubar.Append(self.view_menu, "View")

        self.directory_menu = wx.Menu()
        self.directory_menu.Append(2, "&Source Vids Folder", "Select Input Video Directory")
        self.directory_menu.Append(3, "&Music File", "Select Input Music Directory")
        self.directory_menu.Append(4, "&Output Folder", "Select Output PMV Directory")
        self.directory_menu.AppendSeparator()
        self.directory_menu.Append(9, "&Music Folder", "Select Input Music Directory")
        self.directory_menu.Append(10, "&Music Vid Folder", "Select Input Music Vid Directory")
        self.directory_menu.Append(11, "&Intro Video", "Select Intro Video (Optional)")
        # self.directory_menu.AppendSeparator()
        # self.Bind(wx.EVT_MENU, self.OnOpenVid, id=4)
        self.Bind(wx.EVT_MENU, self.OnOpenMusic, id=9)
        self.Bind(wx.EVT_MENU, self.OnOpenMusicVid, id=10)
        self.Bind(wx.EVT_MENU, self.OnOpenIntro, id=11)
        self.frame_menubar.Append(self.directory_menu, "Directories")

        self.url_menu = wx.Menu()
        self.url_menu.Append(12, "&Open Music URL", "Open Selected Music URL")
        self.url_menu.Append(13, "&Open Video URLs", "Open All Selected Video URLs")
        self.Bind(wx.EVT_MENU, self.OnMusicWebpage, id=12)
        self.Bind(wx.EVT_MENU, self.OnVidWebpages, id=13)
        self.frame_menubar.Append(self.url_menu, "Open URLs")

        self.SetMenuBar(self.frame_menubar)

        ######################
        ## Video Directories
        #####################

        self.mainSizerSplit = wx.BoxSizer(wx.HORIZONTAL)

        self.mainSizerOptions = wx.BoxSizer(wx.VERTICAL)
        self.mainSizerSelections = wx.BoxSizer(wx.VERTICAL)

        self.mainSizerOptions.Add(wx.StaticLine(self.panel), 0, wx.ALL | wx.EXPAND, spacing*2)

        # self.mainSizerOptions.Add(wx.StaticLine(self.panel), 0, wx.ALL | wx.EXPAND, spacing*2)
        self.titleProfile = wx.StaticText(self.panel, -1, 'Profile Management', style=wx.ALIGN_CENTRE)
        self.mainSizerOptions.Add(self.titleProfile, 0, wx.ALL | wx.EXPAND, spacing*2)
        # self.mainSizerOptions.Add(wx.StaticLine(self.panel), 0, wx.ALL | wx.EXPAND, spacing*2)

        self.sizerProfileSelect = wx.BoxSizer(wx.HORIZONTAL)
        self.profileComboLabel = wx.StaticText(self.panel, -1, 'Load')
        self.profileComboBox = wx.ComboBox(self.panel, wx.EXPAND, choices=self.profileList)
        self.profileComboBox.Bind(wx.EVT_COMBOBOX, self.loadProfileIntoUI)
        self.profileSaveBtn = wx.Button(self.panel, label="Save")
        self.profileSaveBtn.Bind(wx.EVT_BUTTON, self.saveProfile)
        self.profileDeleteBtn = wx.Button(self.panel, label="Remove")
        self.profileDeleteBtn.Bind(wx.EVT_BUTTON, self.deleteProfile)
        
        self.sizerProfileSelect.Add(self.profileComboLabel, 0, wx.ALL | wx.EXPAND, spacing)
        self.sizerProfileSelect.Add(self.profileComboBox, 1, wx.ALL | wx.EXPAND, spacing)
        self.sizerProfileSelect.Add(self.profileSaveBtn, 0, wx.ALL | wx.EXPAND, spacing)
        self.sizerProfileSelect.Add(self.profileDeleteBtn, 0, wx.ALL | wx.EXPAND, spacing)

        self.mainSizerOptions.Add(self.sizerProfileSelect, 0, wx.ALL | wx.EXPAND, spacing)


        ######################################################################

        self.mainSizerOptions.Add(wx.StaticLine(self.panel), 0, wx.ALL | wx.EXPAND, spacing*2)
        self.inputMusicTitle = wx.StaticText(self.panel, -1, 'Input Music Details', style=wx.ALIGN_CENTRE)
        self.mainSizerOptions.Add(self.inputMusicTitle, 0, wx.ALL | wx.EXPAND, spacing)

        self.sizerMusicVidFileBool = wx.BoxSizer(wx.HORIZONTAL)
        self.musicVidFileLabel = wx.StaticText(self.panel, -1, 'Use Music Video:')
        self.sizerMusicVidFileBool.Add(self.musicVidFileLabel, 1, wx.ALL, spacing)
        self.musicVidFileBool = wx.CheckBox(self.panel)
        self.musicVidFileBool.SetValue(profileOptions["Use Music Video"])
        self.sizerMusicVidFileBool.Add(self.musicVidFileBool, 1, wx.ALL, spacing)
        self.mainSizerOptions.Add(self.sizerMusicVidFileBool, 0, wx.ALL | wx.EXPAND, spacing)

        self.sizerMusicFileTrim = wx.BoxSizer(wx.HORIZONTAL)
        self.musicFileTrimLabel = wx.StaticText(self.panel, -1, 'Trim Music:')
        self.sizerMusicFileTrim.Add(self.musicFileTrimLabel, 1, wx.ALL, spacing)
        self.musicFileTrim = wx.CheckBox(self.panel)
        self.musicFileTrim.SetValue(profileOptions["Trim Music"])
        self.sizerMusicFileTrim.Add(self.musicFileTrim, 1, wx.ALL, spacing)
        self.mainSizerOptions.Add(self.sizerMusicFileTrim, 0, wx.ALL | wx.EXPAND, spacing)

        self.sizerMusicFileStart = wx.BoxSizer(wx.HORIZONTAL)
        self.musicFileStartLabel = wx.StaticText(self.panel, -1, 'Start:')
        self.sizerMusicFileStart.Add(self.musicFileStartLabel, 1, wx.ALL, spacing)
        self.musicFileStart = NumCtrl(self.panel, value=profileOptions["Start Music"])
        self.sizerMusicFileStart.Add(self.musicFileStart, 1, wx.ALL, spacing)
        self.mainSizerOptions.Add(self.sizerMusicFileStart, 0, wx.ALL | wx.EXPAND, spacing)

        self.sizerMusicFileEnd = wx.BoxSizer(wx.HORIZONTAL)
        self.musicFileEndLabel = wx.StaticText(self.panel, -1, 'End:')
        self.sizerMusicFileEnd.Add(self.musicFileEndLabel, 1, wx.ALL, spacing)
        self.musicFileEnd = NumCtrl(self.panel, value=profileOptions["End Music"])
        self.sizerMusicFileEnd.Add(self.musicFileEnd, 1, wx.ALL, spacing)
        self.mainSizerOptions.Add(self.sizerMusicFileEnd, 0, wx.ALL | wx.EXPAND, spacing)

        self.sizerMusicFileOccurance = wx.BoxSizer(wx.HORIZONTAL)
        self.occuranceLabel = wx.StaticText(self.panel, -1, 'Occurance Factor:')
        self.sizerMusicFileOccurance.Add(self.occuranceLabel, 1, wx.ALL, spacing)
        self.occuranceSlider = FS.FloatSpin(self.panel, value=profileOptions["Music Vid Occurance Factor"], min_val=0.0, max_val=5.0, increment=0.05, agwStyle=FS.FS_LEFT)
        self.occuranceSlider.SetDigits(3)
        self.sizerMusicFileOccurance.Add(self.occuranceSlider, 1, wx.ALL, spacing)
        self.mainSizerOptions.Add(self.sizerMusicFileOccurance, 0, wx.ALL | wx.EXPAND, spacing)


        ######################################################################

        self.mainSizerOptions.Add(wx.StaticLine(self.panel), 0, wx.ALL | wx.EXPAND, spacing*2)
        self.inputVideoTitle = wx.StaticText(self.panel, -1, 'Input Video Details', style=wx.ALIGN_CENTRE)
        self.mainSizerOptions.Add(self.inputVideoTitle, 0, wx.ALL | wx.EXPAND, spacing)

        self.sizerNVidsAvailable = wx.BoxSizer(wx.HORIZONTAL)
        self.vidsAvailableTitle = wx.StaticText(self.panel, -1, 'Number of vids available:')
        self.sizerNVidsAvailable.Add(self.vidsAvailableTitle, 1, wx.ALL, spacing)
        self.vidsAvailableNumber = wx.StaticText(self.panel, -1, '')
        self.sizerNVidsAvailable.Add(self.vidsAvailableNumber, 1, wx.ALL | wx.EXPAND, spacing)
        self.mainSizerOptions.Add(self.sizerNVidsAvailable, 0, wx.ALL | wx.EXPAND, spacing)

        self.sizerRefreshSelectBtn = wx.BoxSizer(wx.HORIZONTAL)
        self.refreshSelectLabel = wx.StaticText(self.panel, -1, 'Update Changes:')
        self.sizerRefreshSelectBtn.Add(self.refreshSelectLabel, 1, wx.ALL | wx.EXPAND, spacing)
        self.refreshSelectBtn = wx.Button(self.panel, label="Refresh Selection")
        self.refreshSelectBtn.Bind(wx.EVT_BUTTON, self.resetAll)
        self.sizerRefreshSelectBtn.Add(self.refreshSelectBtn, 1, wx.ALL, spacing)
        self.mainSizerOptions.Add(self.sizerRefreshSelectBtn, 0, wx.ALL | wx.EXPAND, spacing)

        self.sizerVidLengthMin = wx.BoxSizer(wx.HORIZONTAL)
        self.vidLengthMinLabel = wx.StaticText(self.panel, -1, 'Vid Length (Min):')
        self.sizerVidLengthMin.Add(self.vidLengthMinLabel, 1, wx.ALL | wx.EXPAND, spacing)
        self.vidLengthMin = NumCtrl(self.panel, value=self.minVidLength)
        self.sizerVidLengthMin.Add(self.vidLengthMin, 1, wx.ALL, spacing)
        self.mainSizerOptions.Add(self.sizerVidLengthMin, 0, wx.ALL | wx.EXPAND, spacing)

        self.sizerVidLengthMax = wx.BoxSizer(wx.HORIZONTAL)
        self.vidLengthMaxLabel = wx.StaticText(self.panel, -1, 'Vid Length (Max):')
        self.sizerVidLengthMax.Add(self.vidLengthMaxLabel, 1, wx.ALL | wx.EXPAND, spacing)
        self.vidLengthMax = NumCtrl(self.panel, value=self.maxVidLength)
        self.sizerVidLengthMax.Add(self.vidLengthMax, 1, wx.ALL, spacing)
        self.mainSizerOptions.Add(self.sizerVidLengthMax, 0, wx.ALL | wx.EXPAND, spacing)

        self.videoListDuration = self.videoList[self.videoList['Duration'] < self.maxVidLength * 60]
        self.videoListDuration = self.videoList[self.videoList['Duration'] > self.minVidLength * 60]
        self.vidsAvailableNumber.SetLabel(str(self.videoListDuration.shape[0]))

        self.sizerVidSetLengthBtn = wx.BoxSizer(wx.HORIZONTAL)
        self.setLengthLabel = wx.StaticText(self.panel, -1, 'Confirm Changes:')
        self.sizerVidSetLengthBtn.Add(self.setLengthLabel, 1, wx.ALL | wx.EXPAND, spacing)
        self.refreshDurationBtn = wx.Button(self.panel, label="Set Lengths")
        self.refreshDurationBtn.Bind(wx.EVT_BUTTON, self.resetVideoListDuration)
        self.sizerVidSetLengthBtn.Add(self.refreshDurationBtn, 1, wx.ALL, spacing)
        self.mainSizerOptions.Add(self.sizerVidSetLengthBtn, 0, wx.ALL | wx.EXPAND, spacing)

        self.sizerOrCategoriesBool = wx.BoxSizer(wx.HORIZONTAL)
        self.orCategoriesLabel = wx.StaticText(self.panel, -1, 'Category (Or?):')
        self.sizerOrCategoriesBool.Add(self.orCategoriesLabel, 1, wx.ALL, spacing)
        self.orCategories = wx.CheckBox(self.panel)
        self.orCategories.SetValue(profileOptions["Or Category"])
        self.orCategories.Bind(wx.EVT_CHECKBOX, self.categoryOnCombo)
        self.sizerOrCategoriesBool.Add(self.orCategories, 1, wx.ALL | wx.EXPAND, spacing)
        self.mainSizerOptions.Add(self.sizerOrCategoriesBool, 0, wx.ALL | wx.EXPAND, spacing)

        self.sizerOrPornstarsBool = wx.BoxSizer(wx.HORIZONTAL)
        self.orPornstarsLabel = wx.StaticText(self.panel, -1, 'Pornstar (Or?):')
        self.sizerOrPornstarsBool.Add(self.orPornstarsLabel, 1, wx.ALL, spacing)
        self.orPornstars = wx.CheckBox(self.panel)
        self.orPornstars.SetValue(profileOptions["Or Pornstar"])
        self.orPornstars.Bind(wx.EVT_CHECKBOX, self.pornstarOnCombo)
        self.sizerOrPornstarsBool.Add(self.orPornstars, 1, wx.ALL | wx.EXPAND, spacing)
        self.mainSizerOptions.Add(self.sizerOrPornstarsBool, 0, wx.ALL | wx.EXPAND, spacing)

        self.sizerNVidsSelect = wx.BoxSizer(wx.HORIZONTAL)
        self.nVidsLabel = wx.StaticText(self.panel, -1, 'Select Vids Number:')
        self.sizerNVidsSelect.Add(self.nVidsLabel, 1, wx.ALL, spacing)
        self.nVidsSlider = FS.FloatSpin(self.panel, value=profileOptions["Select Vids N"], min_val=0, max_val=100, increment=1, agwStyle=FS.FS_LEFT)
        self.nVidsSlider.SetDigits(0)
        self.sizerNVidsSelect.Add(self.nVidsSlider, 1, wx.ALL, spacing)
        self.mainSizerOptions.Add(self.sizerNVidsSelect, 0, wx.ALL | wx.EXPAND, spacing)

        self.sizerUrlAddBtn = wx.BoxSizer(wx.HORIZONTAL)
        self.urlAddLabel = wx.StaticText(self.panel, -1, 'Click to Add n Vids:')
        self.sizerUrlAddBtn.Add(self.urlAddLabel, 1, wx.ALL, spacing)
        self.urlAddBtn = wx.Button(self.panel, label="Add URLs")
        self.urlAddBtn.Bind(wx.EVT_BUTTON, self.onAddURLs)
        self.sizerUrlAddBtn.Add(self.urlAddBtn, 1, wx.ALL, spacing)
        self.mainSizerOptions.Add(self.sizerUrlAddBtn, 0, wx.ALL | wx.EXPAND, spacing)

        ###################################################################


        ######################
        ## Video Trimming
        #####################

        self.mainSizerOptions.Add(wx.StaticLine(self.panel), 0, wx.ALL | wx.EXPAND, spacing*2)
        self.vidDetailsTitle = wx.StaticText(self.panel, -1, 'Output Video Details', style=wx.ALIGN_CENTRE)
        self.mainSizerOptions.Add(self.vidDetailsTitle, 0, wx.ALL | wx.EXPAND, spacing)

        self.sizerOutputVid = wx.BoxSizer(wx.HORIZONTAL)
        self.outputVidCropLabel = wx.StaticText(self.panel, -1, 'Crop to Wide View:')
        self.sizerOutputVid.Add(self.outputVidCropLabel, 1, wx.ALL, spacing)
        self.outputVidCrop = wx.CheckBox(self.panel)
        self.outputVidCrop.SetValue(profileOptions["Crop To Wide"])
        self.sizerOutputVid.Add(self.outputVidCrop, 1, wx.ALL, spacing)
        self.mainSizerOptions.Add(self.sizerOutputVid, 0, wx.ALL | wx.EXPAND, spacing)

        self.sizerOutputVidFrac = wx.BoxSizer(wx.HORIZONTAL)
        self.outputVidCropFracLabel = wx.StaticText(self.panel, -1, 'Crop Percentage:')
        self.sizerOutputVidFrac.Add(self.outputVidCropFracLabel, 1, wx.ALL | wx.EXPAND, spacing)
        self.outputVidCropFracSlider = FS.FloatSpin(self.panel, value=profileOptions["Crop Percentage"], min_val=0.0, max_val=0.5, increment=0.005, agwStyle=FS.FS_LEFT)
        self.outputVidCropFracSlider.SetDigits(3)
        self.sizerOutputVidFrac.Add(self.outputVidCropFracSlider, 1, wx.ALL, spacing)
        self.mainSizerOptions.Add(self.sizerOutputVidFrac, 0, wx.ALL | wx.EXPAND, spacing)

        self.sizerAddIntroBool = wx.BoxSizer(wx.HORIZONTAL)
        self.addIntroLabel = wx.StaticText(self.panel, -1, 'Add intro video:')
        self.sizerAddIntroBool.Add(self.addIntroLabel, 1, wx.ALL, spacing)
        self.addIntroBool = wx.CheckBox(self.panel)
        self.addIntroBool.SetValue(profileOptions["Add Intro Video"])
        self.sizerAddIntroBool.Add(self.addIntroBool, 1, wx.ALL, spacing)
        self.mainSizerOptions.Add(self.sizerAddIntroBool, 0, wx.ALL | wx.EXPAND, spacing)

        self.sizerStartTrimVideo = wx.BoxSizer(wx.HORIZONTAL)
        self.startTrimLabel = wx.StaticText(self.panel, -1, 'Start Time:')
        self.sizerStartTrimVideo.Add(self.startTrimLabel, 1, wx.ALL | wx.EXPAND, spacing)
        self.startTrim = NumCtrl(self.panel, value=profileOptions["Vid Start Trim"])
        self.sizerStartTrimVideo.Add(self.startTrim, 1, wx.ALL | wx.EXPAND, spacing)
        self.mainSizerOptions.Add(self.sizerStartTrimVideo, 0, wx.ALL | wx.EXPAND, spacing)

        self.sizerEndTrimVideo = wx.BoxSizer(wx.HORIZONTAL)
        self.endTrimLabel = wx.StaticText(self.panel, -1, 'End Trim:')
        self.sizerEndTrimVideo.Add(self.endTrimLabel, 1, wx.ALL | wx.EXPAND, spacing)
        self.endTrim = NumCtrl(self.panel, value=profileOptions["Vid End Trim"])
        self.sizerEndTrimVideo.Add(self.endTrim, 1, wx.ALL | wx.EXPAND, spacing)
        self.mainSizerOptions.Add(self.sizerEndTrimVideo, 0, wx.ALL | wx.EXPAND, spacing)

        ######################
        ## More configuration
        #####################

        self.sizerNSplits = wx.BoxSizer(wx.HORIZONTAL)
        self.nSplitsLabel = wx.StaticText(self.panel, -1, 'nSplits:')
        self.sizerNSplits.Add(self.nSplitsLabel, 1, wx.ALL | wx.EXPAND, spacing)
        self.nSplitsSlider = FS.FloatSpin(self.panel, value=profileOptions["nSplits"], min_val=0, max_val=50, increment=1, agwStyle=FS.FS_LEFT)
        self.nSplitsSlider.SetDigits(0)
        self.sizerNSplits.Add(self.nSplitsSlider, 1, wx.ALL | wx.EXPAND, spacing)
        self.mainSizerOptions.Add(self.sizerNSplits, 0, wx.ALL | wx.EXPAND, spacing)

        self.sizerSd = wx.BoxSizer(wx.HORIZONTAL)
        self.sdLabel = wx.StaticText(self.panel, -1, 'SD for clip switch:')
        self.sizerSd.Add(self.sdLabel, 1, wx.ALL | wx.EXPAND, spacing)
        self.sdSlider = FS.FloatSpin(self.panel, value=profileOptions["SD For Clip Switch"], min_val=0.0, max_val=5.0, increment=0.05, agwStyle=FS.FS_LEFT)
        self.sdSlider.SetDigits(3)
        self.sizerSd.Add(self.sdSlider, 1, wx.ALL | wx.EXPAND, spacing)
        self.mainSizerOptions.Add(self.sizerSd, 0, wx.ALL | wx.EXPAND, spacing)

        self.sizerGranularity = wx.BoxSizer(wx.HORIZONTAL)
        self.granularityLabel = wx.StaticText(self.panel, -1, 'Granularity:')
        self.sizerGranularity.Add(self.granularityLabel, 1, wx.ALL | wx.EXPAND, spacing)
        self.granularitySlider = FS.FloatSpin(self.panel, value=profileOptions["Granularity"], min_val=0.0, max_val=0.5, increment=0.01, agwStyle=FS.FS_LEFT)
        self.granularitySlider.SetDigits(3)
        self.sizerGranularity.Add(self.granularitySlider, 1, wx.ALL | wx.EXPAND, spacing)
        self.mainSizerOptions.Add(self.sizerGranularity, 0, wx.ALL | wx.EXPAND, spacing)

        self.sizerMinClipLength = wx.BoxSizer(wx.HORIZONTAL)
        self.minClipLengthLabel = wx.StaticText(self.panel, -1, 'Min Clip Length')
        self.sizerMinClipLength.Add(self.minClipLengthLabel, 1, wx.ALL | wx.EXPAND, spacing)
        self.minClipLengthSlider = FS.FloatSpin(self.panel, value=profileOptions["Min Clip Length"], min_val=0.0, max_val=1, increment=0.01, agwStyle=FS.FS_LEFT)
        self.minClipLengthSlider.SetDigits(3)
        self.sizerMinClipLength.Add(self.minClipLengthSlider, 1, wx.ALL | wx.EXPAND, spacing)
        self.mainSizerOptions.Add(self.sizerMinClipLength, 0, wx.ALL | wx.EXPAND, spacing)

        ######################
        ## Other flags
        #####################

        self.sizerRandomiseBool = wx.BoxSizer(wx.HORIZONTAL)
        self.randomiseLabel = wx.StaticText(self.panel, -1, 'Randomise:')
        self.sizerRandomiseBool.Add(self.randomiseLabel, 1, wx.ALL, spacing)
        self.randomiseCB = wx.CheckBox(self.panel)
        self.randomiseCB.SetValue(profileOptions["Randomise"])
        self.sizerRandomiseBool.Add(self.randomiseCB, 1, wx.ALL, spacing)
        self.mainSizerOptions.Add(self.sizerRandomiseBool, 0, wx.ALL | wx.EXPAND, spacing)

        self.sizerResizeBool = wx.BoxSizer(wx.HORIZONTAL)
        self.resizeLabel = wx.StaticText(self.panel, -1, 'Resize:')
        self.sizerResizeBool.Add(self.resizeLabel, 1, wx.ALL, spacing)
        self.resizeCB = wx.CheckBox(self.panel)
        self.resizeCB.SetValue(profileOptions["Resize"])
        self.sizerResizeBool.Add(self.resizeCB, 1, wx.ALL, spacing)
        self.mainSizerOptions.Add(self.sizerResizeBool, 0, wx.ALL | wx.EXPAND, spacing)

        self.sizerFlipVidsBool = wx.BoxSizer(wx.HORIZONTAL)
        self.flipVidLabel = wx.StaticText(self.panel, -1, 'Flip Vids:')
        self.sizerFlipVidsBool.Add(self.flipVidLabel, 1, wx.ALL, spacing)
        self.flipVidCB = wx.CheckBox(self.panel)
        self.flipVidCB.SetValue(profileOptions["Flip Vids"])
        self.sizerFlipVidsBool.Add(self.flipVidCB, 1, wx.ALL, spacing)
        self.mainSizerOptions.Add(self.sizerFlipVidsBool, 0, wx.ALL | wx.EXPAND, spacing)

        self.sizerUseClassifierBool = wx.BoxSizer(wx.HORIZONTAL)
        self.useClassifierLabel = wx.StaticText(self.panel, -1, 'ClassifyModel:')
        self.sizerUseClassifierBool.Add(self.useClassifierLabel, 1, wx.ALL, spacing)
        self.useClassifierBool = wx.CheckBox(self.panel)
        self.useClassifierBool.SetValue(profileOptions["Classify Model"])
        self.sizerUseClassifierBool.Add(self.useClassifierBool, 1, wx.ALL, spacing)
        self.mainSizerOptions.Add(self.sizerUseClassifierBool, 0, wx.ALL | wx.EXPAND, spacing)

        ######################
        ## Output Name
        #####################

        self.sizerUserName = wx.BoxSizer(wx.HORIZONTAL)
        self.userNameLabel = wx.StaticText(self.panel, -1, 'User Name:')
        self.sizerUserName.Add(self.userNameLabel, 1, wx.ALL | wx.EXPAND, spacing)
        self.userNameName = wx.TextCtrl(self.panel, value=self.username)
        self.sizerUserName.Add(self.userNameName, 1, wx.ALL | wx.EXPAND, spacing)
        self.mainSizerOptions.Add(self.sizerUserName, 0, wx.ALL | wx.EXPAND, spacing)

        self.mainSizerSplit.Add(self.mainSizerOptions, 0, wx.ALL | wx.EXPAND, spacing)

        ######################
        ## Music Selection
        #####################

        self.mainSizerMusic = wx.BoxSizer(wx.HORIZONTAL)
        self.sizerMusicTitle = wx.BoxSizer(wx.VERTICAL)
        self.sizerMusicSelection = wx.BoxSizer(wx.VERTICAL)

        self.mainSizerSelections.Add(wx.StaticLine(self.panel), 0, wx.ALL | wx.EXPAND, spacing)

        self.sizerMusicSelectionLabel = wx.StaticText(self.panel, -1, 'Select music from list: ')
        self.sizerMusicTitle.Add(self.sizerMusicSelectionLabel, 1, wx.ALL | wx.EXPAND, spacing)
        self.musicURLSizerLabel = wx.StaticText(self.panel, -1, 'Enter Music URL Here: ')
        self.sizerMusicTitle.Add(self.musicURLSizerLabel, 1, wx.ALL | wx.EXPAND, spacing)
        self.mainSizerMusic.Add(self.sizerMusicTitle, 0, wx.ALL | wx.EXPAND, spacing)

        self.musicComboBox = wx.ComboBox(self.panel, choices=self.musicList)
        self.musicComboBox.Bind(wx.EVT_COMBOBOX, self.musicOnCombo)
        self.sizerMusicSelection.Add(self.musicComboBox, 1, wx.ALL | wx.EXPAND, spacing)
        self.musicURLselect = wx.TextCtrl(self.panel, value='')
        self.sizerMusicSelection.Add(self.musicURLselect, 1, wx.ALL | wx.EXPAND, spacing)
        self.mainSizerMusic.Add(self.sizerMusicSelection, 1, wx.EXPAND, spacing)

        self.mainSizerSelections.Add(self.mainSizerMusic, 0, wx.ALL | wx.EXPAND, spacing)
        self.mainSizerSelections.Add(wx.StaticLine(self.panel), 0, wx.ALL | wx.EXPAND, spacing)

        ######################
        ## Video Selection
        #####################


        ######################
        ## Video Selection
        #####################

        xSize = 200
        ySize = 25

        self.mainSizerCategoryVidSelect = wx.BoxSizer(wx.HORIZONTAL)
        self.sizerCategoryVidSelectLabel = wx.BoxSizer(wx.VERTICAL)
        self.sizerCategoryVidSelectCombo = wx.BoxSizer(wx.VERTICAL)
        self.sizerCategoryVidSelectOutput = wx.BoxSizer(wx.VERTICAL)
        self.categoryComboLabel = wx.StaticText(self.panel, 1, 'Select Category', size=(xSize, ySize))
        self.categoryComboBox = wx.ComboBox(self.panel, choices=self.categoryList, size=(xSize, ySize))
        self.categoryComboBox.Bind(wx.EVT_COMBOBOX, self.categoryOnCombo)
        self.categoryComboSelection = wx.TextCtrl(self.panel, style=wx.TE_MULTILINE | wx.TE_READONLY, size=(xSize, ySize))
        self.sizerCategoryVidSelectLabel.Add(self.categoryComboLabel, 1, wx.ALL | wx.EXPAND, spacing)
        self.sizerCategoryVidSelectCombo.Add(self.categoryComboBox, 1, wx.ALL | wx.EXPAND, spacing)
        self.sizerCategoryVidSelectOutput.Add(self.categoryComboSelection, 1, wx.ALL | wx.EXPAND, spacing)

        self.excludeCategoryComboLabel = wx.StaticText(self.panel, 1, 'Exclude Category', size=(xSize, ySize))
        self.excludeCategoryComboBox = wx.ComboBox(self.panel, choices=self.categoryList, size=(xSize, ySize))
        self.excludeCategoryComboBox.Bind(wx.EVT_COMBOBOX, self.excludeCategoryOnCombo)
        self.excludeCategoryComboSelection = wx.TextCtrl(self.panel, style=wx.TE_MULTILINE | wx.TE_READONLY, size=(xSize, ySize))
        self.sizerCategoryVidSelectLabel.Add(self.excludeCategoryComboLabel, 1, wx.ALL | wx.EXPAND, spacing)
        self.sizerCategoryVidSelectCombo.Add(self.excludeCategoryComboBox, 1, wx.ALL | wx.EXPAND, spacing)
        self.sizerCategoryVidSelectOutput.Add(self.excludeCategoryComboSelection, 1, wx.ALL | wx.EXPAND, spacing)

        #################################################################

        self.pornstarComboLabel = wx.StaticText(self.panel, 1, 'Select Pornstar', size=(xSize, ySize))
        self.pornstarComboBox = wx.ComboBox(self.panel, choices=self.pornstarList, size=(xSize, ySize))
        self.pornstarComboBox.Bind(wx.EVT_COMBOBOX, self.pornstarOnCombo)
        self.pornstarComboSelection = wx.TextCtrl(self.panel, style=wx.TE_MULTILINE | wx.TE_READONLY, size=(xSize, ySize))
        self.sizerCategoryVidSelectLabel.Add(self.pornstarComboLabel, 1, wx.ALL | wx.EXPAND, spacing)
        self.sizerCategoryVidSelectCombo.Add(self.pornstarComboBox, 1, wx.ALL | wx.EXPAND, spacing)
        self.sizerCategoryVidSelectOutput.Add(self.pornstarComboSelection, 1, wx.ALL | wx.EXPAND, spacing)

        self.excludePornstarComboLabel = wx.StaticText(self.panel, 1, 'Exclude Pornstar', size=(xSize, ySize))
        self.excludePornstarComboBox = wx.ComboBox(self.panel, choices=self.pornstarList, size=(xSize, ySize))
        self.excludePornstarComboBox.Bind(wx.EVT_COMBOBOX, self.excludePornstarOnCombo)
        self.excludePornstarComboSelection = wx.TextCtrl(self.panel, style=wx.TE_MULTILINE | wx.TE_READONLY, size=(xSize, ySize))
        self.sizerCategoryVidSelectLabel.Add(self.excludePornstarComboLabel, 1, wx.ALL | wx.EXPAND, spacing)
        self.sizerCategoryVidSelectCombo.Add(self.excludePornstarComboBox, 1, wx.ALL | wx.EXPAND, spacing)
        self.sizerCategoryVidSelectOutput.Add(self.excludePornstarComboSelection, 1, wx.ALL | wx.EXPAND, spacing)


        #################################################################

        self.channelComboLabel = wx.StaticText(self.panel, 1, 'Select Channel', size=(xSize, ySize))
        self.channelComboBox = wx.ComboBox(self.panel, choices=self.channelList, size=(xSize, ySize))
        self.channelComboBox.Bind(wx.EVT_COMBOBOX, self.channelOnCombo)
        self.channelComboSelection = wx.TextCtrl(self.panel, style=wx.TE_MULTILINE | wx.TE_READONLY, size=(xSize, ySize))
        self.sizerCategoryVidSelectLabel.Add(self.channelComboLabel, 1, wx.ALL | wx.EXPAND, spacing)
        self.sizerCategoryVidSelectCombo.Add(self.channelComboBox, 1, wx.ALL | wx.EXPAND, spacing)
        self.sizerCategoryVidSelectOutput.Add(self.channelComboSelection, 1, wx.ALL | wx.EXPAND, spacing)

        self.excludeChannelComboLabel = wx.StaticText(self.panel, 1, 'Exclude Channel', size=(xSize, ySize))
        self.excludeChannelComboBox = wx.ComboBox(self.panel, choices=self.channelList, size=(xSize, ySize))
        self.excludeChannelComboBox.Bind(wx.EVT_COMBOBOX, self.excludeChannelOnCombo)
        self.excludeChannelComboSelection = wx.TextCtrl(self.panel, style=wx.TE_MULTILINE | wx.TE_READONLY, size=(xSize, ySize))
        self.sizerCategoryVidSelectLabel.Add(self.excludeChannelComboLabel, 1, wx.ALL | wx.EXPAND, spacing)
        self.sizerCategoryVidSelectCombo.Add(self.excludeChannelComboBox, 1, wx.ALL | wx.EXPAND, spacing)
        self.sizerCategoryVidSelectOutput.Add(self.excludeChannelComboSelection, 1, wx.ALL | wx.EXPAND, spacing)

        self.mainSizerCategoryVidSelect.Add(self.sizerCategoryVidSelectLabel, 0, wx.ALL, spacing)
        self.mainSizerCategoryVidSelect.Add(self.sizerCategoryVidSelectCombo, 1, wx.ALL, spacing)
        self.mainSizerCategoryVidSelect.Add(self.sizerCategoryVidSelectOutput, 1, wx.ALL, spacing)

        self.mainSizerSelections.Add(self.mainSizerCategoryVidSelect, 0, wx.ALL | wx.EXPAND, spacing)

        ######################
        ## Add Individual Video
        #####################

        self.videoListFiltered = self.videoList
        self.videoListFiltered["Summary"] = self.videoListFiltered["Title"].astype(str) + "--" + self.videoListFiltered.index.astype(str)
        self.videoListFiltered = self.videoListFiltered.sort_values(by="Summary", ascending=True)
        self.videoListFiltered = self.videoListFiltered["Summary"].to_list()

        self.sizerIndividualVid = wx.BoxSizer(wx.HORIZONTAL)

        self.sizerIndividualVidLabel = wx.StaticText(self.panel, -1, 'Select video from list: ')
        self.sizerIndividualVid.Add(self.sizerIndividualVidLabel, 0, wx.ALL | wx.EXPAND, spacing)
        self.individualVidComboBox = wx.ComboBox(self.panel, choices=self.videoListFiltered)
        self.individualVidComboBox.Bind(wx.EVT_COMBOBOX_DROPDOWN, self.onRefreshIndividualVidCombo)
        self.individualVidComboBox.Bind(wx.EVT_COMBOBOX, self.onIndividualVidCombo)
        self.sizerIndividualVid.Add(self.individualVidComboBox, 0, wx.ALL | wx.EXPAND, spacing)

        self.mainSizerSelections.Add(self.sizerIndividualVid, 0, wx.ALL | wx.EXPAND, spacing)

        ######################
        ## Video URLs
        #####################

        self.sizerVideoSelect = wx.BoxSizer(wx.VERTICAL)
        self.videoSelectSizerLabel = wx.StaticText(self.panel, -1, 'Enter Video URLs Here:')
        self.sizerVideoSelect.Add(self.videoSelectSizerLabel, 0, wx.ALL | wx.EXPAND, spacing)

        self.videURLselect = wx.TextCtrl(self.panel, value='', style=wx.TE_MULTILINE)
        self.sizerVideoSelect.Add(self.videURLselect, 1, wx.EXPAND, spacing)
        self.mainSizerSelections.Add(self.sizerVideoSelect, 1, wx.ALL | wx.EXPAND, spacing)

        #################################
        ####### Output Name
        #################################

        self.sizerOutputFile = wx.BoxSizer(wx.HORIZONTAL)
        self.outputFileLabel = wx.StaticText(self.panel, -1, 'Output File Name:')
        self.sizerOutputFile.Add(self.outputFileLabel, 0, wx.ALL | wx.EXPAND, spacing)
        self.outputFileName = wx.TextCtrl(self.panel, value='')
        self.sizerOutputFile.Add(self.outputFileName, 1, wx.ALL | wx.EXPAND, spacing)
        self.mainSizerSelections.Add(self.sizerOutputFile, 0, wx.ALL | wx.EXPAND, spacing)

        ######################
        ## Button
        #####################

        self.runButton = wx.Button(self.panel, label='Start')
        self.runButton.Bind(wx.EVT_BUTTON, self.onMakePMV)
        self.mainSizerSelections.Add(self.runButton, 0, wx.ALL | wx.CENTER, spacing)

        ######################
        ## Log Display
        #####################
        self.logger = wx.TextCtrl(self.panel, style=wx.TE_MULTILINE | wx.TE_READONLY)
        self.mainSizerSelections.Add(self.logger, 0, wx.ALL | wx.EXPAND, spacing)

        self.mainSizerSplit.Add(wx.StaticLine(self.panel, style=wx.LI_VERTICAL), 0, wx.ALL | wx.EXPAND, spacing*2)
        self.mainSizerSplit.Add(self.mainSizerSelections, 0, wx.ALL | wx.EXPAND, spacing)

        # self.mainSizer.Add(wx.StaticLine(self.panel), 0, wx.ALL | wx.EXPAND, spacing)
        self.mainSizer.Add(self.mainSizerSplit, 0, wx.ALL | wx.EXPAND, spacing)
        self.mainSizer.Add(wx.StaticLine(self.panel), 0, wx.ALL | wx.EXPAND, spacing)
        self.panel.SetSizer(self.mainSizer)

        self.Show()

    def reallySimplifyView(self, event):
        self.filterMainSizers(False)
        self.filterAdditionalSizers(False)

    def simplifyView(self, event):
        self.filterAdditionalSizers(True)
        self.filterMainSizers(False)

    def advancedView(self, event):
        self.filterMainSizers(True)
        self.filterAdditionalSizers(True)

    def filterAdditionalSizers(self, OnOff):
        self.sizerProfileSelect.ShowItems(show=OnOff)

        self.sizerVideoSelect.ShowItems(show=OnOff)
        self.sizerIndividualVid.ShowItems(show=OnOff)
        self.mainSizerCategoryVidSelect.ShowItems(show=OnOff)
        self.mainSizerMusic.ShowItems(show=OnOff)

        self.sizerNVidsAvailable.ShowItems(show=OnOff)
        self.sizerNVidsSelect.ShowItems(show=OnOff)
        self.sizerUrlAddBtn.ShowItems(show=OnOff)

    def filterMainSizers(self, OnOff):
        self.sizerMusicVidFileBool.ShowItems(show=OnOff)
        self.sizerMusicFileTrim.ShowItems(show=OnOff)
        self.sizerMusicFileStart.ShowItems(show=OnOff)
        self.sizerMusicFileEnd.ShowItems(show=OnOff)
        self.sizerMusicFileOccurance.ShowItems(show=OnOff)

        self.sizerRefreshSelectBtn.ShowItems(show=OnOff)
        self.sizerVidLengthMin.ShowItems(show=OnOff)
        self.sizerVidLengthMax.ShowItems(show=OnOff)
        self.sizerVidSetLengthBtn.ShowItems(show=OnOff)
        self.sizerOrCategoriesBool.ShowItems(show=OnOff)
        self.sizerOrPornstarsBool.ShowItems(show=OnOff)

        self.sizerOutputVid.ShowItems(show=OnOff)
        self.sizerOutputVidFrac.ShowItems(show=OnOff)
        self.sizerAddIntroBool.ShowItems(show=OnOff)
        self.sizerStartTrimVideo.ShowItems(show=OnOff)
        self.sizerEndTrimVideo.ShowItems(show=OnOff)
        self.sizerNSplits.ShowItems(show=OnOff)
        self.sizerSd.ShowItems(show=OnOff)
        self.sizerGranularity.ShowItems(show=OnOff)
        self.sizerMinClipLength.ShowItems(show=OnOff)
        self.sizerRandomiseBool.ShowItems(show=OnOff)
        self.sizerResizeBool.ShowItems(show=OnOff)
        self.sizerFlipVidsBool.ShowItems(show=OnOff)
        self.sizerUseClassifierBool.ShowItems(show=OnOff)
        self.sizerUserName.ShowItems(show=OnOff)
        # self.panel.Layout()

    def loadProfileIntoUI(self, event):
        self.currentProfile = self.profileComboBox.GetValue()
        profileOptions = loadProfile(self.currentProfile)
        self.setProfileValues(profileOptions)
        
    def saveProfile(self, event):
        self.currentProfile = self.profileComboBox.GetValue()
        profileOptions = self.getProfileValues()
        newProfile = dict()
        newProfile[self.currentProfile] = profileOptions
        addNewProfile(newProfile)
        listOfProfiles = self.profileList
        listOfProfiles.append(self.currentProfile)
        self.profileList = list(dict.fromkeys(listOfProfiles))
        self.profileComboBox.SetItems(self.profileList)

    def deleteProfile(self, event):
        self.currentProfile = self.profileComboBox.GetValue()
        if self.currentProfile != "Default":
            removeProfile(self.currentProfile)
            listOfProfiles = self.profileList
            listOfProfiles.remove(self.currentProfile)
            self.profileList = list(dict.fromkeys(listOfProfiles))
            self.profileComboBox.SetItems(self.profileList)

    def setProfileValues(self, profileOptions):

        self.customVidDir = profileOptions["defaultVideoDownloadPath"]
        self.customMusicDir = profileOptions["defaultMusicDownloadPath"]
        self.customMusicVidDir = profileOptions["defaultMusicVidDownloadPath"]
        self.customOutputDir = profileOptions["defaultNewPMVsPath"]
        self.introVidName = profileOptions["introVideoPath"]
        self.username = profileOptions["Username"]
        self.musicVidFileBool.SetValue(profileOptions["Use Music Video"])
        self.musicFileTrim.SetValue(profileOptions["Trim Music"])
        self.musicFileStart.ChangeValue(profileOptions["Start Music"])
        self.musicFileEnd.ChangeValue(profileOptions["End Music"])
        self.occuranceSlider.SetValue(profileOptions["Music Vid Occurance Factor"])
        self.orCategories.SetValue(profileOptions["Or Category"])
        self.orPornstars.SetValue(profileOptions["Or Pornstar"])
        self.nVidsSlider.SetValue(profileOptions["Select Vids N"])
        self.vidLengthMin.ChangeValue(profileOptions["Min Vid Length"])
        self.vidLengthMax.ChangeValue(profileOptions["Max Vid Length"])
        self.outputVidCrop.SetValue(profileOptions["Crop To Wide"])
        self.outputVidCropFracSlider.SetValue(profileOptions["Crop Percentage"])
        self.addIntroBool.SetValue(profileOptions["Add Intro Video"])
        self.startTrim.ChangeValue(profileOptions["Vid Start Trim"])
        self.endTrim.ChangeValue(profileOptions["Vid End Trim"])
        self.nSplitsSlider.SetValue(profileOptions["nSplits"])
        self.sdSlider.SetValue(profileOptions["SD For Clip Switch"])
        self.granularitySlider.SetValue(profileOptions["Granularity"])
        self.minClipLengthSlider.SetValue(profileOptions["Min Clip Length"])
        self.randomiseCB.SetValue(profileOptions["Randomise"])
        self.resizeCB.SetValue(profileOptions["Resize"])
        self.flipVidCB.SetValue(profileOptions["Flip Vids"])
        self.useClassifierBool.SetValue(profileOptions["Classify Model"])

    def getProfileValues(self):
        profileOptions=dict()
        profileOptions["defaultVideoDownloadPath"] = self.customVidDir
        profileOptions["defaultMusicDownloadPath"] = self.customMusicDir
        profileOptions["defaultMusicVidDownloadPath"] = self.customMusicVidDir
        profileOptions["defaultNewPMVsPath"] = self.customOutputDir
        profileOptions["introVideoPath"] = self.introVidName
        profileOptions["Username"] = self.userNameName.GetValue()
        profileOptions["Use Music Video"] = self.musicVidFileBool.GetValue()
        profileOptions["Trim Music"] = self.musicFileTrim.GetValue()
        profileOptions["Start Music"] = self.musicFileStart.GetValue()
        profileOptions["End Music"] = self.musicFileEnd.GetValue()
        profileOptions["Music Vid Occurance Factor"] = self.occuranceSlider.GetValue()
        profileOptions["Or Category"] = self.orCategories.GetValue()
        profileOptions["Or Pornstar"] = self.orPornstars.GetValue()
        profileOptions["Select Vids N"] = self.nVidsSlider.GetValue()
        profileOptions["Min Vid Length"] = self.vidLengthMin.GetValue()
        profileOptions["Max Vid Length"] = self.vidLengthMax.GetValue()
        profileOptions["Crop To Wide"] = self.outputVidCrop.GetValue()
        profileOptions["Crop Percentage"] = self.outputVidCropFracSlider.GetValue()
        profileOptions["Add Intro Video"] = self.addIntroBool.GetValue()
        profileOptions["Vid Start Trim"] = self.startTrim.GetValue()
        profileOptions["Vid End Trim"] = self.endTrim.GetValue()
        profileOptions["nSplits"] = self.nSplitsSlider.GetValue()
        profileOptions["SD For Clip Switch"] = self.sdSlider.GetValue()
        profileOptions["Granularity"] = self.granularitySlider.GetValue()
        profileOptions["Min Clip Length"] = self.minClipLengthSlider.GetValue()
        profileOptions["Randomise"] = self.randomiseCB.GetValue()
        profileOptions["Resize"] = self.resizeCB.GetValue()
        profileOptions["Flip Vids"] = self.flipVidCB.GetValue()
        profileOptions["Classify Model"] = self.useClassifierBool.GetValue()

        return profileOptions

    def OnOpenIntro(self, event):
        dlg = wx.FileDialog(self, "Choose a file", style=wx.FD_OPEN, defaultFile=self.introVidName)
        if dlg.ShowModal() == wx.ID_OK:
            self.introVidName = dlg.GetPath()
        dlg.Destroy()

    def OnOpenMusicFile(self, event):
        print(self.customMusicDir[:-1])
        dlg = wx.FileDialog(self, "Choose a file", style=wx.FD_OPEN, defaultDir=self.customMusicDir[:-1])
        dlg.SetDirectory(self.customMusicDir[:-1])
        if dlg.ShowModal() == wx.ID_OK:
            self.musicFilePath = dlg.GetPath()

        if self.musicFilePath != "":
            self.musicName = os.path.basename(self.musicFilePath).replace(".mp4","")
            self.changeTitleName()
        dlg.Destroy()

    def joinArtistsFn(self, x):
        ArtistString = ""
        nArtists = 5
        iArtist=1
        ArtistList = []
        while iArtist <= nArtists:
            if str(x["_Artist" + str(iArtist)]) != 'nan':
                ArtistList.append(str(x["_Artist" + str(iArtist)]))
            iArtist = iArtist + 1
        ArtistList = dict.fromkeys(ArtistList)
        ArtistString = " ".join(ArtistList)
        return ArtistString

    def changeTitleName(self):
        if len(self.includePornstars+self.includeChannels+self.includeCategories)>0:
            self.outputFileName.SetValue(" ".join(self.includePornstars+self.includeChannels+self.includeCategories) + ' PMV - ' + self.musicName + ' - ' + self.musicArtist + ' - ' + self.username)
        else:
            fileName = os.path.basename(os.path.normpath(self.customVidDir))
            if fileName != os.path.basename(os.path.normpath(PathList["defaultVideoDownloadPath"])):
                self.outputFileName.SetValue(fileName.replace("LocalRandomVideos","") + ' PMV - ' + self.musicName + ' - ' + self.musicArtist + ' - ' + self.username)
                self.outputFileName.SetValue(fileName.replace("RandomVideos","") + ' PMV - ' + self.musicName + ' - ' + self.musicArtist + ' - ' + self.username)
            else:
                self.outputFileName.SetValue(' PMV - ' + self.musicName + ' - ' + self.musicArtist + ' - ' + self.username)


    def joinSummaryMusicString(self, x):
        SummaryString = x["Artist"] + "--" + x["Title"] + "--" + x["Type"] + "--" + x["Index"]
        return SummaryString

    def OnOpenVid(self, event):
        print(self.customVidDir)
        dlg = wx.DirDialog(self, "Choose a file", defaultPath=self.customVidDir, style=wx.FD_OPEN)
        if dlg.ShowModal() == wx.ID_OK:
            self.customVidDir = dlg.Path + "/"
            self.changeTitleName()
        dlg.Destroy()

    def OnOpenMusic(self, event):
        dlg = wx.DirDialog(self, "Choose a file", defaultPath=self.customMusicDir, style=wx.FD_OPEN)
        if dlg.ShowModal() == wx.ID_OK:
            self.customMusicDir = dlg.Path + "/"
        dlg.Destroy()

    def OnOpenMusicVid(self, event):
        dlg = wx.DirDialog(self, "Choose a file", defaultPath=self.customMusicVidDir, style=wx.FD_OPEN)
        if dlg.ShowModal() == wx.ID_OK:
            self.customMusicVidDir = dlg.Path + "/"
        dlg.Destroy()

    def OnOpenOutput(self, event):
        dlg = wx.DirDialog(self, "Choose a file", defaultPath=self.customOutputDir, style=wx.FD_OPEN)
        if dlg.ShowModal() == wx.ID_OK:
            self.customOutputDir = dlg.Path + "/"
        dlg.Destroy()

    def resetVideoListDuration(self, event):
        self.minVidLength = self.vidLengthMin.GetValue()
        self.maxVidLength = self.vidLengthMax.GetValue()
        self.videoList = self.videoListOriginal
        self.videoList = self.videoList[self.videoList['Duration'] < self.maxVidLength * 60]
        self.videoList = self.videoList[self.videoList['Duration'] > self.minVidLength * 60]
        self.changeVideoList(event)
        self.categoryComboBox.SetItems(self.categoryList)
        self.pornstarComboBox.SetItems(self.pornstarList)
        self.channelComboBox.SetItems(self.channelList)
        self.excludeCategoryComboBox.SetItems(self.categoryList)
        self.excludePornstarComboBox.SetItems(self.pornstarList)
        self.excludeChannelComboBox.SetItems(self.channelList)
        self.vidsAvailableNumber.SetLabel(str(self.videoList.shape[0]))

    def musicOnCombo(self, event):
        self.musicID = self.musicComboBox.GetValue().split('--', 3)[3]
        print(self.musicID)
        self.musicArtist = self.musicComboBox.GetValue().split('--', 1)[0]
        self.musicArtist = self.musicArtist.split('--', 1)[0]
        self.musicName = self.musicComboBox.GetValue().split('--', 1)[1]
        self.musicName = self.musicName.split('--', 1)[0]
        self.musicURL = self.musicListOriginal.iloc[int(self.musicID)]['url']
        self.musicURLselect.ChangeValue(self.musicURL)
        self.changeTitleName()

    def onAddURLs(self, event):
        newURLS = filterForSelection(self.videoList, self.includeCategories, self.includePornstars, self.includeChannels, self.excludeCategories, self.excludePornstars,
                           self.excludeChannels,  self.orCategories.GetValue(), self.orPornstars.GetValue(), int(self.nVidsSlider.GetValue()),
                           self.minVidLength * 60, self.maxVidLength * 60)
        
        self.ImportedURLs = self.ImportedURLs + newURLS
        self.ImportedURLs = list(dict.fromkeys(self.ImportedURLs))
        print(self.ImportedURLs)
        videoURL_List = self.videURLselect.GetValue().split('\n')
        for url in self.ImportedURLs:
            if url not in videoURL_List:
                self.videURLselect.AppendText(url.split("&pkey=",1)[0])
                self.videURLselect.AppendText("\n")

    def onRefreshIndividualVidCombo(self, event):

        df_videoList = filterForSelection(self.videoList, self.includeCategories, self.includePornstars,
                                          self.includeChannels, self.excludeCategories, self.excludePornstars,
                                          self.excludeChannels,  self.orCategories.GetValue(), self.orPornstars.GetValue(), int(self.nVidsSlider.GetValue()),
                                          self.minVidLength * 60, self.maxVidLength * 60, returnDataframe=True)

        self.videoListFiltered = df_videoList

        self.videoListFiltered["Summary"] = self.videoListFiltered["Title"].astype(str) + "--" + self.videoListFiltered.index.astype(str)
        self.videoListFiltered = self.videoListFiltered.sort_values(by="Summary", ascending=True)
        self.videoListFiltered = self.videoListFiltered["Summary"].to_list()

        self.individualVidComboBox.SetItems(self.videoListFiltered)

    def onIndividualVidCombo(self, event):

        self.vidID = self.individualVidComboBox.GetValue().split('--', 1)[1]
        print(self.videoList)
        self.vidURL = self.videoList.loc[int(self.vidID)]['url']

        self.ImportedURLs = self.ImportedURLs + [self.vidURL]
        print(self.ImportedURLs)
        self.ImportedURLs = list(dict.fromkeys(self.ImportedURLs))
        print(self.ImportedURLs)
        videoURL_List = self.videURLselect.GetValue().split('\n')
        for url in self.ImportedURLs:
            if url not in videoURL_List:
                self.videURLselect.AppendText(url.split("&pkey=",1)[0])
                self.videURLselect.AppendText("\n")

    def OnMusicWebpage(self, event):
        musicUrl = self.musicURLselect.GetValue()
        if musicUrl != "":
            webbrowser.open(musicUrl, new=2)

    def OnVidWebpages(self, event):
        videoURL_List = self.videURLselect.GetValue().split('\n')
        for url in videoURL_List:
            if url != "":
                webbrowser.open(url, new=2)

    def categoryOnCombo(self, event):
        self.includeCategories.append(self.categoryComboBox.GetValue().rsplit(' ', 1)[0])
        self.includeCategories = [value for value in self.includeCategories if value != ""]
        self.includeCategories = list(dict.fromkeys(self.includeCategories))
        self.changeVideoList(event)
        self.pornstarComboBox.SetItems(self.pornstarList)
        self.channelComboBox.SetItems(self.channelList)
        self.excludeCategoryComboBox.SetItems(self.categoryList)
        self.excludePornstarComboBox.SetItems(self.pornstarList)
        self.excludeChannelComboBox.SetItems(self.channelList)
        print(self.orCategories.GetValue())
        if self.orCategories.GetValue() == False:
            self.categoryComboBox.SetItems(self.categoryList)
        self.categoryComboSelection.ChangeValue(" ".join(self.includeCategories))
        try:
            self.changeTitleName()
        except AttributeError:
            pass

    def pornstarOnCombo(self, event):
        self.includePornstars.append(self.pornstarComboBox.GetValue().rsplit(' ', 1)[0])
        self.includePornstars = [value for value in self.includePornstars if value != ""]
        self.includePornstars = list(dict.fromkeys(self.includePornstars))
        self.changeVideoList(event)
        self.categoryComboBox.SetItems(self.categoryList)
        self.channelComboBox.SetItems(self.channelList)
        self.excludeCategoryComboBox.SetItems(self.categoryList)
        self.excludePornstarComboBox.SetItems(self.pornstarList)
        self.excludeChannelComboBox.SetItems(self.channelList)
        if self.orPornstars.GetValue() == False:
            self.pornstarComboBox.SetItems(self.pornstarList)
        self.pornstarComboSelection.ChangeValue(" ".join(self.includePornstars))
        try:
            self.changeTitleName()
        except AttributeError:
            pass

    def channelOnCombo(self, event):
        self.includeChannels.append(self.channelComboBox.GetValue().rsplit(' ', 1)[0])
        self.includeChannels = [value for value in self.includeChannels if value != ""]
        self.includeChannels = list(dict.fromkeys(self.includeChannels))
        self.changeVideoList(event)
        self.categoryComboBox.SetItems(self.categoryList)
        self.pornstarComboBox.SetItems(self.pornstarList)
        self.excludeCategoryComboBox.SetItems(self.categoryList)
        self.excludePornstarComboBox.SetItems(self.pornstarList)
        # self.excludeChannelComboBox.SetItems(self.channelList)
        # self.channelComboBox.SetItems(self.channelList)
        self.channelComboSelection.ChangeValue(" ".join(self.includeChannels))
        try:
            self.changeTitleName()
        except AttributeError:
            pass

    def excludeCategoryOnCombo(self, event):
        self.excludeCategories.append(self.excludeCategoryComboBox.GetValue().rsplit(' ', 1)[0])
        self.excludeCategories = [value for value in self.excludeCategories if value != ""]
        self.excludeCategories = list(dict.fromkeys(self.excludeCategories))
        self.changeVideoList(event)
        self.categoryComboBox.SetItems(self.categoryList)
        self.pornstarComboBox.SetItems(self.pornstarList)
        self.channelComboBox.SetItems(self.channelList)
        self.excludeCategoryComboBox.SetItems(self.categoryList)
        self.excludePornstarComboBox.SetItems(self.pornstarList)
        self.excludeChannelComboBox.SetItems(self.channelList)
        self.excludeCategoryComboSelection.ChangeValue(" ".join(self.excludeCategories))

    def excludePornstarOnCombo(self, event):
        self.excludePornstars.append(self.excludePornstarComboBox.GetValue().rsplit(' ', 1)[0])
        self.excludePornstars = [value for value in self.excludePornstars if value != ""]
        self.excludePornstars = list(dict.fromkeys(self.excludePornstars))
        self.changeVideoList(event)
        self.categoryComboBox.SetItems(self.categoryList)
        self.pornstarComboBox.SetItems(self.pornstarList)
        self.channelComboBox.SetItems(self.channelList)
        self.excludeCategoryComboBox.SetItems(self.categoryList)
        self.excludePornstarComboBox.SetItems(self.pornstarList)
        self.excludeChannelComboBox.SetItems(self.channelList)
        self.excludePornstarComboSelection.ChangeValue(" ".join(self.excludePornstars))

    def excludeChannelOnCombo(self, event):
        self.excludeChannels.append(self.excludeChannelComboBox.GetValue().rsplit(' ', 1)[0])
        self.excludeChannels = [value for value in self.excludeChannels if value != ""]
        self.excludeChannels = list(dict.fromkeys(self.excludeChannels))
        self.changeVideoList(event)
        self.categoryComboBox.SetItems(self.categoryList)
        self.pornstarComboBox.SetItems(self.pornstarList)
        self.channelComboBox.SetItems(self.channelList)
        self.excludeCategoryComboBox.SetItems(self.categoryList)
        self.excludePornstarComboBox.SetItems(self.pornstarList)
        self.excludeChannelComboBox.SetItems(self.channelList)
        self.excludeChannelComboSelection.ChangeValue(" ".join(self.excludeChannels))

    def resetVideoList(self, event):
        self.videoListOriginal = pd.read_csv(PathList["combinedPornListPath"])
        self.includeCategories = []
        self.includePornstars = []
        self.includeChannels = []
        self.excludeCategories = []
        self.excludePornstars = []
        self.excludeChannels = []
        self.ImportedURLs = []
        self.videoList = self.videoListOriginal

    def resetAll(self, event):
        self.resetVideoList(event)
        self.resetVideoListDuration(event)
        self.categoryComboSelection.ChangeValue("")
        self.pornstarComboSelection.ChangeValue("")
        self.channelComboSelection.ChangeValue("")
        self.excludeCategoryComboSelection.ChangeValue("")
        self.excludePornstarComboSelection.ChangeValue("")
        self.excludeChannelComboSelection.ChangeValue("")
        self.vidsAvailableNumber.SetLabel(str(self.videoList.shape[0]))
        self.changeTitleName()

    def changeVideoListIncludeCategories(self, event):
        videoList = self.videoList
        includeCategories = self.includeCategories
        self.orCategoriesBool = self.orCategories.GetValue()
        if len(includeCategories) > 0:
            if self.orCategoriesBool == True:
                videoList = videoList.loc[(videoList['_Cat1'].isin(includeCategories)) | (videoList['_Cat2'].isin(includeCategories)) | (videoList['_Cat3'].isin(includeCategories)) | (videoList['_Cat4'].isin(includeCategories)) | (videoList['_Cat5'].isin(includeCategories)) | (videoList['_Cat6'].isin(includeCategories)) | (videoList['_Cat7'].isin(includeCategories)) | (videoList['_Cat8'].isin(includeCategories)) | (videoList['_Cat9'].isin(includeCategories)) | (videoList['_Cat10'].isin(includeCategories)) | (videoList['_Cat11'].isin(includeCategories)) | (videoList['_Cat12'].isin(includeCategories)) | (videoList['_Cat13'].isin(includeCategories)) | (videoList['_Cat14'].isin(includeCategories)) | (videoList['_Cat15'].isin(includeCategories)) | (videoList['_Cat16'].isin(includeCategories)) | (videoList['_Cat17'].isin(includeCategories)) | (videoList['_Cat18'].isin(includeCategories)) | (videoList['_Cat19'].isin(includeCategories)) | (videoList['_Cat20'].isin(includeCategories)) | (
                    videoList['_Cat21'].isin(includeCategories)) | (videoList['_Cat22'].isin(includeCategories)) | (videoList['_Cat23'].isin(includeCategories)) | (videoList['_Cat24'].isin(includeCategories)) | (videoList['_Cat25'].isin(includeCategories)) | (videoList['_Cat26'].isin(includeCategories)) | (videoList['_Cat27'].isin(includeCategories)) | (videoList['_Cat28'].isin(includeCategories)) | (videoList['_Cat29'].isin(includeCategories)) | (videoList['_Cat30'].isin(includeCategories)) | (videoList['_Cat31'].isin(includeCategories)) | (videoList['_Cat32'].isin(includeCategories)) | (videoList['_Cat33'].isin(includeCategories)) | (videoList['_Cat34'].isin(includeCategories)) | (videoList['_Cat35'].isin(includeCategories)) | (videoList['_Cat36'].isin(includeCategories)) | (videoList['_Cat37'].isin(includeCategories)) | (videoList['_Cat38'].isin(includeCategories)) | (videoList['_Cat39'].isin(includeCategories)) | (videoList['_Cat40'].isin(includeCategories))]
            else:
                for cat in includeCategories:
                    videoList = videoList.loc[
                        (videoList['_Cat1'].isin([cat])) | (videoList['_Cat2'].isin([cat])) | (videoList['_Cat3'].isin([cat])) | (videoList['_Cat4'].isin([cat])) | (videoList['_Cat5'].isin([cat])) | (videoList['_Cat6'].isin([cat])) | (videoList['_Cat7'].isin([cat])) | (videoList['_Cat8'].isin([cat])) | (videoList['_Cat9'].isin([cat])) | (videoList['_Cat10'].isin([cat])) | (videoList['_Cat11'].isin([cat])) | (videoList['_Cat12'].isin([cat])) | (videoList['_Cat13'].isin([cat])) | (videoList['_Cat14'].isin([cat])) | (videoList['_Cat15'].isin([cat])) | (videoList['_Cat16'].isin([cat])) | (videoList['_Cat17'].isin([cat])) | (videoList['_Cat18'].isin([cat])) | (videoList['_Cat19'].isin([cat])) | (videoList['_Cat20'].isin([cat])) | (videoList['_Cat21'].isin([cat])) | (videoList['_Cat22'].isin([cat])) | (videoList['_Cat23'].isin([cat])) | (videoList['_Cat24'].isin([cat])) | (videoList['_Cat25'].isin([cat])) | (videoList['_Cat26'].isin([cat])) | (videoList['_Cat27'].isin([cat])) | (
                            videoList['_Cat28'].isin([cat])) | (videoList['_Cat29'].isin([cat])) | (videoList['_Cat30'].isin([cat])) | (videoList['_Cat31'].isin([cat])) | (videoList['_Cat32'].isin([cat])) | (videoList['_Cat33'].isin([cat])) | (videoList['_Cat34'].isin([cat])) | (videoList['_Cat35'].isin([cat])) | (videoList['_Cat36'].isin([cat])) | (videoList['_Cat37'].isin([cat])) | (videoList['_Cat38'].isin([cat])) | (videoList['_Cat39'].isin([cat])) | (videoList['_Cat40'].isin([cat]))]
        self.videoList = videoList
        self.vidsAvailableNumber.SetLabel(str(self.videoList.shape[0]))

    def changeVideoListIncludePornstars(self, event):
        videoList = self.videoList
        includePornstars = self.includePornstars
        self.orPornstarsBool = self.orPornstars.GetValue()
        if len(includePornstars) > 0:
            if self.orPornstarsBool == True:
                videoList = videoList.loc[(videoList['_Pornstar1'].isin(includePornstars)) | (videoList['_Pornstar2'].isin(includePornstars)) | (videoList['_Pornstar3'].isin(includePornstars)) | (videoList['_Pornstar4'].isin(includePornstars)) | (videoList['_Pornstar5'].isin(includePornstars))]
            else:
                for pornstar in includePornstars:
                    videoList = videoList.loc[(videoList['_Pornstar1'].isin([pornstar])) | (videoList['_Pornstar2'].isin([pornstar])) | (videoList['_Pornstar3'].isin([pornstar])) | (videoList['_Pornstar4'].isin([pornstar])) | (videoList['_Pornstar5'].isin([pornstar]))]
        self.videoList = videoList
        self.vidsAvailableNumber.SetLabel(str(self.videoList.shape[0]))

    def changeVideoListIncludeChannles(self, event):
        videoList = self.videoList
        includeChannels = self.includeChannels
        if len(includeChannels) > 0:
            videoList = videoList.loc[(videoList['_Channel'].isin(includeChannels))]
        self.videoList = videoList
        self.vidsAvailableNumber.SetLabel(str(self.videoList.shape[0]))

    def changeVideoListExcludeCategories(self, event):
        videoList = self.videoList
        excludeCategories = self.excludeCategories
        if len(excludeCategories) > 0:
            videoList = videoList.loc[
                (~videoList['_Cat1'].isin(excludeCategories)) & (~videoList['_Cat2'].isin(excludeCategories)) & (~videoList['_Cat3'].isin(excludeCategories)) & (~videoList['_Cat4'].isin(excludeCategories)) & (~videoList['_Cat5'].isin(excludeCategories)) & (~videoList['_Cat6'].isin(excludeCategories)) & (~videoList['_Cat7'].isin(excludeCategories)) & (~videoList['_Cat8'].isin(excludeCategories)) & (~videoList['_Cat9'].isin(excludeCategories)) & (~videoList['_Cat10'].isin(excludeCategories)) & (~videoList['_Cat11'].isin(excludeCategories)) & (~videoList['_Cat12'].isin(excludeCategories)) & (~videoList['_Cat13'].isin(excludeCategories)) & (~videoList['_Cat14'].isin(excludeCategories)) & (~videoList['_Cat15'].isin(excludeCategories)) & (~videoList['_Cat16'].isin(excludeCategories)) & (~videoList['_Cat17'].isin(excludeCategories)) & (~videoList['_Cat18'].isin(excludeCategories)) & (~videoList['_Cat19'].isin(excludeCategories)) & (~videoList['_Cat20'].isin(excludeCategories)) & (
                    ~videoList['_Cat21'].isin(excludeCategories)) & (~videoList['_Cat22'].isin(excludeCategories)) & (~videoList['_Cat23'].isin(excludeCategories)) & (~videoList['_Cat24'].isin(excludeCategories)) & (~videoList['_Cat25'].isin(excludeCategories)) & (~videoList['_Cat26'].isin(excludeCategories)) & (~videoList['_Cat27'].isin(excludeCategories)) & (~videoList['_Cat28'].isin(excludeCategories)) & (~videoList['_Cat29'].isin(excludeCategories)) & (~videoList['_Cat30'].isin(excludeCategories)) & (~videoList['_Cat31'].isin(excludeCategories)) & (~videoList['_Cat32'].isin(excludeCategories)) & (~videoList['_Cat33'].isin(excludeCategories)) & (~videoList['_Cat34'].isin(excludeCategories)) & (~videoList['_Cat35'].isin(excludeCategories)) & (~videoList['_Cat36'].isin(excludeCategories)) & (~videoList['_Cat37'].isin(excludeCategories)) & (~videoList['_Cat38'].isin(excludeCategories)) & (~videoList['_Cat39'].isin(excludeCategories)) & (~videoList['_Cat40'].isin(excludeCategories))]
        self.videoList = videoList
        self.vidsAvailableNumber.SetLabel(str(self.videoList.shape[0]))

    def changeVideoListExcludePornstars(self, event):
        videoList = self.videoList
        excludePornstars = self.excludePornstars
        print(excludePornstars)
        if len(excludePornstars) > 0:
            videoList = videoList.loc[(~videoList['_Pornstar1'].isin(excludePornstars)) & (~videoList['_Pornstar2'].isin(excludePornstars)) & (~videoList['_Pornstar3'].isin(excludePornstars)) & (~videoList['_Pornstar4'].isin(excludePornstars)) & (~videoList['_Pornstar5'].isin(excludePornstars))]
        self.videoList = videoList
        self.vidsAvailableNumber.SetLabel(str(self.videoList.shape[0]))

    def changeVideoListExcludeChannels(self, event):
        videoList = self.videoList
        excludeChannels = self.excludeChannels
        if len(excludeChannels) > 0:
            videoList = videoList.loc[(~videoList['_Channel'].isin(excludeChannels))]
        self.videoList = videoList
        self.vidsAvailableNumber.SetLabel(str(self.videoList.shape[0]))

    def changeVideoList(self, event):
        self.videoList = self.videoListOriginal
        # self.videoList = self.videoList[self.videoList['Duration'] < self.maxVidLength * 60]
        # self.videoList = self.videoList[self.videoList['Duration'] > self.minVidLength * 60]

        videoList = self.videoList
        self.orCategoriesBool = self.orCategories.GetValue()
        self.orPornstarsBool = self.orPornstars.GetValue()
        videoList = filterForSelection(self.videoList, includeCategories=self.includeCategories, includePornstars=self.includePornstars,
                           includeChannels=self.includeChannels, excludeCategories=self.excludeCategories, excludePornstars=self.excludePornstars,
                           excludeChannels=self.excludeChannels, orCategories=self.orCategories.GetValue(), orPornstars=self.orPornstars.GetValue(),
                           minDuration=self.minVidLength * 60, maxDuration=self.maxVidLength * 60, returnDataframe=True)

        self.videoList = videoList
        self.vidsAvailableNumber.SetLabel(str(self.videoList.shape[0]))
        self.recountCategories(event)

    def recountCategories(self, event):

        allCatColumnList = []
        nCat = 40
        i = 0
        while i < nCat:
            allCatColumnList.append('_Cat' + str(i + 1))
            i = i + 1
        dfCategoryList = self.videoList[allCatColumnList].apply(pd.Series.value_counts)
        dfCategoryList['Total'] = dfCategoryList.sum(axis=1)
        dfCategoryList['Category'] = dfCategoryList.index
        dfCategoryList["Summary"] = dfCategoryList["Category"].astype(str) + " " + dfCategoryList["Total"].astype(str)
        dfCategoryList = dfCategoryList.sort_values(by="Total", ascending=False)
        self.categoryList = dfCategoryList["Summary"].to_list()

        dfPornstarList = self.videoList[['_Pornstar1', '_Pornstar2', '_Pornstar3', '_Pornstar4', '_Pornstar5']].apply(pd.Series.value_counts)
        dfPornstarList['Total'] = dfPornstarList.sum(axis=1)
        dfPornstarList['Pornstar'] = dfPornstarList.index
        dfPornstarList["Summary"] = dfPornstarList["Pornstar"].astype(str) + " " + dfPornstarList["Total"].astype(str)
        dfPornstarList = dfPornstarList.sort_values(by="Total", ascending=False)
        self.pornstarList = dfPornstarList["Summary"].to_list()

        dfChannelList = self.videoList[['_Channel', '_Channel_Group']].apply(pd.Series.value_counts)
        dfChannelList['Total'] = dfChannelList.sum(axis=1)
        dfChannelList['Channel'] = dfChannelList.index
        dfChannelList["Summary"] = dfChannelList["Channel"].astype(str) + " " + dfChannelList["Total"].astype(str)
        dfChannelList = dfChannelList.sort_values(by="Total", ascending=False)
        self.channelList = dfChannelList["Summary"].to_list()

    def onMakePMV(self, event):
        self.logger.ChangeValue("Making PMV, please wait...")

        df_Video_Data[0] = self.videoListOriginal

        videoURL_List = self.videURLselect.GetValue().split('\n')

        self.PMV_Final = PMV_Class(DirectoryFile_Info=DirectoryFile_Info(finalVidName = self.outputFileName.GetValue(),
                                                                         vidDownloadDir=self.customVidDir + "/",
                                                                         pythonDir=PathList["pythonPath"],
                                                                         introVidDir=self.introVidName,
                                                                         musicDir=self.customMusicDir,
                                                                         musicVidDir=self.customMusicVidDir,
                                                                         finalVidDir=self.customOutputDir,
                                                                         musicFilePath=self.musicFilePath,
                                                                         ModelStorageDir=PathList["defaultModelStoragePath"]),
                         Configuration=Configuration(startEndTime=[self.startTrim.GetValue(), self.endTrim.GetValue()],
                                                     sd_scale=self.sdSlider.GetValue(),
                                                     nSplits=int(self.nSplitsSlider.GetValue()),
                                                     randomise=self.randomiseCB.GetValue(),
                                                     granularity=self.granularitySlider.GetValue(),
                                                     min_length=self.minClipLengthSlider.GetValue(),
                                                     videoNumber=0,
                                                     minVidLength=self.vidLengthMin.GetValue()*60,
                                                     maxVidLength=self.vidLengthMax.GetValue()*60,
                                                     cropVidFraction=self.outputVidCropFracSlider.GetValue(),
                                                     cropVidBool=self.outputVidCrop.GetValue(),
                                                     resize=self.resizeCB.GetValue(),
                                                     flipBool=False,
                                                     addIntro=self.addIntroBool.GetValue(),
                                                     userName=self.userNameName.GetValue(),
                                                     UseClassifyModel=self.useClassifierBool.GetValue()),
                         Video_Select=None,
                         URL_Data=URL_Data(videoURLs=videoURL_List,
                                           musicURL=self.musicURLselect.GetValue()),
                         Music_Info=Music_Info(musicName=self.musicName,
                                               musicType='mp3',
                                               songStart=self.musicFileStart.GetValue(),
                                               songEnd=self.musicFileEnd.GetValue(),
                                               musicVideoBool=self.musicVidFileBool.GetValue(),
                                               musicVideoOccuranceFactor=self.occuranceSlider.GetValue(),
                                               trimSong=self.musicFileTrim.GetValue()))


        self.logger.ChangeValue("Making PMV! " + self.PMV_Final.DirectoryFile_Info.finalVidName + ". Check terminal for progress.")

if __name__ == '__main__':
    app = wx.App()
    frame = MyFrame()
    app.MainLoop()