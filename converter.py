from __future__ import division, print_function
import os, time, csv, sys
from preferences import convert_width_ratio, codec, test_mode, mega_folders
from functions import local_folders, make_local_folders
from Mega_Api import move_file_in_mega

#Variables
cwd = os.getcwd()
downloaded_folder_path = cwd + "/" + local_folders['downloaded']
working_on_folder_path = cwd + "/" + local_folders['workingon']
converted_folder_path = cwd + "/" + local_folders['converted']
skipped_folder_path = cwd + "/" + local_folders['skipped']
finished_folder_path = cwd + "/" + local_folders['finished']
logs_folder_path = cwd + '/Logs'
avgConvertFPS = 1
data_dict = {'frames': 1, 'time': 1}
dict_file = local_folders['data'] + '/dict.csv'

date_time = time.strftime('%Y %m %d %H%M', time.gmtime())
def print_and_write(string):
    strfDateTime = time.strftime('%Y %m %d %H%M%S', time.gmtime())
    string = str(string)#.encode('utf-8')
    print(strfDateTime + ' - ' + string)
    with open(logs_folder_path + '/' + date_time + ' CONVERT_PrintLog.txt', 'a') as file:
        file.write(strfDateTime + ' - ' + string + "\n")
        file.close()

def write_dict(dictFile, dataDict):
    print_and_write('Writing dictionary to file')
    f = open(dictFile, 'w')
    w = csv.writer(f, delimiter=';')
    for key, val in dataDict.items():
        print_and_write(key + ' ' + str(val))
        w.writerow([key, val])
    f.close()

def read_dict_to_mem():
    f = open(dict_file, 'r')
    for key, val in csv.reader(f, delimiter=';'):
        data_dict[key] = val
    f.close()

def getAVGFPS():
    frames = int(data_dict['frames'])
    second = int(data_dict['time'])
    avgFps =  frames / second
    return(avgFps)

