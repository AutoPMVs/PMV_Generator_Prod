# import pickle
import copy
import shutil
import _pickle as pickle
import time
import datetime
import statistics
import pandas as pd
from os import path
import glob
import tensorflow as tf
import string
import os
from skimage.metrics import structural_similarity as ssim
import matplotlib.pyplot as plt
import numpy as np
import cv2
import pytesseract
# Import everything needed to edit video clips
from moviepy.editor import *


pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract'
# from Admin_Fns.allPaths import PathList

def setValue(val):
    if round(val, 3) == 0.0:
        return int(0)
    elif round(val, 3) == 1.0:
        return int(1)
    else:
        return val

def get_Category_Scores(name, model, mean_image, imageFolder):
    x = np.array([process(imageFolder + "/" + name, mean_image)])
    preds = model.predict(x)
    y = preds.argmax(axis=-1)
    categories = ["blowjob_handjob", "cunnilingus", "other", "sex_back", "sex_front", "titfuck"]
    results = preds[0].tolist()
    return results

def get_fps_ffmpeg(source_name):
    # loading video dsa gfg intro video
    clip = VideoFileClip(source_name).subclip(0, 10)
    # getting frame rate of the clip
    rate = clip.fps
    # printing the fps
    return rate

def ExtractFrames(InputVid, outDir):
    vidcap = cv2.VideoCapture(InputVid)
    frameLength = round(vidcap.get(cv2.CAP_PROP_FRAME_COUNT),0)
    fps = vidcap.get(cv2.CAP_PROP_FPS)
    if fps == 0:
        fps = get_fps_ffmpeg(InputVid)
    print(frameLength, fps)
    success, image = vidcap.read()
    count = 0
    nFrames = fps
    nImage=0
    prevValue = 0
    while success:
        # print(count, round(count % nFrames,0))
        fpsExtract = round(fps,0)-1
        if prevValue==fpsExtract or count==0:
            # print("Extracted")
            status = cv2.imwrite(outDir + "/" + str(nImage) + ".jpg", image)
            if round(count % (nFrames*100),0) == 0:
                print('Frame: ' + str(count) + "\t out of \t" + str(frameLength) + "\t", success, status)
            nImage=nImage+1
        prevValue = round(count % nFrames,0)
        count += 1  # save frame as JPEG file
        success, image = vidcap.read()


def mse(imageA, imageB):
    err = np.sum((imageA.astype("float") - imageB.astype("float")) ** 2)
    err /= float(imageA.shape[0] * imageA.shape[1])
    return err

def compare_images(imageA, imageB, title, plotBool=False):
    s = ssim(imageA, imageB)
    m = mse(imageA, imageB)
    if plotBool:
        fig = plt.figure(title)
        plt.suptitle("MSE: %.2f, SSIM: %.2f" % (m, s))
        ax = fig.add_subplot(1, 2, 1)
        plt.imshow(imageA, cmap=plt.cm.gray)
        plt.axis("off")
        ax = fig.add_subplot(1, 2, 2)
        plt.imshow(imageB, cmap=plt.cm.gray)
        plt.axis("off")
        plt.show()
    return s, m

def inputCompareImages(image1, image2):
    # and the original + photoshop
    original = cv2.imread(image1)
    contrast = cv2.imread(image2)
    # convert the images to grayscale
    original = cv2.cvtColor(original, cv2.COLOR_BGR2GRAY)
    contrast = cv2.cvtColor(contrast, cv2.COLOR_BGR2GRAY)
    s, m = compare_images(original, contrast, "1 vs 2")
    return s, m

def process(file, mean_image):
    img = cv2.imread(file)
    img = cv2.resize(img, (224, 224))
    img = img.astype("float32")
    img -= mean_image
    return img

