import google.generativeai as genai
from dotenv import load_dotenv
import os

def configure_api(api_key):
    load_dotenv()
    gemini_api_key = os.getenv("GEMINI_API_KEY")
    genai.configure(api_key=gemini_api_key)

def ask_gemini(prompt):
    model = genai.GenerativeModel("gemini-2.0-flash")
    response = model.generate_content(prompt)
    return response.text

def generate_travel_plan(form_data):
    user_input = f"""
    Poszukuję zaplanowanej podróży w Polsce. 
    Chcę pojechać {form_data['destination']} {form_data['special_occasions']}. Wyjeżdżam z {form_data['departure']}. 
    Termin wyjazdu to od {form_data['start_date']} do {form_data['end_date']}. Jadę {form_data['company']}. Jest nas {form_data['adults']} dorosłych i {form_data['children']} dzieci. 
    Interesuje mnie {', '.join(form_data['travel_style'])} styl podróżowania. Całkowity budżet wynosi około {form_data['budget'] * (form_data['adults'] + form_data['children'])} zł. 
    Chcę dotrzeć tam jednym z podanych środków transportu {', '.join(form_data['transport'])}. Na miejscu chcę poruszać się {', '.join(form_data['local_transport'])}. 
    Interesuje mnie nocleg w {form_data['accommodation']}. Moja lista zainteresowań to: {', '.join(form_data['interests'])}. W kwestii jedzenia: {form_data['food_preferences']}. 
    {', '.join(form_data['amenities'])}. Stwórz plan wycieczki gotowy do wydruku zawierający {form_data['itinerary_detail']}.
    """
    return ask_gemini(user_input)
