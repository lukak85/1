import os

# each website is separate project
def create_project_dir(directory):
    if not os.path.exists(directory):
        print('Creating project '+ directory)
        os.makedirs(directory)

# create queue and crawled files
def create_queue_file(project_name, starting_pages):
    queue_file = project_name + '/frontier.txt'
    
    # Create a file with starting pages or put them in if the
    # queue is empty
    if not os.path.isfile(queue_file) or os.stat(queue_file).st_size == 0:
        write_file(queue_file, starting_pages)
        return starting_pages
    # Make into an array element from the file and return it
    else:
        return file_to_array(queue_file)
    
# create new file    
def write_file(path, data):
    f = open(path, 'w')

    page_data = ""

    for page in data:
        page_data += page + '\n'
    
    f.write(page_data)
    f.close()

# Add data to existing file
def append_to_file(path, data):
    with open(path, 'a') as file:

        # Go trough all the links, writing them to a text file
        page_data = ""

        for page in data:
            page_data += page + '\n'

        file.write(page_data)

# Delete content of the file
def delete_file_content(path):
    with open(path, 'w'):
        pass

# Write and detect duplicates with a set (not a list)
def file_to_set(file_name):
    results = set()
    with open(file_name, 'rt') as f:
        for line in f:
            results.add(line.replace('\n', ''))
    return results

def file_to_array(file_name):
    results = []
    with open(file_name, 'rt') as f:
        for line in f:
            results.append(line)
    return results

def set_to_file(links, file_name):
    with open(file_name,"w") as f:
        for l in sorted(links):
            f.write(l+"\n")
