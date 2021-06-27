import youtube_dl
import sys

arg = sys.argv
selectDir = arg[1]
line = arg[2]

# ydl_opts = {'outtmpl': selectDir + r'/test.%(ext)s',
#             'format': 'bestvideo[height=1080]',
#             'simulate': True,
#             'dump_single_json': True,
#             'writeinfojson': True,          # only download single song, not playlist
#             'listformats': True}
#
# with youtube_dl.YoutubeDL(ydl_opts) as ydl:
#     try:
#         info_dict = ydl.extract_info(line, download=False)
#     except Exception as e:
#         print(e)

ydl_opts = {'outtmpl': selectDir + '%(title)s' + '.mp4', # .%(ext)s',
            'format': 'best[height>720]', #'best',# 'best[height>=480]/best[height<=720]', #'worstaudio/best[height<=720]',
            'videoformat': "mp4",
            'playlist': 'no',
            'verbose': 'false',
            'add_header': 'false'}
            # 'cookiefile': cookieFile}

iAttempt=0
if line=="":
    iAttempt=6
while iAttempt < 6:
    if iAttempt < 3:
        try:
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                ydl.download([line])
            break
        except Exception as e:
            print(line, "Error: ", iAttempt)
            if "requested format not available" in str(e):
                iAttempt = 2
            pass
    if iAttempt >= 3:
        try:
            ydl_opts = {'outtmpl': selectDir + '%(title)s' + '.mp4',  # .%(ext)s',
                        'format': 'best',
                        'videoformat': "mp4",
                        'playlist': 'no',
                        'verbose': 'false',
                        'add_header': 'false'}
            print(line, "Error: ", iAttempt)
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                ydl.download([line])
            break
        except:
            print(line, "Error: ", iAttempt)
            pass
    iAttempt = iAttempt + 1
    # elif iAttempt == 4:
    #     try:
    #         ydl_opts = {'outtmpl': selectDir + '%(title)s' + '.mp4',  # .%(ext)s',
    #                     'format': 'best',
    #                     'videoformat': "mp4",
    #                     'playlist': 'no',
    #                     'verbose': 'false',
    #                     'add_header': 'false'}
    #         print("Error retrying - Attempt: ", iAttempt)
    #         with youtube_dl.YoutubeDL(ydl_opts) as ydl:
    #             ydl.download([line])
    #         break
    #     except:
    #         pass


