import pickle
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
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract'
# from Admin_Fns.allPaths import PathList

def setValue(val):
    if round(val, 3) == 0.0:
        return int(0)
    elif round(val, 3) == 1.0:
        return int(1)
    else:
        return val

class ImageClass:
    def __init__(self, Similarity_MSE, Similarity_Score, score_other, score_blowjob_handjob, score_cunnilingus,
                 score_titfuck, score_sex_front, score_sex_back):
        self.Similarity_MSE = int(Similarity_MSE)
        self.Similarity_Score = setValue(Similarity_Score)
        self.score_other = setValue(score_other)
        self.score_blowjob_handjob = setValue(score_blowjob_handjob)
        self.score_cunnilingus = setValue(score_cunnilingus)
        self.score_titfuck = setValue(score_titfuck)
        self.score_sex_front = setValue(score_sex_front)
        self.score_sex_back = setValue(score_sex_back)

def get_Category_Scores(name, model, mean_image, imageFolder):
    x = np.array([process(imageFolder + "/" + name, mean_image)])
    preds = model.predict(x)
    y = preds.argmax(axis=-1)
    categories = ["blowjob_handjob", "cunnilingus", "other", "sex_back", "sex_front", "titfuck"]
    results = preds[0].tolist()
    return results

def ExtractFrames(InputVid, outDir):
    vidcap = cv2.VideoCapture(InputVid)
    frameLength = round(vidcap.get(cv2.CAP_PROP_FRAME_COUNT),0)
    fps = round(vidcap.get(cv2.CAP_PROP_FPS),0)
    print(frameLength, fps)
    success, image = vidcap.read()
    count = 0
    nFrames = fps
    nImage=0
    while success:
        if count % nFrames == 0:
            status = cv2.imwrite(outDir + "/" + str(nImage) + ".jpg", image)
            if count % (nFrames*100) == 0:
                print('Frame: ' + str(count) + "\t out of \t" + str(frameLength) + "\t", success, status)
            nImage=nImage+1
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
    _, thresh = cv2.threshold(gray, 5, 255, cv2.THRESH_BINARY)

    contours, hierarchy = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    try:
        cnt = contours[0]
    except:
        print(inputImage)
        return(0,0,0,0)
    x, y, w, h = cv2.boundingRect(cnt)

    crop = img[y:y + h, x:x + w]
    return x, y, w, h

def processImages(imageFolder, modelStoragePath, existingFrameList=[]):
    time1 = datetime.datetime.now()

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

    if len(existingFrameList)>0:
        frameList = existingFrameList
    else:
        frameList=[]
        for i, image in enumerate(lst):
            if i < 100000:
                results = get_Category_Scores(image, model, mean_image, imageFolder)
                if i>1:
                    s, m = inputCompareImages(directory + "/" + image, directory + "/" + lst[i - 1])
                else:
                    s=1
                    m=0
                # frameClass = ImageClass(Similarity_MSE=m,
                #                         Similarity_Score=s,
                #                         score_blowjob_handjob = round(results[0], 3),
                #                         score_cunnilingus = round(results[1], 3),
                #                         score_other = round(results[2], 3),
                #                         score_sex_back = round(results[3], 3),
                #                         score_sex_front = round(results[4], 3),
                #                         score_titfuck = round(results[5], 3))
                frameInfo = [m, s, round(results[0], 3), round(results[1], 3), round(results[2], 3), round(results[3], 3), round(results[4], 3), round(results[5], 3)]
                frameList.append(frameInfo)

    time2 = datetime.datetime.now()
    print("Image Process Time: \t", time2 - time1)
    return frameList

def calculateSceneChanges(df_Video):
    list_MSE = df_Video["MSE"].to_list()

    try:
        sd_MSE = statistics.stdev(list_MSE)
    except:
        print(df_Video)
        print(list_MSE)
        pass
    max_MSE = max(list_MSE)
    mean_MSE = sum(list_MSE) / len(list_MSE)

    cutoff_MSE = (mean_MSE + sd_MSE*0.7) / max_MSE
    print('cutoff_MSE', cutoff_MSE)

    scene_change_list = []

    Time_From_Scene_Change = 0
    iRow = 0
    while iRow < df_Video.shape[0]:
        newMSE = df_Video.loc[iRow]["MSE"] / max_MSE
        df_Video.at[iRow, "MSE"] = newMSE
        if df_Video.loc[iRow]["MSE"] > cutoff_MSE:
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

