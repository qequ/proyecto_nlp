import requests
from bs4 import BeautifulSoup
import json


def search_movie_href(search_param: str):
    # Search the href of a movie given an aproximate movie name
    # if there is no match returns an empty string

    r = requests.post(url="https://imsdb.com/search.php",
                      data={"search_query": search_param})

    soup = BeautifulSoup(r.text, 'html.parser')

    info_td = soup.find(string="Search results for '{}'".format(
        search_param)).find_parent("td")

    # we get the first of the list
    p = info_td.find('p')

    if p == None:
        return ''

    return p.find('a', href=True)['href']


def get_genres_and_href_script(search_href: str):
    # return a list of genres of the movie and the href for the script

    genres = []  # genres list
    script_href = ''

    r = requests.get(url="https://imsdb.com{}".format(search_href))

    soup = BeautifulSoup(r.text, 'html.parser')
    movie_data = soup.find_all("table", {"class": "script-details"})

    anchors = movie_data[0].find_all("a")

    for data in anchors:
        if 'writer' in data['href']:
            # anchor about the writer we are not interested about
            continue

        if 'genre' in data['href']:
            # the href has the pattern /genre/{movie_genre}
            genres.append(data['href'].split('/')[2])

        if 'scripts' in data['href']:
            script_href = data['href']

    return genres, script_href


def get_script(script_href):
    # returns the movie script as a string
    script_string = ''

    r = requests.get(url="https://imsdb.com{}".format(script_href))

    soup = BeautifulSoup(r.text, 'html.parser')

    td_script_children = soup.find("td", {"class": "scrtext"}).findChildren()
    for elem in td_script_children[0]:
        if elem.name == 'script':
            continue
        script_string += "{}\n".format(elem.text)

    return script_string


def scrap_movies(movie_list):
    # takes a movie_list file and returns a json with movie genres and script

    scrapped_data = {}

    with open(movie_list, 'r') as f:
        file_data = f.read()
    movie_list = file_data.split('\n')

    for movie in movie_list:
        search_href = search_movie_href(movie)

        if search_href == '':
            # the movie has not been found
            continue

        genres, script_href = get_genres_and_href_script(search_href)
        script = get_script(script_href)

        scrapped_data[movie] = {'genres': genres, 'script': script}

    return scrapped_data


if __name__ == '__main__':
    movies_dict = scrap_movies("movie_list.txt")
    with open('movies_scripts.json', "w") as f:
        json.dump(movies_dict, f)
