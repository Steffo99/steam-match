import requests

# Get the Steam API key from steamapi.txt
f = open("steamapi.txt", "r")
key = f.read()
f.close()
del f


def get_steam_games_owned(steamid: int, freetoplay=True) -> list:
    # Request the list of games played
    params = {
        "steamid": steamid,
        "key": key,
        "format": "json",
        "include_appinfo": 1
    }
    if freetoplay:
        params["include_played_free_games"] = 1
    r = requests.get("http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/", params=params)
    if r.status_code != 200:
        raise Exception("Error during the API request.")
    # Extract app ids
    games_owned = list()
    data = r.json()
    for game in data["response"]["games"]:
        games_owned.append(game["name"])
    # Return the list
    return games_owned


def and_games(steamids: list):
    current = set(get_steam_games_owned(steamids.pop(0)))
    for player in steamids:
        current = current & set(get_steam_games_owned(player))
    return current


def or_games(steamids: list):
    current = set(get_steam_games_owned(steamids.pop(0)))
    for player in steamids:
        current = current | set(get_steam_games_owned(player))
    return current


def diff_games(first, second):
    current = set(get_steam_games_owned(first, False)) - set(get_steam_games_owned(second, False))
    return current


def xor_games(first, second):
    current = set(get_steam_games_owned(first)) ^ set(get_steam_games_owned(second))
    return current
