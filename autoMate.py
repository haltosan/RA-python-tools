import os
import shutil
import glob

workingDir = r'V:\FHSS-JoePriceResearch\RA_work_folders\Ethan_Simmons\WeldImages'
os.chdir(workingDir)


def fname(file: str) -> str:
    """Returns file's name from a path string"""
    return file.split(os.sep)[-1]

def ffolder(file: str) -> str:
    """Returns file's folder from a path string"""
    return ''.join( file.split(os.sep)[:-1] )

def bulkCopy(files: list, destFolder: str):
    """Copy files indicated in files list to destination folder"""
    for file in files:
        shutil.copy2(file, destFolder)

def rename(files: list, destFolder: str, renameFunction):
    """Renames all files in the list depending on the rename function\
This moves files to the new location and renames them there
The rename function replaces the file name and is passed the original file path"""
    for file in files:
        shutil.copy2(file, destFolder)
        newFile = os.path.join(destFolder, fname(file))
        os.rename(newFile, os.path.join(ffolder(newFile),renameFunction(file)))
