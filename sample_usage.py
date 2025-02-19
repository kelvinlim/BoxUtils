#! /usr/bin/env python

import os
import argparse
import textwrap

__version_info__ = ('1', '0', '0')
__version__ = '.'.join(__version_info__)

version_history = \
"""
1.0.0 - initial version  
"""

"""
Sample usage of the BoxUtils package

"""
import BoxUtils

def test_box_api(parent_folder:str ='0'):
    
    """
    Exercise the BoxUtils API
    
    Args:
    
    """
    # Create a BoxUtils object
    # be sure that the .jwt.env and .jwt.config.json files 
    # are in the same directory as this script
    box_utils = BoxUtils.BoxUtils()

    # create a folder testfolder in the root folder
    # can change the parent folder id to create the folder in a different folder
    parent_folder = '0' # set to the root folder
    parent_folder = '306368557395'

    folder_name = 'testfolder'
    results = box_utils.create_folder(parent_folder, folder_name)
    test_folder_id = results.id
    test_folder_name = results.name

    print(f"Created folder {test_folder_name} with id {test_folder_id}")

    # create several local files
    local_files = ['hello.txt', 'hello2.txt', 'hello3.txt']
    for local_file in local_files:
        with open(local_file, 'w') as f:
            f.write('hello')
            
    # upload these files to the test folder
    for local_file in local_files:
        results = box_utils.upload_file(local_file, test_folder_id)
        # message
        print(f"Uploaded {local_file} with id {results.id} to folder {test_folder_id}")
        pass

    # download the last uploaded file into a new file
    file_id = results.id
    box_utils.download_file(file_id, 'hello12345.txt')
    print(f"Downloaded file {file_id} to hello12345.txt")

    # delete a folder, should fail since there is a file in the folder
    folder_id_delete = test_folder_id
    results = box_utils.delete_folder(folder_id_delete)

    # delete the files we uploaded so that we can delete the directory
    if results == False:
        print(f"Folder {test_folder_name} delete failed, deleting files")
        # get the items in the folder
        items = box_utils.list_folder(test_folder_id)
        # delete the files we uploaded
        for item in items.entries:
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
        print(f"Deleted temporary file: {local_file}")


if __name__ == "__main__":
    
    # provide a description of the program with format control
    description = textwrap.dedent('''\
    
    Exercise the BoxUtils API
    
 
    ''')
    
    parser = argparse.ArgumentParser(
        description=description, formatter_class=argparse.RawTextHelpFormatter)

    parser.add_argument("--folder", type = str,
                     help="box id of folder to operate on, default 0",
                      default="0") 

    parser.add_argument("--env", type = str,
                     help="name of env file in the current directory, default .env",
                      default=".env") 

    parser.add_argument("--config", type = str,
                     help="name of json config file in the current directory, default config.json",
                      default="config.json") 
        
    parser.add_argument("--cmd", type = str,
                    help="cmd - [list, summarize], default list",
                    default = 'list')
    
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
    test_box_api(parent_folder=args.folder)

