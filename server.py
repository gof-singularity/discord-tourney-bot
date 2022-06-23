from multiprocessing import Process

import requests, json
from PIL import Image
import cairosvg
import os
from html2image import Html2Image
hti = Html2Image()
import bs4
def create_tournament(tournament_name):
    response = requests.post(f'https://api.challonge.com/v1/tournaments.json',
                             params={"api_key": "q1zaMKGU0PGgNoL2DzZJLXGHXiaQLMFMAM4Huxap",
                                     "tournament[name]": tournament_name,
                                     "tournament[tournament_type]": "round robin",
                                     "tournament[open_signup]": "false",
                                     "tournament[ranked_by]": "points scored",
                                     "tournament[start_at]": "2022-06-22T03:00:00"},
                             headers={"User-Agent": "PostmanRuntime/7.29.0"})
    return json.loads(response.text)['tournament']['id']

def add_participants(tournament_id, participant_name):
    response = requests.post(f'https://api.challonge.com/v1/tournaments/{tournament_id}/participants/bulk_add.json',
                             params={"api_key": "q1zaMKGU0PGgNoL2DzZJLXGHXiaQLMFMAM4Huxap",
                                     "participants[][name]": participant_name},
                             headers={"User-Agent": "PostmanRuntime/7.29.0"})
    if response.status_code==200:
        return f"Player **{participant_name}** was successfully added"
    else:
        return f"Error, player {participant_name} already exists or some other problem"

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
    p = Process(target=crop_rounds_images, args=(tournament_id,))
    p.daemon = True
    p.start()
    p.join()
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
    response = requests.get(f"https://api.challonge.com/v1/tournaments/{tournament_id}.json",
                             params={"api_key": "q1zaMKGU0PGgNoL2DzZJLXGHXiaQLMFMAM4Huxap"},
                             headers={"User-Agent": "PostmanRuntime/7.29.0"})
    json_data = json.loads(response.text)
    svg_image = json_data['tournament']['live_image_url']
    participant_count = json_data['tournament']['participants_count']
    svg_code = requests.get(svg_image, params={"api_key": "q1zaMKGU0PGgNoL2DzZJLXGHXiaQLMFMAM4Huxap"},
                            headers={"User-Agent": "PostmanRuntime/7.29.0"})
    if os.path.exists(f'{tournament_id}.png'):
        os.remove(f'{tournament_id}.png')
    cairosvg.surface.PNGSurface.convert(svg_code.text, write_to=f'{tournament_id}.png')
    im = Image.open(f'{tournament_id}.png')
    if im.mode in ('RGBA', 'LA'):
        background = Image.new(im.mode[:-1], im.size, (255, 255, 255))
        background.paste(im, im.split()[-1])
        im = background
    im.convert("RGB").save(f'{tournament_id}.jpg', quality=100)
    final_directory = os.path.join(os.getcwd(), f'{tournament_id}')
    if not os.path.exists(final_directory):
        os.makedirs(final_directory)
    OUTPUT_DIR = f'{tournament_id}'
    im = Image.open(f'{tournament_id}.jpg')
    width, height = im.size
    im_crop = im.crop((0, 108, width, height-75))
    im_crop.save(f'{tournament_id}.jpg', quality=100)
    for i, row in enumerate(split_into_rows(im_crop, im_crop.height/((participant_count*(participant_count-1)/2)//(participant_count//2)))):
        save_path = os.path.join(OUTPUT_DIR, f'{i+1}.jpg')
        row.save(save_path)

def get_round_image(tournament_id, round):
    if os.path.exists(f'{tournament_id}/{round}.jpg'):
        return f'{tournament_id}/{round}.jpg'
    else: return "There is no such tournament or round"

def get_leaderboard(tournament_id):
    response = requests.get(f'https://api.challonge.com/v1/tournaments/{tournament_id}.json',
                            params={"api_key": "q1zaMKGU0PGgNoL2DzZJLXGHXiaQLMFMAM4Huxap"},
                            headers={"User-Agent": "PostmanRuntime/7.29.0"})
    unique_hash = json.loads(response.text)['tournament']['url']
    response2 = requests.get(f'https://challonge.com/{unique_hash}/standings',
                       params={"api_key": "q1zaMKGU0PGgNoL2DzZJLXGHXiaQLMFMAM4Huxap"},
                       headers={"User-Agent": "PostmanRuntime/7.29.0"})
    with open("response.html", "w") as f:
        f.write(response2.text)
    soup = bs4.BeautifulSoup(response2.text, "html")
    div = soup.find("div", {"class": "standings-container"})
    content = str(div)
    hti.screenshot(html_str=content, save_as=f'{tournament_id}_leaderboard.png')
    return f'{tournament_id}_leaderboard.png'


print(get_leaderboard(11331400))
# hti.screenshot(html_file='response.html', save_as='blue_page.png')