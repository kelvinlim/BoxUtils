#! /usr/bin/env python

import os
import argparse
import textwrap
from pprint import pprint
import json
from datetime import datetime

__version_info__ = ('1', '0', '3')
__version__ = '.'.join(__version_info__)

version_history = \
"""
1.0.3 - change result of list_folder to a list of items instead of box class
        This was done to support pagination for folders with more than 1000 items, 
        which is the limit fo the Box API. 

        This introduces a breaking change in the API. The list_folder method 
        now returns a list of items instead of a box class. Instead of using the box class,
        you  now use the list of items to access the properties of the items in the folder.

        Example usage:
        # get the items in the folder
        items = box_utils.list_folder(test_folder_id)
        # delete the files we uploaded
        for item in items:   # use items instead of items.entries
            if item.type == 'file':
                box_utils.delete_file(item.id)
                print(f"Deleted file with name {item.name} and id {item.id}")

1.0.2 - removed extraneous cmd option
1.0.1 - fixed bug in parent folder, pass arguments for env and config
1.0.0 - initial version  
"""

"""
Sample usage of the BoxUtils package

"""
from box_utils import BoxUtils

def test_box_api(env: str, config: str, pattern = "*.txt", parent_folder:str ='0'):
    
    """
    Exercise the BoxUtils API
    
    Args:
    
    """
    # Create a BoxUtils object
    # be sure that the .jwt.env and .jwt.config.json files 
    # are in the same directory as this script
    box_utils = BoxUtils(env=env, config=config)

    folder_name = 'mainfolder'
    results = box_utils.create_folder(parent_folder, folder_name)
    main_folder_id = results.id
    main_folder_name = results.name

    print(f"Created main folder {main_folder_name} with id {main_folder_id}")

    folder_name = 'testfolder'
    results = box_utils.create_folder(main_folder_id, folder_name)
    test_folder_id = results.id
    test_folder_name = results.name

    print(f"Created test folder {test_folder_name} with id {test_folder_id}")


    # create several local files
    local_files = ['hello.txt', 'hello1.txt', 'hello2.txt', 'hello3.txt']
    for local_file in local_files:
        with open(local_file, 'w') as f:
            f.write('hello')
        print(f"Created local file {local_file}")
    
    # upload first file to the main_folder
    results = box_utils.upload_file(local_files[0], main_folder_id)
    # message
    print(f"Uploaded {local_files[0]} with to folder {main_folder_name}")  
      
    # upload these files to the test folder
    for local_file in local_files[1:]:
        results = box_utils.upload_file(local_file, test_folder_id)
        # message
        print(f"Uploaded {local_file} with id {results.id} to folder {test_folder_id}")
        uploaded_file_id = results.id
        pass

    print(f"Recursively index folder {parent_folder}")
    start_time = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    folder_contents = box_utils.index_folder_recursively(parent_folder)
    end_time = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    # get list of the files that contain pattern
    file_list = box_utils.search_items(pattern)
    print(f"file items that contain {pattern}")
    pprint(file_list)

    print(f"start: {start_time}")
    print(f"end:   {end_time}")
    
    # save file output to a file
    datestr = datetime.now().strftime("%Y%m%d_%H%M")
    out_file = f"filelist_{datestr}.json"
    with open(out_file,'w') as fp:
        json.dump(file_list, fp, indent=4)
        
    # download the last uploaded file into a new file
    file_id = results.id
    box_utils.download_file(uploaded_file_id, 'hello12345.txt')
    print(f"Downloaded file {uploaded_file_id} to hello12345.txt")

    # delete a folder, should fail since there is a file in the folder
    folder_id_delete = test_folder_id
    results = box_utils.delete_folder(folder_id_delete)

    # delete the files we uploaded so that we can delete the directory
    if results == False:
        print(f"Folder {test_folder_name} delete failed, deleting files")
        # get the items in the folder
        items = box_utils.list_folder(test_folder_id)
        # delete the files we uploaded
        for item in items:
            if item.type == 'file':
                box_utils.delete_file(item.id)
                print(f"Deleted file with name {item.name} and id {item.id}")

    # now can delete folder since it is empty
    folder_id_delete = test_folder_id
    results = box_utils.delete_folder(folder_id_delete)
    if results:
        print(f"Deleted folder {test_folder_name} id {folder_id_delete}")

        
    # clean up the local files we created
    local_files.append('hello12345.txt')
    for local_file in local_files:
        os.remove(local_file)
        print(f"Deleted local file: {local_file}")
        
    # get the information for the file main_folder/hello.txt
    file_list = box_utils.search_items("*/hello.txt")

    # delete the files in main_folder
    for file in file_list:
        if file['type'] == 'file':
            results = box_utils.delete_file(file['box_id'])
            print(f"Deleted file with name {file['name']} and id {file['box_id']}")        
        
    # delete the main_folder
    results = box_utils.delete_folder(main_folder_id)
    
    if results:
        print(f"Deleted folder {main_folder_name} id {main_folder_id}")    
        
if __name__ == "__main__":
    
    # provide a description of the program with format control
    description = textwrap.dedent('''\
    
    Exercise the BoxUtils API
    
    Requires two files.
    
    box.env - contains the following settings    
    # JWT Settings
    JWT_USER_ID = 397xxx
    ENTERPRISE_ID = 686xxx
    
    box.config.json - contains the following settings
    downloaded from the Box developer console.
    
    # Sample app configuration file
    {
        "boxAppSettings": {
        "clientID": "1u3gto5in5gff7ve8031tx8x6kl8xxxx",
        "clientSecret": "********************************",
        "appAuth": {
            "publicKeyID": "",
            "privateKey": "",
            "passphrase": ""
        }
        },
        "enterpriseID": "686XXX"
    }
    
    ''')
    
    parser = argparse.ArgumentParser(
        description=description, formatter_class=argparse.RawTextHelpFormatter)

    parser.add_argument("--folder", type = str,
                     help="box id of folder to operate on, default 0",
                      default="0") 

    parser.add_argument("--env", type = str,
                     help="name of env file in the current directory, default box.env",
                      default="box.env") 

    parser.add_argument("--config", type = str,
                     help="name of json config file in the current directory, default box.config.json",
                      default="box.config.json") 

    parser.add_argument("--pattern", type = str,
                     help="pattern to use for file search, default *.txt",
                      default="*.txt")
        
    parser.add_argument("-H", "--history", action="store_true", help="Show program history")
     
    
    parser.add_argument("--verbose", type=int, help="verbose level default 2",
                         default=2) 
        
    parser.add_argument('-V', '--version', action='version', version=f'%(prog)s {__version__}')

    args = parser.parse_args()
        
    if args.history:
        print(f"{os.path.basename(__file__) } Version: {__version__}")
        print(version_history)
        exit(0)
        
    # call the test function
    test_box_api(parent_folder=args.folder, env = args.env, config=args.config, pattern=args.pattern)

