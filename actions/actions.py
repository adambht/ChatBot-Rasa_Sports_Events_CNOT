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




from fuzzywuzzy import fuzz, process
from rasa_sdk.events import SlotSet


import yaml
from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from pathlib import Path




class ActionGetCompetitionInfo(Action):
    def name(self) -> Text:
        return "action_get_competition_info"

    async def run(
            self,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]
    ) -> List[Dict[Text, Any]]:

        competition_name = tracker.get_slot('competition_name')


        if not competition_name: # If the competition name is not provided
            dispatcher.utter_message(text="Unfortunately, I couldn't find any details. You should provide a correct one, please let me know which competition you'd like to inquire about.")
            return []

        data_file_path = Path('YAML_FILES/All_Competitions.yaml')
        competitions_data = self.read_yaml_file(data_file_path)

        competition_details = self.get_competition_details(competition_name, competitions_data)

        if competition_details:
            response = f"""
        Event Name: {competition_details['Competition_Name']}  
        Date: {competition_details.get('Date', 'N/A')}  
        Location: {competition_details.get('Location', 'N/A')}  
        Country: {competition_details.get('Country', 'N/A')}  
        Description: {competition_details.get('Description', 'N/A')}  
        """
            dispatcher.utter_message(
                text=response.strip())  # Use two spaces for Markdown line breaks



        else:
            dispatcher.utter_message(text=f"Sorry, I couldn't find details for {competition_name}.")

        return []

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

        # Load the data from your YAML file that contains all the competitions
        data_file_path = Path('YAML_FILES/All_Competitions.yaml')
        competitions_data = ActionGetCompetitionInfo().read_yaml_file(data_file_path)

        # If the competition name exists, fetch its date
        if competition_name:
            competition_details = ActionGetCompetitionInfo().get_competition_details(competition_name, competitions_data)
            if competition_details and 'Date' in competition_details:
                dispatcher.utter_message(text=f"The competition will be held on {competition_details['Date']}.")
            else:
                dispatcher.utter_message(text=f"Sorry, I couldn't find the date for {competition_name}.")
            return []

        # If no competition name is given or remembered
        dispatcher.utter_message(text="Sorry, I didn't catch which competition you're asking about.")
        return []





class ActionGetCompetitionsByDate(Action):
    def name(self) -> Text:
        return "action_get_competitions_by_date"

    async def run(
            self,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]
    ) -> List[Dict[Text, Any]]:

        date = tracker.get_slot('date')

        if not date:
            dispatcher.utter_message(text="Please provide a date to search for events.")
            return []

        data_file_path = Path('YAML_FILES/All_Competitions.yaml')
        competitions_data = ActionGetCompetitionInfo().read_yaml_file(data_file_path)


        events_on_date = [comp for comp in competitions_data if comp.get('Date', '').lower() == date.lower()]
        if events_on_date:
            events_list = "\n".join([f"**{event['Competition_Name']}** in {event.get('Location', 'N/A')}  " for event in events_on_date])  # Added double spaces
            dispatcher.utter_message(text=f"Here are the events happening on {date}:  \n{events_list}")  # Added double space after the colon
        else:
            dispatcher.utter_message(text=f"Sorry, I couldn't find any events on {date}.")
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

        # Load the data from your YAML file that contains all the competitions
        data_file_path = Path('YAML_FILES/All_Competitions.yaml')
        competitions_data = ActionGetCompetitionInfo().read_yaml_file(data_file_path)

        # If the competition name exists, fetch its location
        if competition_name:
            competition_details = ActionGetCompetitionInfo().get_competition_details(competition_name, competitions_data)
            if competition_details and 'Location' in competition_details and 'Country' in competition_details:
                dispatcher.utter_message(text=f"The competition is happening in {competition_details['Location']}, {competition_details['Country']}")
            else:
                dispatcher.utter_message(text=f"Sorry, I couldn't find the location for {competition_name}.")
            return []

        # If no competition name is given or remembered
        dispatcher.utter_message(text="Sorry, I didn't catch which competition you're asking about.")
        return []






class ActionGetCompetitionsByLocation(Action):
    def name(self) -> Text:
        return "action_get_competitions_by_location"

    async def run(
            self,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]
    ) -> List[Dict[Text, Any]]:

        location = tracker.get_slot('location')

        if not location:
            dispatcher.utter_message(text="Please provide a location to search for events.")
            return []

        data_file_path = Path('YAML_FILES/All_Competitions.yaml')
        competitions_data = ActionGetCompetitionInfo().read_yaml_file(data_file_path)

        events_in_location = [comp for comp in competitions_data if comp.get('Location', '').lower() == location.lower()]
        if events_in_location:
            events_list = "\n".join([f"{event['Competition_Name']} on {event.get('Date', 'N/A')}  " for event in events_in_location])
            dispatcher.utter_message(text=f"Here are the events happening in {location}:  \n{events_list}")
        else:
            dispatcher.utter_message(text=f"Sorry, I couldn't find any events in {location}.")
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

        data_file_path = Path('YAML_FILES/All_Competitions.yaml')
        competitions_data = ActionGetCompetitionInfo().read_yaml_file(data_file_path)

        if competition_name:
            competition_details = ActionGetCompetitionInfo().get_competition_details(competition_name, competitions_data)
            if competition_details and 'Country' in competition_details and 'Location' in competition_details:
                dispatcher.utter_message(text=f"The competition is in {competition_details['Country']} ({competition_details['Location']})")
            else:
                dispatcher.utter_message(text=f"Sorry, I couldn't find the country for {competition_name}.")
            return []

        dispatcher.utter_message(text="Sorry, I didn't catch which competition you're asking about.")
        return []



class ActionGetCompetitionsByCountry(Action):
    def name(self) -> Text:
        return "action_get_competitions_by_country"

    async def run(
            self,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]
    ) -> List[Dict[Text, Any]]:

        country = tracker.get_slot('country')

        if not country:
            dispatcher.utter_message(text="Please provide a country to search for events.")
            return []

        # Load the data from your YAML file that contains all the competitions
        data_file_path = Path('YAML_FILES/All_Competitions.yaml')
        competitions_data = ActionGetCompetitionInfo().read_yaml_file(data_file_path)

        # Filter the competitions based on the provided country
        events_in_country = [comp for comp in competitions_data if comp.get('Country', '').lower() == country.lower()]

        if events_in_country:
            # Create a list of events happening in the specified country
            events_list = "\n".join(
                [f"{event['Competition_Name']} on {event.get('Date', 'N/A')}  " for event in events_in_country])
            dispatcher.utter_message(text=f"Here are the events happening in {country}:  \n{events_list}")
        else:
            dispatcher.utter_message(text=f"Sorry, I couldn't find any events in {country}.")

        return []






