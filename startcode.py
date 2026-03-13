import json
from database_wrapper import Database

# verbinding maken met database
db = Database(
    host="localhost",
    gebruiker="user",
    wachtwoord="password",
    database="attractiepark_casus_a"
)

db.connect()

# ------------------------------------------------
# bezoeker ophalen
# ------------------------------------------------

bezoeker_id = 1

query = f"SELECT * FROM bezoeker WHERE id = {bezoeker_id}"
resultaat = db.execute_query(query)

bezoeker = resultaat[0]

print("Bezoeker:", bezoeker["naam"])

# ------------------------------------------------
# voorzieningen ophalen
# ------------------------------------------------

query = "SELECT * FROM voorziening"
voorzieningen = db.execute_query(query)

print("Aantal voorzieningen:", len(voorzieningen))

# ------------------------------------------------
# geschikte attracties zoeken
# ------------------------------------------------

geschikte_attracties = []

for voorziening in voorzieningen:

    if voorziening["type"] != "horeca" and voorziening["type"] != "winkel":

        if bezoeker["lengte"] >= voorziening["attractie_min_lengte"]:

            attractie = {
                "naam": voorziening["naam"],
                "type": voorziening["type"],
                "geschatte_wachttijd": voorziening["geschatte_wachttijd"],
                "doorlooptijd": voorziening["doorlooptijd"]
            }

            geschikte_attracties.append(attractie)

# ------------------------------------------------
# 1 horeca kiezen
# ------------------------------------------------

horeca_item = None

for voorziening in voorzieningen:

    if voorziening["type"] == "horeca":
        horeca_item = {
            "naam": voorziening["naam"],
            "type": "horeca",
            "geschatte_wachttijd": voorziening["geschatte_wachttijd"],
            "doorlooptijd": voorziening["doorlooptijd"]
        }
        break

# ------------------------------------------------
# JSON maken
# ------------------------------------------------

voorzieningen_output = []

voorzieningen_output.extend(geschikte_attracties)

if horeca_item:
    voorzieningen_output.append(horeca_item)

dagprogramma = {
    "bezoekersgegevens": {
        "naam": bezoeker["naam"],
        "leeftijd": bezoeker["leeftijd"],
        "lengte": bezoeker["lengte"]
    },
    "voorzieningen": voorzieningen_output
}

# ------------------------------------------------
# bestand opslaan
# ------------------------------------------------

with open("dagprogramma_bezoeker_x.json", "w") as f:
    json.dump(dagprogramma, f, indent=4)

print("JSON bestand gemaakt")

db.close()

