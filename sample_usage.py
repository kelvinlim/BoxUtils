#! /usr/bin/env python

import os

"""
Sample usage of the BoxUtils package

"""
import BoxUtils

# Create a BoxUtils object
# be sure that the .jwt.env and .jwt.config.json files 
# are in the same directory as this script
box_utils = BoxUtils.BoxUtils()

# create a folder testfolder in the root folder
# can change the parent folder id to create the folder in a different folder
parent_folder = '0' # set to the root folder
folder_name = 'testfolder'
results = box_utils.create_folder(parent_folder, folder_name)
test_folder_id = results.id
print(f"Created folder {folder_name} with id {test_folder_id}")

# create several local files
local_files = ['hello.txt', 'hello2.txt', 'hello3.txt']
for local_file in local_files:
    with open(local_file, 'w') as f:
        f.write('hello')
        
# upload these files to the test folder
for local_file in local_files:
    results = box_utils.upload_file(local_file, test_folder_id)
    # message
    print(f"Uploaded {local_file} to folder {test_folder_id}")
    
# download the last uploaded file into a new file
file_id = results.id
box_utils.download_file(file_id, 'hello12345.txt')
print(f"Downloaded file {file_id} to hello12345.txt")

# delete a folder, should fail since there is a file in the folder
folder_id_delete = test_folder_id
results = box_utils.delete_folder(folder_id_delete)

# delete the files we uploaded so that we can delete the directory
if results == False:
    print("Folder delete failed, deleting files")
    # get the items in the folder
    items = box_utils.list_folder(test_folder_id)
    # delete the files we uploaded
    for item in items.entries:
        if item.type == 'file':
            box_utils.delete_file(item.id)
            print(f"Deleted file {item.id}")

# now can delete folder since it is empty
folder_id_delete = test_folder_id
results = box_utils.delete_folder(folder_id_delete)
if results:
    print(f"Deleted folder {folder_id_delete}")
    
# clean up the local files we created
local_files.append('hello12345.txt')
for local_file in local_files:
    os.remove(local_file)
