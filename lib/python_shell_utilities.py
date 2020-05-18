# All functions to improve Python interaction with shells must be placed here.
#
# Author: Vitor Santos <vitorhgsantos90@gmail.com>

import subprocess, sys, platform, shutil, stat, errno, re, os, distutils.dir_util, glob, getpass, zipfile, filecmp

######################  SHELL INTERACTION   ######################

# Print message before exit
def exit_script(message):
    print(message)
    sys.exit()

# Verify if parameter is a string
def string_verifier(parameter):
    if type(parameter) is not str:
        exit_script("Please insert a string for command shell in order to execute it.")  

# Function to execute commands
def execute_command(command, raise_exception=False):
    string_verifier(command)

    try:    
        subprocess.run(command, shell=True, stderr=subprocess.PIPE)
    except subprocess.CalledProcessError as e:
        if raise_exception:
            raise
        else:
            return e.returncode
    else:
        return 0

# Prompt for user input 
def user_input(input_message, password_input=False):
    user_input = ""

    # Check python version and use its own input function
    while user_input == "":
        user_input = getpass.getpass(input_message) if password_input else (str(input(input_message)))
    
    return user_input

# Return arguments as a Python array
def get_arguments():
    # In this case, sys.argv[0] is the name of the script
    return sys.argv[1:]

# Return arguments as a Python array and detect inconsistencies
def parse_arguments(command_usage): 
    arguments = get_arguments()

    if len(arguments) == 0:
        exit_script(command_usage)
    
    return arguments

# Check if user prompt is an equivalent to "yes"
def user_prompt_yes(answer=""):
    return True if answer == "yes" or answer == "y" else False

# Check if user prompt is an equivalent to "no"
def user_prompt_no(answer=""):
    return True if answer == "no" or answer == "n" else False

######################  FILE SYSTEM INTERACTION   ######################

# Callable function from remove_tree function
def fix_permissions_and_retry(func, path, exc_info):
    if not os.access(path, os.W_OK):
        try:
            os.chmod(path, stat.S_IWUSR | stat.S_IWGRP | stat.S_IWOTH)
            func(path)
        except OSError as e:
            if e.errno == 2:
                print("No such file or directory. Script will carry on.")
    else:
        raise IOError("It was not possible to convert permissions in order to edit the file system.")

# Remove folder with children
def remove_tree(path):
    shutil.rmtree(path, onerror=fix_permissions_and_retry)

# Remove file
def remove_file(file_path):
    try:
        os.remove(file_path)
    except OSError as e:
        if e.errno == errno.ENOENT:
            print("File doesn't exist. Script will carry on.")
        else:
            raise

# Check if path exists or not. It can be a directory or a file. Wildcards supported.
def check_if_path_exists(path):
    return True if glob.glob(path) else False

# Check if entity (file or directory) exists. If not, it will be created. Paths must be absolute
def check_entity_and_create(path, type):
    if not check_if_path_exists(path):
        if type == "directory":
            os.makedirs(path, mode=0o774)
        elif type == "file":
            check_entity_and_create(path, "directory")
            open(path, "w").close()

# Copy file to destination, making sure all parent directories exist. Paths must be absolute
def copy_file(source_path, dest_path):
    check_entity_and_create('dest_path', "directory")
    shutil.copy(source_path, dest_path)

# Check if destination file exists. If not, the source file will be copied to destination
def check_dest_file_and_copy(source_path, dest_path):
    if not check_if_path_exists(dest_path):
        copy_file(source_path, dest_path)

# Copy files and folders recursively to a destination path. Paths must be absolute
def copy_tree_recursively(root_source_path, dest_path):
    if check_if_path_exists(root_source_path):
        check_entity_and_create(dest_path, "directory")
        distutils.dir_util.copy_tree(root_source_path, dest_path)
    else:
        print("Root directory doesn't exist. Script will carry on.")

