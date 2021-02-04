# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
import re 
import requests
import json
import os
import sqlite3
import random

professors = {
    "professor Kowalski": "B111",
    "doktor Nowak": "A321"
}
db = sqlite3.connect('actions\db.db')

class ActionShowFloor(Action):

    def name(self) -> Text:
        return "action_show_floor"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        class_number_slot = tracker.get_slot("class_number")

        class_number = re.search("\d", class_number_slot) 

        if class_number.group(0) == '1': 
            dispatcher.utter_message(text="The class "+ class_number_slot+" is on the ground floor.")
        elif class_number.group(0) == '2':
            dispatcher.utter_message(text="The class "+class_number_slot +" is on the first floor.")
        elif class_number.group(0) == '3': 
            dispatcher.utter_message(text="The class "+class_number_slot +" is on the second floor.")

        

        return []
class ActionFindProfessor(Action):

    def name(self) -> Text:
        return "action_find_professor"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        professors = {
        "professor Kowalski": "B111",
        "doktor Nowak": "A321"
        }
        c = db.cursor()
        professor_name_slot = tracker.get_slot("professors").split(" ")
        c.execute("SELECT * FROM professors")
        rows = c.fetchall()
        for row in rows: 
            if row[1].find(professor_name_slot[1]) != -1: 
                dispatcher.utter_message(text=row[1]+" has office hours in room "+row[2]+". And here is the email: "+row[3])
            else: 
                dispatcher.utter_message(text="Could not find a professor. Please try again.")
        
        return []    
class ActionRestaurants(Action):
    def name(self) -> Text: 
        return "action_restaurants"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        city_slot = tracker.get_slot("city")
        print(city_slot)

        if city_slot is None: 
            dispatcher.utter_message(text="Could not find city. Type the name again.")
        else: 
            API_KEY = '2627418a4b420f092e622415db65827c'
            url_cities = 'https://developers.zomato.com/api/v2.1/cities?q='+city_slot
            header = {"User-agent": "curl/7.43.0", "Accept": "application/json", "user_key": API_KEY}
            response = requests.get(url_cities, headers=header)
            json = response.json()
            id = json['location_suggestions'][0]['id']
            dispatcher.utter_message(text="Your city is "+json['location_suggestions'][0]['name'] + ".What kind of cuisine do you like?")

class ActionRestaurantsRecommend(Action):
    def name(self) -> Text: 
        return "action_restaurants_recommend"
    
    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        city_slot = tracker.get_slot("city")
        #print(city_slot)
        food_slot = tracker.get_slot("food")
        print(food_slot)

        if city_slot is None: 
            dispatcher.utter_message(text="Could not find city. Type the name again.")
        else: 
            API_KEY = '2627418a4b420f092e622415db65827c'
            url_cities = 'https://developers.zomato.com/api/v2.1/cities?q='+city_slot
            header = {"User-agent": "curl/7.43.0", "Accept": "application/json", "user_key": API_KEY}
            response = requests.get(url_cities, headers=header)
            json = response.json()
            id = json['location_suggestions'][0]['id']

            url_search = 'https://developers.zomato.com/api/v2.1/search?entity_id='+str(id)+'&entity_type=city&q='+food_slot.lower()+'&sort==cost&order=asc'  
            header = {"User-agent": "curl/7.43.0", "Accept": "application/json", "user_key": API_KEY}
            print(url_search)
            response = requests.get(url_search, headers=header)
            json_restaurants = response.json()
            how_many = int(json_restaurants["results_shown"])
            random_number = random.randint(0, how_many)
            name = json_restaurants['restaurants'][random_number]['restaurant']['name']
            url_site = json_restaurants['restaurants'][random_number]['restaurant']['url']
            address = json_restaurants['restaurants'][random_number]['restaurant']['location']['address']
            dispatcher.utter_message(text="Here is a recommended restaurant for you. It is called "+name+". Here is some information about it: "+url_site+". The address is: "+address+".")   
        
        

