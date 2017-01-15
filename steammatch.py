import requests

# Get the Steam API key from steamapi.txt
f = open("steamapi.txt", "r")
key = f.read()
f.close()
del f

class InvalidVanityURLError(Exception):
    def __init__(self, error, vanity):
        self.error = error
        self.vanity = vanity

class SteamGame:
    def __init__(self, d: dict):
        self.appid = int(d["appid"])
        self.name = d["name"]
        self.icon = d["img_icon_url"]
        self.grid = d["img_logo_url"]

    def __hash__(self) -> int:
        return self.appid

    def __eq__(self, other) -> bool:
        return self.appid == other.appid


def resolve_vanity(name: str) -> int:
    r = requests.get("http://api.steampowered.com/ISteamUser/ResolveVanityURL/v0001/?key={key}&vanityurl={name}".format(key=key, name=name))
    if r.status_code != 200:
        raise Exception("Error during the API request: " + str(r.status_code) + "\n" + str(r.content))
    j = r.json()["response"]
    if j["success"] == 42:
        raise InvalidVanityURLError("Vanity url not found", name)
    elif j["success"] != 1:
        raise Exception("Unknown exception: {message}".format(message=j["message"]))
    return j["steamid"]


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
    data = r.json()
    owned = list()
    for game in data["response"]["games"]:
        owned.append(SteamGame(game))
    return owned


def and_games(steamids: list) -> set:
    for index, player in enumerate(steamids):
        try:
            steamids[index] = int(player)
        except ValueError:
            steamids[index] = int(resolve_vanity(player))
    current = set(get_steam_games_owned(steamids.pop(0)))
    for player in steamids:
        current = current & set(get_steam_games_owned(player))
    return current


def or_games(steamids: list) -> set:
    for index, player in enumerate(steamids):
        try:
            steamids[index] = int(player)
        except ValueError:
            steamids[index] = int(resolve_vanity(player))
    current = set(get_steam_games_owned(steamids.pop(0)))
    for player in steamids:
        current = current | set(get_steam_games_owned(player))
    return current


def diff_games(first, second):
    try:
        first = int(first)
    except ValueError:
        first = int(resolve_vanity(first))
    try:
        second = int(second)
    except ValueError:
        second = int(resolve_vanity(second))
    result = set(get_steam_games_owned(first)) - set(get_steam_games_owned(second))
    return result


def xor_games(first, second):
    try:
        first = int(first)
    except ValueError:
        first = int(resolve_vanity(first))
    try:
        second = int(second)
    except ValueError:
        second = int(resolve_vanity(second))
    result = set(get_steam_games_owned(first)) ^ set(get_steam_games_owned(second))
    return result
