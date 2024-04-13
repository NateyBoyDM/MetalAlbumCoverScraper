import requests
from pathlib import Path
from PIL import Image
from bs4 import BeautifulSoup as bs
from colorama import Fore
import sys
import os

# Vars
searchStr = ""

albumName = ""
albumYear = ""
artistName = ""
filePath = ""
homeStr = ""
exportStr = ""
savedVersion = ""
onWindows = False

yes = "y"
enter = ""
no = "n"

fg = Fore.GREEN
fr = Fore.RED
res = Fore.RESET

reusePath = ""


def Album_Details():
    global albumName
    global artistName
    albumName = input("Please enter Album Name: ")
    artistName = input("Now, please enter the artist name: ")


def Home_Dir():
    global homeStr
    global onWindows

    homeYN = input(
        "Would you like to use your home directory as the beginning of the path, " + fg + "Y" + res + " or " +
        fr + "N" + res + "? (Ex, you'd only have " "to type Desktop to save the file) ")

    if homeYN.lower().strip() == yes or enter:
        home = Path.home()
        homeStrT = str(home) + "/"
        if ":" in homeStrT:
            onWindows = True
            homeStr = homeStrT
        else:
            homeStr = homeStrT
    elif homeYN == no:
        homeStr = ""


def File_Path():
    global filePath
    path = input("Where would you like the image to be saved? ")
    filePath = homeStr + path


def Album_Format():
    global searchStr
    global exportStr
    global filePath

    artistNameF = artistName.replace(' ', '_')
    albumNameF = albumName.replace(' ', '_')

    searchStr = (artistNameF + '/' + albumNameF)

    exportStrT = ""
    exportStr = ""

    imgStr = (artistName + " " + albumName + albumYear)

    if filePath.endswith("/"):
        exportStrT += filePath + imgStr + ".jpeg"
    else:
        filePath += "/"
        exportStrT += filePath + imgStr + ".jpeg"

    if onWindows:
        exportStr = exportStrT.replace("/", "\\")
    else:
        exportStr = exportStrT


def Url(multiple, version):
    url = 'https://www.metal-archives.com/albums/' + searchStr
    if multiple:
        url = url + "/" + version
    r = requests.get(url)
    soup = bs(r.content, 'html.parser')
    return soup


def Image_Scraper(soup):
    soupF = soup.find_all('a', {'id': 'cover'})

    def DownloadIMG():
        if soupF:
            for a in soupF:
                downloadImage = a['href']
                img = Image.open(requests.get(downloadImage, stream=True).raw)
                try:
                    img.save(exportStr, "JPEG")
                except:
                    makeDir = input("Directory " + filePath + " does not exist! Would you like to create this directory? "  + fg + "Y " + res + " or " +
        fr + "N " + res)
                    if makeDir == yes:
                        os.mkdir(filePath)
                        if savedVersion != "":
                            Restart_Scraper(True, savedVersion)
                        else:
                            Restart_Scraper(False, "")
                    else:
                        back = input("Would you like to reenter the path? "  + fg + "Y" + res + "or" +
        fr + "N" + res)
                        if back == yes:
                            Restart_Directory()
                        else:
                            sys.exit("Failed to save file to " + filePath + ".")
            return True
        else:
            return False

    if not DownloadIMG():
        soupM = soup.find_all('ul')
        if soupM:
            divTag = soup.find("div", {"id": "content_wrapper"})
            versionsList = divTag.find_all("li")
            versionNums = []
            versionYears = []

            print("There are multiple versions of this album listed. ")

            i = 1
            for version in versionsList:
                text = version.find_all('a')[0]
                versionNums.append(str(text).rsplit('"', 1)[0].rsplit('/', 1)[1])
                print(str(i) + ". " + version.text.strip().replace("\n", " "))
                versionYears.append(version.text.strip().split("in ", 1)[1].split(" by", 1)[0])
                i += 1

            selectedVersion = input(
                "Which version would you like to select? Please enter one of the numbers shown above. ")

            global savedVersion
            savedVersion = versionNums[int(selectedVersion) - 1]
            global albumYear
            albumYear = " " + versionYears[int(selectedVersion) - 1]
            Restart_Scraper(True, savedVersion)

        else:
            sys.exit(
                "No albums found! Maybe check https://www.metal-archives.com to see if the album you are looking for "
                "is listed in the database or under a different name... ")


def Restart_Directory():
    Home_Dir()
    File_Path()

def Restart_Scraper(versionNeeded, version):
    if versionNeeded:
        Album_Format()
        Image_Scraper(Url(True, version))
    else:
        Image_Scraper(Url(False, ""))


def Initial():
    Album_Details()
    Home_Dir()
    File_Path()
    Album_Format()
    Image_Scraper(Url(False, ""))


def Multiple(samePath):
    global albumYear
    albumYear = ""
    Album_Details()
    if not samePath:
        Home_Dir()
        File_Path()
    Album_Format()
    Image_Scraper(Url(False, ""))


Initial()

multiple = True
while multiple:
    endImgPrompt = input("Image saved to " + exportStr + "! Would you like to scrape another image? "
                         + fg + "Y" + res + " or " + fr + "N" + res + "? ")
    if endImgPrompt.lower().strip() == yes:
        samePath = input(
            "Would you like to use the previous file path? " + fg + "Y" + res + " or " + fr + "N" + res + "? ")
        if samePath.lower().strip() == yes:
            Multiple(True)
        else:
            Multiple(False)
    else:
        multiple = False
print("Thank you, have a nice day!")