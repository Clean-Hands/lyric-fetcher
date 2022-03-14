from fileinput import filename
import requests
from bs4 import BeautifulSoup, element
import os
import sys

artist = sys.argv[1]
song = sys.argv[2]

# artist = "ajr"
# song = "weak"

song_hyphen = song.replace(" ","-")
artist_hyphen = artist.replace(" ","-")

song_info = f"{artist_hyphen}-{song_hyphen}"

link = f"https://www.genius.com/{song_info}-lyrics"

lyrics_array = []
lyrics_string = ""

response = requests.get(link)
soup = BeautifulSoup(response.content, "html.parser")

lyrics = soup.find_all(class_="Lyrics__Container-sc-1ynbvzw-6 jYfhrf")

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
                item2 = item.split("<")[0]
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
                    item2 = item.split("<")[0]
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

print(lyrics_string)

filename = f".\{song_info}.txt"

os.makedirs(os.path.dirname(filename), exist_ok=True)

with open(filename, "w", encoding="utf-8") as f:
    f.write(lyrics_string)