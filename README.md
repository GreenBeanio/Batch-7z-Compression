# Batch 7z Compression

# What Does It Do?

This script will batch compress files and directories with 7z.

# How To Use It?

- Create a directory and place in all the files and directories you wish to compress.
  - This will individually compress each item (file or directory) in the directory.
    - It will not compress the main directory.
- When running the script pass the path to the directory with compression items inside of it as a python argument.
  - python3 batch_7z_compression.py "/path/holding/compression/directory/"

# Outputs

It will output a csv with statistics about the compressions. If you don't specify a path in the python script then it will use the current working directory.

# Running The Python Scripts

- You will need 7z installed on your machine.

### Windows

- Initial Run
  - cd /your/folder
  - python3 -m venv env
  - call env/Scripts/activate.bat
  - python3 -m pip install -r requirements.txt
  - python3 batch_7z_compression.py
- Running After
  - cd /your/folder
  - call env/Scripts/activate.bat && python3 batch_7z_compression.py
- Running Without Terminal Staying Around
  - Change the file type from py to pyw
  - You should just be able to click the file to launch it
  - May need to also change python3 to just python if it doesn't work after the change
    - In the first line of the code change python3 to python

### Linux

- Initial Run
  - cd /your/folder
  - python3 -m venv env
  - source env/bin/activate
  - python3 -m pip install -r requirements.txt
  - python3 batch_7z_compression.py
- Running After
  - cd /your/folder
  - source env/bin/activate && python3 batch_7z_compression.py
- Running Without Terminal Staying Around
  - Run the file with nohup
    - nohup python3 batch_7z_compression.py > /dev/null &
  - May have to set executable if it doesn't work
    - chmod +x batch_7z_compression.py
