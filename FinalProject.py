#Title: Final Project git hub:https://github.com/snsarnow/206finalproject
#Ticket Master api key:  vpuocOuAAzZoQtLZalLRNHbMxxuecGWU
 
from textwrap import indent
import matplotlib.pyplot as plt
import requests
import sqlite3
import json
import os


#GET INFO FROM API
def get_events_ticket_master():
    pages_lst=[1,2,3,4]
    lst_events =[]
    for page in pages_lst:
        baseURL='https://app.ticketmaster.com/discovery/v2/events.json?apikey=vpuocOuAAzZoQtLZalLRNHbMxxuecGWU&size=200&page={}&classificationName=Music'
        formatedURL = baseURL.format(page)
        #print(formatedURL)
        response_API = requests.get(formatedURL)
        data = json.loads(response_API.text)
        #print(data['_embedded'])
        #print("NEW PAGE __________________")
        for i in range(len(data['_embedded']['events'])):
            lst_events.append(data['_embedded']['events'][i])
    #print(len(lst_events))
    event_concert_lst=[]
    for i in range(len(lst_events)):
        event_classification_id= lst_events[i]['classifications'][0]['segment']['id']
        if event_classification_id == 'KZFzniwnSyZfZ7v7nJ':
            if 'priceRanges' in lst_events[i]:
                if 'name' in lst_events[i]['_embedded']['venues'][0]:
                    event_concert_lst.append(lst_events[i])
    
    #print(len(event_concert_lst))
    return event_concert_lst



# Create Ticket_masker Database
def setUpDatabase(db_name):
    path = os.path.dirname(os.path.abspath(__file__))
    conn = sqlite3.connect(path+'/'+db_name)
    cur = conn.cursor()
    return cur, conn



# CREATE TABLE FOR TICKET MASTER INFORMATION IN DATABASE AND ADD INFORMATION
def create_TicketMaster_table(cur, conn):
    cur.execute("CREATE TABLE IF NOT EXISTS TicketMasterEvents (event_id TEXT UNIQUE PRIMARY KEY, event_title TEXT, date TEXT, location TEXT, max_price INTEGER, min_price INTEGER)")
    conn.commit()

# ADD EVENT INFORMATION 
def add_ticket_master_event_info(data, cur, conn):
    for event in data:
        id = event['id']
        title= event['name']
        date = event['dates']['start']['localDate']
        location = event['_embedded']['venues'][0]['name']
        min_price= int(event['priceRanges'][0]['max'])
        max_price = int(event['priceRanges'][0]['min'])
        cur.execute(
            """
            INSERT OR IGNORE INTO TicketMasterEvents (event_id, event_title, date, location, max_price, min_price)
            VALUES (?, ?, ?, ?,?, ?)
            """,
            (id, title, date, location, min_price, max_price,)
        )
    conn.commit()


#CALCULATE AVERAGE PRICE
def TM_avg_price(cur, conn):
    cur.execute("""SELECT event_title, max_price, min_price
    FROM TicketMasterEvents
    """ )
    res = cur.fetchall()

    all_avgs = []
    for event in res:
        avg_price = (event[1] + event[2])/2
        event_avg = "Concert: " + event[0] + ", Average Price: " + str(avg_price)
        all_avgs.append(event_avg)
    
    with open("TM_avg_prices.txt", "w") as outfile:
        for avg in all_avgs:
            json_obj = json.dumps(avg)
            outfile.write(json_obj)
            outfile.write('\n')



#MAIN FUNCTION 
print("START MAIN CALL")

TM_concert_lst= get_events_ticket_master()
print("CONCERT LST DONE")

#print(TM_concert_lst[0])
#print(TM_concert_lst[0].keys())

cur,conn= setUpDatabase("ticket_master.db")
print("set up database  DONE")

create_TicketMaster_table(cur, conn)
print("create table  DONE")

add_ticket_master_event_info(TM_concert_lst, cur, conn)
print ("Add events to table DONE")

TM_avg_price(cur, conn)
print("avg price txt DONE")