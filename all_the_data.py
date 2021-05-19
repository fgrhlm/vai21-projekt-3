#!/usr/bin/env python3
import sys
import json
import time
import requests
import urllib
from bs4 import BeautifulSoup

#########################
######### Prefs #########
#########################
 
# Billboard Hot 100 URL
url_bb = "https://www.billboard.com/charts/hot-100"

# Vita lögner så att vi inte blir blockerade
request_headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.11; rv:42.0) Gecko/20100101 Firefox/42.0",
}

###########################
######### Funcs ###########
###########################

# Hämtar htmlinnehållet från Billboard Hot 100
def get_billboard_page():
    print(f"Requesting billboard data..")
    r = requests.get(url_bb,headers=request_headers);
    
    print(f"Response: {r.status_code}")
    if r.status_code == 200:
        print("Success!")
        return r.text
    else:
        print("Request failed! exiting... ")
        sys.exit()

# Parsar html och spottar ut json i formatet:
# {"song": "LÅTNAMN", "artist": "ARTISTNAMN"}
def parse_billboard_data(t):
    print("Parsing billboard data..")
    j = []
    s = BeautifulSoup(t,"html.parser")

    # Ram
    f = s.find_all("span",{"class":"chart-element__information"})

    for n in f:
        # Låtnamn
        f_sn = n.find("span",{"class":"chart-element__information__song"})
        # Artistnamn
        f_an = n.find("span",{"class":"chart-element__information__artist"})

        print(f"\t{f_an.text} - {f_sn.text}")
        j.append({"song": f_sn.get_text(),"artist":f_an.get_text()})

    return j

# Hämtar information om en låt från ascap.com
# Härifrån får vi kompositörer och förlag 
def get_song_ascap_data(artist,song):
        url_base = "https://ace-api.ascap.com/api/wservice/MobileWeb/service/ace/api/v3.0/search/title/"
        url_ext1 = f"{urllib.parse.quote(song,safe='')}?limit=100&page=1&universe=OTTOnly&socUniverse=SVW&searchType2=perfName&searchValue2="
        url_ext2 = urllib.parse.quote(artist.split(" ")[0],safe='')
        url_full = f"{url_base}{url_ext1}{url_ext2}"

        print(url_full)
        r = requests.get(url_full,headers=request_headers);
    
        print(f"Response: {r.status_code}")
        if r.status_code == 200:
            print("Success!")
            return r.json()
        else:
            print("Request failed! exiting... ")
            sys.exit()

# Hittar och returnerar en lista med kompositörer
def extract_writers(t):
    writers = []
    for n in t["result"][0]["interestedParties"]:
        if n["roleCde"] == "W":
            writers.append(n["fullName"])
    
    return writers

# Försöker hämta metadata från ASCAP, men såklart finns ju int allt tillgängligt där via..
# så om int de finns så får de va.. Måst fösök hitt en bättre datakälla...
def join_meta(t):
    j = []
    for n in t:
        print("ASCAP REQUEST..")
        a = n["artist"]
        s = n["song"]
        try:
            d = extract_writers(get_song_ascap_data(a,s))
            o = {"artist": a, "song": s, "writers": d}
            j.append(o)
        except:
            print(f"ASCAP returned 404 on {a} - {s}")

        # Verkar vara ganska slö o sned API och bara säkä att den tillåter cross-origin
        # Så lika bra att vara snäll o int DOS:a den :)
        time.sleep(3)

    return j

# Sparar ner dict som json
def save_data_to_file(d,name):
    print(f"Saving: {name}")
    with open(name,"w") as o:
        json.dump(d,o)

# # # # # # # # # # # # # # #
#  MAGIC! - MAGIC! - MAGIC! #
# # # # # # # # # # # # # # #
if __name__ == '__main__':
    # Hämta billboard datan
    t = get_billboard_page()
    
    # Parse och formattera datan
    data_bb = parse_billboard_data(t)
    save_data_to_file(data_bb,"data/billboard_top_100.json")

    # Hämta kompositörer och kombinera med billboard datan
    data_merged = join_meta(data_bb)
    save_data_to_file(data_merged,"data/billboard_top_100_with_writers.json")