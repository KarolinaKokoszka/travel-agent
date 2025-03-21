import streamlit as st
from travel_agent import generate_travel_plan

def main():
    st.title("Planer Podróży")

    with st.form("travel_form"):
        destination_type = st.radio("Dokąd chcesz jechać?", ["Gdziekolwiek", "Konkretne miejsce"])
        destination = st.text_input("Podaj miejsce docelowe") if destination_type == "Konkretne miejsce" else "Gdziekolwiek"

        departure = st.text_input("Skąd wyjeżdżasz?")
        start_date = st.date_input("Rozpoczęcie")
        end_date = st.date_input("Zakończenie")

        company = st.radio("Towarzystwo", ["Samotnie", "Z rodziną", "Z partnerem/partnerką", "Ze znajomymi", "W grupie zorganizowanej"])
        adults = st.number_input("Ilość dorosłych", min_value=1, step=1)
        children = st.number_input("Ilość dzieci", min_value=0, step=1)

        travel_style = st.multiselect("Styl podróżowania", [
            "Luksusowy (5* hotele, prywatne wycieczki)",
            "Budżetowy (hostele, couchsurfing)",
            "Ekologiczny (slow travel, ekoturystyka)",
            "Backpacking (minimalistycznie, z plecakiem)",
            "City break"
        ])
        budget = st.slider("Jaki masz budżet na osobę?", min_value=100, max_value=10000, step=100)

        transport = st.multiselect("Jak chcesz dotrzeć?", [
            "Samolotem", "Pociągiem", "Samochodem", "Autobusem", "Autokarem", "Rowerem"
        ])
        local_transport = st.multiselect("Jak chcesz się poruszać na miejscu?", [
            "Komunikacja miejska", "Pieszo", "Rower", "Samochód"
        ])
        accommodation = st.radio("Rodzaj noclegu", [
            "Hotel", "Hostel", "Apartament", "Camping", "Airbnb", "Bez różnicy, byle było czysto, albo brudno"
        ])

        interests = st.multiselect("Zainteresowania i aktywności", [
            "Kultura i historia", "Przyroda i trekking", "Sporty wodne", "Życie nocne", "Shopping",
            "Lokalne doświadczenia (warsztaty, gotowanie)", "Atrakcje dla dzieci", "Parki rozrywki"
        ])
        food_preferences = st.radio("Preferencje kulinarne", [
            "Nie mam ograniczeń", "Kuchnia wegetariańska", "Kuchnia wegańska", "Inne"
        ])

        itinerary_detail = st.radio("Jak szczegółowy ma być plan podróży?", [
            "Luźne propozycje, bez sztywnego harmonogramu", "Harmonogram z godzinami i rezerwacjami"
        ])
        special_occasions = st.radio("Czy jest jakaś specjalna okazja związana z wyjazdem?", [
            "Z okazji rocznicy", "Na podróż poślubną", "Z okazji urodzin", "Bez okazji"
        ])
        amenities = st.multiselect("Udogodnienia, których potrzebujesz:", [
            "Dostępność dla wózka inwalidzkiego", "Brak schodów w miejscach noclegu i atrakcji",
            "Możliwość podróżowania ze zwierzętami", "Pokój hotelowy przystosowany dla osób z niepełnosprawnością"
        ])

        submit = st.form_submit_button("Generuj plan podróży")

        if submit:
            form_data = {
                "destination": destination,
                "departure": departure,
                "start_date": start_date,
                "end_date": end_date,
                "company": company,
                "adults": adults,
                "children": children,
                "travel_style": travel_style,
                "budget": budget,
                "transport": transport,
                "local_transport": local_transport,
                "accommodation": accommodation,
                "interests": interests,
                "food_preferences": food_preferences,
                "itinerary_detail": itinerary_detail,
                "special_occasions": special_occasions,
                "amenities": amenities
            }
            response = generate_travel_plan(form_data)
            st.subheader("Plan podróży")
            st.write(response)

if __name__ == "__main__":
    main()
