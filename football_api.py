import requests
from apikey import apiFootballKey
from premier_league_teams import teams_mapping

api_base = "https://api-football-v1.p.rapidapi.com/v3"

headers = {
    "X-RapidAPI-Key": apiFootballKey,
    "X-RapidAPI-Host": "api-football-v1.p.rapidapi.com"
}


def get_fixtures(team, number=1):
    team_id = teams_mapping[team]
    querystring = {"team":team_id,"season":"2023", "next":str(number)}
    url = api_base + "/fixtures"
    response = requests.get(url, headers=headers, params=querystring).json()
    fixture_id = response['response'][0]['fixture']['id']
    home = response['response'][0]['teams']['home']
    away = response['response'][0]['teams']['away']
    return {'id':fixture_id, 'home': home['name'], 'home_id': home['id'], 'away':away['name'], 'away_id': away['id']}


def get_odds(fixture_id):
    querystring = {"fixture":fixture_id}
    url = api_base + "/odds"
    response = requests.get(url, headers=headers, params=querystring).json()
    response = response['response'][0]
    match_winner_odds = {}
    for bookmaker in response['bookmakers']:
        for bet in bookmaker['bets']:
            if bet['name'] == "Match Winner":
                match_winner_odds[bookmaker['name']] = bet['values']

    home_total = 0
    draw_total = 0
    away_total = 0
    bookmaker_count = len(response['bookmakers'])

    # Iterate through each bookmaker's odds
    for bookmaker, odds in match_winner_odds.items():
        for odd in odds:
            if odd['value'] == 'Home':
                home_total += float(odd['odd'])
            elif odd['value'] == 'Draw':
                draw_total += float(odd['odd'])
            elif odd['value'] == 'Away':
                away_total += float(odd['odd'])

    # Calculate averages
    avg_home = round(home_total / bookmaker_count, 2)
    avg_draw = round(draw_total / bookmaker_count, 2)
    avg_away = round(away_total / bookmaker_count, 2)

    return {'home_win': avg_home, 'draw': avg_draw, 'away_win': avg_away}

def get_team_stats(team_id):
    querystring = {"league":"39","season":"2023","team":str(team_id)}
    url = api_base + "/teams/statistics"
    response = requests.get(url, headers=headers, params=querystring).json()
    response = response['response']

    form_clean = '-'.join('Win' if char == 'W' else 'Loss' if char == 'L' else 'Draw' for char in response['form'][::-1])
    return {'form': form_clean, 'failed_to_score': response['failed_to_score'], 'clean_sheet': response['clean_sheet']}

def get_match_details(input):
    fixture = get_fixtures(input)
    odds = get_odds(fixture['id'])
    home_stats = get_team_stats(fixture['home_id'])
    away_stats = get_team_stats(fixture['away_id'])

    out = f'''The game is between {fixture['home']} (home) and {fixture['away']}.
    These are the odds: {odds}.
    Here are some stats for {fixture['home']}: {home_stats}.
    Here are some stats for {fixture['away']}: {away_stats}.'''
    return out

