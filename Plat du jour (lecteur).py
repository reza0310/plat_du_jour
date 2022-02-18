from random import randint
print("Chargement...")
with open("donnees.txt", "r", encoding="utf-8") as f:
    donnees = f.readlines()
service = []
prixs = {"bon marché":1, "Coût moyen":2, "assez cher":3}
difficultes = {"très facile":1, "facile":2, "Niveau moyen":3, "difficile":4}
nombre_plats = int(input("Nombre de plats? "))
diff_min = int(input("Difficulté min (de 1 à 4)? "))
diff_max = int(input("Difficulté max (de 1 à 4)? "))
prix_min = int(input("Prix min (de 1 à 4)? "))
prix_max = int(input("Prix max (de 1 à 4)? "))
temps_min = [int(i) for i in input("Temps min (format XXHXX)? ").split("H")]
temps_max = [int(i) for i in input("Temps max (format XXHXX)? ").split("H")]
for plats in donnees:
    plats = plats.replace("\n", "").split('; ')
    plat = {"nom":str(plats[3].split('recettes/recette')[1].split("_")[:-1][1]).capitalize().replace('-', " "), "temps":plats[0].replace(" ", "").replace("min", "").upper(), "niveau":difficultes[plats[1]], "prix":prixs[plats[2]], "url":plats[3]}
    service.append(plat)
    if plat["temps"].find("J") != -1:
        plat["temps"] = str(int(int(plat["temps"].split("J")[0])+float("0."+plat["temps"].split("J")[1].replace("H", ""))*24))+"H"
    heures = plat["temps"].find("H")
    if (plat["niveau"] < diff_min or plat["niveau"] > diff_max) or (plat["prix"] < prix_min or plat["prix"] > prix_max):
        service.remove(plat)
    elif heures == -1 and not temps_min[1]+60*temps_min[0] <= int(plat["temps"]) <= temps_max[1]+60*temps_max[0]:
        service.remove(plat)
    elif heures != -1:
        valeurs = [int(i) for i in plat["temps"].split("H") if i]
        if len(valeurs) == 2 and not temps_min[1]+60*temps_min[0] <= valeurs[1]+60*valeurs[0] <= temps_max[1]+60*temps_max[0]:
            service.remove(plat)
        elif not temps_min[1]+60*temps_min[0] <= 60*valeurs[0] <= temps_max[1]+60*temps_max[0]:
            service.remove(plat)
print("Avec vos critères, il reste", len(service), "plats.")
for i in range(nombre_plats):
    try:
        selection = service[randint(0, len(service))]
        print("-"+selection["nom"]+" (temps: "+selection["temps"]+"m, niveau: "+str(selection["niveau"])+"/4, prix: "+str(selection["prix"])+"/3) à: "+selection["url"])
        service.remove(selection)
    except IndexError:
        print("Plus de plats.")