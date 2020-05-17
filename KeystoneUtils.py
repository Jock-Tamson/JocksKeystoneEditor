from ColorDictionary import STANDARD_COLOR_DICTIONARY
import os
import threading
import sys
from tkinter import messagebox

OpenLinkedFileCallback = None

#strip outer quotes.  Had to not use strip to avoid removing consecutive "" from the end
def RemoveOuterQuotes(val: str) -> str:
    if (len(val) < 2):
        return val
    result = val.lstrip()
    if (result[0] == '\"'):
        result = result.rstrip()
        if (result[-1] == '\"'):
            result = result[1:]
            result = result[:-1]
            return result
    return val

#From a string containing <code value> elements find code and return value
#returns "" if code not found
def ParseBracketedCodes(val: str, code: str) -> str:
    result = ""
    start = val.find("<" + code)
    if (start >= 0):
        end = val.find(">", start)
        parts = val[start:end].split(" ")
        if (len(parts) > 1):
            result = parts[1]
    return result

def ReverseDictionaryLookup(dict, val) -> str:
    for item in [p for p in dict.items() if (p[1] == val)]:
        val = item[0]
    return val

def ReverseColorLookup(val) -> str:
    return ReverseDictionaryLookup(STANDARD_COLOR_DICTIONARY, val)


#Take two color values and return the first averaged by X% of the second where X is an int between 0 and 100
def AverageRGBValues(val1: str, val2: str, avg: int = 50) -> str:
    if (not val1.startswith("#")):
        val1 = STANDARD_COLOR_DICTIONARY[val1]
    if (not val2.startswith("#")):
        val2 = STANDARD_COLOR_DICTIONARY[val2]
    r1 = int("0x" + val1[1:3],0)
    g1 = int("0x" + val1[3:5],0)
    b1 = int("0x" + val1[5:7],0)
    r2 = int("0x" + val2[1:3],0)
    g2 = int("0x" + val2[3:5],0)
    b2 = int("0x" + val2[5:7],0)
    pct = avg/100
    r = int((r1 * (1 - pct)) + (r2 * pct))
    g = int((g1 * (1 - pct)) + (g2 * pct))
    b = int((b1 * (1 - pct)) + (b2 * pct))
    return "#%2.2X%2.2X%2.2X" % (r,g,b)

def GetFileName(filePath: str) -> str:
    filePath = os.path.abspath(filePath)
    directory, fileName = os.path.split(filePath)
    directory = directory #Makes warnings happy
    return fileName

def GetUniqueFilePath(filePath: str, seed: int = 1, paranthetical: bool = True, usedNames: list = None) -> str:
    filePath = os.path.abspath(filePath)
    directory, origFileName = os.path.split(filePath)
    origFileName, extension = os.path.splitext(origFileName)
    fileName = origFileName
    idx = seed
    while os.path.exists(filePath) or ((usedNames != None) and (usedNames.__contains__(fileName))):      
        if (paranthetical):
            add = "(%d)" % idx
        else:
            add = "%d" % idx
        fileName = origFileName + add + extension
        filePath = os.path.join(directory, fileName)
        idx = idx + 1
    return filePath

#returns path from root path
def GetDirPathFromRoot(rootPath, fullPath) -> str:
    rootPath = os.path.abspath(rootPath)
    fullPath = os.path.abspath(fullPath)
    if (rootPath != fullPath):
        dirName = fullPath.replace(rootPath, "")
        if (dirName[0] == '\\'):
            dirName = dirName[1:]
        if (dirName[-1] == '\\'):
            dirName = dirName[:-1]
        return dirName
    else:
        return '.'

def SetOpenLinkedFileCallback(callback):
    global OpenLinkedFileCallback
    OpenLinkedFileCallback = callback

def TriggerOpenLinkedFileCallback(path):
    global OpenLinkedFileCallback
    if (OpenLinkedFileCallback != None):
        t =  threading.Thread(name='openlinkedfilecallback_'+ path, target=OpenLinkedFileCallback, args=(path, )) 
        t.start()

#https://shanetully.com/2013/08/cross-platform-deployment-of-python-applications-with-pyinstaller/
def GetResourcePath(relativePath)->str:
    try:
        basePath = sys._MEIPASS
    except Exception:
        basePath = ''

    path = os.path.join(basePath, relativePath)

    if not os.path.exists(path):
        return None

    return path

def NameForMatch(name)->str:

    if (name == None):
        return None

    #ignore whitespace
    name = name.strip()

    #don't match blank strings
    if (name == ""):
        return None
    
    #case doesn't matter
    name = str.upper(name)

    #underscores don't matter
    if (len(name) > 1):
        name = name.replace("_", "")

    return name

def MatchKeyName(compName, nameList)->[str, str, str]:
    matchName = NameForMatch(compName)
    if (matchName == None):
        return None
    matches = [[name, alt_name, desc] for name, alt_name, desc in nameList if ((matchName == NameForMatch(name)) or (matchName == NameForMatch(alt_name)))]
    if (len(matches) > 0):
        return matches[0]
    else:
        return None

    
