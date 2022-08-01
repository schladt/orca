# quick and dirty scrip to collect exe files from a windows host for sample analysis
# this script will search the filesystem for any windows PE less than 20 MB and copy to the provided destination

import os
# from winmagic import magic
import shutil

target_dir = os.path.join('z:\\', 'bin')

for root, dirs, files in os.walk("C:\\"):
    for name in files:
        filename=os.path.join(root, name)
        try:
            # filetype = magic.from_file(filename)
            filesize = os.path.getsize(filename)
            ext = filename.split('.')[-1].lower()
            # if 'pe32' in filetype.lower() and filesize < 20000000 and (ext=='dll' or ext=='exe'):
            if filesize < 20000000 and (ext=='dll' or ext=='exe'):
                print(f'Found {filename} with type {ext} and size {filesize}')
                target_path = os.path.join(target_dir, name)
                shutil.copyfile(filename, target_path)

        except:
            pass # ignore errors (mostly permissions)