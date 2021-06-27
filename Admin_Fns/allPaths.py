import pandas as pd
import xlrd
import os

def ImportPathList(currentDir):
    d = {}
    df_pathList = pd.read_excel(currentDir + "/" + r"Resources\DataLists\PathListReduced.xlsx",engine='openpyxl')
    for i in range(df_pathList.shape[0]):
        cell_value_key = df_pathList.iloc[i, 0]
        cell_value = df_pathList.iloc[i, 1]
        if cell_value[0:3]==currentDir[0:3]:
            d[cell_value_key] = cell_value
        else:
            d[cell_value_key] = currentDir + "/" + cell_value
    return d

currentDir = os.getcwd()
currentDirList = currentDir.split("\\")
if "PMV_Generator_Git" in currentDirList:
    if currentDirList[-1]!="PMV_Generator_Git":
        currentDirList = currentDirList[0:-1]
currentDir = "\\".join(currentDirList)
PathList = ImportPathList(currentDir)
