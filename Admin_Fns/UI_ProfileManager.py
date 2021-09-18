import pandas as pd
import xlrd
import os

def DataFrameToDict(df_profiles, profile, currentDir):
    d = df_profiles.T.to_dict()
    d_select = d[profile]
    for entry in d_select:
        if "Path" in entry:
            if d_select[entry][0:2] != currentDir[0:2] and r":" not in d_select[entry][0:2]:
                d_select[entry] = currentDir + "/" + d_select[entry]
    return d_select

def loadDefaultProfile():
    currentDir = os.getcwd()
    profilePath = currentDir + "/" + r"Resources\DataLists\UI_Profiles.csv"

    df_profiles = pd.read_csv(profilePath)
    df_profiles = df_profiles.set_index("index")

    dictProfile = DataFrameToDict(df_profiles, "Default", currentDir)
    availProfiles=df_profiles.index.to_list()
    return dictProfile, availProfiles

def loadProfile(profile):
    currentDir = os.getcwd()
    profilePath = currentDir + "/" + r"Resources\DataLists\UI_Profiles.csv"

    df_profiles = pd.read_csv(profilePath)
    df_profiles = df_profiles.set_index("index")

    dictProfile = DataFrameToDict(df_profiles, profile, currentDir)
    return dictProfile

def addNewProfile(newDict):
    currentDir = os.getcwd()
    profilePath = currentDir + "/" + r"Resources\DataLists\UI_Profiles.csv"
    # profilePath = r"E:\Python Main\PycharmProjects\PMV_Generator_Git\Resources\DataLists\UI_Profiles.csv"
    df_profiles = pd.read_csv(profilePath, index_col="index")

    df1 = pd.DataFrame.from_dict(newDict, orient='index')
    df_profiles = pd.concat([df_profiles, df1])

    df_profiles.reset_index(inplace=True)
    df_profiles.drop_duplicates(subset=["index"], inplace=True, keep='last')
    df_profiles.to_csv(profilePath, index=False)

def removeProfile(Profile):
    if Profile != "Default":
        currentDir = os.getcwd()
        profilePath = currentDir + "/" + r"Resources\DataLists\UI_Profiles.csv"
        # profilePath = r"E:\Python Main\PycharmProjects\PMV_Generator_Git\Resources\DataLists\UI_Profiles.csv"
        df_profiles = pd.read_csv(profilePath, index_col="index")

        df_profiles = df_profiles[df_profiles.index!=Profile]

        df_profiles.reset_index(inplace=True)
        df_profiles.drop_duplicates(subset=["index"], inplace=True)
        df_profiles.to_csv(profilePath, index=False)



# profileName = "Test"
# customDict = {profileName:{'Use Music Video': False, 'Trim Music': False, 'Start Music': 0, 'End Music': 0, 'Music Vid Occurance Factor': 0.4, 'Min Vid Length': 0, 'Max Vid Length': 20, 'Or category': True, 'Or Pornstar': True, 'Select Vids N': 0, 'Crop To Wide': True, 'Crop Percentage': 0.14, 'Add Intro Video': False, 'Vid Start Trim': 30, 'Vid End Trim': 20, 'nSplits': 3, 'SD For Clip Switch': 1.9, 'Granularity': 0.04, 'Min Clip Length': 0.24, 'Randomise': True, 'Resize': True, 'Flip Vids': False, 'Classify Model': True, 'User Name': False, 'defaultMusicDownloadPath': 'E:\\Python Main\\PycharmProjects\\PMV_Generator_Git\\Admin_Fns/Resources/TempMusic/', 'defaultMusicVidDownloadPath': 'E:\\Python Main\\PycharmProjects\\PMV_Generator_Git\\Admin_Fns/Resources/TempMusicVid/', 'defaultNewPMVsPath': 'E:\\Python Main\\PycharmProjects\\PMV_Generator_Git\\Admin_Fns/Resources/NewPMVs/', 'defaultVideoDownloadPath': 'E:\\Python Main\\PycharmProjects\\PMV_Generator_Git\\Admin_Fns/Resources/TempVids/', 'introVideoPath': 'E:\\Python Main\\PycharmProjects\\PMV_Generator_Git\\Admin_Fns/Resources/IntroVids/AutoPMVsIntro_quieter.mp4'}}
# loadDefaultProfile()
# changeDefaultProfile("Default")
# addNewProfile(customDict)