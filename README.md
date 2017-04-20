# MegaAutoConvert
###### Completely reworked. Now it can download and convert files simultaneously. Facebook messages are not implemented yet in this version.

Converting videos from Mega.co.nz and uploads back the converted videos

I'm a beginner coder, so do not expect so much about this python script, but it does the job well.

Just fill up the variables in the credentials.py and start the main.py. The script works mostly fine.


The script is using ffmpeg h265 encoding and sets the bitrate to the third of the video's width. For example: an 1280x720 video will be converted with 1280*0.3 = 384K bitrate. This method is enough for me to convert from h264, to get a little below average quality with h265 (HEVC) and much smaller file size.
Only videos with .MP4 and .mp4 extensions will be converted at the moment.

There is a lot of thing to do with it, but it works fine in this state.
Tho scipt is not handling any errors, exceptions, these will be added in the future.
### How to run:
Start main.py. This is the script that handles up and downloads.
Start converter.py. This scipt handles the converting of the downloaded files.
You cant start the watcher.py, this script sends you a Facebook message if one of the above is not running.

### Functionality:

- Downloads 1 file at a time from a specific folder in the Mega account, converts the file and reuploads to an other folder.
- After downloading, the downloaded file in the Mega account will be moved to an other folder called: CURRENTLY_WORKING_ON. When finished converting and uploading, moves this file to FINISHED folder.
- Estimated time for converting: The script counts the frames in the video file and counts the spent seconds with converting and counts the estimated fprames converted per second and now it can make a fairly accourate estimation for the conversion.
- if the video's bitrate is under the required bitrate, the video will not be converted 
- After finishing all the videos, it will check for new videos once every minute
- Creates a log file
- It can notify you about the converting process by Facebook messages. It looks like this: https://snag.gy/hj9zO5.jpg

Readme, commenting and script is now a mess, but it will be updated as i have time to work on it.
Also requirements.txt will be added.

### TODO

- main.py should spawn the other processes if they are not running.
- ~~Skipped video files will be moved to an other folder.~~
- ~~Mega api request errors will be handled.~~
- ~~Video converting errors will be logged and failed files will be moved.~~
- Will detect corrupted videos and log them.
- Write the ffmpeg output lines to a file, get estimated finish time from that, instead of the frame counting method before the encoding.
  - Frame counting before encoding to get estimated finish time is extremely slow.
  - Live estimated finish time will be available.
- Status update request for raw, converted, corrupted video files by Facebook message.
- Customized ffmpeg encoding.
- Getting new settings for encoding, etc... From a textfile on Mega.
- ~~Downloading multiple files, depending on disk space, while converting to speed up the process~~

### Issues

-  ~~'ascii' codec can't encode character u'\u2019' in position 26: ordinal not in range(128) and things like that~~
  - maybe fixed, still experimenting

### Client

There will be a client script that uploads raw files and downloads the finished files on your computer. It will upload only files for the 50% percent of the free storage in the Mega account.

- The client will check the downloaded files if they are corrupted
- Will try to fix corrupted files, or sends notification and moves the files to an other folder
- Option for a source folder. All the video files from this folder(and subfolders) will be uploaded.
  - Will move the downloaded files to the original file's folder.
  - Optionally deletes the older files after the newer ones are verified.

### Webpage

Logging, change settings. 
Later...

### Changelog:

#### 2017.04.14
##### V0.5
- Now checking file integrity before uploading. The log will be uploaded if it contains errors.
- The "can't encode character" issue is maybe gone.
- Minor bugfixes.
- Added "Total_Video_Conversion_Info.txt", for total converted file's size ratio
- Added watcher.py This script sends you a message if the main.py or converter.py is not running.

#### 2017.04.14
##### V0.4
- Completely reworked
- now it is running 2 processes. 1 is downloading, and an other one is converting the files
- Downloading files to the server, depending on free disk space. Can be mmodified in the preferences.py
- credentials.py renamed to preferences.py
- Code is now a bit less of a mess
- Facebook messages are not implemented at all in this version

#### 2017.04.10
##### V0.3
- Testmode and Send Facebook massage variables moved to credentials.py
- Some work on Facebook messages
- Skipped video files will be moved to SKIPPED folder from CURRENTLY_WORKING_ON folder when video file is found there before downloading a new file
- Mega api request errors handled now
