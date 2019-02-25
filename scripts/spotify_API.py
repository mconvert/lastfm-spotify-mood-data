import requests
import base64
import json
import csv
import keys

def spotify_search_request(query, token):
	""" I: string - query of artist and track name
		   string - spotify access token
		O: spotify request response
	"""
	url = 'https://api.spotify.com/v1/search'
	auth = 'Bearer ' + token

	headers = {'Accept': 'application/json', 'Content-Type': 'application/json', 'Authorization': auth}
	params = (('q', query), ('type', 'track'), ('limit', 1), ('market', 'JP'))

	response = requests.get(url, headers=headers, params=params)
	return response


def spotify_request_access_token():
	""" O: string - new access token
	"""
	client_id = keys.client_id()
	client_secret = keys.client_secret()
	auth_string = client_id+':'+client_secret
	auth = base64.b64encode(auth_string.encode("utf-8")).decode("utf-8")

	auth = 'Basic ' + auth

	headers = {'Authorization': auth}
	data = {'grant_type': 'client_credentials'}

	response = requests.post('https://accounts.spotify.com/api/token', headers=headers, data=data)
	resp_json = response.json()

	return resp_json["access_token"]


def song_found(content):
	if content["tracks"]["total"] == 0:
		return False
	else:
		return True


def parse_csv_data(file):
	with open(file) as f:
		data = [{k: v for k, v in row.items()}
			for row in csv.DictReader(f, skipinitialspace=True)]
	return data


def setup_output_csv(outfile):
	categories = "artist,track,g12,g15,g5,g32,g2,g16,g28,g17,g14,g6,g8,g29,g25,g9,g7,g11,g31,g1,on_spotify,sample_url\n"
	with open(outfile, 'w') as f:
		f.write(categories)


def record_entry(outfile, e):
	with open(outfile, 'a') as f:
		if ',' in e["artist"]:
			e["artist"] = '"' + str(e["artist"]) + '"'
		if ',' in e["track"]:
			e["track"] = '"' + str(e["track"]) + '"'
		out_entry = "{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{}\n".format(e["artist"], e["track"], e["g12"], e["g15"],e["g5"],e["g32"],e["g2"],e["g16"],e["g28"],e["g17"],e["g14"],e["g6"],e["g8"],e["g29"],e["g25"],e["g9"],e["g7"],e["g11"],e["g31"],e["g1"],e["on_spotify"],e["sample_url"])
		f.write(out_entry)

def create_availability_entry(entry, availability, url):
	out_entry = dict(entry)
	out_entry["on_spotify"] = availability
	out_entry["sample_url"] = url
	return out_entry


def get_sample_url(content):
	return content["tracks"]["items"][0]["preview_url"]


if __name__ == "__main__":

	token = spotify_request_access_token()

	data_file = "../data/lastfm_mood.csv"
	mood_data = parse_csv_data(data_file)

	out_file = "../data/lastfm_mood_spotify.csv"
	setup_output_csv(out_file)

	for i, entry in enumerate(mood_data):
		artist = entry["artist"]
		track = entry["track"]

		query = artist + " " + track

		while (True):

			response = spotify_search_request(query, token)
			resp_json = response.json()

			if response.status_code == 200: # if 200
				if song_found(resp_json):
					
					sample_url = get_sample_url(resp_json)

					if sample_url == None:
						availability = False
						print("{} Found - NO PREVIEW: {} | {} ".format(i, artist, track))
					else:
						availability = True
						print("{} Found - WITH PREVIEW: {} | {} ".format(i, artist, track))
				else:
					print("{} Not Found: {} | {} ".format(i, artist, track))
					availability = False
					sample_url = None

				out_entry = create_availability_entry(entry, availability, sample_url)
				record_entry(out_file, out_entry)	
				break

			else:
				if response.status_code == 401: # token expired
					print("{} Error: {}".format(i, response.status_code))
					token = spotify_request_access_token()
				elif response.status_code == 429: # too many requests
					print("{} Error: {}".format(i, response.status_code))
				else:
					print("{} Error: {}".format(i, response.status_code))
				



