import os
import fbchat
import time
from preferences import *
from functions import local_folders

global not_running_downloader_sent
global not_running_converter_sent
not_running_downloader_sent = False
not_running_converter_sent = False

client = fbchat.Client(fb_email, fb_password)
def check_downloader_pid():
    txt = open(local_folders['data'] + '/downloader.pid')
    pid = int(txt.read())
    txt.close()
    print (pid)
    global not_running_downloader_sent
    try:
        os.kill(pid, 0)
    except OSError:
        print("Downloader not running")
        if not not_running_downloader_sent: client.send(FB_UID, "Mega Auto Converter's downloader is not running!")
        not_running_downloader_sent = True
        with open('downloader_running.txt', 'w') as f:
            f.write('False')
    else:
        not_running_downloader_sent = False
        print("Downloader running")
        with open('downloader_running.txt', 'w') as f:
            f.write('True')

def check_converter_pid():
    txt = open(local_folders['data'] + '/converter.pid')
    pid = int(txt.read())
    txt.close()
    print (pid)
    global not_running_converter_sent
    try:
        os.kill(pid, 0)
    except OSError:
        print("Converter not running")
        if not not_running_converter_sent: client.send(FB_UID, "Mega Auto Converter's converter is not running!")
        not_running_converter_sent = True
        with open('converter_running.txt', 'w') as f:
            f.write('False')
    else:
        not_running_converter_sent = False
        print("Converter running")
        with open('converter_running.txt', 'w') as f:
            f.write('True')

def periodic_status_update():
    file_name = 'Total_Video_Conversion_Info.txt'
    file_list = os.listdir(os.getcwd() + '/Logs')
    print(file_list)
    info_file = None
    info = None
    for file in file_list:
        if file_name in file:
            print('File Found! ' + file_name)
            info_file = file
    with open(os.getcwd() + '/Logs/' + info_file, 'r') as f:
        info = f.read()
    return info

time_ = 0
prev_status = ''
while True:
    check_downloader_pid()
    check_converter_pid()
    if time.time() - time_ > 3600:
        time_ = time.time()
        status = periodic_status_update()
        if prev_status != status:
            prev_status = status
            print(status)
            client.send(FB_UID, "Status update: " + status)
    time.sleep(10)
