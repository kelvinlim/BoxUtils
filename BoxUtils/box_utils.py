"""
Handles the box client object creation
orchestrates the authentication process
"""

import argparse
import glob
import sys
import json
from pathlib import Path
import textwrap
import shutil

from dotenv import dotenv_values  # pip install python-dotenv
import os
import logging
import dotenv
from box_sdk_gen import (
    BoxClient,
    BoxJWTAuth,
    FileWithInMemoryCacheTokenStorage,
    JWTConfig,
)

from box_sdk_gen import BoxAPIError
from box_sdk_gen.client import BoxClient as Client
from box_sdk_gen.schemas import File, Files
from box_sdk_gen.managers.files import CopyFileParent
from box_sdk_gen.managers.uploads import (
    PreflightFileUploadCheckParent,
    UploadFileAttributes,
    UploadFileAttributesParentField,
)
from box_sdk_gen.managers.zip_downloads import CreateZipDownloadItems
from box_sdk_gen import ByteStream

from box_sdk_gen.schemas import Folder, FolderMini, FileMini, WebLinkMini
from box_sdk_gen.managers.folders import Items, CreateFolderParent

__version_info__ = ('0', '1', '0')
__version__ = '.'.join(__version_info__)

version_history = \
"""
0.1.0 - initial version  
"""

ENV_JET = ".jwt.env"

logging.basicConfig(level=logging.INFO)
logging.getLogger("box_sdk_gen").setLevel(logging.CRITICAL)



class ConfigJWT:
    """application configurations"""

    def __init__(self) -> None:
        dotenv.load_dotenv(ENV_JET)

        # JWT configurations
        self.jwt_config_path = os.getenv("JWT_CONFIG_PATH")
        self.jwt_user_id = os.getenv("JWT_USER_ID")
        self.enterprise_id = os.getenv("ENTERPRISE_ID")

        self.cache_file = os.getenv("CACHE_FILE", ".jwt.tk")

    def __repr__(self) -> str:
        return f"ConfigJWT({self.__dict__})"


    def get_jwt_enterprise_client(self, config) -> BoxClient:
        """Returns a box sdk Client object"""

        jwt = JWTConfig.from_config_file(
            config_file_path=config.jwt_config_path,
            token_storage=FileWithInMemoryCacheTokenStorage(".ent" + config.cache_file),
        )
        auth = BoxJWTAuth(jwt)

        client = BoxClient(auth)

        return client


    def get_jwt_user_client(self, config, user_id: str) -> BoxClient:
        """Returns a box sdk Client object"""

        jwt = JWTConfig.from_config_file(
            config_file_path=config.jwt_config_path,
            token_storage=FileWithInMemoryCacheTokenStorage(".user" + config.cache_file),
        )
        auth = BoxJWTAuth(jwt)
        auth = auth.with_user_subject(user_id)

        client = BoxClient(auth)

        return client
    
