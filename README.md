# BoxUtils

A class using the box_sdk_gen python SDK for doing basic file and folder operations.

## Configuration Info Locations



Key information is stored in the developer console for the selected app in Platform Apps.

The User ID and Enterprise ID is found on the General. Settings/App Info section.

The service account which folders/files should be shared with is located on the General Settings/Service Account Info section.

The app configuration json file can be downloaded under the Configuration/App Settings section.

Two files are required for initialization of the class

1. box.env - contains information about  the JWT user id and the enterprise id

  ```
  # JWT Settings
  JWT_USER_ID = 397515XXXX
  ENTERPRISE_ID = 686XXX
  ```

2. box.config.json - contains the JWT credentials. This is downloaded from the box dev console.

  ```
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
  ```

## Sample usage

You can find the full sample usage script in the [sample_usage.py](sample_usage.py) file.


## For package creation and publishing

Be sure to update the setup.py with version information.

```bash
# create the dist
python -m build

# upload the package
# credentials for pypi.org are kept in ~/.pypirc
twine upload dist/*

```