def makeDataframe(frameList, categorySelect, blockLateClips = True):
    results_list = []
    for image in frameList:
        # results_list.append([image.score_blowjob_handjob,
        #                      image.score_cunnilingus,
        #                      image.score_other,
        #                      image.score_sex_back,
        #                      image.score_sex_front,
        #                      image.score_titfuck,
        #                      image.score_sex_back + image.score_sex_front,
        #                      image.Similarity_Score,
        #                      image.Similarity_MSE])
        results_list.append(image+[image[5]+image[6]])

    # frameClass = ImageClass(Similarity_MSE=m,
    #                         Similarity_Score=s,
    #                         score_blowjob_handjob = round(results[0], 3),
    #                         score_cunnilingus = round(results[1], 3),
    #                         score_other = round(results[2], 3),
    #                         score_sex_back = round(results[3], 3),
    #                         score_sex_front = round(results[4], 3),
    #                         score_titfuck = round(results[5], 3))

    df = pd.DataFrame(results_list, columns=["MSE", "similarity_score", "blowjob_handjob", "cunnilingus", "other", "sex_back", "sex_front", "titfuck", "sex"])
    # df = pd.DataFrame(results_list, columns=["blowjob_handjob", "cunnilingus", "other", "sex_back", "sex_front", "titfuck", "sex", "similarity_score", "MSE"])
    df = df.astype(float)
    if "blowjob_handjob" in categorySelect:
        df["other_nsfw"] = df["cunnilingus"] + df["titfuck"]
    else:
        df["other_nsfw"] = df["cunnilingus"] + df["titfuck"] + df["blowjob_handjob"]
    df["category"] = df[categorySelect].idxmax(axis=1)
    df["max_score"] = df[categorySelect].max(axis=1)
    try:
        df = calculateSceneChanges(df)
    except:
        print(df)
        pass
    df, SectionsDict, StartEndTimes = makeDataframeSections(df, categorySelect, blockLateClips)
    return df, SectionsDict, StartEndTimes

def makeVideoDict(frameList, picklePath, allVideoDict, videoName, dictKey, successfulLoad):
    videoDict = dict()
    videoDict[dictKey] = frameList
    if successfulLoad:
        allVideoDict.update(videoDict)
        # print(picklePath)
        with open(picklePath, 'wb') as handle:
            pickle.dump(allVideoDict, handle, protocol=pickle.HIGHEST_PROTOCOL)
    else:
        filePath = picklePath.replace("PickledVideos.pickle", "")
        filePath = filePath + "Pickled Videos/" + videoName.replace(".mp4", "") + ".pickle"
        with open(filePath, 'wb') as handle:
            pickle.dump(videoDict, handle, protocol=pickle.HIGHEST_PROTOCOL)
    return videoDict

def makePlots(df, plotBool, categorySelect=None, blockLateClips = True):
    if categorySelect is None:
        categorySelect = ["other", "other_nsfw", "sex", "finish"]
    if plotBool:
        # df, SectionsDict = makeDataframe(videoDict, categorySelect, blockLateClips)
        # df.set_index("Time (s)", inplace=True)
        # df = df.reindex(range(df.index.max())).fillna(0)

        df2 = df.pivot(index="Time (s)", columns="category", values="max_score")
        df2 = df2.reindex(range(df2.index.max())).fillna(0)

        df2.plot(title="FrameList")
        plt.show()
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

def makeDataframeSections(dataframeFrames, categorySelect, blockLateClips):
    if categorySelect is None:
        categorySelect = ["other", "other_nsfw", "sex"]

    StartEndTimes = getStartEndTrim(dataframeFrames)
    startTime = StartEndTimes[0]
    endTime = StartEndTimes[1]
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
        if df_section["section"].mean() == dataframeFrames["section"].max():
            if df_section.shape[0] > 10:
                mindex = int(df_section.index.max() - 10)
                maxdex = int(df_section.index.max())
                df_section_new = df_section.loc[mindex:maxdex]
                df_section_new["category"] = "finish"
                SectionsDict["finish"].append([df_section_new["Time (s)"].min(), df_section_new["Time (s)"].max()])
            else:
                df_section_new = df_section
                df_section_new["category"] = "finish"
                SectionsDict["finish"].append([df_section_new["Time (s)"].min(), df_section_new["Time (s)"].max()])
            df_SectionsList.append(df_section_new)
        elif df_section["Time (s)"].min() > dataframeFrames["Time (s)"].max() * 0.9 and (df_section["category"].mode()[0] != categorySelect[len(categorySelect)-1] or finishingBool) and (df_section[categorySelect[len(categorySelect)-1]+"_total"].mean()-df_section[categorySelect[len(categorySelect)-1]+"_N"].mean())<3:
            if (df_section["category"].mode()[0] != categorySelect[0]) or (df_section[categorySelect[0]+"_total"].mean()==df_section[categorySelect[0]+"_N"].mean()):
                df_section_new = df_section
                df_section_new["category"] = "finish"
                df_SectionsList.append(df_section_new)
                SectionsDict["finish"].append([df_section_new["Time (s)"].min(), df_section_new["Time (s)"].max()])
                finishingBool=True
        else:
            if (df_section["category"].mode()[0] == categorySelect[len(categorySelect)-1] and df_section["Time (s)"].min() > dataframeFrames["Time (s)"].max() / 4) or df_section["Time (s)"].min() > dataframeFrames["Time (s)"].max() / 2 and blockLateClips:
                stopNewCatFirst = True
            if df_section["category"].mode()[0] == categorySelect[0] and stopNewCatFirst:
                skip = True
            else:
                df_SectionsList.append(df_section)
                SectionsDict[df_section["category"].mode()[0]].append([df_section["Time (s)"].min(), df_section["Time (s)"].max()])

    dataframeFrames = pd.concat(df_SectionsList)

    return dataframeFrames, SectionsDict, StartEndTimes

