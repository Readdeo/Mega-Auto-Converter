import os, csv, time, fbchat, sys
from mega import Mega
from functions import print_and_write, local_folders, get_disk_info, make_local_folders
from preferences import fb_email, fb_password, FB_UID, send_FB_message, mega_email, mega_password, test_mode, free_space_percent
from Mega_Api import look_for_files_in_mega_folder, find_mega_folder_ID, get_files_from_mega, download_file_from_mega
from Mega_Api import move_file_in_mega, create_folder_in_mega, upload_to_mega

# logging.basicConfig(filename='DEBUG.log',level=logging.DEBUG)

def read_filename_dict_to_mem():
    filename_dict_file = os.getcwd() + '/' + local_folders['data'] + '/file_names.csv'
    if os.path.isfile(filename_dict_file):
        f = open(filename_dict_file, 'r')
        for key, val in csv.reader(f, delimiter=';'):
            file_name_dict[key] = val
        f.close()
        print_and_write('File names loaded successfully!')
    else:
        print_and_write('File names csv not found. Continuing...')

def to_unicode_or_bust(obj, encoding='utf-8'):
     if isinstance(obj, basestring):
         if not isinstance(obj, unicode):
             obj = unicode(obj, encoding)
     return obj

if __name__ == "__main__":
    # Creating local folders
    make_local_folders()

    print_and_write("Mega_Auto_converter started")
    if send_FB_message: client = fbchat.Client(fb_email, fb_password)

    # variables
    cwd = os.getcwd()
    download_files = True
    files_in_raw = []
    file_name_dict = {}
    converted_folder_path = cwd + "/" + local_folders['converted']
    if test_mode == True:
        from preferences import mega_folders_test as mega_folders
    else:
        from preferences import mega_folders

    # Loading saved file names to dictionary
    read_filename_dict_to_mem()

    # creating pid file in tmp
    print_and_write('Makeing PID file')
    pid = str(os.getpid())
    pidfile = local_folders['data'] + '/downloader.pid'
    with open(pidfile, 'w+') as f:
        f.write(pid)
        f.close()

    files = get_files_from_mega()

    # Creating mega folders
    for folder in mega_folders:
        create_folder_in_mega(mega_folders[folder], files)

    # Do forever
    while True:
        print_and_write('----------------------------------------------------------------------------------')

        # Getting files list from mega raw folder
        if not files_in_raw:
            print_and_write("No files to download")

            files = get_files_from_mega()

            files_in_raw, no_files_in_raw =look_for_files_in_mega_folder(mega_folders['raw'], files)
            print_and_write(str(no_files_in_raw) + " Files found in raw folder on Mega:")
            for file in files_in_raw:
                print_and_write(file)
        else:
            print_and_write("File list not empty, continuing downloading")

        # Getting disk space info
        disk_info = get_disk_info()
        print_and_write("Disk space info: " + str(disk_info))
        if int(disk_info['percent']) > free_space_percent:
            print_and_write("Free disk space is over " + str(free_space_percent) + "%"  + "(" + str(disk_info['percent']) + ")")
            download_files = False
        else:
            print_and_write("Free disk space is under " + str(free_space_percent) + "%"  + "(" + str(disk_info['percent']) + ")")
            download_files = True

        # print_and_write(files_in_raw)
        if download_files:
            if files_in_raw:

                # Downloading file
                print_and_write("Downloading from Mega: " + files_in_raw[0])
                file_to_download = files_in_raw[0]
                download_file_from_mega(files_in_raw[0])

                # Removing special characters from file name
                dl_location = cwd + "/" + local_folders['downloading']
                downloaded_file = dl_location + "/" + file_to_download

                # Creating trimmed file name
                file_extension = file_to_download[-4:]
                trimmedFilename = ''.join(e for e in file_to_download if e.isalnum())
                trimmedFilename = trimmedFilename[0:-3] + file_extension

                # Writing file names to dictionary and file
                file_name_dict[trimmedFilename] = file_to_download
                # asd = to_unicode_or_bust(files_in_raw[0])
                with open (cwd + '/' + local_folders['data'] + '/file_names.csv', 'a+') as f:
                    f.write(trimmedFilename + ';' + files_in_raw[0] + '\n')
                # Renaming and moving downloaded file
                os.rename(local_folders['downloading'] + '/' + file_to_download, local_folders['downloaded'] + '/' + trimmedFilename)

                # Moving file on mega to DOWNLOADED folder
                if not test_mode: move_file_in_mega(file_to_download, mega_folders['downloaded'])

                print_and_write("Deleting " + file_to_download + " from list")
                del files_in_raw[0]
                # print_and_write(files_in_raw)
        else:
            print_and_write("Disk is more than " + str(free_space_percent) + "% full. Not downloading")

        # Uploading part
        converted_files = os.listdir(converted_folder_path)
        print_and_write('Files in the converted folder:')
        print_and_write(converted_files)

        if converted_files:
            file_to_upload_path = converted_folder_path + "/" + converted_files[0]
            file_to_upload_name = converted_files[0]

            # Checking converted file integrity
            chk_cmd = 'ffmpeg -v error -i {} -map 0:1 -f null - 2>{}.log'.format(file_to_upload_path, file_to_upload_path)
            print(chk_cmd)
            os.system(chk_cmd)
            error_file = file_to_upload_path + '.log'
            error_file_size = os.path.getsize(error_file)
            if error_file_size == 0:
                print_and_write('No errors in video file')
                os.remove(error_file)
            else:
                print_and_write('Error in video file!')

            del converted_files[0]

            # Renaming file to its original name before uploading
            try:
                converted_file_name_H265 = converted_folder_path + "/H265_" + file_name_dict[file_to_upload_name[5:]]
                os.rename(file_to_upload_path, converted_file_name_H265)
            except Exception as e:
                print_and_write('Original file name not found for file: ' + str(e))
                converted_file_name_H265 = file_to_upload_path

            upload_to_mega(converted_file_name_H265, mega_folders['converted'])
            os.remove(converted_file_name_H265)
            try:
                move_file_in_mega(file_name_dict[file_to_upload_name[5:]], mega_folders['finished'])
            except Exception as e:
                print_and_write('Exception when moving file on mega. Maybe file not found? ' + str(e))
        if files_in_raw: sleeptime = 5
        else: sleeptime = 180
        print_and_write("Sleeping " + str(sleeptime) + " seconds, downloading files: " + str(download_files) + '. Disk space: ' + disk_info['percent'] + '%')
        time.sleep(sleeptime)