# Get children from directory. They can be all types of children or files or directories exclusively. Wildcards not supported. Paths must be absolute
def get_children_from_directory(path, children_type="all"):
    if check_if_path_exists(path) and os.path.isdir(path):
        if children_type == "directory":
            return [path + f + "/" for f in os.listdir(path) if os.path.isdir(os.path.join(path, f))]
        elif children_type == "file":
            return [path + f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]    
        else:
            return [(path + f + "/" if os.path.isdir(os.path.join(path, f)) else path + f) for f in os.listdir(path)] 
    else:
        exit_script("Directory doesn't exist.")

# Get tree from path provided with wildcards. The wildcard must be used at the end of the path. Paths must be absolute
def get_tree_from_wildcard_path(path):
    tree = []
    array_of_directories = glob.glob(path)

    for directory in array_of_directories:
        tree.append(get_children_from_directory(directory))

    return array_of_directories

# Rename files and directories
def rename_path_file_directory(old_name="", new_name=""):
    os.rename(old_name, new_name) if check_if_path_exists(old_name) else None

######################  TEXT MANIPULATION   ######################

# Replace text detected in a regex pattern with a new string, given a file path
def replace_text_in_files_regex(file_path, pattern, new_string):
    # Read contents from file as a single string
    file_string = read_file_to_string(file_path)

    # Use RE package to allow for replacement (also allowing for (multiline) REGEX)
    file_string = re.sub(pattern, new_string, file_string)

    # Write contents to file.
    write_string_to_file(file_path, file_string)

# Read contents from file as a single string
def read_file_to_string(file_path):
    with open(file_path, "r") as opened_file:
        output_string = opened_file.read()
        return output_string

# Concatenate file in destination path with the contents of file in source path
def concatenate_text_files(source_path, dest_path):
    with open(source_path) as source_file:
        with open(dest_path, 'w') as dest_file:
            dest_file.write(source_file.read())

# Write string provided as a parameter to a file
def write_string_to_file(file_path, string=""):
    with open(file_path, "w") as opened_file:
        opened_file.write(string) 

# Copy lines matched by pattern from file in source path to file in destination path
def copy_line_to_file(source_path, pattern, dest_path):
    with open(source_path) as source_file:
        pattern_detector = re.compile(pattern)
        detected_lines = []

        # Import all detected lines to array
        for line in enumerate(source_file):
            if not pattern_detector.match(line[1]) == None:
                detected_lines.append(line[1])
        
        # Create file and write detected lines to file
        check_entity_and_create(dest_path, "file")
        os.chmod(dest_path, stat.S_IWRITE)
        with open(dest_path, 'a') as dest_file:
            for line in detected_lines:
                dest_file.write(line)

######################  ZIP/UNZIP FILES   ######################

# Zip an array of files into a file provided as a path
def create_zip_file_with_files(zip_file_path, entities_array=[], is_recursive=False):
    check_entity_and_create(zip_file_path, "file")
    
    with zipfile.ZipFile(zip_file_path, "w") as new_zip:
        for entity in entities_array:
            if check_if_path_exists(entity) and os.path.isdir(entity):
                zip_entities_to_zip_file(entity, new_zip, is_recursive)
            else:
                new_zip.write(entity)       

# Function that zips files and directories to zip. It can be recursive to child directories
def zip_entities_to_zip_file(entity, new_zip, is_recursive=False):
    for dirpath, dirnames, filenames in os.walk(entity):
        new_zip.write(dirpath)

        for filename in filenames:
            new_zip.write(os.path.join(dirpath, filename))

        if (not dirnames == [] and not dirnames == None) and is_recursive:
            for dirname in dirnames:
                zip_entities_to_zip_file(dirname, new_zip, is_recursive)

# Extract a zip file to a provided directory
def extract_zip_content(zip_file_path, dir_to_extract):
    with zipfile.ZipFile(zip_file_path, "r") as zip_file:
        zip_file.extractall(dir_to_extract)
