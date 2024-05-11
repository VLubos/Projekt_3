"""
projekt_3.py: třetí projekt do Engeto Online Python Akademie
author: Luboš Vavruška
email: lubos.vavruska@seznam.cz
discord: 
"""

#import sys #varianta pro spuštění z příkazového řádku
import csv

import requests 
from bs4 import BeautifulSoup


def parseWeb(web: str) -> str: #parsování webových stránek
    connect_timeout = 10
    read_timeout = 10
    response = requests.get(web, timeout=(connect_timeout, read_timeout))    
    html = BeautifulSoup(response.text, features="html.parser")
    return html

def filterTags(parsed: str, tag: str) -> list: #vyhledání všech prvků určitého tagu
    filteredTags = parsed.find_all(tag)
    return filteredTags

#webPage = sys.argv[1] #varianta pro spuštění z příkazového řádku
parsedWeb = parseWeb("https://volby.cz/pls/ps2017nss/ps32?xjazyk=CZ&xkraj=12&xnumnuts=7103")
linksToMunicipalities = filterTags(parsedWeb, "a")


pureLinks = list() #získání odkazů na stránky s výsledky v jednotlivých obcích
for link in linksToMunicipalities:
    pureLink = ("https://volby.cz/pls/ps2017nss/"+link["href"])
    if "311" in pureLink and pureLink not in pureLinks:
        pureLinks.append(pureLink)

#ODSADIT?
for member in pureLinks: #parsování získaných odkazů
    data = dict()
    overallData = []

    parsedMunicipality = parseWeb(member)
    code = str(member)[str(member).index("xobec=")+6:str(member).index("xobec=")+12] #Zjištění hodnoty code pro výsledný přehled
    data["Code"] = code
    
    findLocation = filterTags(parsedMunicipality, "h3") #Zjištění hodnoty location pro výsledný přehled
    for item in findLocation:
        if "Obec:" in str(item):
            location = (str(item).split(" ")[1]).replace("\n</h3>", "") 
    data["Location"] = location
    
    registeredRough = (parsedMunicipality.find_all("td", {"headers": "sa2"}))[0] #Zjištění hodnoty registered pro výsledný přehled
    registered = str(registeredRough).replace("""<td class="cislo" data-rel="L1" headers="sa2">""", "").replace("</td>", "")
    data["Registered"] = registered

    envelopesRough = (parsedMunicipality.find_all("td", {"headers": "sa5"}))[0] #Zjištění hodnoty envelopes pro výsledný přehled
    envelopes = str(envelopesRough).replace("""<td class="cislo" data-rel="L1" headers="sa5">""", "").replace("</td>", "")
    data["Envelopes"] = envelopes

    validRough = (parsedMunicipality.find_all("td", {"headers": "sa6"}))[0] #Zjištění hodnoty valid pro výsledný přehled
    valid = str(validRough).replace("""<td class="cislo" data-rel="L1" headers="sa6">""", "").replace("</td>", "")
    data["Valid"] = valid

    parties = parsedMunicipality.find_all("td", {"headers": "t1sa1 t1sb2"}) #Zjištění hodnot parties/ votes pro výsledný přehled
    partiesModified = []
    for party in parties:
        party = str(party).replace("""<td class="overflow_name" headers="t1sa1 t1sb2">""", "").replace("</td>", "")
        partiesModified.append(party)

    votes = parsedMunicipality.find_all("td", {"headers": "t1sa2 t1sb3"})
    votesModified = []
    for vote in votes:
        vote = str(vote).replace("""<td class="cislo" headers="t1sa2 t1sb3">""", "").replace("</td>", "")
        votesModified.append(vote)

    for i in range(0, len(parties)):
        data[partiesModified[i]] = votesModified[i]
        overallData.append(data)

csv_file = open("electionsResult.csv", mode="a") #Zápis dat do csv
writer = csv.DictWriter(csv_file, fieldnames=overallData[0].keys())
writer.writeheader()
for entry in overallData:
    writer.writerow(entry)
csv_file.close()


