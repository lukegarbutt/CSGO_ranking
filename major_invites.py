import requests
from bs4 import BeautifulSoup
import operator
from operator import itemgetter

def fetch_events_links(url, min_prize_pool=200000):
    tournament_link_list = []
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'html5lib')
    tournament_table = soup.find(class_='divTable table-full-width tournament-card')
    for tournament in tournament_table.find_all(class_='divRow'):
        try:
            prize_money = tournament.find(class_='Prize').text[1:].strip().replace(',','')
        except Exception as e:
            print(e)
            prize_money = 0
        if int(prize_money) > min_prize_pool:
            tournament_link_list.append('https://liquipedia.net' + tournament.find('b').find('a')['href'])
    return(tournament_link_list)

def process_event(url, list_of_player_dicts):
    print(url)
    dict_of_player_winnings = list_of_player_dicts[1]
    dict_of_player_teams = list_of_player_dicts[0]
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'html5lib')
    list_of_player_ints = ['1', '2', '3', '4', '5']
    list_of_team_info = []
    for teamcard in soup.find_all(class_='teamcard'):
        team_name = teamcard.find('center').find('b').text.strip()
        players = []
        for row in teamcard.find_all('tr'):
            # print(row.text)
            # print(row.text[0])
            try:
                if row.text[0] in list_of_player_ints:
                    player_text = row.text.replace(u'\xa0', u' ')
                    # print(player_text.split(' '))
                    if player_text != 'TBD':
                        players.append(player_text.split(' ')[1])
            except Exception as e:
                pass
        if team_name != 'TBD':
            list_of_team_info.append([team_name, players])
    results_table = soup.find(class_='prizepooltable')
    for row in results_table.find_all('tr'):
        cells = row.find_all('td')
        if len(cells) == 3:
            prize_money = cells[1].text[1:]
        try:
            team_name_ = row.find(class_='team-template-text').text.strip()
            for item in list_of_team_info:
                if item[0] == team_name_:
                    player_share = int(prize_money.replace(',', '')) / len(item[1])
                    for player in item[1]:
                        if player in dict_of_player_winnings:
                            dict_of_player_winnings[player] += player_share
                        else:
                            dict_of_player_winnings[player] = player_share
                        dict_of_player_teams[player] = team_name_
        except Exception as e:
            pass
    list_of_player_dicts = [dict_of_player_teams, dict_of_player_winnings]
    return list_of_player_dicts


def rank_teams(list_of_player_winnings, dict_of_player_teams, dict_of_player_winnings):
    dict_of_team_winnings = {}
    dict_of_team_lineup = {}
    for item in list_of_player_winnings:
        if item[0] in dict_of_player_teams:
            if dict_of_player_teams[item[0]] in dict_of_team_winnings:
                dict_of_team_winnings[dict_of_player_teams[item[0]]] += item[1]
            else:
                dict_of_team_winnings[dict_of_player_teams[item[0]]] = item[1]
            if dict_of_player_teams[item[0]] in dict_of_team_lineup:
                dict_of_team_lineup[dict_of_player_teams[item[0]]].append(item[0])
            else:
                dict_of_team_lineup[dict_of_player_teams[item[0]]] = [item[0]]

    print(dict_of_team_winnings)
    print(dict_of_team_lineup)
    sorted_dict = sorted(dict_of_team_winnings.items(), key=operator.itemgetter(1))
    print(sorted_dict)


dict_of_player_winnings = {}
dict_of_player_teams = {}
list_of_player_dicts = [dict_of_player_teams, dict_of_player_winnings]
for url in fetch_events_links('https://liquipedia.net/counterstrike/Premier_Tournaments', 200000):
    if url == 'https://liquipedia.net/counterstrike/World_Electronic_Sports_Games/2017':
        continue
    list_of_player_dicts = process_event(url, list_of_player_dicts)

list_of_player_winnings = []
for item in list_of_player_dicts[1]:
    list_of_player_winnings.append([item, list_of_player_dicts[1][item]])


list_of_player_winnings = sorted(list_of_player_winnings, key=lambda player_item: player_item[1], reverse=True)
print(list_of_player_winnings)
print(dict_of_player_teams)
rank_teams(list_of_player_winnings, dict_of_player_teams, dict_of_player_winnings)