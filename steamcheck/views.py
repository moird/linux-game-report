from steamcheck import app
from flask import jsonify, render_template
import os
import steamapi
import json


@app.route('/')
def index():
    return render_template("index.html")


@app.route('/report/<name>')
def report(name=None):
    """
    This will generate the report based on the users Steam ID.  Returns JSON
    :param name: Steam ID (either numerical ID or vanity url: steamcommunity.com/id/moird
    :return: Json object that contains listing of all linux games and general information about them:
    {
        "steamuser": "real steam name",
        "image": "steam user image url",
        "games": [{'gametitle', {"linux":true}}]
        "error": ""
    }
    """
    process_report = {}
    try:
        # See if we are running on heroku or not.  Could probably set an environment variable for this as well.
        if os.path.exists('/app/assets/GAMES.json'):
            linux_game_list = '/app/assets/GAMES.json'
            winehq_list = '/app/assets/winehq.json'
        else:
            linux_game_list = './assets/GAMES.json'
            winehq_list = './assets/winehq.json'

        with open(linux_game_list) as linux_game_list_raw:
            linux_games = json.load(linux_game_list_raw)

        with open(winehq_list) as winehq_raw:
            winehq_apps = json.load(winehq_raw)

        steam_connection = steamapi.core.APIConnection(api_key=os.environ['steam_api_key'])

        try:
            user = steamapi.user.SteamUser(userid=int(name))
        except ValueError:
            # When we get further this as a fallback will be taken out, really don't want to do this.
            user = steamapi.user.SteamUser(userurl=name)

        process_report['steamuser'] = user.name
        process_report['image'] = user.avatar
        process_report['games'] = {}
        for game in user.games:
            linux = False
            winehq = False
            if str(game.id) in linux_games:
                linux = True
            if game.name in winehq_apps:
                winehq = winehq_apps[game.name]
            process_report['games'][game.id] = {"name": game.name, "linux": linux, "winehq":winehq}
    except Exception as e:
        process_report['error'] = e
    return jsonify(**process_report)