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
bezoeker_id = 1  # pas id aan om een andere bezoeker te selecteren

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
select_query = "SELECT * FROM voorziening WHERE actief = 1"
voorzieningen = db.execute_query(select_query)

# print de resultaten van de query op een overzichtelijke manier
pprint.pp(voorzieningen)

# print de naam van de eerste voorziening
print(voorzieningen[0]["naam"])

# altijd verbinding sluiten met de database als je klaar bent
db.close()

# -----------------------------------------
# Hulplijsten en variabelen maken
# -----------------------------------------
dagprogramma_voorzieningen = []
totale_duur = 0

toegevoegde_attracties = []

# voorkeuren uit de database omzetten naar lijsten
voorkeuren_attractietypes = []
if bezoeker["voorkeuren_attractietypes"] is not None and bezoeker["voorkeuren_attractietypes"] != "":
    voorkeuren_attractietypes = [soort.strip().lower() for soort in bezoeker["voorkeuren_attractietypes"].split(",")]

voorkeuren_eten = []
if bezoeker["voorkeuren_eten"] is not None and bezoeker["voorkeuren_eten"] != "":
    voorkeuren_eten = [eten.strip().lower() for eten in bezoeker["voorkeuren_eten"].split(",")]

lievelingsattracties = []
if bezoeker["lievelingsattracties"] is not None and bezoeker["lievelingsattracties"] != "":
    lievelingsattracties = [naam.strip() for naam in bezoeker["lievelingsattracties"].split(",")]

# voorzieningen sorteren op totale duur
voorzieningen.sort(key=lambda voorziening: voorziening["geschatte_wachttijd"] + voorziening["doorlooptijd"])

# -----------------------------------------
# STAP 2: hier komt een lijst met alle voorzieningen
# -----------------------------------------
# Eerst attracties toevoegen die passen bij de voorkeuren van de bezoeker
for voorziening in voorzieningen:

    if voorziening["type"] not in ["achtbaan", "water", "draaien", "familie", "simulator"]:
        continue

    # controle op lengte
    if voorziening["attractie_min_lengte"] is not None:
        if bezoeker["lengte"] < voorziening["attractie_min_lengte"]:
            continue

    if voorziening["attractie_max_lengte"] is not None:
        if bezoeker["lengte"] > voorziening["attractie_max_lengte"]:
            continue

    # controle op leeftijd
    if voorziening["attractie_min_leeftijd"] is not None:
        if bezoeker["leeftijd"] < voorziening["attractie_min_leeftijd"]:
            continue

    # controle op gewicht
    if voorziening["attractie_max_gewicht"] is not None:
        if bezoeker["gewicht"] > voorziening["attractie_max_gewicht"]:
            continue

    # eerst alleen attracties toevoegen die in de voorkeuren staan
    if voorziening["type"].lower() not in voorkeuren_attractietypes:
        continue

    duur = voorziening["geschatte_wachttijd"] + voorziening["doorlooptijd"]

    if totale_duur + duur > bezoeker["verblijfsduur"]:
        continue

    attractie = {
        "naam": voorziening["naam"],
        "type": voorziening["type"],
        "overdekt": bool(voorziening["overdekt"]),
        "geschatte_wachttijd": voorziening["geschatte_wachttijd"],
        "doorlooptijd": voorziening["doorlooptijd"],
        "attractie_min_lengte": voorziening["attractie_min_lengte"],
        "attractie_max_lengte": voorziening["attractie_max_lengte"],
        "attractie_min_leeftijd": voorziening["attractie_min_leeftijd"],
        "attractie_max_gewicht": voorziening["attractie_max_gewicht"]
    }

    if voorziening["naam"] in lievelingsattracties:
        attractie["is_favoriet"] = True

    dagprogramma_voorzieningen.append(attractie)
    totale_duur += duur
    toegevoegde_attracties.append(voorziening["naam"])

# Daarna andere geschikte attracties toevoegen als er nog tijd over is
for voorziening in voorzieningen:

    if voorziening["type"] not in ["achtbaan", "water", "draaien", "familie", "simulator"]:
        continue

    if voorziening["naam"] in toegevoegde_attracties:
        continue

    if voorziening["attractie_min_lengte"] is not None:
        if bezoeker["lengte"] < voorziening["attractie_min_lengte"]:
            continue

    if voorziening["attractie_max_lengte"] is not None:
        if bezoeker["lengte"] > voorziening["attractie_max_lengte"]:
            continue

    if voorziening["attractie_min_leeftijd"] is not None:
        if bezoeker["leeftijd"] < voorziening["attractie_min_leeftijd"]:
            continue

    if voorziening["attractie_max_gewicht"] is not None:
        if bezoeker["gewicht"] > voorziening["attractie_max_gewicht"]:
            continue

    duur = voorziening["geschatte_wachttijd"] + voorziening["doorlooptijd"]

    if totale_duur + duur > bezoeker["verblijfsduur"]:
        continue

    attractie = {
        "naam": voorziening["naam"],
        "type": voorziening["type"],
        "overdekt": bool(voorziening["overdekt"]),
        "geschatte_wachttijd": voorziening["geschatte_wachttijd"],
        "doorlooptijd": voorziening["doorlooptijd"],
        "attractie_min_lengte": voorziening["attractie_min_lengte"],
        "attractie_max_lengte": voorziening["attractie_max_lengte"],
        "attractie_min_leeftijd": voorziening["attractie_min_leeftijd"],
        "attractie_max_gewicht": voorziening["attractie_max_gewicht"]
    }

    if voorziening["naam"] in lievelingsattracties:
        attractie["is_favoriet"] = True

    dagprogramma_voorzieningen.append(attractie)
    totale_duur += duur
    toegevoegde_attracties.append(voorziening["naam"])

