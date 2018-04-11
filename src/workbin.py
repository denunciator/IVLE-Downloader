import requests
import os
import config
import re


# given a file, download it to the specified path
def downloadFile(efile, path, token):
    if efile['isDownloaded']:
        return

    print ("Downloading file: " + efile['FileName'])
    fileid = efile['ID']
    url = config.downloadurl
    payload = {'APIKey': config.APIKey, 'AuthToken': token, 'ID': fileid, 'target': 'workbin'}
    response = requests.get(url, params=payload, stream=True)

    fpath = os.path.join(path, efile['FileName'])
    fhandler = open(fpath, 'wb')
    fhandler.write(response.content)


# given a path, create the directory
def makedir(path):
    if not os.path.exists(path):
        os.makedirs(path)


# given a folder, download files contained, and traverse subfolders recursively
def traverseFolder(folder, path, token):
    files = folder['Files']
    for eachfile in files:
        downloadFile(eachfile, path, token)

    subfolders = folder['Folders']
    for subfolder in subfolders:
        folderName = re.sub(r'\\|/|\*|"|\?|:|\||<|>', "-", subfolder['FolderName'])
        subpath = os.path.join(path, folderName)
        makedir(subpath)
        traverseFolder(subfolder, subpath, token)


# given a workbin, create subdirs for its folders, and traverse each folder
def traverseWorkBin(wbin, path, token):
    folders = wbin['Folders']
    for folder in folders:
        folderName = re.sub(r'\\|/|\*|"|\?|:|\||<|>', "-", folder['FolderName'])
        fpath = os.path.join(path, folderName)
        makedir(fpath)
        traverseFolder(folder, fpath, token)


def getFiles(modules, token):
    url = config.hosturl + "Workbins"
    payload = {'APIKey': config.APIKey, 'AuthToken': token, 'Duration': '0', 'TitleOnly': 'false'}

    for module in modules:
        name = re.sub(r'\\|/|\*|"|\?|:|\||<|>', "-", module['CourseCode'])

        if name in config.exclude:
            print ("Skipping module " + name + "...\n")
            continue

        path = os.path.join(config.filepath, name)
        makedir(path)

        print ("Downloading for module " + name + "...")

        payload['CourseID'] = module['ID']
        response = requests.get(url, params=payload)

        data = response.json()

        # list the workbins of each module
        workbins = data['Results']
        print (str(len(workbins)) + " workbin(s) found")

        if len(workbins) > 1:  # if there are more than one workbin, create a folder for each workbin
            for wbin in workbins:
                wbinpath = os.path.join(path, wbin['Title'])
                makedir(wbinpath)
                traverseWorkBin(wbin, wbinpath, token)
        else:  # otherwise, just download directly to the module folder
            for wbin in workbins:
                traverseWorkBin(wbin, path, token)

        print ("")
