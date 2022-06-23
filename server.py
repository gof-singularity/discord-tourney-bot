import requests, json
from PIL import Image
import cairosvg
import os

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
    # await crop_rounds_images()
    return response.status_code

def get_participants_names_ids(tournament_id):
    res = []
    response = requests.get(f'https://api.challonge.com/v1/tournaments/{tournament_id}/participants.json',
                            params={"api_key": "q1zaMKGU0PGgNoL2DzZJLXGHXiaQLMFMAM4Huxap"},
                            headers={"User-Agent": "PostmanRuntime/7.29.0"})
    data_json = json.loads(response.text)
    for item in data_json:
        res.append({'id':item['participant']['id'], 'username': item['participant']['name']})
    return res

def split_into_rows(im, row_height):
    y = 0
    while y < im.height:
        top_left = (0, y)
        bottom_right = (im.width, min(y + row_height, im.height))
        yield im.crop((*top_left, *bottom_right))
        y += row_height

def crop_rounds_images(tournament_id):
    svg_image = json.loads(requests.get(f"https://api.challonge.com/v1/tournaments/{tournament_id}.json",
                             params={"api_key": "q1zaMKGU0PGgNoL2DzZJLXGHXiaQLMFMAM4Huxap"},
                             headers={"User-Agent": "PostmanRuntime/7.29.0"}).text)['tournament']['live_image_url']
    svg_code = requests.get(svg_image, params={"api_key": "q1zaMKGU0PGgNoL2DzZJLXGHXiaQLMFMAM4Huxap"},
                            headers={"User-Agent": "PostmanRuntime/7.29.0"})
    cairosvg.surface.PNGSurface.convert(svg_code.text, write_to=f'{tournament_id}.png')
    im = Image.open(f'{tournament_id}.png')
    final_directory = os.path.join(os.getcwd(), f'{tournament_id}')
    if not os.path.exists(final_directory):
        os.makedirs(final_directory)
    OUTPUT_DIR = f'{tournament_id}'
    width, height = im.size
    im_crop = im.crop((0, 108, width, height-75))
    im_crop.save(f'{tournament_id}.png', quality=100)
    for i, row in enumerate(split_into_rows(im_crop, 182.5)):
        save_path = os.path.join(OUTPUT_DIR, f'{i+1}.png')
        row.save(save_path)

print(crop_rounds_images(11329318))