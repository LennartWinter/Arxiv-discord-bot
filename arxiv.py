import urllib, urllib.request
import discord
import requests
import time

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

URL = "https://arxiv.org/search/advanced?advanced=&terms-0-term=&terms-0-operator=AND&terms-0-field=title&classification-physics_archives=all&classification-include_cross_list=include&date-filter_by=all_dates&date-year=&date-from_date=&date-to_date=&date-date_type=submitted_date&abstracts=show&size=50&order=-submitted_date"

def getHTML():
    print(URL)
    req = urllib.request.Request(URL, headers={'User-Agent': 'Mozilla/5.0'})
    data = urllib.request.urlopen(req)
    return data.read().decode('utf-8')

@client.event
async def on_ready():
    while True:
        time.sleep(50)
        print("Checking Arxiv...")
        html = getHTML()
        with open("data/oldArxiv.txt", "r", encoding="UTF-8") as f:
            oldArxiv = f.read()
        if oldArxiv == html:
            pass
        else:
            with open("data/oldArxiv.txt", "w", encoding="UTF-8") as f:
                f.write(html)
            print("Arxiv updated!")
            # split by <a href="
            link = html.split('<a href="')[16].split('"')[0]
            with open("data/ArxivNotify.txt", "r", encoding="UTF-8") as f:
                ArxivNotify = f.read()
            channels = ArxivNotify.split("\n")
            for channel in channels:
                if channel == "":
                    pass
                else:
                    channel = client.get_channel(int(channel))
                    await channel.send(f"New paper published on arXiv: {link}")

with open("data/token.env", "r") as f:
    token = f.read()
client.run(token)
