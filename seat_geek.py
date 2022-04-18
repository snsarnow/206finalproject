from textwrap import indent
import matplotlib.pyplot as plt
import requests
import sqlite3
import json
import os

#PULL EVENT DATA FROM SEAT GEEK API
def get_events(num_of_pgs):
    url = "https://api.seatgeek.com/2/events?client_id=MjY1NDY4OTd8MTY0OTk0NTE3My42OTY4NTg2&client_secret=a005a2e60e8f8d3e548cc78a3371d72d28b95a3d4b5a3070f41db576d70cd3ad&type=concert&per_page=25&page="+str(num_of_pgs)
    response = requests.get(url)
    data = json.loads(response.content)

    #print(data)
    concerts_only = []
    for event in data['events']:
        if event['type'] == 'concert':
            concerts_only.append(event["id"])
    #MAKE SURE LIST HAS AT LEAST 100 ITEMS
    print(len(concerts_only)) 
    return concerts_only


#CREATE JSON FILE
def create_json(concert_list):
    info_list = []
    for event_id in concert_list:
        base_url = "https://api.seatgeek.com/2/events/{}?client_id=MjY1NDY4OTd8MTY0OTk0NTE3My42OTY4NTg2&client_secret=a005a2e60e8f8d3e548cc78a3371d72d28b95a3d4b5a3070f41db576d70cd3ad"
        formatted_url = base_url.format(event_id)
        response = requests.get(formatted_url)
        information = json.loads(response.content)
        info_list.append(information)
    return info_list

    
# CREATE DATABASE
def setUpDatabase(db_name):
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path+'/'+db_name)
    cur = conn.cursor()
    return cur, conn

# CREATE TABLE FOR EVENT INFORMATION IN DATABASE AND ADD INFORMATION
def create_events_table(cur, conn):
    cur.execute("CREATE TABLE IF NOT EXISTS Seat_Geek_Events (event_id INTEGER UNIQUE PRIMARY KEY, event_title TEXT, performers TEXT, dates TEXT, location TEXT, max_price INTEGER, min_price INTEGER)")
    conn.commit()

def add_events(info, cur, conn):
    for i in info:
        event_id = i['id']
        event_title = i['title']
        performers = i['performers'][0]['name']
        dates = i['datetime_utc']
        location = i['venue']['name_v2']
        max_price = i['stats']['highest_price']
        min_price = i['stats']['lowest_price']
        if max_price is None and min_price is None:
            continue
        else:
            #avg_price = (max_price + min_price)/ 2
            cur.execute("INSERT OR IGNORE INTO Seat_Geek_Events (event_id, event_title, performers, dates, location, max_price, min_price) VALUES (?,?,?,?,?,?,?)", (event_id, event_title, performers, dates, location, max_price, min_price))
            conn.commit() 

#CALCULATING AVERAGE PRICE
def avg_price(cur, conn):
    cur.execute("""SELECT event_title, max_price, min_price
    FROM Seat_Geek_Events 
    """ )
    results = cur.fetchall()

    all_avgs = []
    for cost in results:
        avg_price = (cost[1] + cost[2])/2
        event_avg = "Concert: " + cost[0] + ", Average Price: " + str(avg_price)
        all_avgs.append(event_avg)
    
    with open("avg_prices.txt", "w") as outfile:
        for avg in all_avgs:
            json_obj = json.dumps(avg)
            outfile.write(json_obj)
            outfile.write('\n')

    
#MAXIMUM PRICE VISUAL
def max_price_visual(cur, conn):
    cur.execute("""SELECT event_title, max_price
    FROM Seat_Geek_Events 
    """ )
    results = cur.fetchall()

    x = []
    y = []
    for concert, max_price in results:
        x.append(concert)
        y.append(max_price)
    plt.bar(x,y)
    plt.ylabel('Maximum Ticket Price')
    plt.xlabel('Event title')
    plt.title('Maximum Prices for Concerts')
    plt.show()

#AVERAGE PRICE VISUAL

#MAIN FUNCTION
page_number = input("Page Number: ")
concert_list = get_events(page_number)
info_list = create_json(concert_list)
#print(info_list)
cur, conn = setUpDatabase("seat_geek.db")
create_events_table(cur,conn)
add_events(info_list, cur, conn)
avg_price(cur, conn)
max_price_visual(cur, conn)