def getImageSize(inputImage):
    img = cv2.imread(inputImage)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    color = int(gray[0:5, 0:5].mean())
    color = min(color, 20)
    _, thresh = cv2.threshold(gray, color+1, 255, cv2.THRESH_BINARY)

    contours, hierarchy = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    try:
        # find the biggest countour by the area
        cnt = max(contours, key = cv2.contourArea)
    except:
        print(inputImage)
        return (0, 0, 0, 0)
    x, y, w, h = cv2.boundingRect(cnt)
    # print(x, y, w, h)
    height, width = img.shape[:2]
    newWidth = w
    actWidth = width
    newHeight = h
    actHeight = height

    # # draw contours
    # ctr = copy.copy(img)
    # cv2.rectangle(ctr, (x, y), (x + w, y + h), (0, 255, 0), 5)
    # # display results with matplotlib
    # # original
    # original = img[:, :, ::-1]  # flip color for maptolib display
    # plt.subplot(221), plt.imshow(original)
    # plt.title('Original Image'), plt.xticks([]), plt.yticks([])
    # # Threshold
    # plt.subplot(222), plt.imshow(thresh, cmap='gray')
    # plt.title('threshold binary'), plt.xticks([]), plt.yticks([])
    # # draw contours
    # # selected area for future crop
    # ctr = ctr[:, :, ::-1]  # flip color for maptolib display
    # plt.subplot(223), plt.imshow(ctr)
    # plt.title('Selected area'), plt.xticks([]), plt.yticks([])
    # plt.show()

    return (newWidth, actWidth, newHeight, actHeight)

def processImages(imageFolder, modelStoragePath, existingFrameList=[], findSizes=False):
    time1 = datetime.datetime.now()
    print(findSizes)

    if modelStoragePath == "":
        weightPath = r'model/weights.h5'
        meanImagePath = r"model/mean.npy"
    else:
        weightPath = modelStoragePath + r'/model/weights.h5'
        meanImagePath = modelStoragePath + r"/model/mean.npy"

    directory = imageFolder
    lst = os.listdir(directory)
    lst = [int(i.replace(".jpg", "")) for i in lst]
    lst.sort()
    lst = [str(i) + ".jpg" for i in lst]

    model = tf.keras.models.load_model(weightPath)
    mean_image = np.load(meanImagePath)
    imageSizeList = []

    if len(existingFrameList)>0:
        frameList = existingFrameList
    else:
        frameList=[]
        for i, image in enumerate(lst):
            if i < 100000: #and i>119:
                results = get_Category_Scores(image, model, mean_image, imageFolder)
                if i>1:
                    s, m = inputCompareImages(directory + "/" + image, directory + "/" + lst[i - 1])
                else:
                    s=1
                    m=0
                if findSizes:
                    newWidth, actWidth, newHeight, actHeight = getImageSize(directory + "/" + image)
                    if abs(newWidth)<actWidth*0.6 and abs(newHeight)>0.95*actHeight:
                        # s=1
                        m=0
                    print(image, "\t", newWidth, "\t", actWidth, "\t", newHeight, "\t", actHeight, "\t", m)
                    imageSizeList.append(abs(newWidth))


                frameInfo = [m, s, round(results[0], 3), round(results[1], 3), round(results[2], 3), round(results[3], 3), round(results[4], 3), round(results[5], 3)]
                # print(image, frameInfo)
                frameList.append(frameInfo)

    time2 = datetime.datetime.now()
    print("Image Process Time: \t", time2 - time1)
    return frameList

def calculateMSEcutoff(df_Video):
    list_MSE = df_Video["MSE"].to_list()

    try:
        sd_MSE = statistics.stdev(list_MSE)
    except:
        # print(df_Video)
        # print(list_MSE)
        pass
    max_MSE = max(list_MSE)
    mean_MSE = sum(list_MSE) / len(list_MSE)

    cutoff_MSE = (mean_MSE + sd_MSE*0.7) / max_MSE
    # print('cutoff_MSE', cutoff_MSE)

    return max_MSE, cutoff_MSE

def calculateSceneChanges(df_Video):
    max_MSE, cutoff_MSE = calculateMSEcutoff(df_Video)

    scene_change_list = []

    Time_From_Scene_Change = 0
    iRow = 0
    while iRow < df_Video.shape[0]:
        newMSE = df_Video.loc[iRow]["MSE"] / max_MSE
        df_Video.at[iRow, "MSE"] = newMSE
        if df_Video.loc[iRow]["MSE"] > cutoff_MSE or df_Video.loc[iRow]["MSE"]==0:
            scene_change_list.append(1)
        else:
            if iRow > 0:
                if df_Video.loc[iRow]["category"] != df_Video.loc[iRow-1]["category"]:
                    scene_change_list.append(1)
                elif df_Video.loc[iRow]["max_score"] <0.8:
                    scene_change_list.append(1)
                else:
                    scene_change_list.append(0)
            else:
                scene_change_list.append(0)
        iRow = iRow + 1
    df_Video["scene_change"] = scene_change_list
    return df_Video