if __name__ == "__main__":
    print_and_write("FFMPEG Converter started.")

    raw_total_size = 1
    conv_total_size = 1
    file_counter = 0
    make_local_folders()

    # creating pid file in tmp
    print_and_write('Makeing PID file')
    pid = str(os.getpid())
    pidfile = local_folders['data'] + '/converter.pid'
    with open(pidfile, 'w+') as f:
        f.write(pid)
        f.close()

    # Creating dictionary for estimated time counting
    if os.path.isfile(dict_file):
        print_and_write('Data dictionary reading')
        read_dict_to_mem()
    else:
        print_and_write('Data dictionary Created')
        write_dict(dict_file, data_dict)

    # Getting files from DOWNLOADED folder
    working_time = 0
    while True:

        downloaded_files = os.listdir(downloaded_folder_path)
        print_and_write(' ')
        print_and_write('----------------------------------------------------------------------------------')
        if downloaded_files:
            start_time = time.time()
            print_and_write("Found files to convert!")
            for file in downloaded_files:
                print_and_write(file)

            convertable_filename = downloaded_files[0] #.decode('utf-8')
            convertable_file_path = downloaded_folder_path + '/' + convertable_filename
            del downloaded_files[0]

            convert_file_path = working_on_folder_path + '/H265_' +  convertable_filename

            print_and_write('new file: ' + convert_file_path)
            # Renaming the files
            print_and_write('Renaming file')

            skipped_file_path = skipped_folder_path + '/' + convertable_file_path

            # Getting width of video file
            widthO = os.popen(
                'ffprobe -v error -of flat=s=_ -select_streams v:0 -show_entries stream=width ' + convertable_file_path).read()
            widthS = widthO.split('=')

            width = int(widthS[1])

            target_bitrate = int(width * convert_width_ratio)

            # Getting bitrate of video file
            video_bitrate = os.popen(
                'ffprobe -v error -of flat=s=_ -select_streams v:0 -show_entries stream=bit_rate ' + convertable_file_path).read()
            video_bitrate = video_bitrate.split('"')
            video_bitrate = int(video_bitrate[1]) / 1000

            if not video_bitrate > target_bitrate:
                target_bitrate = video_bitrate*0.75
                print_and_write('Video bitrate is lower than target bitrate! Continuing with new target bitrate value.')

            print_and_write('Starting converting from ' + str(video_bitrate) + ' to ' + str(target_bitrate) + ' bitrate.')

            print_and_write('Calculating estimated time. Average converting fps: ' + str(getAVGFPS()))
            print_and_write('Getting frames count')
            Frames = os.popen(
                'ffprobe -v error -count_frames -select_streams v:0 -show_entries stream=nb_read_frames -of default=nokey=1:noprint_wrappers=1 ' + convertable_file_path).read()

            avg_fps = getAVGFPS()
            if avg_fps == 0: avg_fps = 1
            estTime = time.strftime('%H:%M:%S', time.gmtime(int(Frames) / avg_fps))
            print_and_write('Estimated time: ' + str(estTime))

            ffmpeg_cmd = 'ffmpeg -i ' + convertable_file_path + ' -strict -2 -preset medium -c:v ' + codec + ' -b:v ' + str(
                target_bitrate) + 'k -maxrate ' + str(target_bitrate) + ' ' + convert_file_path
            start_time = time.time()
            os.system(ffmpeg_cmd)

            converting_time = int(time.time() - start_time)
            # strf_conv_time = time.strftime('%H:%M', converting_time)
            # print_and_write('Converting finished in ' + str(strf_conv_time))

            # adding video values to the dictionari's variables
            data_dict['frames'] = int(data_dict['frames']) + int(Frames)
            data_dict['time'] = int(data_dict['time']) + int(converting_time)

            # writing dictionary to file
            write_dict(dict_file, data_dict)
            avgConvertFPS = int(Frames) / int(converting_time)
            print_and_write('AVG Converting FPS ' + str(avgConvertFPS))

            file_counter = file_counter + 1

            try:
                raw_file_size = os.path.getsize(convertable_file_path)
            except Exception:
                print_and_write('Unexpected error while getting raw file size:' + sys.exc_info()[1])
                rawFileSize = 1

            try:
                converted_file_size = os.path.getsize(convert_file_path)
            except Exception:
                print_and_write('Unexpected error while getting converted file size:' + sys.exc_info()[1])
                convertedFileSize = 1

            if converted_file_size == 0: converted_file_size = 1
            if raw_file_size == 0: raw_file_size = 1
            raw_total_size = raw_total_size + raw_file_size
            conv_total_size = conv_total_size + converted_file_size

            total_size_ratio = conv_total_size / raw_total_size *100

            fileSizeRatio = converted_file_size / raw_file_size * 100

            print(converted_file_size, raw_file_size, fileSizeRatio)

            spent_time = time.time() - start_time
            working_time = working_time + spent_time
            strf_working_time = time.strftime('%d Day, %H:%M:%S', time.gmtime(working_time))

            print_and_write('The new file is ' + '{:.2f}'.format(fileSizeRatio) + '% smaller than the original.')
            total_size_info_txt = 'Total size comparison: ' + str(int(int(raw_total_size)/1000000)) + 'MB / ' \
                                 + str(int(int(conv_total_size)/1000000)) \
                                 + 'MB ' + str(total_size_ratio) + '%, ' + str(file_counter) + ' files converted in ' + strf_working_time
            print_and_write(total_size_info_txt)

            # Logging file info to textfile
            with open(logs_folder_path + '/' + date_time +  'Video_Conversion_Info.txt', 'a') as f:
                f.write('Converted raw file: ' + convertable_filename + '\n')
                f.write('Raw / converted file size: {:.2f}'.format(
                    int(raw_file_size) / 1000000) + 'MB' + ' / {:.2f}'.format(
                    int(converted_file_size) / 1000000) + 'MB' + ' / {:.2f}'.format(fileSizeRatio) + '% smaller' + '\n')
                f.write('\n')

            with open(logs_folder_path + '/' + date_time +  'Video_Conversion_Info.csv', 'a') as f:
                f.write(convertable_filename + ',' + str(raw_file_size) + ',' + str(converted_file_size) + ',' + str(fileSizeRatio) + '\n')

            with open(logs_folder_path + '/Total_Video_Conversion_Info.txt', 'w') as f:
                f.write(total_size_info_txt)

            with open(logs_folder_path + '/' + date_time +  'Total_Video_Conversion_Info.csv', 'a') as f:
                f.write(
                    convertable_filename + ',' + str(raw_total_size) + ',' + str(conv_total_size) + ',' + str(total_size_ratio) + ',finished' + '\n')

            if fileSizeRatio > 99:
                with open(local_folders['downloaded'] + '/' + convertable_filename + '_CONVERTING.log') as f:
                    f.write('fileSizeRatio is more than 100 for this file: ' + str(total_size_ratio) + '%. Filename: ' + convertable_filename)

            os.rename(convert_file_path, converted_folder_path + '/H265_' + convertable_filename)
            os.remove(convertable_file_path)
            print_and_write("Converting finished " + '/H265_' + convertable_filename)

            # else:
            #     print_and_write('Bitrate is lower than target bitrate. Moving file to skipped directory ' + skipped_file_path)
            #     print_and_write('Video bitrate: ' + str(video_bitrate) + ' target bitrate: ' + str(target_bitrate))
            #     os.rename(convertable_file_path, skipped_folder_path + '/' + convertable_filename)
            #     # Logging file info to textfile
            #     with open(logs_folder_path + '/Video_Conversion_Info.txt', 'a') as f:
            #         f.write('File SKIPPED: ' + convertable_filename + '\n')
            #         f.write('\n')
            #
            #     with open(logs_folder_path + '/Video_Conversion_Info.csv', 'a') as f:
            #         f.write(
            #             str(convertable_filename) + ',0,0,0,skipped' + '\n')

        print('sleeping')
        time.sleep(10)
