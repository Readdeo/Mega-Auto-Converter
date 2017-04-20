import time
import subprocess
import os
import unicodedata
from preferences import test_mode

local_folders = {'data':'data', 'downloading':'DOWNLOADING', 'logs':'Logs', 'finished':'FINISHED', 'downloaded':'DOWNLOADED', 'converted':'CONVERTED', 'skipped':'SKIPPED', 'workingon':'WORKING_ON'}

date_time = time.strftime('%Y %m %d %H%M', time.gmtime())
logs_folder_path = os.getcwd() + '/Logs'

def print_and_write(string):
    strfDateTime = time.strftime('%Y %m %d %H%M%S', time.gmtime())
    if isinstance(string, unicode):
        string = unicodedata.normalize('NFKD', string).encode('ascii','ignore')
    else:
        string = str(string)
    print(strfDateTime + ' - ' + string)
    with open(logs_folder_path + '/' + date_time + ' Downloader_PrintLog.txt', 'a') as file:
        file.write(strfDateTime + ' - ' + string + "\n")
        file.close()

def make_local_folders():
    for folder in local_folders:
        if not os.path.isdir(os.getcwd() + "/" + local_folders[folder]):
            os.mkdir(os.getcwd() + "/" + local_folders[folder], 0777)
        else:
            print(str(os.getcwd() + "/" + local_folders[folder]))

def get_disk_info():
    df = subprocess.Popen(['df', "main.py"], stdout=subprocess.PIPE)
    output = df.communicate()[0]
    device, size, used, available, percent, mountpoint = \
        output.split("\n")[1].split()
    percent = percent[0:-1]
    return {'device':device, 'size':size, 'used':used, 'available':available, 'percent':percent, 'mountpoint':mountpoint}