def makeDataframe(frameList, categoryGroupings=None, blockLateClips = True, orignalTable=False):
    if categoryGroupings is None:
        categoryGroupings = [[["other"], ["cunnilingus"], ["titfuck"], ["blowjob_handjob"], ["sex_back", "sex_front"]],
                         ["other", "cunnilingus", "titfuck", "blowjob_handjob", "sex"]]

    results_list = []
    for image in frameList:
        newImage = image[0:2] + [x / sum(image[2:8]) for x in image[2:8]] +[image[5]+image[6]]
        newImage = [round(x, 4) for x in newImage]
        results_list.append(newImage)

    df = pd.DataFrame(results_list, columns=["MSE", "similarity_score", "blowjob_handjob", "cunnilingus", "other", "sex_back", "sex_front", "titfuck", "sex"])
    df = df.astype(float)

    categoryGroup = categoryGroupings[1]
    categoryInputs = categoryGroupings[0]
    iCatGroup=0
    while iCatGroup< len(categoryGroup):
        catInputs = categoryInputs[iCatGroup]
        df[categoryGroup[iCatGroup]] = df[catInputs].sum(axis=1)
        # for input in categoryInputs[iCatGroup]:
        #     df[categoryGroup]=df[categoryGroup]+df[input]
        iCatGroup = iCatGroup + 1


    # if "blowjob_handjob" in categorySelect:
    #     df["other_nsfw"] = df["cunnilingus"] + df["titfuck"]
    # else:
    #     df["other_nsfw"] = df["cunnilingus"] + df["titfuck"] + df["blowjob_handjob"]
    df["category"] = df[categoryGroup].idxmax(axis=1)
    df["max_score"] = df[categoryGroup].max(axis=1)
    try:
        df = calculateSceneChanges(df)
    except:
        print(df)
        pass
    df, SectionsDict, StartEndTimes = makeDataframeSections(df, categoryGroup, blockLateClips, orignalTable=orignalTable)
    return df, SectionsDict, StartEndTimes

def makeVideoDict(frameList, picklePath, allVideoDict, videoName, dictKey, successfulLoad, updateBool):
    videoDict = dict()
    videoDict[dictKey] = frameList
    if successfulLoad and updateBool:
        allVideoDict = loadClassifyPickleFile(picklePath)
        allVideoDict.update(videoDict)
        # print(picklePath)
        with open(picklePath, 'wb') as handle:
            pickle.dump(allVideoDict, handle) #, protocol=pickle.HIGHEST_PROTOCOL)
    elif successfulLoad==False:
        filePath = picklePath.replace("PickledVideos.pickle", "")
        filePath = filePath + "Pickled Videos/" + videoName.replace(".mp4", "") + ".pickle"
        with open(filePath, 'wb') as handle:
            pickle.dump(videoDict, handle) #, protocol=pickle.HIGHEST_PROTOCOL)
    return videoDict

def makePlots(df, plotBool, categorySelect=None, plotMainOnly=True):
    if categorySelect is None:
        categorySelect = ["other", "cunnilingus", "titfuck", "blowjob_handjob", "sex"]
    if plotBool:
        # df, SectionsDict = makeDataframe(videoDict, categorySelect, blockLateClips)
        # df.set_index("Time (s)", inplace=True)
        # df = df.reindex(range(df.index.max())).fillna(0)

        df2 = df.pivot(index="Time (s)", columns="category", values="max_score")
        df2 = df2.reindex(range(df2.index.max())).fillna(0)
        df2.plot(title="FrameList")
        plt.show()
        if plotMainOnly==False:
            df["similarity_score"].plot(title="similarity_score")
            plt.show()
            df["MSE"].plot(title="MSE")
            plt.show()
            df["scene_change"].plot(title="scene_change")
            plt.show()

def makeImageFolder(inputVideo, imageFolder, reImage):
    if path.isdir(imageFolder) == False:
        os.mkdir(imageFolder)
        ExtractFrames(inputVideo, imageFolder)
    elif reImage:
        for f in glob.glob(imageFolder + "/*"): os.remove(f)
        ExtractFrames(inputVideo, imageFolder)
    elif not os.listdir(imageFolder):
        ExtractFrames(inputVideo, imageFolder)

