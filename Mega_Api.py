# -*- coding: UTF-8 -*-
from __future__ import division, print_function
import time
import fbchat
import os
import os.path
import sys
import csv
import logging
import subprocess
from mega import Mega
from functions import print_and_write, local_folders
from preferences import test_mode, send_FB_message, mega_email, mega_password
from subprocess import Popen, PIPE, CalledProcessError

# Changelog:
# - tried to fix ascii character issue with .encode('utf-8')
# - convertWidthRatio introduced in credentials.py
# - can set encoding codec in credentials.py

mega = Mega()
m = mega.login(mega_email, mega_password)

def get_files_from_mega():
    print_and_write("Getting files from mega")
    files = ""
    for i in range(0, 10):
        try:
            files = m.get_files()
            break
        except Exception as e:
            print_and_write("get_files_from_mega failed with: " + str(e))
            time.sleep(5)
    return files

def find_mega_folder_ID(folder_name, files):
    for file_Dict in files:
        file = files[file_Dict]
        file_Name = file['a']['n']
        file_Dir = file['p']
        if file_Name == folder_name:
            file_ID = file['h']
            return file_ID

def look_for_files_in_mega_folder(folder, files):
    mega_file_list = []
    fileCounter = 0
    for fileDict in files:
        file = files[fileDict]
        fileName = file['a']['n'].encode('utf-8')
        fileDir = file['p']
        if fileDir == find_mega_folder_ID(folder, files):
            # if '.mp4' in fileName or '.MP4' in fileName: # this will look only for mp4 files
            fileCounter = fileCounter + 1
            mega_file_list.append(fileName)

    return mega_file_list, fileCounter

def download_file_from_mega(file_Name):
    cwd = os.getcwd()
    try:
        for i in range(0, 10):
            try:
                file = m.find(file_Name.decode('utf-8'))
                if str(file) == 'None':
                    print_and_write('File not found on server: ' + file_Name)
                else:
                    break
            except Exception as e:
                print_and_write("m.find failed in download_... with: " + str(e))
                time.sleep(2)
        for i in range(0, 10):
            try:
                downloaded_path = str(cwd + "/" + local_folders['downloaded'])
                dl_location = cwd + "/" + local_folders['downloading']
                m.download(file, dl_location)
                file_name = file[0] #.encode('utf-8')

                # Checking if file is existing in the destination
                print_and_write('Checking if file is existing in the destination')
                downloaded_file = dl_location + "/" + file_Name
                print('downloaded_file ')
                print(downloaded_file)
                if os.path.isfile(downloaded_file):
                    print_and_write("Successfully downloaded: " + str(file_Name))
                    break
                else:
                    print_and_write("File not found in folder. Trying download again...")
            except Exception as e:
                print_and_write("download_file_from_mega failed with: " + str(e))
                time.sleep(2)
    except Exception as e:
        time.sleep(2)

def move_file_in_mega(fileName, folder):
    print_and_write("Starting moving file on mega: " + fileName) #.encode('utf-8'))
    for i in range(0, 10):
        try:
            file = m.find(fileName.decode('utf-8'))
            break
        except Exception as e:
            print("file = m.find failed in move_file_in_mega with: " + str(e))
            time.sleep(2)

    for i in range(0, 10):
        try:
            folder_ = m.find(folder)
            break
        except Exception as e:
            print("folder_ = m.find failed in move_file_in_mega with: " + str(e))
            time.sleep(2)

    for i in range(0, 10):
        try:
            resp = m.move(file[0], folder_)
            if str(resp) == "0":
                print_and_write("File moved successfully. Code: " + str(resp))
                break
            else:
                print_and_write("m.move failed! Error code: " + str(resp))
        except Exception as e:
            print("m.move failed in move_file_in_mega with: " + str(e))
            time.sleep(2)

def create_folder_in_mega(folder, files):
    foundfolder = False
    for fileDict in files:
        file = files[fileDict]
        fileName = file['a']['n']
        fileDir = file['p']
        if fileName == folder:
            fileID = file['h']
            foundfolder = True
            print_and_write('Folder ' + folder + ' found!')
    if foundfolder == False:
        print_and_write("Creating folder on mega: " + folder)
        for i in range(0, 10):
            try:
                m.create_folder(folder)
                break
            except Exception as e:
                print_and_write('create_folder_in_mega failed with: ' + str(e))
                time.sleep(2)
        print_and_write('Folder ' + folder + ' created on mega!')

def upload_to_mega(file, folder_):
    print_and_write('File uploading started: ' + file)
    try:
        for i in range(0, 10):
            try:
                folder = m.find(folder_)
                break
            except Exception as e:
                print_and_write('Failed! m.find ' + str(e))
                time.sleep(2)
        for i in range(0, 10):
            try:
                m.upload(file, folder[0])
                break
            except Exception as e:
                print_and_write('Failed! m.upload ' + str(e))
                time.sleep(2)

        print_and_write('File upload finished')
    except Exception as e:
        print_and_write('Failed! uploadFile ' + str(e))
        time.sleep(2)
