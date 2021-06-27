from __future__ import unicode_literals
import math
import random
import youtube_dl
import pandas as pd
from Admin_Fns.getVideoInfoFn import getVidInfoFn

def getVidInfo(PMV):
    urls = PMV.URL_Data.videoURLs

    startTimeMain = PMV.Configuration.startTime
    endTimeMain = PMV.Configuration.subtractEnd

    getVidInfoFn(urls, startTimeMain, endTimeMain)

