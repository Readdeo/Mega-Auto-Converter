#Facebook user's ID who receives the sent messages
FB_UID = XXXXX

#Facebook account credentials. This account sends the messages.
fb_email = "XXXXX"
fb_password = "XXXXX"

#Mega.co.nz account credentials
mega_email = "XXXXX"
mega_password = "XXXXX"

# if testMode is true, the script will use other folders in Mega to do the job
test_mode = False
# if this is true, the script will notify you with Facebook messages
send_FB_message = False


mega_folders_test = {'converted':'TEST_CONVERTED', 'raw': 'TEST', 'finished': 'TESTFINISHED',
                    'cwo': 'TEST_CWO', 'skipped': 'SKIPPED', 'downloaded': 'TEST_DOWNLOADED'}

mega_folders = {'converted':'CONVERTED', 'raw': 'RAW', 'finished': 'FINISHED',
                    'cwo': 'CURRENTLY_WORKING_ON', 'skipped': 'SKIPPED', 'downloaded': 'DOWNLOADED'}

free_space_percent = 50

# encoding variables for ffmpeg
convert_width_ratio = 0.3
codec = "libx265"

