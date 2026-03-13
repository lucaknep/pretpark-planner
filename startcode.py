from pathlib import Path
import json
import pprint
from database_wrapper import Database

# -----------------------------------------
# Database initialisatie en verbinden
# -----------------------------------------
# parameters voor connectie met de database
db = Database(host="localhost", gebruiker="user", wachtwoord="password", database="attractiepark_casus_a")
# altijd verbinding openen om query's uit te voeren
db.connect()

# -----------------------------------------
# Haal de eigenschappen op van een bezoeker
# -----------------------------------------
bezoeker_id = 1 # pas id aan om een andere bezoeker te selecteren

# SQL-query om alle gegevens van één bezoeker op te halen op basis van het ID.
select_query = f"SELECT * FROM bezoeker WHERE id = {bezoeker_id}"
resultaat = db.execute_query(select_query)

# haal de eerste rij uit het resultaat.
bezoeker = resultaat[0]

# voorbeeld van hoe je bij een eigenschap komt
print(bezoeker['naam']) 

# -----------------------------------------
# Haal alle voorzieningen op
# -----------------------------------------
# pas deze query aan en voeg queries toe om de juiste voorzieningen op te halen
select_query = "SELECT * FROM voorziening"
voorzieningen = db.execute_query(select_query)

# print de resultaten van de query op een overzichtelijke manier
pprint.pp(voorzieningen) 

# print de naam van de eerste voorziening
print(voorzieningen[0]["naam"])

# -----------------------------------------
# STAP 2: maak een lijst met geschikte voorzieningen
# -----------------------------------------
voorzieningen_output = []

# 1 passende horecavoorziening bewaren
gekozen_horeca = None

# voorkeuren eten uit database omzetten naar lijst
voorkeuren_eten = bezoeker["voorkeuren_eten"].split(",")

for i in range(len(voorkeuren_eten)):
    voorkeuren_eten[i] = voorkeuren_eten[i].strip()

for voorziening in voorzieningen:

    # alleen attracties selecteren voor FR5
    if voorziening["type"] != "horeca" and voorziening["type"] != "winkel":

        geschikt = True

        # leeftijd controleren
        if voorziening["attractie_min_leeftijd"] is not None:
            if bezoeker["leeftijd"] < voorziening["attractie_min_leeftijd"]:
                geschikt = False

        # minimale lengte controleren
        if voorziening["attractie_min_lengte"] is not None:
            if bezoeker["lengte"] < voorziening["attractie_min_lengte"]:
                geschikt = False

        # maximale lengte controleren
        if voorziening["attractie_max_lengte"] is not None:
            if bezoeker["lengte"] > voorziening["attractie_max_lengte"]:
                geschikt = False

        # maximaal gewicht controleren
        if voorziening["attractie_max_gewicht"] is not None:
            if bezoeker["gewicht"] > voorziening["attractie_max_gewicht"]:
                geschikt = False

        if geschikt:
            attractie = {
                "naam": voorziening["naam"],
                "type": voorziening["type"],
                "overdekt": bool(voorziening["overdekt"]),
                "geschatte_wachttijd": voorziening["geschatte_wachttijd"],
                "doorlooptijd": voorziening["doorlooptijd"],
                "attractie_min_lengte": voorziening["attractie_min_lengte"],
                "attractie_max_lengte": voorziening["attractie_max_lengte"],
                "attractie_min_gewicht": None,
                "attractie_max_gewicht": voorziening["attractie_max_gewicht"],
                "is_favoriet": False
            }

            voorzieningen_output.append(attractie)

    # 1 passende horecagelegenheid zoeken voor FR9
    if voorziening["type"] == "horeca" and gekozen_horeca is None:
        if voorziening["productaanbod"] in voorkeuren_eten:
            gekozen_horeca = {
                "naam": voorziening["naam"],
                "type": "Horeca",
                "geschatte_wachttijd": voorziening["geschatte_wachttijd"],
                "doorlooptijd": voorziening["doorlooptijd"],
                "productaanbod": voorziening["productaanbod"]
            }

# gevonden horeca toevoegen
if gekozen_horeca is not None:
    voorzieningen_output.append(gekozen_horeca)

# -----------------------------------------
# STAP 3: bereken totale duur
# -----------------------------------------
totale_duur = 0

for voorziening in voorzieningen_output:
    totale_duur = totale_duur + voorziening["geschatte_wachttijd"] + voorziening["doorlooptijd"]

# -----------------------------------------
# altijd verbinding sluiten met de database als je klaar bent
# -----------------------------------------
db.close()

# verzamel alle benodigde gegevens in een dictionary
dagprogramma = {
    "bezoekersgegevens" : {
        "naam": bezoeker['naam'],
        "verblijfsduur": bezoeker["verblijfsduur"],
        "leeftijd": bezoeker["leeftijd"],
        "lengte": bezoeker["lengte"],
        "gewicht": bezoeker["gewicht"],
        "voorkeuren_attractietypes": bezoeker["voorkeuren_attractietypes"].split(","),
        "lievelingsattracties": bezoeker["lievelingsattracties"].split(","),
        "voorkeuren_eten": bezoeker["voorkeuren_eten"].split(","),
        "rekening_houden_met_weer": bool(bezoeker["rekening_houden_met_weer"])
    },
    "weergegevens" : {
        # STAP 4: vul aan met weergegevens
        "temperatuur": 15,
        "kans_op_regen": 20
    }, 
    "voorzieningen": voorzieningen_output,
    "totale_duur": totale_duur
}

# spaties uit lijsten halen
for i in range(len(dagprogramma["bezoekersgegevens"]["voorkeuren_attractietypes"])):
    dagprogramma["bezoekersgegevens"]["voorkeuren_attractietypes"][i] = dagprogramma["bezoekersgegevens"]["voorkeuren_attractietypes"][i].strip()

for i in range(len(dagprogramma["bezoekersgegevens"]["lievelingsattracties"])):
    dagprogramma["bezoekersgegevens"]["lievelingsattracties"][i] = dagprogramma["bezoekersgegevens"]["lievelingsattracties"][i].strip()

for i in range(len(dagprogramma["bezoekersgegevens"]["voorkeuren_eten"])):
    dagprogramma["bezoekersgegevens"]["voorkeuren_eten"][i] = dagprogramma["bezoekersgegevens"]["voorkeuren_eten"][i].strip()

# uiteindelijk schrijven we de dictionary weg naar een JSON-bestand, die kan worden ingelezen door de acceptatieomgeving
with open('dagprogramma_bezoeker_x.json', 'w') as json_bestand_uitvoer:
    json.dump(dagprogramma, json_bestand_uitvoer, indent=4)

