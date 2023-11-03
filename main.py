import urllib, urllib.request
import os
import discord
from bs4 import BeautifulSoup
import re
import requests
import numpy as np
import cv2
import pyautogui

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    activity = discord.Game(name="$help", type=1)
    await client.change_presence(status=discord.Status.online, activity=activity)
    print(f'We have logged in as {client.user}')

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    args = message.content.split(' ')
    args[0] = args[0].lower()
    if args[0] == "$arxiv":
        if len(args) <= 2:
            embedVar = discord.Embed(title="$arXiv help", description="A simple command for searching arxiv papers", color=0x00ff00)
            embedVar.add_field(name="Usage", value="$arxiv [paper/author/search] [args]", inline=False)
            embedVar.add_field(name="Example", value="`$arxiv search quantum computing`\n`$arxiv paper 4 quantum computing`\n`$arxiv author Yazhen Wang`", inline=False)
            await message.channel.send(embed=embedVar)
        else:
            if args[1] == 'paper':
                try:
                    int(args[2])
                    search = args[3]
                    for i in range(4, len(args)):
                        search += '+' + args[i]
                    search = checkURL(search)
                    data = getHTML(f'http://export.arxiv.org/api/query?search_query=all:{search}&start={int(args[2])}&max_results=1')
                except:
                    search = args[2]
                    for i in range(3, len(args)):
                        search += '+' + args[i]
                    data = getHTML(f'http://export.arxiv.org/api/query?search_query=all:{search}&start=0&max_results=1')
                title = data.split('<title>')[1].split('</title>')[0]
                abstract = data.split('<summary>')[1].split('</summary>')[0]
                abstract = BeautifulSoup(abstract, "html.parser").text
                abstract = beautify(abstract)
                title = beautify(title)
                if len(abstract) > 1024:
                    abstract = abstract[:1021] + '...'
                if len(title) > 256:
                    title = title[:253] + '...'
                embedVar = discord.Embed(title=title, description=abstract, color=0x00ff00)
                authorCount = len(data.split('<author>')) - 1
                authors = []
                for i in range(authorCount):
                    authors.append(data.split('<author>')[i+1].split('</author>')[0].split('<name>')[1].split('</name>')[0])
                embedVar.add_field(name="Author(s)", value=f'{", ".join(authors)}', inline=False)
                link = data.split("<id>")[2].split("</id>")[0]
                embedVar.add_field(name="Source", value=link, inline=True)
                await message.channel.send(embed=embedVar)
            elif args[1] == 'author':
                try:
                    int(args[2])
                    search = args[3]
                    for i in range(4, len(args)):
                        search += '+' + args[i]
                    args[2] = int(args[2])-1
                    search = checkURL(search)
                    data = getHTML(f'http://export.arxiv.org/api/query?search_query=au:{search}&start={(int(args[2])*10)-1}&max_results=10')
                except:
                    search = args[2]
                    for i in range(3, len(args)):
                        search += '+' + args[i]
                    data = getHTML(f'http://export.arxiv.org/api/query?search_query=au:{search}')
                titles = []
                links = []
                for i in range(len(data.split('<title>')) - 1):
                    titles.append(f"{i+1}. {data.split('<title>')[i+1].split('</title>')[0]}")
                    links.append(data.split('<id>')[i+2].split('</id>')[0])
                final = ""
                count = 0
                for title in titles:
                    link = links[count]
                    final += f'{title}\n{link}\n\n'
                    count += 1
                author = search.replace('+', ' ')
                embedVar = discord.Embed(title=f'Papers by {author}', description=final, color=0x00ff00)
                await message.channel.send(embed=embedVar)
            elif args[1] == 'search':
                try:
                    search = str(args[3])
                    for i in range(4, len(args)):
                        search += '+' + args[i]
                    args[2] = int(args[2])-1
                    data = getHTML(f'http://export.arxiv.org/api/query?search_query=all:{search}&start={args[2]*10}&max_results=10')
                except:
                    search = str(args[2])
                    for i in range(3, len(args)):
                        search += '+' + args[i]
                    data = getHTML(f'http://export.arxiv.org/api/query?search_query=all:{search}')
                titles = []
                for i in range(len(data.split('<title>')) - 1):
                    try:
                        index = i
                        i = args[2]*10+i+1
                    except:
                        pass
                    title = f"{i}. {data.split('<title>')[index+1].split('</title>')[0]}"
                    title = beautify(title)
                    titles.append(title)
                links = []
                for i in range(len(data.split('<id>')) - 1):
                    try:
                        links.append(data.split('<id>')[i+2].split('</id>')[0])
                    except:
                        pass
                final = ""
                count = 0
                for title in titles:
                    link = links[count]
                    final += f'{title}\n{link}\n\n'
                    count += 1
                search = search.split('+')
                search = ' '.join(search)
                embedVar = discord.Embed(title=f'Search results for {search}', description=final, color=0x00ff00)
                await message.channel.send(embed=embedVar)
            else:
                embedVar = discord.Embed(title="$arXiv help", description="A simple command for searching arxiv papers", color=0x00ff00)
                embedVar.add_field(name="Usage", value="$arxiv [paper/author/search] [args]", inline=False)
                embedVar.add_field(name="Example", value="$arxiv search quantum computing\n$arxiv paper 4 quantum computing\n$arxiv author Yazhen Wang", inline=False)
                await message.channel.send(embed=embedVar)

    elif args[0] == "$cern":
        if len(args) <= 1:
            embedVar = discord.Embed(title="$CERN help", description="A simple command for searching CERN papers", color=0x00ff00)
            embedVar.add_field(name="Usage", value="$CERN [args]", inline=False)
            embedVar.add_field(name="Example", value="$CERN tests of general relativity", inline=False)
            await message.channel.send(embed=embedVar)
        else:
            search = args[1]
            for i in range(2, len(args)):
                search += '+' + args[i]
            search = checkURL(search)
            data = getHTML(f'https://cds.cern.ch/search?ln=en&sc=1&p={search}&action_search=Search&op1=a&m1=a&p1=&f1=&c=Articles+%26+Preprints&c=Books+%26+Proceedings&c=Presentations+%26+Talks&c=Periodicals+%26+Progress+Reports&c=Multimedia+%26+Outreach&c=International+Collaborations')
            try:
                title = data.split('?ln=en" class="titlelink">')[1].split('</a>')[0]
                title = BeautifulSoup(title, "html.parser").text
                link = data.split('<a href="https://cds.cern.ch/record/')[1].split('" class="titlelink">')[0]
                link = f'https://cds.cern.ch/record/{link}'
                abstract = "Content not found."
                data = getHTML(link)
                try:
                    abstract = data.split('Abstract')[1].split('</td><td style="padding-left:5px;">')[1].split('</td>')[0]
                except:
                    try:
                        abstractCount = len(data.split('Abstract'))
                        largest = ""
                        for i in range(abstractCount):
                            try:
                                abstract = data.split('Abstract')[i+1].split('</td><td style="padding-left:5px;">')[1].split('</td>')[0]
                                if len(abstract) > len(largest):
                                    largest = abstract
                                break
                            except:
                                pass
                        if len(largest) > 0:
                            abstract = largest
                        else:
                            raise Exception
                    except:
                        try:
                            abstract = data.split('</td><td style="padding-left:5px;">')[1].split('</td>')[0]
                        except:
                            abstract = "No description given."
            except:
                await message.channel.send("No results found.")
            abstract = BeautifulSoup(abstract, "html.parser").text
            abstract = beautify(abstract)
            title = beautify(title)
            if len(abstract) > 1024:
                abstract = abstract[:1021] + '...'
            if len(title) > 256:
                title = title[:253] + '...'
            if len(link) > 1024:
                link = link[:1021] + '...'
            embedVar = discord.Embed(title=title, description=abstract, color=0x00ff00)
            embedVar.add_field(name="Source", value=link, inline=True)
            await message.channel.send(embed=embedVar)

    elif args[0] == "$wikipedia":
        if len(args) <= 1:
            embedVar = discord.Embed(title="$Wikipedia help", description="A simple command for searching Wikipedia articles", color=0x00ff00)
            embedVar.add_field(name="Usage", value="$Wikipedia [args]", inline=False)
            embedVar.add_field(name="Example", value="$Wikipedia quantum computing", inline=False)
            await message.channel.send(embed=embedVar)
        else:
            search = args[1]
            for i in range(2, len(args)):
                search += '+' + args[i]
            url = checkURL(search)
            data = getHTML(f'https://en.wikipedia.org/w/index.php?search={url}&title=Special%3ASearch&ns0=1')
            title = data.split('<title>')[1].split('</title>')[0].split(' - Wikipedia')[0]
            try:
                abstract = data.split('<p>')[1].split('</p>')[0]
            except:
                try:
                    abstract = data.split('<p class="mw-empty-elt">')[1].split('</p>')[0]
                except:
                    abstract = "No description given."
            abstract = BeautifulSoup(abstract, "html.parser").text
            abstract = re.sub(r'\[.*?\]+', '', abstract)
            embedVar = discord.Embed(title=title, description=abstract, color=0x00ff00)
            embedVar.add_field(name="Source", value=f'https://en.wikipedia.org/w/index.php?search={url}&title=Special%3ASearch&ns0=1', inline=True)
            await message.channel.send(embed=embedVar)

    elif args[0] == "$help":
        embedVar = discord.Embed(title="Help", description="Welcome to Papers! Papers is a simple to use educational bot to search through scientific papers and articles on discord.", color=0x00ff00)
        embedVar.add_field(name="$Wikipedia", value="A simple command for searching Wikipedia articles\n`$Wikipedia uncertainty principle`", inline=False)
        embedVar.add_field(name="$CERN", value="A simple command for searching CERN papers\n`$CERN annual year report 2022`", inline=False)
        embedVar.add_field(name="$arXiv", value="A simple command for searching arXiv papers\n`$arXiv search tests on general relativity`\n`$arXiv paper 5 tests on general relativity`\n`$arXiv author Yazhen Wang`", inline=False)
        await message.channel.send(embed=embedVar)

