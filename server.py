import requests, json
def get_matches(tournament_id):
  matches = []
  response = requests.get(f'https://api.challonge.com/v1/tournaments/{tournament_id}/matches.json', params={"api_key": "q1zaMKGU0PGgNoL2DzZJLXGHXiaQLMFMAM4Huxap"},
                          headers={"User-Agent": "PostmanRuntime/7.29.0"})
  data_json = json.loads(response.text)
  for match in data_json:
      matches.append({"id": match['match']['id'], 'player1_id': match['match']['player1_id'],
                "player2_id": match['match']["player2_id"], "round": match['match']['round'],
                "winner_id": match['match']["winner_id"]})
  return matches

def set_winner(tournament_id, match_id, winner_id: str):
    match = json.loads(requests.get(f'https://api.challonge.com/v1/tournaments/{tournament_id}/matches/{match_id}.json',
                               params={"api_key": "q1zaMKGU0PGgNoL2DzZJLXGHXiaQLMFMAM4Huxap"},
                               headers={"User-Agent": "PostmanRuntime/7.29.0"}).text)
    if match['match']['player1_id'] == winner_id:
        score = "1-0"
    else: score = "0-1"
    response = requests.put(f'https://api.challonge.com/v1/tournaments/{tournament_id}/matches/{match_id}.json',
                          params={"api_key": "q1zaMKGU0PGgNoL2DzZJLXGHXiaQLMFMAM4Huxap",
                                  "match[winner_id]": winner_id, "match[scores_csv]": score},
                          headers={"User-Agent": "PostmanRuntime/7.29.0"})
    return response.status_code

def start_tournament(tournament_id):
    response = requests.post(f'https://api.challonge.com/v1/tournaments/{tournament_id}/start.json',
                             params={"api_key": "q1zaMKGU0PGgNoL2DzZJLXGHXiaQLMFMAM4Huxap"},
                             headers={"User-Agent": "PostmanRuntime/7.29.0"})
    return response.status_code

print(set_winner(11329318, 280540812, 174301808))