def getStartEndTrim(dfScore):
    dfScore["similarity_score_diff"] = dfScore["similarity_score"].diff()
    list_Score = dfScore["similarity_score"].to_list()

    sd_Score = statistics.stdev(list_Score)
    max_Score = max(list_Score)
    min_Score = min(list_Score)
    mean_Score = sum(list_Score) / len(list_Score)
    # print(mean_Score, max_Score, sd_Score)

    try:
        if max_Score-min_Score>0.6:
            diffRequiredMin = mean_Score - sd_Score*4
            if diffRequiredMin<0:
                diffRequiredMin=0.1
            diffRequiredMax = 0.95
            print([diffRequiredMin, diffRequiredMax])
            jTotal = 45
            iScore = 0
            firstChange = 0
            while iScore < len(list_Score):
                j=0
                AllTrue=0
                while j<jTotal:
                    if diffRequiredMin<list_Score[iScore+j]<diffRequiredMax:
                        AllTrue = AllTrue+1
                    j=j+1
                if AllTrue==jTotal:
                    firstChange = iScore
                    break
                iScore = iScore + 1

            iScore = len(list_Score)-1
            lastChange = len(list_Score)-1
            while iScore >= 0:
                j=0
                AllTrue=0
                while j<jTotal:
                    if diffRequiredMin<list_Score[iScore-j]<diffRequiredMax:
                        AllTrue = AllTrue+1
                    j=j+1
                if AllTrue==jTotal:
                    lastChange = iScore-1
                    break
                iScore = iScore - 1
        else:
            firstChange = 1
            lastChange = len(list_Score)-2
    except IndexError:
        firstChange = 1
        lastChange = len(list_Score)-2
        pass

    return [firstChange, lastChange]

