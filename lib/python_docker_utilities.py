# All functions to improve Python interaction with Docker must be placed here.
#
# Author: Vitor Santos <vitorhgsantos90@gmail.com>

import platform, time
import python_shell_utilities

# Initiate Docker Swarm
def initiate_docker_swarm():
    return_code = python_shell_utilities.execute_command_and_return_status("docker node ls")

    if not return_code == 0:
        python_shell_utilities.execute_command_and_return_status("docker swarm init") 

# Get hostname. This is typically used to give a name to the stack
def get_hostname():
    return python_shell_utilities.execute_command_and_return_output("docker node ls --filter \"role=manager\" --format \"{{.Hostname}}\"", True)

# Submit secret to Docker, by using a temporary file during this function's execution
def submit_secret_to_docker(secret_input, secret_name):
    python_shell_utilities.check_entity_and_create("./temp/temp.txt", "file")
    python_shell_utilities.write_string_to_file("./temp/temp.txt", secret_input)
    python_shell_utilities.execute_command_and_return_status("docker secret create " + secret_name + " ./temp/temp.txt")
    python_shell_utilities.remove_file("./temp/temp.txt")

# Get image ID from name
def get_image_id_from_name(image_name):
    return python_shell_utilities.execute_command_and_return_output("docker images docker-registry.inesctec.pt/recap/recap-docker-images/" + image_name + " --format \"{{.ID}}\"")

# Get container id from its correspondent image's name
def get_container_ids_from_image_name(image_name):
    image_id = get_image_id_from_name(image_name)
    return python_shell_utilities.execute_command_and_return_output("docker ps -aq --filter ancestor=" + image_id + " --filter status=running").split("\n")

# Check if all specified images were downloaded
def check_downloaded_images(images_array=[]):
    for image in images_array:
        output = get_image_id_from_name(image)

        if output == "":
            return False
    
    return True

# Check if volume directories exist
def check_volume_directories_and_create(stack_name, volume_directories=[]):
    for volume_directory in volume_directories:
        if platform.system() == "Linux":
            python_shell_utilities.check_entity_and_create("/var/lib/docker/volumes/" + stack_name + volume_directory, "directory")
        elif platform.system() == "Windows":
            python_shell_utilities.execute_command_and_return_status("docker exec -it volume-holder mkdir -p /vm-root/var/lib/docker/volumes/" + stack_name + volume_directory)

# Remove information on volume that is only valid for a single container execution
def remove_unique_container_data(stack_name, volumes_array=[]):
    for volume in volumes_array:
        if platform.system() == "Linux":
            python_shell_utilities.remove_tree("/var/lib/docker/volumes/" + stack_name + volume)
        elif platform.system() == "Windows":
            python_shell_utilities.execute_command_and_return_status("docker exec -it volume-holder rm -r /vm-root/var/lib/docker/volumes/" + stack_name + volume)

# Copy files from host to volume
def copy_host_file_tree_to_volume(host_directory, volume_directory):
    if platform.system() == "Linux":
        python_shell_utilities.copy_tree_recursively(host_directory, volume_directory)
    elif platform.system() == "Windows":
        host_directory_in_volume = host_directory.split('/')[-2]

        # These operations are necessary becuase the folder is copied, instead of its content
        python_shell_utilities.execute_command_and_return_status("docker cp " + host_directory + " volume-holder:/vm-root" + volume_directory)
        python_shell_utilities.execute_command_and_return_status("docker exec -it volume-holder cp -a /vm-root" + volume_directory + host_directory_in_volume + "/. /vm-root" + volume_directory)
        python_shell_utilities.execute_command_and_return_status("docker exec -it volume-holder rm -r /vm-root" + volume_directory + host_directory_in_volume)

# Copy files from volume to host
def copy_volume_file_tree_to_host(volume_directory, host_directory):
    if platform.system() == "Linux":
        python_shell_utilities.copy_tree_recursively(volume_directory, host_directory)
    elif platform.system() == "Windows":
        python_shell_utilities.execute_command_and_return_status("docker cp volume-holder:/vm-root" + volume_directory + " " + host_directory)

# Remove stack safely, giving time for all containers to be deleted.
def remove_stack_safely(final_message, wait_time=30.0):
    # Stack name obtained from hostname, the same as in fresh_start.py
    stack_name = python_shell_utilities.execute_command_and_return_output("docker node ls --filter \"role=manager\" --format \"{{.Hostname}}\"")

    # Remove stack
    python_shell_utilities.execute_command_and_return_status("docker stack rm " + stack_name)

    # Timer added in order to wait for all containers to be closed before a new deployment
    current_time = 0

    while not current_time == wait_time:
        print("Time elapsed: " +  str(current_time) + " seconds out of " + str(wait_time) + ".")
        time.sleep(1.0)
        current_time += 1

    print(final_message)

# Perform Docker system prune which will ersae all images, containers and networks not being used or running
def docker_system_prune(prune_volumes=False):
    python_shell_utilities.execute_command_and_return_status("docker system prune --force --volumes") \
        if prune_volumes \
        else python_shell_utilities.execute_command_and_return_status("docker system prune --force")

# Remove containers
def remove_containers(containers_array=[], container_status_filter=""):
    for container in containers_array:
        if container_status_filter == "running" or container_status_filter == "exited" or container_status_filter == "dead":
            python_shell_utilities.execute_command_and_return_status("docker rm -f $(docker ps --all --filter \"status=" + container_status_filter + "\" --filter \"name=" + container + "\")")
        else:
            python_shell_utilities.execute_command_and_return_status("docker rm -f " + container)

# Remove volumes
def remove_volumes(volumes_array=[]):
    for volume in volumes_array:
        python_shell_utilities.execute_command_and_return_status("docker volume rm -f $(docker volume ls --quiet --filter name=" + volume + ")") 

# Remove images
def remove_images(images_array=[]):
    for image in images_array:
        python_shell_utilities.execute_command_and_return_output("docker rmi -f $(docker images " + image + ")")

# Remove secrets
def remove_secrets(secrets_array=[]):
    for secret in secrets_array:
        python_shell_utilities.execute_command_and_return_status("docker secret rm $(docker secret ls --filter name=" + secret + ")")
