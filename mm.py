import os

# each website is separate project
def create_project_dir(directory):
    if not os.path.exists(directory):
        print('Creating project '+ directory)
        os.makedirs(directory)

# create queue and crawled files
def create_data_files(project_name, base_url):
    queue = project_name + '/queue.txt'
    crawled = project_name + '/crawled.txt'
    
    if not os.path.isfile(queue):
        write_file(queue, base_url)

    if not os.path.isfile(crawled):
        write_file(crawled, '')
    
# create new file    
def write_file(path, data):
    f = open(path, 'w')
    f.write(data)
    f.close()

# add data to existing file
def append_to_file(path, data):
    with open(path, 'a') as file:
        file.write(data + '\n')

# delete content of the file
def delete_file_content(path):
    with open(path, 'w'):
        pass

# write and detect duplicates with a set (not a list)
def file_to_set(file_name):
    results = set()
    with open(file_name, 'rt') as f:
        for line in f:
            results.add(line.replace('\n', ''))
    return results

def set_to_file(links, file_name):
    with open(file_name,"w") as f:
        for l in sorted(links):
            f.write(l+"\n")