def makeDataframeSections(dataframeFrames, categorySelect, blockLateClips, orignalTable=False):
    if categorySelect is None:
        categorySelect = ["other", "cunnilingus", "titfuck", "blowjob_handjob", "sex"]

    origDataframeFrames = dataframeFrames[:]
    StartEndTimes = getStartEndTrim(dataframeFrames)
    startTime = StartEndTimes[0]
    endTime = StartEndTimes[1]
    if orignalTable==False:
        dataframeFrames = dataframeFrames.loc[startTime:endTime]

    dataframeFrames["section"] = dataframeFrames["scene_change"].cumsum()
    dataframeFrames['section_length'] = dataframeFrames.groupby(['section'])['scene_change'].transform('count')
    dataframeFrames = dataframeFrames[dataframeFrames['section_length']>3]
    dataframeFrames.reset_index(inplace=True)
    dataframeFrames["Time (s)"] = dataframeFrames["index"]
    dataframeFrames = dataframeFrames.drop(columns = ["index"])
    dataframeFrames["TotalLength (s)"] = dataframeFrames.shape[0]

    for cat in categorySelect:
        dataframeFrames[cat + '_N'] = dataframeFrames[dataframeFrames['category']==cat]["scene_change"].cumsum()
        dataframeFrames[cat + '_N'].fillna(method='ffill', inplace=True)
        dataframeFrames[cat + '_N'].fillna(0, inplace=True)
        dataframeFrames[cat + '_total'] = dataframeFrames[cat + '_N'].max()

    sections_n_list = dataframeFrames["section"].to_list()
    sections_n_list = list(dict.fromkeys(sections_n_list))
    # dfLength = dataframeFrames.shape[0]
    stopNewCatFirst=False
    finishingBool=False

    SectionsDict=dict()
    for cat in categorySelect:
        SectionsDict[cat] = []
    SectionsDict["finish"]=[]

    df_SectionsList=[]
    for iSection in sections_n_list:
        df_section = dataframeFrames[dataframeFrames["section"] == iSection]
        if df_section["section"].mean() == dataframeFrames["section"].max() and df_section["category"].mode()[0] != categorySelect[0]:
            if df_section.shape[0] > 60:
                mindex = int(df_section.index.max() - 30)
                maxdex = int(df_section.index.max())
                df_section_new = df_section.loc[mindex:maxdex]
                df_section_new["category"] = "finish"
                SectionsDict["finish"].append([df_section_new["Time (s)"].min(), df_section_new["Time (s)"].max()])
            else:
                df_section_new = df_section
                df_section_new["category"] = "finish"
                SectionsDict["finish"].append([df_section_new["Time (s)"].min(), df_section_new["Time (s)"].max()])
            df_SectionsList.append(df_section_new)
        elif (df_section["Time (s)"].max() > dataframeFrames["Time (s)"].max() - 60 and (df_section["category"].mode()[0] != categorySelect[len(categorySelect)-1] or finishingBool) and (df_section[categorySelect[len(categorySelect)-1]+"_total"].mean()-df_section[categorySelect[len(categorySelect)-1]+"_N"].mean())<10) and (df_section["category"].mode()[0] != categorySelect[0]): # or (df_section[categorySelect[0]+"_total"].mean()==df_section[categorySelect[0]+"_N"].mean()):
                df_section_new = df_section
                df_section_new["category"] = "finish"
                df_SectionsList.append(df_section_new)
                SectionsDict["finish"].append([df_section_new["Time (s)"].min(), df_section_new["Time (s)"].max()])
                finishingBool=True
        elif len(df_SectionsList)>0:
            if (df_section["category"].mode()[0] == categorySelect[len(categorySelect)-1] and df_section["Time (s)"].min() > dataframeFrames["Time (s)"].max() / 4) or df_section["Time (s)"].min() > dataframeFrames["Time (s)"].max() / 2 and blockLateClips:
                stopNewCatFirst = True
            if df_section["category"].mode()[0] == categorySelect[0] and stopNewCatFirst:
                skip = True
            else:
                df_SectionsList.append(df_section)
                SectionsDict[df_section["category"].mode()[0]].append([df_section["Time (s)"].min(), df_section["Time (s)"].max()])
        else:
            df_SectionsList.append(df_section)
            SectionsDict[df_section["category"].mode()[0]].append([df_section["Time (s)"].min(), df_section["Time (s)"].max()])

    dataframeFrames = pd.concat(df_SectionsList)

    if len(SectionsDict["finish"])>1:
        if len(SectionsDict["finish"])>1 and SectionsDict["finish"][-1][1]-SectionsDict["finish"][-1][0]<5:
            SectionsDict["finish"] = SectionsDict["finish"][:-1]
        elif SectionsDict["finish"][-1][1]-SectionsDict["finish"][-1][0]>=3:
            SectionsDict["finish"][-1] = [SectionsDict["finish"][-1][0], SectionsDict["finish"][-1][1]-1]


    if orignalTable:
        dataframeFrames["index"] = dataframeFrames["Time (s)"]
        dataframeFrames.set_index("index", inplace=True)
        dataframeFrames = pd.concat([dataframeFrames, origDataframeFrames])
        dataframeFrames = dataframeFrames[~dataframeFrames.index.duplicated(keep='first')]
        dataframeFrames.sort_index(inplace=True)
        dataframeFrames.reset_index(inplace=True)
        dataframeFrames["Time (s)"] = dataframeFrames["index"]
        dataframeFrames = dataframeFrames.drop(columns = ["index"])

    dataframeFramesColumns = dataframeFrames.columns
    removeCols = ["Time (s)"]
    dataframeFramesColumns = [col for col in dataframeFramesColumns if col not in removeCols]
    dataframeFrames["Time (hh:mm:ss)"] = pd.to_datetime(dataframeFrames["Time (s)"], unit='s').dt.strftime("%H:%M:%S") #.apply(pd.to_timedelta, unit='s')
    dataframeFrames = dataframeFrames[["Time (s)", "Time (hh:mm:ss)"]+dataframeFramesColumns]


    return dataframeFrames, SectionsDict, StartEndTimes

def folderToName(InputFilePath):

    inputVideoName = os.path.basename(InputFilePath)

    inputVid = inputVideoName.replace(r"’", r"'")
    inputVid = inputVid.replace("&nbsp", r" ")
    printable = set(string.printable)
    inputVidIter = filter(lambda x: x in printable, inputVid)
    inputVid = "".join(inputVidIter)

    inputVideoName = inputVideoName.replace(".mp4", "")

    return inputVideoName

def getDictKey(inputVideoName, vidId="", df_Videos_All=pd.DataFrame()):
    # inputVideoName = folderToName(inputVideo)
    dictKey = os.path.basename(inputVideoName)

    if vidId != "":
        dictKey = dictKey + " - " + vidId
    else:
        if df_Videos_All.shape[0] > 0:
            selected_df = df_Videos_All[df_Videos_All["Title"] == inputVideoName]
            if selected_df.shape[0] > 0:
                dictKey = inputVideoName + " - " + selected_df["id"].to_list()[0]  # + ".pickle"]
            else:
                dictKey = inputVideoName

    return dictKey

