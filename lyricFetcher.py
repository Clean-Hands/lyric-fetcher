import subprocess
from time import sleep
import requests
from bs4 import BeautifulSoup, element
import os
from os.path import exists
import re
import unicodedata
import mediaUpdater

# creates a .txt file with the lyrics as the content and the artist and song name as the title
def make_file(filename, lyrics_string):
    os.makedirs(os.path.dirname(filename), exist_ok=True)

    with open(filename, "w", encoding="utf-8") as f:
        f.write(lyrics_string)

# closes open lyrics and then opens the current lyrics in notepad
def update_lyric_display(filename):
    subprocess.call("taskkill /f /im notepad.exe", shell=True)
    subprocess.Popen(["notepad.exe", filename])

no_media = False
old_song_info = ""

while True:

    sleep(1)

    media_info = mediaUpdater.get_media_info()

    if media_info == None:
        if no_media == True:
            continue
        else:
            print("\nNo media is playing.")
            no_media = True
            continue
    else:
        no_media = False
    
    artist = media_info['artist']
    song = media_info['title']

    # remove features from the title of the song
    if " (feat." in song:
        song = song.split(" (feat.", 1)[0]
    if " (with" in song:
        song = song.split(" (with", 1)[0]

    # replace ampersands with "and"
    song = song.replace("&", "and")

    # remove all characters that are not whitespace nor letters
    artist = re.sub(r'[^\w\s]', '', artist)
    song = re.sub(r'[^\w\s]', '', song)

    # replace all accented characters with their non-accented counterparts
    artist = unicodedata.normalize('NFD', artist)\
                        .encode('ascii', 'ignore')\
                        .decode("utf-8")
    song = unicodedata.normalize('NFD', song)\
                      .encode('ascii', 'ignore')\
                      .decode("utf-8")

    # make all double/triple/etc. spaces only one space
    artist = re.sub(' +', ' ', artist)
    song = re.sub(' +', ' ', song)

    # replace all spaces with hyphens
    song_hyphen = song.replace(" ","-")
    artist_hyphen = artist.replace(" ","-")

    song_info = f"{artist_hyphen.lower()}-{song_hyphen.lower()}"

    filename = f".\lyrics\{song_info}.txt"

    if old_song_info == song_info:
        continue
    else:
        old_song_info = song_info
        if exists(filename):
            print(f"\nSONG: {song_info}")
            print("Lyrics are already downloaded.")
            update_lyric_display(filename)
            continue

    link = f"https://www.genius.com/{song_info}-lyrics"

    lyrics_array = []
    lyrics_string = ""

    print(f"\nSONG: {song_info}")
    print("Requesting lyrics...")

    response = requests.get(link)

    if str(response) == "<Response [404]>":
        print("Lyrics were unable to be fetched. It is possible that the song name on Genius" +
            " does not match the media's name, or maybe the current media does not have lyrics on Genius." +
            " A file will still be made to function as a placeholder.")
        make_file(filename, "Lyrics were unable to be fetched. It is possible that the song name on Genius" +
            " does not match the media's name, \nor maybe the current media does not have lyrics on Genius." +
            " A file has still been made to function as a placeholder.")
        update_lyric_display(filename)
        continue
    else:
        print("Lyrics successfully fetched.")

    print("Downloading lyrics...")

    soup = BeautifulSoup(response.content, "html.parser")

    lyrics = soup.find_all(class_="Lyrics__Container-sc-1ynbvzw-6 YYrds")

    if len(lyrics) == 0:
        lyrics = soup.find(class_="LyricsPlaceholder__Message-uen8er-3 jlYyFx")
        lyrics_string = lyrics.string

    else:
        for lyric in lyrics:
            for linebreak in lyric:
                linebreak_string = str(linebreak)
                linebreak_first_two = linebreak_string[:2]
                if linebreak_string[:2] == "<s":
                    continue
                if linebreak_string[:2] == "<b":
                    if lyrics_array[-1] == "\n":
                        try:
                            boolean = lyrics_array[-2] == "\n"
                        except:
                            lyrics_array.append("\n")
                        else:
                            if boolean:
                                lyrics_array.append("\n")
                    else:
                        lyrics_array.append("\n")

                elif linebreak_string[:2] == "<a":
                    linebreak_split = str(linebreak.find_all("span"))
                    linebreak_split = linebreak_split.split(">")
                    for item in linebreak_split:
                        item2 = item.split("<", 1)[0]
                        if item2 not in {"[", "]", ""}:
                            # print(item)
                            lyrics_array.append(item2)
                        if item.endswith("<br/") and lyrics_array[-1] != "\n":
                            lyrics_array.append("\n")
                else:
                    if type(linebreak) == element.Tag:
                        # print(linebreak.text)
                        linebreak_split = linebreak_string.split(">")
                        for item in linebreak_split:
                            item2 = item.split("<", 1)[0]
                            if item2 not in {"[", "]", ""}:
                                # print(item)
                                lyrics_array.append(item2)
                            if item.endswith("<br/") and lyrics_array[-1] != "\n":
                                lyrics_array.append("\n")
                        # lyrics_array[-1] = lyrics_array[-1] + linebreak.text + "{"
                        continue
                    else:
                        lyrics_array.append(linebreak)

        lyrics_iter = iter(lyrics_array)

        for item in lyrics_iter:
            if item == "":
                continue
            else:
                if item[-1] == "(":
                    item = item + next(lyrics_iter, "") + next(lyrics_iter, "")
                if item[0] == "[":
                    item = "\n" + item
                if item[-1] == "{":
                    item = item[:-1]
                    test = next(lyrics_iter, "")
                    item += test

            # item = item + "\n"
            lyrics_string += item

    # print(lyrics_string)
    print("Lyrics downloaded.")
    print("Saving lyrics as a .txt file...")
    
    make_file(filename, lyrics_string)
    print("Lyrics saved.")

    update_lyric_display(filename)