# Python Utilities

A set of Python libraries that automate repeating tasks, making them usable with a single function call.

## Shell Utilities

A Python library that serves as an interface for Python scripts to execute commands and interact with shells.

Tested operating systems and shells:
* Linux with Bash;
* Windows with Powershell.

### List of Features

* Shell command execution with status code return;
* Shell command execution with output return;
* Prompt for user input. Secret prompts, used for credential inputs, are possible;
* Check if user prompt is `yes`;
* Check if user prompt is `no`;
* Remove trees;
* Remove files;
* Check if file or directory exists;
* Check if file or directory exists and, if not, they'll be created;
* Copy files and folders;
* Copy trees;
* Get a list of all files or directories (or both) from a directory;
* Get a directory tree from a path with wildcards (only at the end of path);
* Rename a file or directory;
* Text replacement in files;
* Read file content into strings;
* Text append in files from input string;
* Text append between files;
* Copy lines from source to destination file;
* Create `.zip` files;
* Copy files and directories to `.zip` files;
* Extract `.zip` files.

## Docker Utilities

A Python library that has recurrent operations in Docker packed into a set of function to be called.

All features work in Linux and Windows.

### List of Features

* Check and initiate Docker Swarm in local host machine;
* Submit a single secret to Docker by creating a temporary file;
* Get an image's ID from its name;
* Get a container's ID from its parent image's name;
* Check the existence of an array of images, provided as a parameter;
* Check the existence of an array of volumes and create them, provided as a parameter;
* Remove directories in volume that are only valid for previous executions;
* Copy a directory from host to a specified volume;
* Copy a directory from a specified volume to host;
* Remove stack with a timer in order to make further operations safer. The default time is 30 seconds;
* Remove all Docker entities, with a parameter to define if the volumes will also be removed;
* Remove Docker containers, providing their name and current status;
* Remove Docker volumes, providing their name;
* Remove Docker images, providing their name;
* Remove Docker secrets, providing their name.

## How to use

In the script that will use the library, copy the following lines and paste them at the beginning:

```python
import sys

# Import all libraries from this repository
sys.path.insert(0, './python-utilities/lib/')

import python_shell_utilities # For Shell utilities
import python_docker_utilities # For Docker utilities
```

When the main script is executed, the library is compiled in a `.pyc` file to be used by the script.