def getChannel(inputVideoName, df_Videos_All=pd.DataFrame()):
    channel = ""
    if df_Videos_All.shape[0] > 0:
        selected_df = df_Videos_All[df_Videos_All["Title"] == inputVideoName]
        if selected_df.shape[0] > 0:
            channel = selected_df["_Channel"].to_list()[0]

    return channel

def loadClassifyPickleFile(picklePath):
    if "PickledVideos.pickle" not in picklePath:
        picklePath = picklePath + "/" + r"PickledVideos.pickle"

    print(picklePath)
    iAttempt = 0
    while iAttempt<10:
        try:
            with open(picklePath, 'rb') as handle:
                allVideoDict = pickle.load(handle)
            break
        except Exception as e:
            print(str(e))
            print("Error loading pickled dictionary. Attempt " + str(iAttempt+1))
            time.sleep(60)
            pass
            iAttempt = iAttempt + 1

    return allVideoDict

def getVidClassifiedData(inputVideo, allVideoDict, vidId="", modelStoragePath="", plotBool=False, reImage=False, df_Videos_All=pd.DataFrame(), autoClear=True, categoryGroupings=None):
    if categoryGroupings is None:
        categoryGroupings = [[["other"], ["cunnilingus"], ["titfuck"], ["blowjob_handjob"], ["sex_back", "sex_front"]],
                         ["other", "cunnilingus", "titfuck", "blowjob_handjob", "sex"]]
    inputVideoName = os.path.basename(inputVideo)

    inputVideoName = folderToName(inputVideoName)
    channel = getChannel(inputVideoName, df_Videos_All)
    dictKey = getDictKey(inputVideoName, vidId, df_Videos_All)

    if modelStoragePath == "":
        imageFolder = "Frames/" + dictKey
        picklePath =  r"E:\Python Main\PycharmProjects\PMV_Generator_Git\Classify_Model/PickledVideos.pickle"
    else:
        imageFolder = modelStoragePath + "/" + "Frames/" + dictKey
        picklePath = modelStoragePath + "/" + r"PickledVideos.pickle"

    imageFolder = imageFolder.replace(r"’", r"'")
    imageFolder = imageFolder.replace("&nbsp", r" ")
    imageFolder = imageFolder.strip()
    printable = set(string.printable)
    imageFolderIter = filter(lambda x: x in printable, imageFolder)
    imageFolder = "".join(imageFolderIter)
    imageDirExcFrames = imageFolder.replace("Frames/", "")
    if all(ch == " " for ch in imageDirExcFrames):
        imageFolder = "Frames/unknownName" + str(time.time()).replace(".", "")

    successfulLoad = True
    findSizes=False
    if channel == "Blacked Raw" or channel == "Tushy Raw" or channel == "Deeper" or channel == "Banana Fever":
        findSizes=True

    if successfulLoad:
        if dictKey in allVideoDict and reImage==False:
            print("Loaded: ", dictKey)
            frameList = allVideoDict[dictKey]
            # makeImageFolder(inputVideo, imageFolder, reImage)
            # frameList = processImages(imageFolder, modelStoragePath)
            videoDict = makeVideoDict(frameList, picklePath, allVideoDict, inputVideoName, dictKey, successfulLoad, updateBool=False)
        else:
            print("New: ", dictKey)
            makeImageFolder(inputVideo, imageFolder, reImage)
            frameList = processImages(imageFolder, modelStoragePath, findSizes=findSizes)
            videoDict = makeVideoDict(frameList, picklePath, allVideoDict, inputVideoName, dictKey, successfulLoad, updateBool=True)
    else:
        print("Error in pickled dictionary - Aborting")
        print("...")
        quit()

    print("File loaded")
    outputDict = dict()
    dataframeFrames, sectionDict, startEndTimes = makeDataframe(videoDict[dictKey], categoryGroupings)
    makePlots(dataframeFrames, plotBool, categoryGroupings[1])
    outputDict["Sections"] = sectionDict
    # outputDict["Sections"] = makeSections(dataframeFrames, blockLateClips=True)
    outputDict["StartEndTimes"] = startEndTimes

    if autoClear:
        try:
            shutil.rmtree(imageFolder)
        except:
            pass

    return outputDict

