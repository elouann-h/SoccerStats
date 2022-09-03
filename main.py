####################################################################################################
#
#       ENGLISH
#
# This program convert a text file input into two csv files.
# It's useful for render per players statistics from a soccer match.
#
# Just enter your passes sequences into the input.txt file (there is an example in commentary mode).
# You can comment a sequence by adding a * at the beginning of the line.
# Then execute this program and you will get two csv files, one for the passes and one for the statistics.
#
#       FRANCAIS
#
# Ce programme convertit un fichier texte en deux fichiers csv.
# Il est utile pour afficher les statistiques par joueurs d'un match de foot.
#
# Entrez simplement vos séquences de passes dans le fichier input.txt (il y a un exemple en mode commentaire).
# Vous pouvez commenter une séquence en ajoutant un * au début de la ligne.
# Ensuite, exécutez ce programme et vous obtiendrez deux fichiers csv, un pour les passes et un pour les statistiques.
#
#
# Python 3.9 (venv) required
#
####################################################################################################

import json


SYMBOLS = ["but", "tc", "tnc", "/", "to", "gd"]


def starts_with_a_symbol(string):
    return any(string.startswith(symbol) for symbol in SYMBOLS)


def ends_with_a_symbol(string):
    return any(string.endswith(symbol) for symbol in SYMBOLS)


def get_symbol(string):
    if starts_with_a_symbol(string):
        return string.split(" ")[0]
    else:
        return string.split(" ")[1]


def get_player(string):
    if starts_with_a_symbol(string):
        return string.split(" ")[1].split("-")[0]
    else:
        return string.split(" ")[0].split("-")[-1]


def get_players(string):
    temporary_string = ""
    for char in string.split("-"):
        temporary_string += get_player(char) + "-"
    return temporary_string.split("-")[0:-1]


STATS_FILE = open("input.txt", "r")
STATS_RENDERING_FILE = open("stats_rendering.json", "w")
PASSES_RENDERING_FILE = open("passes_rendering.json", "w")

stats_per_player = {}
given_passes_per_player = {}
received_passes_per_player = {}

all_players = []

for action in STATS_FILE.read().splitlines():
    if action.startswith("*"):
        continue
    PLAYER_MOVES = action.split("-")

    for moveIndex in range(PLAYER_MOVES.__len__()):
        move = PLAYER_MOVES[moveIndex]

        if moveIndex == 0:
            if get_player(move) in stats_per_player:
                if "recovered" in stats_per_player[get_player(move)]:
                    stats_per_player[get_player(move)]["recovered"] += 1
                else:
                    stats_per_player[get_player(move)]["recovered"] = 1
            else:
                stats_per_player[get_player(move)] = {"recovered": 1}

        if get_player(move) not in all_players:
            all_players.append(get_player(move))

        if get_player(move) in stats_per_player:
            if "played" in stats_per_player[get_player(move)]:
                stats_per_player[get_player(move)]["played"] += 1
            else:
                stats_per_player[get_player(move)]["played"] = 1
        else:
            stats_per_player[get_player(move)] = {"played": 1}

        if starts_with_a_symbol(move) or ends_with_a_symbol(move):
            if get_symbol(move) == "but":
                assistant = get_player(PLAYER_MOVES[moveIndex - 1])
                if assistant in stats_per_player:
                    if "assist" in stats_per_player[assistant]:
                        stats_per_player[assistant]["assist"] += 1
                    else:
                        stats_per_player[assistant]["assist"] = 1
                else:
                    stats_per_player[assistant] = {"assist": 1}
            if get_player(move) in stats_per_player:
                if get_symbol(move) in stats_per_player[get_player(move)]:
                    stats_per_player[get_player(move)][get_symbol(move)] += 1
                else:
                    stats_per_player[get_player(move)][get_symbol(move)] = 1
            else:
                stats_per_player[get_player(move)] = {get_symbol(move): 1}

    players_in_chain = get_players(action)
    i = 0
    while i < players_in_chain.__len__() - 1:
        passer, receiver = players_in_chain[i], players_in_chain[i + 1]
        if passer in given_passes_per_player:
            if receiver in given_passes_per_player[passer]:
                given_passes_per_player[passer][receiver] += 1
            else:
                given_passes_per_player[passer][receiver] = 1
        else:
            given_passes_per_player[passer] = {receiver: 1}

        if receiver in received_passes_per_player:
            if passer in received_passes_per_player[receiver]:
                received_passes_per_player[receiver][passer] += 1
            else:
                received_passes_per_player[receiver][passer] = 1
        else:
            received_passes_per_player[receiver] = {passer: 1}

        i += 1


STATS_RENDERING_FILE.write(json.dumps(stats_per_player, indent=4))
PASSES_RENDERING_FILE.write(json.dumps({"given": given_passes_per_player, "received": received_passes_per_player}, indent=4))
STATS_RENDERING_FILE, PASSES_RENDERING_FILE = open("stats_rendering.json", "r"), open("passes_rendering.json", "r")

stats_json, passes_json = json.load(STATS_RENDERING_FILE), json.load(PASSES_RENDERING_FILE)

STATS_CSV, PASSES_CSV = open("stats_rendering.csv", "w+"), open("passes_rendering.csv", "w+")

stats_csv_table = "[Numéro joueur],Ballons joués,Ballons perdus,% de passe,Ballons récupérés,Tirs,Tirs cadrés,Passes décisives,Buts\n"
for player in all_players:
    stats_csv_table += f"{player}"
    played, lost, recovered, shots_on_target, shots_not_in_target, assists, goals = 0, 0, 0, 0, 0, 0, 0

    if player in stats_json:
        if "played" in stats_json[player]:
            played = stats_json[player]["played"]
        if "/" in stats_json[player]:
            lost = stats_json[player]["/"]
        if "recovered" in stats_json[player]:
            recovered = stats_json[player]["recovered"]
        if "tc" in stats_json[player]:
            shots_on_target = stats_json[player]["tc"]
        if "tnc" in stats_json[player]:
            shots_not_in_target = stats_json[player]["tnc"]
        if "assist" in stats_json[player]:
            assists = stats_json[player]["assist"]
        if "but" in stats_json[player]:
            goals = stats_json[player]["but"]

    passes_percent = (100 - lost * 100 / played) if played > 0 else 0
    shots = shots_on_target + (shots_not_in_target - shots_on_target)

    stats_csv_table += f",{played},{lost},{passes_percent},{recovered},{shots},{shots_on_target},{assists},{goals}\n"
STATS_CSV.write(stats_csv_table)

passes_csv_table = f"[Numéro joueur],{','.join([player for player in all_players])}\n"
for player in all_players:
    passes_csv_table += f"{player}"
    for receiver in all_players:
        passes_done_to_receiver = 0

        if player in passes_json['given']:
            if receiver in passes_json["given"][player]:
                passes_done_to_receiver = passes_json["given"][player][receiver]

        if player == receiver:
            passes_done_to_receiver = "XXX"

        passes_csv_table += f",{passes_done_to_receiver}"
    passes_csv_table += "\n"

PASSES_CSV.write(passes_csv_table)