# Lievelingsattracties nog een tweede keer toevoegen
for voorziening in voorzieningen:

    if voorziening["naam"] not in lievelingsattracties:
        continue

    if voorziening["type"] not in ["achtbaan", "water", "draaien", "familie", "simulator"]:
        continue

    duur = voorziening["geschatte_wachttijd"] + voorziening["doorlooptijd"]

    if totale_duur + duur > bezoeker["verblijfsduur"]:
        continue

    favoriete_attractie = {
        "naam": voorziening["naam"],
        "type": voorziening["type"],
        "overdekt": bool(voorziening["overdekt"]),
        "geschatte_wachttijd": voorziening["geschatte_wachttijd"],
        "doorlooptijd": voorziening["doorlooptijd"],
        "attractie_min_lengte": voorziening["attractie_min_lengte"],
        "attractie_max_lengte": voorziening["attractie_max_lengte"],
        "attractie_min_leeftijd": voorziening["attractie_min_leeftijd"],
        "attractie_max_gewicht": voorziening["attractie_max_gewicht"],
        "is_favoriet": True
    }

    dagprogramma_voorzieningen.append(favoriete_attractie)
    totale_duur += duur

# Horeca halverwege toevoegen
for voorziening in voorzieningen:

    if voorziening["type"] != "horeca":
        continue

    if voorziening["productaanbod"] is None:
        continue

    if voorziening["productaanbod"].lower() in voorkeuren_eten:

        horeca = {
            "naam": voorziening["naam"],
            "type": "horeca",
            "geschatte_wachttijd": voorziening["geschatte_wachttijd"],
            "doorlooptijd": voorziening["doorlooptijd"],
            "productaanbod": voorziening["productaanbod"]
        }

        eetpauze = {
            "type": "eetpauze",
            "duur": 15
        }

        horeca_duur = horeca["geschatte_wachttijd"] + horeca["doorlooptijd"] + 15

        if totale_duur + horeca_duur <= bezoeker["verblijfsduur"]:
            midden = len(dagprogramma_voorzieningen) // 2
            dagprogramma_voorzieningen.insert(midden, horeca)
            dagprogramma_voorzieningen.insert(midden + 1, eetpauze)
            totale_duur += horeca_duur

        break

# Souvenirwinkel aan het einde toevoegen
for voorziening in voorzieningen:

    if voorziening["type"] != "winkel":
        continue

    if voorziening["productaanbod"] is None:
        continue

    # in de SQL staat "Souveniers" gespeld, dus hier op "souvenir" controleren
    if "souvenir" in voorziening["productaanbod"].lower():

        winkel = {
            "naam": voorziening["naam"],
            "type": "winkel",
            "geschatte_wachttijd": voorziening["geschatte_wachttijd"],
            "doorlooptijd": voorziening["doorlooptijd"],
            "productaanbod": voorziening["productaanbod"]
        }

        winkel_duur = winkel["geschatte_wachttijd"] + winkel["doorlooptijd"]

        if totale_duur + winkel_duur <= bezoeker["verblijfsduur"]:
            dagprogramma_voorzieningen.append(winkel)
            totale_duur += winkel_duur

        break

# verzamel alle benodigde gegevens in een dictionary
dagprogramma = {
    "bezoekersgegevens": {
        "naam": bezoeker['naam'],
        "leeftijd": bezoeker["leeftijd"],
        "lengte": bezoeker["lengte"],
        "gewicht": bezoeker["gewicht"],
        "verblijfsduur": bezoeker["verblijfsduur"],
        "voorkeuren_attractietypes": [soort.strip() for soort in bezoeker["voorkeuren_attractietypes"].split(",")] if bezoeker["voorkeuren_attractietypes"] else [],
        "voorkeuren_eten": [eten.strip() for eten in bezoeker["voorkeuren_eten"].split(",")] if bezoeker["voorkeuren_eten"] else [],
        "lievelingsattracties": [naam.strip() for naam in bezoeker["lievelingsattracties"].split(",")] if bezoeker["lievelingsattracties"] else [],
        "rekening_houden_met_weer": bool(bezoeker["rekening_houden_met_weer"])
    },
    "weergegevens": {
        # STAP 4: vul aan met weergegevens
        "temperatuur": 15,
        "kans_op_regen": 0
    },
    "voorzieningen": dagprogramma_voorzieningen,
    "totale_duur": totale_duur
}

# uiteindelijk schrijven we de dictionary weg naar een JSON-bestand, die kan worden ingelezen door de acceptatieomgeving
with open('dagprogramma_bezoeker_x.json', 'w') as json_bestand_uitvoer:
    json.dump(dagprogramma, json_bestand_uitvoer, indent=4)

print("Dagprogramma gemaakt!")