def makeSections(dataframeFrames, categorySelect=None, blockLateClips = True):
    if categorySelect is None:
        categorySelect = ["other", "other_nsfw", "sex"]

    StartEndTimes = getStartEndTrim(dataframeFrames)


    startTime = StartEndTimes[0]
    endTime = StartEndTimes[1]

    dataframeFrames = dataframeFrames.loc[startTime:endTime]
    dataframeFrames["section"] = dataframeFrames["scene_change"].cumsum()
    n_sections = dataframeFrames["section"].max()+1
    SectionsDict=dict()
    for cat in categorySelect:
        SectionsDict[cat] = []
    SectionsDict["finish"]=[]

    iSection = 0
    stopNewCatFirst=False
    cat_first = 'other'
    cat_last = 'sex'
    dfLength = dataframeFrames.shape[0]
    df_SectionsList = []
    while iSection < n_sections:
        df_section = dataframeFrames[dataframeFrames["section"] == iSection]
        if df_section.shape[0]>3:
            category = df_section["category"].mode()[0]
            startIndex = df_section.index.min()
            if (category == cat_last and startIndex > dfLength/4) or startIndex > dfLength/2 and blockLateClips:
                stopNewCatFirst = True
            if category == cat_first and stopNewCatFirst:
                skip=True
            else:
                df_SectionsList.append(df_section)
        iSection = iSection + 1
    iSection=0
    while iSection < len(df_SectionsList):
        df_section = df_SectionsList[iSection]
        category = df_section["category"].mode()[0]
        sectionCatProb = df_section[category].mean()
        if iSection == len(df_SectionsList)-1:
            if df_section.shape[0]>10:
                SectionsDict[category].append([df_section.index.min(), df_section.index.max()-10])
                SectionsDict["finish"].append([df_section.index.max()-10, df_section.index.max()])
            else:
                SectionsDict["finish"].append([df_section.index.min(), df_section.index.max()])

        elif sectionCatProb>0.9:
            SectionsDict[category].append([df_section.index.min(), df_section.index.max()])
        # print(category, sectionCatProb, df_section.index.min(), df_section.index.max())
        iSection = iSection + 1

    totalLength = 0
    for cat in categorySelect:
        for section in SectionsDict[cat]:
            totalLength = totalLength + section[1]-section[0]
        # print(SectionsDict[cat])
    # print(totalLength)

    return SectionsDict

def getDictKey(inputVideo, vidId="", df_Videos_All=pd.DataFrame()):

    inputVideoName = os.path.basename(inputVideo)

    inputVid = inputVideoName.replace(r"’", r"'")
    inputVid = inputVid.replace("&nbsp", r" ")
    printable = set(string.printable)
    inputVidIter = filter(lambda x: x in printable, inputVid)
    inputVid = "".join(inputVidIter)

    dictKey = os.path.basename(inputVid)
    inputVideoName = inputVideoName.replace(".mp4", "")

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