class BoxUtils:
    
    def __init__(self, **kwargs):
        
        # load self.config
        self.config = {}
        for key, value in kwargs.items():
            self.config[key] = value

        # read in .env file
        if 'env' in self.config:
            self.config.update(dotenv_values(self.config['env']))
        
        if 'config' in self.config:
            # Open and read the YAML file
            with open(self.config['config'], 'r') as file:
                data = json.load(file)
                self.config.update(data)

        self.client = self.setup_box_client()
        
        # list a folder
        folder_id = '306368557395' # BoxAPITest
        self.test_cmd( args.cmd,folder_id=folder_id)
        pass
    
    def setup_box_client(self):
        """setup the box client"""
        config = ConfigJWT()
        client = config.get_jwt_enterprise_client(config)
        return client   
    
    def test_cmd(self, cmd: str, **kwargs):
        """
        different test commands
        """
        if cmd == 'test':
            # need the folder_id
            folder_id = kwargs.get('folder_id', '0')
            items = self.list_folder(folder_id)
            print(f"\nFolder {folder_id} has {len(items.entries)} items")
            for item in items.entries:
                print(f"{item.name} [{item.id},{item.type}]")

            # get file details
            file_id = '1771382171648' # hello.txt
            file_info = self.get_file_details(file_id)
            
            # download a file
            self.download_file(file_id, 'hello12345.txt')
            
            # create a folder
            folder_name = 'testfolder'
            results = self.create_folder(folder_id, folder_name)
            new_folder_id = results.id
                        
            # upload a file
            local_path = 'hellotest.txt'
            results = self.upload_file(local_path, new_folder_id)
            new_file_id = results.id
            
            # delete a folder, should fail since there is a file in the folder
            folder_id_delete = new_folder_id
            results = self.delete_folder(folder_id_delete)
            
            # delete the file we uploaded
            file_id_delete = new_file_id
            self.delete_file(file_id_delete)
            pass
        
            # now can delete folder since it is empty
            folder_id_delete = new_folder_id
            results = self.delete_folder(folder_id_delete)
            
        pass
    def list_folder(self, folder_id):
        """
        Lists items in a folder.
        
        Args:
            folder_id (str): The ID of the folder to list.
        
        https://github.com/box-community/box-python-gen-workshop/blob/main/workshops/files/files.md
        
        """
        try:
            items = self.client.folders.get_folder_items(folder_id)
            return items
        except Exception as e:
            print(f"Error listing folder: {e}")
            return None

    def create_folder(self, parent_folder_id, folder_name):
        """
        Creates a new folder within a parent folder.
        
        https://github.com/box-community/box-python-gen-workshop/blob/main/workshops/folders/folders.md
        
        Args:
            parent_folder_id (str): The ID of the parent folder.
            folder_name (str): The name of the new folder.
        """
        try:
            parent_arg = CreateFolderParent(parent_folder_id)
            folder = self.client.folders.create_folder(
                folder_name,
                parent_arg,
            )
        except BoxAPIError as box_err:
            if box_err.response_info.body.get("code", None) == "item_name_in_use":
                box_folder_id = box_err.response_info.body["context_info"][
                    "conflicts"
                ][0]["id"]
                folder = self.client.folders.get_folder_by_id(box_folder_id)
            else:
                raise box_err

        # logging.info("Folder %s with id: %s", folder.name, folder.id)
        return folder
    
    def delete_folder(self, folder_id, recursive=False):
        """
        Deletes a folder.
        
        Args:
            folder_id (str): The ID of the folder to delete.
            recursive (bool): Whether to delete the folder recursively.
        """
        try:
            self.client.folders.delete_folder_by_id(folder_id, recursive=recursive)            
            print(f"Folder '{folder_id}' deleted.")
            return True
        except BoxAPIError as err:
            if err.response_info.body.get("code", None) == "folder_not_empty":
                logging.info(
                    f"Folder {folder_id} is not empty"
                )
                # # print(f"Folder {tmp.name} is not empty, deleting recursively")
                # try:
                #     client.folders.delete_folder_by_id(folder_id, recursive=True)
                # except BoxAPIError as err_l2:
                #     raise err_l2
        except Exception as e:
            print(f"Error deleting folder: {e}")
        
        return False
        
    def download_file(self, file_id: str, local_path_to_file: str):
        """
        Download a file from Box
        
        Args:
            file_id (str): ID of the file to download
            local_path_to_file (str): Local path to save
        
        """
        file_stream: ByteStream = self.client.downloads.download_file(file_id)

        with open(local_path_to_file, "wb") as file:
            shutil.copyfileobj(file_stream, file)

    def upload_file(self, file_path: str, folder_id: str) -> File:
        """
        Upload a file to a Box folder
        
        Args:
            file_path (str): Path to the file to upload
            folder_id (str): ID of the folder to upload the file to
        """

        file_size = os.path.getsize(file_path)
        file_name = os.path.basename(file_path)

        try:
            # pre-flight check

            pre_flight_arg = PreflightFileUploadCheckParent(id=folder_id)
            self.client.uploads.preflight_file_upload_check(name=file_name, size=file_size, parent=pre_flight_arg)

            # upload new file
            upload_arg = UploadFileAttributes(file_name, UploadFileAttributesParentField(folder_id))
            files: Files = self.client.uploads.upload_file(upload_arg, file=open(file_path, "rb"))

            box_file = files.entries[0]
        except BoxAPIError as err:
            if err.response_info.body.get("code", None) == "item_name_in_use":
                logging.warning("File already exists, updating contents")
                box_file_id = err.response_info.body["context_info"]["conflicts"]["id"]
                try:
                    # upload new version

                    upload_arg = UploadFileAttributes(file_name, UploadFileAttributesParentField(folder_id))
                    files: Files = self.client.uploads.upload_file_version(
                        box_file_id, upload_arg, file=open(file_path, "rb")
                    )

                    box_file = files.entries[0]
                except BoxAPIError as err2:
                    logging.error("Failed to update %s: %s", box_file.name, err2)
                    raise err2
            else:
                raise err

        return box_file


    def delete_file(self, file_id):
        """Deletes a file."""
        try:
            self.client.files.delete_file_by_id(file_id)
            print(f"File '{file_id}' deleted.")
            return True
        except Exception as e:
            print(f"Error deleting file: {e}")
            return False

    def get_file_details(self, file_id):
        """Gets details of a file (size, type, etc.)."""
        try:
            file_info = self.client.files.get_file_by_id(file_id)
            # name
            # id
            return file_info
        except Exception as e:
            print(f"Error getting file details: {e}")
            return None


if __name__ == "__main__":
    
    # provide a description of the program with format control
    description = textwrap.dedent('''\
    A description of the program goes here.
    
    Account information is read from a .env file which contains the 
    APITOKEN, DATACENTER and DIRECTORYID.
    
    Here are some examples of using the command. Text following the $ is
    the command that is entered at the command line in a terminal window.
    
    $ LNPIQualtrics
    Without any arguments, the mailingLists are listed with their index. 
    ''')
    
    parser = argparse.ArgumentParser(
        description=description, formatter_class=argparse.RawTextHelpFormatter)

    parser.add_argument("--env", type = str,
                     help="name of env file in the current directory, default .jwt.env",
                      default=".jwt.env") 

    parser.add_argument("--config", type = str,
                     help="name of json config file in the current directory, default .jwt.config.json",
                      default=".jwt.config.json") 
        
    parser.add_argument("--cmd", type = str,
                    help="cmd -  default test",
                    default = 'test')

    parser.add_argument("-H", "--history", action="store_true", help="Show program history")
     
    # parser.add_argument("--quiet", help="Don't output results to console, default false",
    #                     default=False, action = "store_true")  
    
    parser.add_argument("--verbose", type=int, help="verbose level default 2",
                         default=2) 
        
    parser.add_argument('-V', '--version', action='version', version=f'%(prog)s {__version__}')

    args = parser.parse_args()
            
    if args.history:
        print(f"{os.path.basename(__file__) } Version: {__version__}")
        print(version_history)
        exit(0)

    obj = BoxUtils(     cmd=args.cmd, 
                        verbose=args.verbose, 
                        config=args.config,
                        env=args.env,
                    )