import sys
import os
import time
import shutil
sys.path.insert(0, os.path.abspath('.'))

from lib.dobot import Dobot

bot = Dobot('/dev/ttyUSB0')

print('Bot status:', 'connected' if bot.connected() else 'not connected')

# initially move the arm up (need to place the arm right on the paper)
bot.move_to_relative(0, 0, 10, 0.5)

#open the file function
def open_file(file_name):
    global FILE
    FILE = open(file_name, "r")

def get_file_list():
    # get file path of all .armcode files in current directory
    # if queue folder doesn't exist, create folder
    try:
        file_list = [f for f in os.listdir('queue') if f.endswith('.armcode')]
    except FileNotFoundError:
        print("No .armcode file found in queue folder OR No queue folder found\nCreated Queue Folder...")
        os.mkdir("queue")
        file_list = [f for f in os.listdir('queue') if f.endswith('.armcode')]
    # return 0 if nothing found
    if len(file_list) == 0:
        return 0
    file_list.sort()
    for i in range (0, len(file_list)):
        file_list[i] = 'queue/' + file_list[i]
    #print(file_list)
    return file_list

# function to return a line of a text file
def get_line():
    line = FILE.readline()
    if line == '':
       return ""
    else:
        return line.split(',')

# get the first letter of line
def get_first_letter(line):
    return line[0]

# function to parse the instruction/co-ordinates from the .armcode file
def parse_instruction(file_name):
    open_file(file_name)
    # loop till line is empty
    while 1:
        line = get_line()
        print(line)
        if line == "":
            break
        # if lenght of line is > 3
        if len(line) > 1:
            x = float(line[1])
            y = float(line[2])
            print("coordinates: (%.2f, %.2f)"% (x, y))
        else:
            z = 10.0 # reduandant code, but just to be clear

        if get_first_letter(line) == 'm':
            print("move the arm using the api\n")
            bot.move_to_relative(y, x, 0, 0.5)
        elif get_first_letter(line) == 'd\n' or get_first_letter(line) == 'd':
            print("pen down\n")
            bot.move_to_relative(0, 0, -z, 0.5)
        elif get_first_letter(line) == 'u\n' or get_first_letter(line) == 'u':
            print("pen up\n")
            bot.move_to_relative(0, 0, z, 0.5)
        elif get_first_letter(line) == 's':
            print("stop\n")
        else:
            print("error\n")
    
    print("END\n")
    
def poll_queue():
    ##### THIS IS FOR DRAWING MULTIPLE .armcode FILES #####
    # Also this queues from the queue folder and waits for the next file to be ready
    try: 
        while 1:
            file_list = get_file_list()
            # if file list is empty, wait till .armcode file is found
            if file_list == 0:
                print("No .armcode file found in queue folder\nWaiting for .armcode file to be created...")
                while 1:
                    file_list = get_file_list()
                    if file_list != 0:
                        print("Files found")
                        print(file_list)
                        break
            # loop through all files
            for file_name in file_list:
                parse_instruction(file_name)
                # try catch block to move to finished folder after finisning the file
                try :
                    shutil.move(file_name, "finished/")
                except:
                    # create finished folder if it doesn't exist
                    os.mkdir("finished")
                    shutil.move(file_name, "finished/")
                # wait 2 seconds before next file
                file_list = get_file_list()
                time.sleep(2)
    except KeyboardInterrupt:
        exit()

    ##### THIS IS FOR ONE .armcode FILES #####
    ## parse_instruction('examples/06-13T14-10-30 hello world.armcode')

def main():
    poll_queue()

if __name__ == '__main__':
    main()