def getVidClassifiedData(inputVideo, vidId="", modelStoragePath="", plotBool=False, reImage=False, df_Videos_All=pd.DataFrame()):
    inputVideoName = os.path.basename(inputVideo)
    # print(inputVideoName)
    # print(inputVideo)
    inputVideoPath = inputVideo.replace(inputVideoName, "")
    categorySelect = ["other", "other_nsfw", "sex"]

    if modelStoragePath == "":
        imageFolder = "Frames/" + inputVideoName.replace(".mp4", "")
        picklePath =  r"E:\Python Main\PycharmProjects\PMV_Generator_Git\Classify_Model/PickledVideos.pickle"
    else:
        imageFolder = modelStoragePath + "/" + "Frames/" + inputVideoName.replace(".mp4", "")
        picklePath = modelStoragePath + "/" + r"PickledVideos.pickle"

    imageFolder = imageFolder.replace(r"’", r"'")
    imageFolder = imageFolder.replace("&nbsp", r" ")
    printable = set(string.printable)
    imageFolderIter = filter(lambda x: x in printable, imageFolder)
    imageFolder = "".join(imageFolderIter)

    dictKey = getDictKey(imageFolder, vidId, df_Videos_All)


    blockLateClips = True
    print(picklePath)
    successfulLoad = False
    iAttempt = 0
    while iAttempt<10:
        try:
            with open(picklePath, 'rb') as handle:
                allVideoDict = pickle.load(handle)
            successfulLoad=True
            break
        except Exception as e:
            print(str(e))
            print("Error loading pickled dictionary. Attempt " + str(iAttempt+1))
            time.sleep(60)
            pass
            iAttempt = iAttempt + 1

    if successfulLoad:
        if dictKey in allVideoDict:
            frameList = allVideoDict[dictKey]
            videoDict = makeVideoDict(frameList, picklePath, allVideoDict, inputVideoName, dictKey, successfulLoad)
        else:
            makeImageFolder(inputVideo, imageFolder, reImage)
            frameList = processImages(imageFolder, modelStoragePath)
            videoDict = makeVideoDict(frameList, picklePath, allVideoDict, inputVideoName, dictKey, successfulLoad)
    else:
        print("Error in pickled dictionary - Aborting")
        print("...")
        quit()

    print("File loaded")
    outputDict = dict()
    dataframeFrames, sectionDict, startEndTimes = makeDataframe(videoDict[dictKey], categorySelect)
    makePlots(dataframeFrames, plotBool, categorySelect)
    outputDict["Sections"] = sectionDict
    # outputDict["Sections"] = makeSections(dataframeFrames, blockLateClips=True)
    outputDict["StartEndTimes"] = startEndTimes

    # videoDict["Sections"] = makeSections(videoDict[dictKey], blockLateClips=True)

    return outputDict


# picklePath = r"E:\Python Main\PycharmProjects\PMV_Generator_Git\Classify_Model\PickledVideos.pickle"
# with open(picklePath, 'rb') as handle:
#     allVideoDict = pickle.load(handle)
#
# print("Ahhhh")

# inputVideo = r"E:\Python Main\PycharmProjects\PMV_Generator_Git\Resources\TempVids\Sex\Brazzers - Petite sexy blonde Alina Lopez fucked hard during interview.mp4"
# inputVideo = r"E:\Python Main\PycharmProjects\PMV_Generator_Git\Resources\TempVids\RandomVideosShe Is Nerdy89\She Is Nerdy - Monroe Fox - princess anal adventure.mp4"
# # inputVideo2 = r"E:\Python Main\PycharmProjects\PMV_Generator_Git\Resources\TempVids\RandomVideosSpy Fam53\SPYFAM Sex Addict Step Dad Spies On Slutty Step Daughter.mp4"
# # inputVideo3 = r"C:\Users\vince\Pictures\Python\PMV_Generator_Git\Resources\TempVids\Casting\Very beautiful woman enjoys her first casting fuck.mp4"
# # inputVideo4 = r"C:\Users\vince\Pictures\Python\PMV_Generator_Git\Resources\TempVids\Blacked\BLACKED Dani Daniels and Anikka Interracial Threesome.mp4"
# # inputVideo5 = r"C:\Users\vince\Pictures\Python\PMV_Generator_Git\Resources\TempVids\ASMR\Quirky teen playing with boobs ASMR bra fetish.mp4"
# # inputVideo6 = r"C:\Users\vince\Pictures\Python\PMV_Generator_Git\Resources\TempVids\RandomVideosyinyleon7\Kinky real amateur couple fuck in garage, I had to fuck her ass too!!.mp4"
# # fileDir = r"C:\Users\vince\Pictures\Python\PMV_Generator_Git\Resources\TempVids\Vixen"
# # fileDir = r"C:\Users\vince\Pictures\Python\PMV_Generator_Git\Resources\TempVids\Tushy"
# # fileList = os.listdir(fileDir)


# df_Videos_All = pd.read_csv(r"E:\Python Main\PycharmProjects\PMV_Generator_Git\Resources\DataLists\combinedPornDir.csv")
# # iFile = 0
# # fileList = [inputVideo]
# # while iFile < len(fileList):
# #     file = fileList[iFile]
# file = inputVideo# fileDir + "/" + file
# vidDict = getVidClassifiedData(file, plotBool=True, df_Videos_All=df_Videos_All) #, reImage=True)
# print(vidDict["Sections"])
# # iFile = iFile + 1


