import google.genai as genai
from google.genai.types import Tool, GenerateContentConfig, GoogleSearch

from dotenv import load_dotenv
import os

def setup_tools():
    tools = []
    google_search_tool = Tool(
        google_search=GoogleSearch()
    )
    tools.append(google_search_tool)
    return tools

load_dotenv()
gemini_api_key = os.getenv("GEMINI_API_KEY")
def configure_api(api_key):
    global client
    client = genai.Client(api_key=api_key)

configure_api(gemini_api_key)

def ask_gemini(prompt):
    response = client.models.generate_content(
        model='gemini-2.0-flash',
        contents=prompt,
    )
    return response.text


def find_events(destination, start_date, end_date):
    search_query = (f"""Wydarzenia w {destination} od {start_date} do {end_date}. Odpowiedź zapisz w schemacie JSON:
                    Use this JSON schema:

                    Event = 'event_name': str, 'event_date': str, 'time': str
                    Return: list[Event] """
                    )
    response = client.models.generate_content(
        model='gemini-2.0-flash',
        contents=search_query,
        config=GenerateContentConfig(
            tools=setup_tools(),
            #response_mime_type='application/json',
            #response_schema=Event,
        )
    )
    return response.text

def find_city(departure):
    search_query = (f"""Atrakcyjne miasto w okolicach {departure}. Odpowiedź zapisz jako jedno słowo"""
                    )
    response = client.models.generate_content(
        model='gemini-2.0-flash',
        contents=search_query,
        config=GenerateContentConfig(
            tools=setup_tools(),
            # response_mime_type='application/json',
            # response_schema=Event,
        )
    )
    return response.text

def generate_travel_plan(form_data):
    if form_data["destination"] == "Gdziekolwiek":
        form_data["destination"] = find_city(form_data["departure"])
    events = find_events(form_data['destination'], form_data['start_date'], form_data['end_date'])
    #print(events)

    user_input = f"""
    Poszukuję zaplanowanej podróży w Polsce.
    Chcę pojechać {form_data['destination']} {form_data['special_occasions']}. Wyjeżdżam z {form_data['departure']}.
    Termin wyjazdu to od {form_data['start_date']} do {form_data['end_date']}. Jadę {form_data['company']}. Jest nas {form_data['adults']} dorosłych i {form_data['children']} dzieci.
    Interesuje mnie {', '.join(form_data['travel_style'])} styl podróżowania. Całkowity budżet wynosi około {form_data['budget'] * (form_data['adults'] + form_data['children'])} zł.
    Chcę dotrzeć tam jednym z podanych środków transportu {', '.join(form_data['transport'])}. Na miejscu chcę poruszać się {', '.join(form_data['local_transport'])}.
    Interesuje mnie nocleg w {form_data['accommodation']}. Moja lista zainteresowań to: {', '.join(form_data['interests'])}. W kwestii jedzenia: {form_data['food_preferences']}.
    {', '.join(form_data['amenities'])}. Stwórz plan wycieczki gotowy do wydruku zawierający {form_data['itinerary_detail']}.

    Weź pod uwagę, że w zadanym czasie miejsce mają następujące wydarzenia:
    {events}
    
    Proszę, aby odpowiedź była sformatowana w sposób estetyczny, z odstępami między sekcjami, pogrubieniami i punktami. Unikaj zbędnych wstępów.
    """

    return ask_gemini(user_input)

form_data = {
    'destination': 'Krzeszowice',
    'start_date': '29.03.2025',
    'end_date': '31.03.2025',
    'special_occasions': 'na weekendowy wypad',
    'departure': 'Warszawa',
    'company': 'rodzina',
    'adults': 2,
    'children': 2,
    'travel_style': ['relaksowy', 'kulturalny'],
    'budget': 1500,  # budżet na osobę
    'transport': ['pociąg', 'samochód'],
    'local_transport': ['tramwaj', 'pieszo'],
    'accommodation': 'hotel',
    'interests': ['muzea', 'historia', 'architektura'],
    'food_preferences': 'wegetariańska',
    'amenities': ['basen', 'internet Wi-Fi'],
    'itinerary_detail': 'plan wycieczki na 3 dni, z uwzględnieniem wszystkich atrakcji i wydarzeń'
}

print(generate_travel_plan(form_data))