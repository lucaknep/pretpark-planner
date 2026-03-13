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
 
 
select_query = "SELECT * FROM voorziening WHERE actief = 1"
voorzieningen = db.execute_query(select_query)
 
# FR5: filter attracties op lengte, leeftijd en gewicht
attractie_types = ["achtbaan", "water", "draaien", "familie", "simulator"]
toegestane_attracties = []
for v in voorzieningen:
    if v["type"] not in attractie_types:
        continue
    if v["attractie_min_lengte"] and bezoeker["lengte"] < v["attractie_min_lengte"]:
        continue
    if v["attractie_max_lengte"] and bezoeker["lengte"] > v["attractie_max_lengte"]:
        continue
    if v["attractie_min_leeftijd"] and bezoeker["leeftijd"] < v["attractie_min_leeftijd"]:
        continue
    if v["attractie_max_gewicht"] and bezoeker["gewicht"] > v["attractie_max_gewicht"]:
        continue
    toegestane_attracties.append(v)
 
 
# print de resultaten van de query op een overzichtelijke manier
pprint.pp(toegestane_attracties)
 
 
 
# altijd verbinding sluiten met de database als je klaar bent
db.close()
 
# verzamel alle benodigde gegevens in een dictionary # voorbeeld van hoe je bij een eigenschap komt
        # STAP 1: vul aan met andere benodigde eigenschappen
dagprogramma = {
    "bezoekersgegevens" : {
        "naam": bezoeker['naam'],
         "leeftijd": bezoeker['leeftijd'],
         "lengte":bezoeker['lengte'],
         "gewicht":bezoeker['gewicht'],
         "verblijfsduur":bezoeker['verblijfsduur'],
         "voorkeuren_attractietypes":bezoeker['voorkeuren_attractietypes'],
        "voorkeuren_eten":bezoeker['voorkeuren_eten'],
        "lievelingsattractie":bezoeker['lievelingsattracties'],
        "rekening_houden_met_weer":bezoeker['rekening_houden_met_weer'],
         
    },
    "weergegevens" : {
        # STAP 4: vul aan met weergegevens
    },
    "voorzieningen": toegestane_attracties,
 
   
    "totale_duur": 0 # STAP 3: aanpassen naar daadwerkelijke totale duur
}
 
# uiteindelijk schrijven we de dictionary weg naar een JSON-bestand, die kan worden ingelezen door de acceptatieomgeving
with open('dagprogramma_bezoeker_x.json', 'w') as json_bestand_uitvoer:
    json.dump(dagprogramma, json_bestand_uitvoer, indent=4)


