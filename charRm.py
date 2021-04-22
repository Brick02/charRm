import os
import datetime
import random
import sys
import time

class parms:
    illegal = """!@#$%^&*'? :;|"""
    protected_paths = []
    protected_paths.append(os.getcwd())
    protected_paths.append(sys.argv[0])
    extensions = []
    target_path = ""
    all = False
    recursive = False
    running = True
    selected = []
    start = time.time()



class Messages:
    help = """charrm  [-flags] [directory or file]
    \n
    charrm is a tool that removes illegal characters from filenames and directories
    \n
    -h, --help          Displays this page\n
    -r, --recursive     Apply directories and their contents recursively\n
    -i, --illegal       Specify which characters you want to remove: -i " *" removes spaces and stars\n
    -ext --extensions   Only apply to certain file extensions. Separated by coma: -ext jpg,png,txt\n
    Hint: use *all to effect everything in the current directory.
    \nRoses are red, this UI is terrible, i'm looking for a rope necklace that's wearable
    """
    r = "testingr"


def is_safe(path):
    if path in parms.protected_paths:
        return False
    if len(parms.extensions):
        if os.path.splitext(path)[1] not in parms.extensions:
            return False
    return True
def safe_paths(paths):
    safe = []
    for path in paths:
        if is_safe(path):
            safe.append(path)
    return safe

def randstr(size):
    string = ""
    for i in range(size):
        string = string + random.choice("ABCDEF1234567890")
    return string

def check(filename, illegal):
    for char in os.path.basename(filename):
        if char in illegal:
            return True
    return False

def check_files(files, illegal):
    bad_files = []
    bad_dirs = []
    bad_paths = []
    for file in files:
        if check(file, illegal):
            if is_safe(file):
                bad_paths.append(file)
                if os.path.isdir(file):
                    bad_dirs.append(file)
                if os.path.isfile(file):
                    bad_files.append(file)
    return bad_paths #[bad_dirs, bad_files]

def get_new_name(filename, illegal):
    old_name = os.path.basename(filename)
    new_name = old_name.translate({ord(x): '' for x in illegal})
    return os.path.dirname(filename) + "/" + new_name

def get_new_names(bad_paths, illegal):
    good_paths = []
    for path in bad_paths:
        good_paths.append(get_new_name(path, illegal))
    return good_paths


def backup(original, new_names):
    name = str(randstr(4))+ ".bak"
    f = open(name, "w")
    f.write("Backup of file names\n")
    f.write(str(datetime.datetime.now()) + "\n\n")
    for i in range(len(original)):
        f.write(str(original[i]) + ">>>" + str(new_names[i]) + "\n")
    f.close()
    if not os.path.isfile(name):
        sys.exit("ERROR: could not make a backup for some reason. idk")

def span(dir):
    contents = os.listdir(dir)
    # print(contents)
    files = []
    bottom = False
    for path in contents:
        #print(path)
        files.append(dir + "/" + path)
        if os.path.isdir(dir + "/" + path) and parms.recursive == True:
            files.extend(span(dir + "/" + path))
    return files

def span_rename(dir, illegal):
    contents = os.listdir(dir)
    files = []
    for path in contents:
        #print(path)
        if os.path.isfile(dir + "/" + path):
            if is_safe(path):
                os.rename(dir + "/" + path, get_new_name(dir + "/" + path, illegal))
        files.append(dir + "/" + path)
        if os.path.isdir(dir + "/" + path) and parms.recursive == True:
            files.extend(span_rename(dir + "/" + path, illegal))
    if is_safe(dir) and dir in parms.selected:
        os.rename(dir, get_new_name(dir, illegal))
    return files

def arg_handle(args):

    for i, arg in enumerate(args):
        try:
            if arg == "-ext" or arg == "--extension":
                if args[i+1][0] == ".":
                    ext = args[i + 1].split(",")
                    parms.extensions = ext
                else:
                    parms.running = False
                    return "Please enter valid extensions: -ext .jpg,.png"
        except:
            parms.running = False
            return "You have not enter any values for -ext"

        try:
            if arg == "-i" or arg == "--illegal":
                if args[i+1][0] == '"' or True:
                    ill = args[i + 1]
                    parms.illegal = ill
                else:
                    parms.running = False
                    return "No valid set of illegal characters"
        except:
            parms.running = False
            return "you have not entered any value for -i"


        if arg == "-h" or arg == "--help":
            parms.running = False
            return Messages.help

        if arg == "-r" or arg == "recursive":
            parms.recursive = True

    if args[-1] == "*all":
        parms.all = True
        parms.target_path = os.getcwd()
    else:
        if os.path.exists(args[-1]):
            parms.target_path = os.getcwd() + "/" + args[-1]
        else:
            parms.running = False
            return args[-1] + "  is not a file or directory"

def confirm(selected):
    choices = ['n','no','y','yes']
    get_input = True
    dir_num = 0
    file_num = 0
    for path in selected:
        if os.path.isdir(path):
            dir_num+=1
        if os.path.isfile(path):
            file_num+=1
        print(path)
    text = ""
    text = text+(str(dir_num) + " directories and ")#*bool(dir_num)
    text = text+(str(file_num) + " files")#*bool(file_num)
    print("\nFound:   " + text + " in " + str(round(time.time() - parms.start, 3)) + " seconds")
    print("make sure these are the ones you want to rename. BE CAREFUL!!!\n")
    while get_input:
        user_in = input("Would you like to continue? y/n\n")
        if user_in not in choices:
            print("please enter")
        else:
            if user_in == "n" or user_in == "no":
                sys.exit()
            else:
                get_input = False


def main(args):
    if parms.recursive == False and parms.all == False:
        if check(parms.target_path, parms.illegal):
            parms.selected = parms.target_path
            confirm([parms.selected])
            if is_safe(parms.selected):
                new_name = get_new_name(parms.selected, parms.illegal)
                backup([parms.selected], [new_name])
                os.rename(parms.selected, new_name)
                sys.exit("renamed one file")
        else:
            sys.exit(parms.target_path + " does not contain any illegal characters")

    all_files = span(parms.target_path)
    bad_paths = check_files(all_files, parms.illegal)
    if len(bad_paths) != 0:
        parms.selected = safe_paths(bad_paths)
        confirm(parms.selected)
        new_paths = get_new_names(bad_paths, parms.illegal)
        backup(parms.selected, new_paths)
        span_rename(parms.target_path, parms.illegal)
        sys.exit("renamed " + str(len(parms.selected)) + " file/dirs")

    else:
        sys.exit("no illegal characters found")

args = sys.argv
args = args[1:]
if len(args) == 0:
    sys.exit("Too few arguments. try --help")
args_handle_exceptions = arg_handle(args)
if args_handle_exceptions:
    print(args_handle_exceptions)

if parms.running:
    main(args)

'''
print(88888888)
print("ext  >>  " + str(parms.extensions))
print("illegal >>  " + str(parms.illegal))
print("target path >>  " + str(parms.target_path))
'''