def checkURL(url):
    print(url)
    with open('data/whitelist.txt') as f:
        whitelist = f.read().splitlines()
    for i in range(len(url)):
        if url[i] not in whitelist:
            url = url[:i] + '+' + url[i+1:]
    return url

def getHTML(url):
    print(url)
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    data = urllib.request.urlopen(req)
    return data.read().decode('utf-8')

def beautify(text):
    text = text.replace('&amp;', '&')
    text = text.replace('\\alpha', 'α')
    text = text.replace('\\beta', 'β')
    text = text.replace('\\gamma', 'γ')
    text = text.replace('\\delta', 'δ')
    text = text.replace('\\epsilon', 'ε')
    text = text.replace('\\zeta', 'ζ')
    text = text.replace('\\eta', 'η')
    text = text.replace('\\theta', 'θ')
    text = text.replace('\\iota', 'ι')
    text = text.replace('\\kappa', 'κ')
    text = text.replace('\\lambda', 'λ')
    text = text.replace('\\mu', 'μ')
    text = text.replace('\\nu', 'ν')
    text = text.replace('\\xi', 'ξ')
    text = text.replace('\\omicron', 'ο')
    text = text.replace('\\pi', 'π')
    text = text.replace('\\rho', 'ρ')
    text = text.replace('\\sigma', 'σ')
    text = text.replace('\\tau', 'τ')
    text = text.replace('\\upsilon', 'υ')
    text = text.replace('\\phi', 'φ')
    text = text.replace('\\chi', 'χ')
    text = text.replace('\\psi', 'ψ')
    text = text.replace('\\omega', 'ω')
    text = text.replace('\\Gamma', 'Γ')
    text = text.replace('\\Delta', 'Δ')
    text = text.replace('\\Theta', 'Θ')
    text = text.replace('\\Lambda', 'Λ')
    text = text.replace('\\Xi', 'Ξ')
    text = text.replace('\\Pi', 'Π')
    text = text.replace('\\Sigma', 'Σ')
    text = text.replace('\\Upsilon', 'Υ')
    text = text.replace('\\Phi', 'Φ')
    text = text.replace('\\Psi', 'Ψ')
    text = text.replace('\\Omega', 'Ω')
    text = text.replace('\\rightarrow', '→')
    text = text.replace('\\Rightarrow', '⇒')
    text = text.replace('\\leftarrow', '←')
    text = text.replace('\\Leftarrow', '⇐')
    text = text.replace('\\textit', '')
    text = text.replace('\\textbf', '')
    text = text.replace('\\text', '')
    text = text.replace('\\mathrm', '')
    text = text.replace('\\bigtriangleup', '△')
    text = text.replace('\\bigtriangledown', '▽')
    text = text.replace('\\bar', '¯')
    text = text.replace('{', '')
    text = text.replace('}', '')
    text = text.replace('*', '\*')
    text = text.replace('_', '\_')
    text = text.replace('`', '\`')
    text = text.replace('~', '\~')
    text = text.replace('|', '\|')
    text = text.replace('$', '*')
    return text

with open("data/token.env", "r") as f:
    token = f.read()
client.run(token)