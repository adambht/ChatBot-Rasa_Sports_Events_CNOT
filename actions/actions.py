# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

# from typing import Any, Text, Dict, List
#
# from rasa_sdk import Action, Tracker
# from rasa_sdk.executor import CollectingDispatcher
#
#
# class ActionHelloWorld(Action):
#
#     def name(self) -> Text:
#         return "action_hello_world"
#
#     def run(self, dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
#
#         dispatcher.utter_message(text="Hello World!")
#
#         return []


import yaml
from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from pathlib import Path

from fuzzywuzzy import fuzz, process
from rasa_sdk.events import SlotSet


import yaml
from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from pathlib import Path
from fuzzywuzzy import fuzz, process
from rasa_sdk.events import SlotSet


class ActionGetCompetitionInfo(Action):
    def name(self) -> Text:
        return "action_get_competition_info"

    def read_yaml_file(self, file_path: Text) -> List[Dict[Text, Any]]:
        """Reads the YAML file and returns the data as a list of dictionaries."""
        with open(file_path, 'r', encoding='utf-8') as file:
            return yaml.safe_load(file)

    def get_competition_details(self, competition_name: Text, competitions_data: List[Dict[Text, Any]]) -> Dict[Text, Any]:
        """Extracts the competition details from the YAML data based on the competition name."""
        for competition in competitions_data:
            if competition_name.lower() in competition['Competition_Name'].lower():
                return competition
        return {}

    async def run(
            self,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]
    ) -> List[Dict[Text, Any]]:
        competition_name = tracker.get_slot('competition_name')
        latest_message = tracker.latest_message.get('text')

        data_file_path = Path('YAML_FILES/All_Competitions.yaml')
        competitions_data = self.read_yaml_file(data_file_path)
        competition_names = [comp['Competition_Name'] for comp in competitions_data]

        # If a new competition is mentioned in the latest message, update the slot
        closest_match = process.extractOne(latest_message, competition_names, scorer=fuzz.token_sort_ratio)
        if closest_match and closest_match[1] >= 80:
            competition_name = closest_match[0]
            dispatcher.utter_message(text=f"Got it! You're asking about {competition_name}.")
            return [SlotSet("competition_name", competition_name)]

        # Case 1: Asking about the remembered competition's details
        if competition_name:
            competition_details = self.get_competition_details(competition_name, competitions_data)
            if competition_details:
                response = (
                    f"Details for {competition_details['Competition_Name']}:\n"
                    f"Date: {competition_details.get('Date', 'N/A')}\n"
                    f"Location: {competition_details.get('Location', 'N/A')}\n"
                    f"Country: {competition_details.get('Country', 'N/A')}\n"
                    f"Description: {competition_details.get('Description', 'N/A')}\n"
                )
                dispatcher.utter_message(text=response)
            else:
                dispatcher.utter_message(text=f"Sorry, I couldn't find details for {competition_name}.")
            return []

        # Case 2: Asking for event details without specifying a competition
        dispatcher.utter_message(text="Sorry, I didn't catch which competition you're asking about.")
        return []


class ActionGetCompetitionDate(Action):
    def name(self) -> Text:
        return "action_get_competition_date"

    async def run(
            self,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]
    ) -> List[Dict[Text, Any]]:

        competition_name = tracker.get_slot('competition_name')
        date = tracker.get_slot('date')

        data_file_path = Path('YAML_FILES/All_Competitions.yaml')
        competitions_data = ActionGetCompetitionInfo().read_yaml_file(data_file_path)

        # Case 1: Asking about the remembered competition's date
        if competition_name and not date:
            competition_details = ActionGetCompetitionInfo().get_competition_details(competition_name, competitions_data)
            if competition_details and 'Date' in competition_details:
                dispatcher.utter_message(text=f"The competition will be held on {competition_details['Date']}.")
            else:
                dispatcher.utter_message(text=f"Sorry, I couldn't find the date for {competition_name}.")
            return []

        # Case 2: Asking about events happening on a specific date
        if date:
            events_on_date = [comp for comp in competitions_data if comp.get('Date', '').lower() == date.lower()]
            if events_on_date:
                events_list = "\n".join([f"{event['Competition_Name']} in {event.get('Location', 'N/A')}" for event in events_on_date])
                dispatcher.utter_message(text=f"Here are the events happening on {date}:\n{events_list}")
            else:
                dispatcher.utter_message(text=f"Sorry, I couldn't find any events on {date}.")
            return []

        dispatcher.utter_message(text="Sorry, I didn't catch which competition or date you're asking about.")
        return []


class ActionGetCompetitionLocation(Action):
    def name(self) -> Text:
        return "action_get_competition_location"

    async def run(
            self,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]
    ) -> List[Dict[Text, Any]]:

        competition_name = tracker.get_slot('competition_name')
        location = tracker.get_slot('location')

        data_file_path = Path('YAML_FILES/All_Competitions.yaml')
        competitions_data = ActionGetCompetitionInfo().read_yaml_file(data_file_path)

        # Case 1: Asking about the remembered competition's location
        if competition_name and not location:
            competition_details = ActionGetCompetitionInfo().get_competition_details(competition_name, competitions_data)
            if competition_details and 'Location' in competition_details:
                dispatcher.utter_message(text=f"The competition is happening in {competition_details['Location']}.")
            else:
                dispatcher.utter_message(text=f"Sorry, I couldn't find the location for {competition_name}.")
            return []

        # Case 2: Asking about events happening in a specific location
        if location:
            events_in_location = [comp for comp in competitions_data if comp.get('Location', '').lower() == location.lower()]
            if events_in_location:
                events_list = "\n".join([f"{event['Competition_Name']} on {event.get('Date', 'N/A')}" for event in events_in_location])
                dispatcher.utter_message(text=f"Here are the events happening in {location}:\n{events_list}")
            else:
                dispatcher.utter_message(text=f"Sorry, I couldn't find any events in {location}.")
            return []

        dispatcher.utter_message(text="Sorry, I didn't catch which competition or location you're asking about.")
        return []


class ActionGetCompetitionCountry(Action):
    def name(self) -> Text:
        return "action_get_competition_country"

    async def run(
            self,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]
    ) -> List[Dict[Text, Any]]:

        competition_name = tracker.get_slot('competition_name')
        country = tracker.get_slot('country')

        data_file_path = Path('YAML_FILES/All_Competitions.yaml')
        competitions_data = ActionGetCompetitionInfo().read_yaml_file(data_file_path)

        # Case 1: Asking about the remembered competition's country
        if competition_name and not country:
            competition_details = ActionGetCompetitionInfo().get_competition_details(competition_name, competitions_data)
            if competition_details and 'Country' in competition_details:
                dispatcher.utter_message(text=f"The competition is in {competition_details['Country']}.")
            else:
                dispatcher.utter_message(text=f"Sorry, I couldn't find the country for {competition_name}.")
            return []

        # Case 2: Asking for events in a specific country (by country entity)
        if country:
            events_in_country = [comp for comp in competitions_data if comp.get('Country', '').lower() == country.lower()]
            if events_in_country:
                events_list = "\n".join([f"{event['Competition_Name']} on {event.get('Date', 'N/A')}" for event in events_in_country])
                dispatcher.utter_message(text=f"Here are the events happening in {country}:\n{events_list}")
            else:
                dispatcher.utter_message(text=f"Sorry, I couldn't find any events in {country}.")
            return []

        dispatcher.utter_message(text="Sorry, I didn't catch which competition or country you're asking about.")
        return []
