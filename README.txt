Required to install:
	https://www.python.org/
	https://www.jetbrains.com/pycharm/download/#section=windows
	https://www.ffmpeg.org/
	https://imagemagick.org/index.php
Recommended to install:
	https://nordvpn.com/
Download classified video list here:
	https://mega.nz/file/jyBzUADR#zh00XpTJDYTUx8h8_B2dSo19_8ltDh_g0xJvugbVEVM

Join the subreddit here:
	https://www.reddit.com/r/AutoPMVs/

//////////////////////// Installation ////////////////////////
Install all of the above listed programs
Before doing anything else you need to add some directories to your environment path variables (Windows -> Edit environment variables for your account):
	Python Scripts Folder - C:\...\Python\Scripts\
	Python exe Folder - C:\...\Python\
	Your ffmpeg path - C:\...\ffmpeg\bin
	Image Magick path - c:\...\ImageMagick-7.0.11-Q8
Version numbers, drive letters and paths may vary slightly.
Once this is done restart the pc to register the changes.

Once the restart is complete, download the program from the git repositry and open in pycharm.
Setup a virtual environment in that project folder.
Now, double click the PMV_Generator_Prod\install_requirements.bat file to install python packages
	OR go to Terminal (in pycharm) and type pip install -r requirements.txt
In Resources/Datalists/PathListReduced change the 2 fields coloured red to your own paths:
	AudioSegmentPath - Where you installed ffmpeg
	pythonPath - Where you installed python (or your virtual environment for this project)
If you still get a file not found error then restart your pc and try again (windows might need a restart to register the new paths)
Then run UI_Main_Simplified and make PMVs!

//////////////////////// Overview ////////////////////////
On the left hand side are the options for making your pmv.
On the right hand side is a series of options to download videos and music for your pmv. 
If you already have videos you want to use then you can use that rather than the downloader.
All files (music and video) MUST be an mp4!
Use an online converter to change the format if required.

//////////////////////// Selecting Input Folders ////////////////////////
Directories->Source Vids Folder
	Then select the directory of your input vids or the folder where you want to download them to.
Directories->Music File
	Select the mp4 file you want to use as music
...alternatively...
Directories->Music Folder
	Select the folder you want to download music to

//////////////////////// Downloading Content ////////////////////////
I recoomend using a vpn for this so your ip address doesn't get blacklisted for too many download requests.
Not essential but always recommended for porn!

You can either select options using the menus on the right hand side of the UI.
	E.g- Select Category - Anal, Select Pornstar - Tori Black
	Then on the left hand side Select Vids Number (how many videos you want to use)
	Then click "Add URLs"
	You should see 'N' urls appear
Or you can manually paste the video urls you want into the Enter Video URLs box.

Likewise for music, you can select a song from a predefined list, or enter a url in the box below.

//////////////////////// Other Settings ////////////////////////
For Music:
	You can select whether or not you want to trim the start and end of the music using a checkbox on the left hand side.
	If Start and End are set to zero then the program will try and automatically trim silence from the beginning and end.
	Or you can manually select a start time and an end time in seconds.
	You can also choose to use the music video as part of the input to keep the original video in the song!

For Video:
	When selecting you can put a min/max length on the videos you want to include. Then set the lengths with the button.
	You can change the category/pornstar selection from 'or' to 'and'.
	'Or' is the default so if you select "Riley Reid" and "Tori Black" your videos will be filtered for videos containing either of the two.
		If the checkbox is deselected you'll only have videos involving both.

//////////////////////// Output Video Settings ////////////////////////
Crop to wide view - crops the top and bottom off the video (removes most watermarks and things that can ruin a video or have it taken down!)
Crop percentage - How much to crop
Add intro video - Allows you to include a title video for your vid. Change the Directories->Intro Vid path to your title vid if using this
Start Time - How much to trim off your input videos (the database already includes specific start/end times for most videos that should remove most intros and credits)
End Time - How much to trim off your input videos (the database already includes specific start/end times for most videos that should remove most intros and credits)
nSplits - How many sections to split the music into for calculating "switch points" in the song
SD for clip switch - How many standard deviations above the mean difference does a change in audio have to be to trigger a "switch point"
Min clip length - "What is the minimum length of audio needed between each "switch point"
Randomise - Randomise the order in which videos apppear or keep it in a constant order.
Resize - Resize videos of different aspect ratios to the same size (Should be kept on)
Flip vids - Mirror the vids so that watermarks appear backwards (good option for coinfusing take down algos if you decide not to crop the vids)
ClassifyModel - Run an image classifier to determine sections of the video and scene changes.
UserName - Input your username for file name making and intro videos.

//////////////////////// Classify Model ////////////////////////
This makes the generation process take muuuuuuch longer than normal but it's probably worth it.
This takes a frame a second from each input video and determines whether or not it is a normal scene, a foreplay scene or a sex scene.
It then checks whether a scene has changed between the two frames.
This information is then passed to the generator so that all normal, foreplay and sex scenes appear together and that you don't have a scene or camera change in the middle of a clip in your pmv.
It gives the final pmv a much more refeined and professional feel.
Once a video is classified, the information is stored in a pickle file so you won't have to do it again and it'll be quicker next time.
There are already some (>2500) info for classified videos stored with the program. But you can download more from the megalink above.
If you have some videos from a previous update that you'd like to keep classified then move your old file to:
	PMV_Generator_Prod\Classify_Model\PickledVideos\
	Then, when next in the UI, click File->Merge Data or File->Merge Classfied Videos List
Likewise for your saved videos or music list but the old csvs in PMV_Generator_Prod\Resources\DataLists\PornLists\ and PMV_Generator_Prod\Resources\DataLists\MusicLists\ respectively.
	Then, when next in the UI, click File->Merge Data

You can also optimise how much of each classified act you want with the sliders on the RHS
	These only adjust to the percentage you would have had otherwise based off the amount in the scenes
	If you set anything to zero, thta type of act is removed from the scene
	If you choose to have original video sound, you cna also choose to delay it until a certain act (can cut out music from intros from getting in your PMV)

