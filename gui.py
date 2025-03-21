from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QPushButton,
    QRadioButton, QButtonGroup, QLineEdit, QDateEdit, QSpinBox, QComboBox,
    QTextEdit, QCheckBox, QGroupBox, QFormLayout, QHBoxLayout, QScrollArea, QMessageBox
)
import sys
from travel_agent import generate_travel_plan

class TravelPlanner(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Planer Podróży")
        self.setGeometry(100, 100, 600, 800)
        
        # Tworzenie głównego widgetu przewijania
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.setCentralWidget(self.scroll_area)
        
        # Główny widget i układ
        self.central_widget = QWidget()
        self.layout = QVBoxLayout()
        
        #---------------------------------------Miejsce docelowe---------------------------------------
        self.destination_group = QGroupBox("Dokąd chcesz jechać?")
        self.destination_layout = QVBoxLayout()

        #Przyciski radiowe - jednokrotny wybór
        self.radio_anywhere = QRadioButton("Gdziekolwiek")
        self.radio_specific = QRadioButton("Konkretne miejsce")
        self.radio_anywhere.setChecked(True) #opcjia pierwsza domyślnie zaznaczona

        # Dodanie przycisków do ukladu
        self.destination_layout.addWidget(self.radio_anywhere)
        self.destination_layout.addWidget(self.radio_specific)

        # Skąd wyjeżdżasz? - pole tekstowe możliwe do wypełnienia jeśli wybierze się opcje "Konkretne miejsce"
        self.destination_input = QLineEdit()
        self.destination_input.setPlaceholderText("Podaj miejsce docelowe")
        self.destination_input.setEnabled(False)
        self.radio_specific.toggled.connect(lambda: self.destination_input.setEnabled(self.radio_specific.isChecked()))
        
        # Dodanie pola tekstowego do ukladu
        self.destination_layout.addWidget(self.destination_input)

        self.destination_group.setLayout(self.destination_layout)
        self.layout.addWidget(self.destination_group)
        
        #---------------------------------------Miejsce wyjazdu---------------------------------------
        self.layout.addWidget(QLabel("Skąd wyjeżdżasz?"))
        self.departure_input = QLineEdit()
        self.layout.addWidget(self.departure_input)
        
        #---------------------------------------Data rozpoczęcia---------------------------------------

        #----------------------------------------------------------------------------------
        #TU MOŻNA ZROBIĆ KALENDARZ A JAK NIE TO TZEBA POPRAWIC DATE DOMYŚLNĄ NP. NA AKTUALNĄ
        #W OBECNEJ WERSJI DATA CZASEM ZMIENIA SIE PRZYPADKIEM -NIEŚWIADOMIE MOZNA TO ZROBIC - OD SCROLOWANIA MYSZKĄ 
        #----------------------------------------------------------------------------------

        self.layout.addWidget(QLabel("Data rozpoczęcia:"))
        self.start_date_input = QDateEdit()
        self.layout.addWidget(self.start_date_input)
        
        #---------------------------------------Data zakończenia---------------------------------------

        #----------------
        #TO SAMO CO WYŻEJ
        #----------------

        self.layout.addWidget(QLabel("Data zakończenia:"))
        self.end_date_input = QDateEdit()
        self.layout.addWidget(self.end_date_input)
        
        #---------------------------------------Towarzystwo---------------------------------------
        self.company_group = QGroupBox("Towarzystwo")
        self.company_layout = QVBoxLayout()

        #Przyciski radiowe - jednokrotny wybór
        self.radio_solo = QRadioButton("Samotnie")
        self.radio_family = QRadioButton("Z rodziną")
        self.radio_partner = QRadioButton("Z partnerem/partnerką")
        self.radio_friends = QRadioButton("Ze znajomymi")
        self.radio_group = QRadioButton("W grupie zorganizowanej")
        self.radio_solo.setChecked(True) # pierwsza opcjia domyślnie

        # Dodanie przycisków do układu
        self.company_layout.addWidget(self.radio_solo)
        self.company_layout.addWidget(self.radio_family)
        self.company_layout.addWidget(self.radio_partner)
        self.company_layout.addWidget(self.radio_friends)
        self.company_layout.addWidget(self.radio_group)

        self.company_group.setLayout(self.company_layout)
        self.layout.addWidget(self.company_group)
        
        #---------------------------------------Ilość dorosłych---------------------------------------

        #----------------------------------------------------------------------------------
        #W OBECNEJ WERSJI LICZBA DOROSŁYCH CZASEM ZMIENIA SIE PRZYPADKIEM -NIEŚWIADOMIE MOZNA TO ZROBIC - OD SCROLOWANIA MYSZKĄ 
        #----------------------------------------------------------------------------------

        self.layout.addWidget(QLabel("Ilość dorosłych:"))
        self.adults_input = QSpinBox()
        self.adults_input.setMinimum(1)
        self.layout.addWidget(self.adults_input)
        
        #---------------------------------------Ilość dzieci---------------------------------------

        #----------------------------------------------------------------------------------
        #TO SAMO CO WYZEJ
        #----------------------------------------------------------------------------------

        self.layout.addWidget(QLabel("Ilość dzieci:"))
        self.children_input = QSpinBox()
        self.children_input.setMinimum(0)
        self.layout.addWidget(self.children_input)
        
        #---------------------------------------Styl podróżowania---------------------------------------
        self.style_group = QGroupBox("Styl podróżowania")
        self.style_layout = QVBoxLayout()

        # Checkboxy - wybór wielokrotny
        self.check_city = QCheckBox("City break")
        self.check_financial = QCheckBox("Budżetowy (hostele, couchsurfing)")
        self.check_backpacking = QCheckBox("Backpacking (minimalistycznie, z plecakiem)")
        self.check_ecological = QCheckBox("Ekologiczny (slow travel, ekoturystyka)")
        self.check_luxury = QCheckBox("Luksusowy (5* hotele, prywatne wycieczki)")

        # Dodanie checkboxów do układu
        self.style_layout.addWidget(self.check_city)
        self.style_layout.addWidget(self.check_financial)
        self.style_layout.addWidget(self.check_backpacking)
        self.style_layout.addWidget(self.check_ecological)
        self.style_layout.addWidget(self.check_luxury)

        self.style_group.setLayout(self.style_layout)
        self.layout.addWidget(self.style_group)
        
        #---------------------------------------Budżet---------------------------------------

        #----------------------
        #MOŻNA ZOBIĆ SUWAK!!!
        #----------------------

        self.layout.addWidget(QLabel("Jaki masz budżet na osobę?"))
        self.budget_input = QSpinBox()
        self.budget_input.setMinimum(100)
        self.budget_input.setMaximum(100000)
        self.layout.addWidget(self.budget_input)
        
        #---------------------------------------Środek transportu do miejsca docelowego---------------------------------------
        self.transport_group = QGroupBox("Jak chcesz dotrzeć?")
        self.transport_layout = QVBoxLayout()

        # Checkboxy - wybór wielokrotny
        self.check_car = QCheckBox("Samochodem")
        self.check_train = QCheckBox("Pociągiem")
        self.check_bus = QCheckBox("Autobusem")
        self.check_coach = QCheckBox("Autokarem")
        self.check_bike = QCheckBox( "Rowerem")
        self.check_plane = QCheckBox("Samolotem")

        # Dodanie checkboxów do układu
        self.transport_layout.addWidget(self.check_car)
        self.transport_layout.addWidget(self.check_train)
        self.transport_layout.addWidget(self.check_bus)
        self.transport_layout.addWidget(self.check_coach)
        self.transport_layout.addWidget(self.check_bike)
        self.transport_layout.addWidget(self.check_plane)

        self.transport_group.setLayout(self.transport_layout)
        self.layout.addWidget(self.transport_group)
        
        #---------------------------------------Środek transportu w miejscu docelowym---------------------------------------   
        self.local_transport_group = QGroupBox("Jak chcesz się poruszać na miejscu?")
        self.local_transport_layout = QVBoxLayout()

        # Checkboxy - wybór wielokrotny
        self.check_local_public = QCheckBox("Komunikacją miejską")
        self.check_local_foot = QCheckBox("Pieszo")
        self.check_local_bike = QCheckBox("Rowerem")
        self.check_local_car = QCheckBox("Samochodem")

        # Dodanie checkboxów do układu
        self.local_transport_layout.addWidget(self.check_local_public)
        self.local_transport_layout.addWidget(self.check_local_foot)
        self.local_transport_layout.addWidget(self.check_local_bike)
        self.local_transport_layout.addWidget(self.check_local_car)

        self.local_transport_group.setLayout(self.local_transport_layout)
        self.layout.addWidget(self.local_transport_group)

        #---------------------------------------Nocleg---------------------------------------
        self.accommodation_group = QGroupBox("Rodzaj noclegu")
        self.accommodation_layout = QVBoxLayout()

        #Przyciski radiowe - jednokrotny wybór
        self.radio_hotel = QRadioButton("Hotel")
        self.radio_hostel = QRadioButton("Hostel")
        self.radio_apartment = QRadioButton("Apartament")
        self.radio_camping = QRadioButton("Camping")
        self.radio_airbnb = QRadioButton("Airbnb")
        self.radio_all = QRadioButton("Bez różnicy")
        self.radio_all.setChecked(True) # ostatnia opcjia domyślnie

        # Dodanie przycisków do układu
        self.accommodation_layout.addWidget(self.radio_hotel)
        self.accommodation_layout.addWidget(self.radio_hostel)
        self.accommodation_layout.addWidget(self.radio_apartment)
        self.accommodation_layout.addWidget(self.radio_camping)
        self.accommodation_layout.addWidget(self.radio_airbnb)
        self.accommodation_layout.addWidget(self.radio_all)

        self.accommodation_group.setLayout(self.accommodation_layout)
        self.layout.addWidget(self.accommodation_group)

        #---------------------------------------Zainteresownia i aktywnoci---------------------------------------
        self.interests_group = QGroupBox("Zainteresowania i aktywności")
        self.interests_layout = QVBoxLayout()

        # Checkboxy - wybór wielokrotny
        self.check_culture = QCheckBox("Kultura i historia")
        self.check_nature = QCheckBox("Przyroda i trekking")
        self.check_water_sports = QCheckBox("Sporty wodne")
        self.check_nightlife = QCheckBox("Życie nocne")
        self.check_shopping = QCheckBox("Shopping")
        self.check_local_experience = QCheckBox("Lokalne doświadczenia (warsztaty, gotowanie)")
        self.check_kids = QCheckBox("Atrakcje dla dzieci")
        self.check_amusement_parks = QCheckBox("Parki rozrywki")

        # Dodanie checkboxów do układu
        self.interests_layout.addWidget(self.check_culture)
        self.interests_layout.addWidget(self.check_nature)
        self.interests_layout.addWidget(self.check_water_sports)
        self.interests_layout.addWidget(self.check_nightlife)
        self.interests_layout.addWidget(self.check_shopping)
        self.interests_layout.addWidget(self.check_local_experience)
        self.interests_layout.addWidget(self.check_kids)
        self.interests_layout.addWidget(self.check_amusement_parks)

        self.interests_group.setLayout(self.interests_layout)
        self.layout.addWidget(self.interests_group)

        #---------------------------------------Preferencje kulinarne---------------------------------------
        self.food_group = QGroupBox("Preferencje kulinarne")
        self.food_layout = QVBoxLayout()

        #Przyciski radiowe - jednokrotny wybór
        self.radio_none = QRadioButton("Nie mam ograniczeń")
        self.radio_vege = QRadioButton( "Kuchnia wegetariańska")
        self.radio_vegan = QRadioButton("Kuchnia wegańska")
        self.radio_none.setChecked(True) # pierwsza opcjia domyślnie

        # Dodanie przycisków do układu
        self.food_layout.addWidget(self.radio_none)
        self.food_layout.addWidget(self.radio_vege)
        self.food_layout.addWidget(self.radio_vegan)

        self.food_group.setLayout(self.food_layout)
        self.layout.addWidget(self.food_group)
        
        #---------------------------------------Szczegółowość planu podróży---------------------------------------
        self.itinerary_group = QGroupBox("Jak szczegółowy ma być plan podróży?")
        self.itinerary_layout = QVBoxLayout()

        #Przyciski radiowe - jednokrotny wybór
        self.radio_loose = QRadioButton("Luźne propozycje, bez sztywnego harmonogramu")
        self.radio_detailed = QRadioButton( "Harmonogram z godzinami")
        self.radio_loose.setChecked(True) # pierwsza opcjia domyślnie

        # Dodanie przycisków do układu
        self.itinerary_layout.addWidget(self.radio_loose)
        self.itinerary_layout.addWidget(self.radio_detailed)

        self.itinerary_group.setLayout(self.itinerary_layout)
        self.layout.addWidget(self.itinerary_group)
        
        #---------------------------------------Okazja---------------------------------------
        self.occasion_group = QGroupBox("Czy jest jakaś specjalna okzajia związana z wyjazdem?")
        self.occasion_layout = QVBoxLayout()

        #Przyciski radiowe - jednokrotny wybór
        self.radio_without = QRadioButton("Bez okazji")
        self.radio_birthday = QRadioButton( "Z okazji urodzin")
        self.radio_anniversary = QRadioButton("Z okazji rocznicy")
        self.radio_honeymoon = QRadioButton("Na podróż poślubną")
        self.radio_without.setChecked(True) # pierwsza opcjia domyślnie

        # Dodanie przycisków do układu
        self.occasion_layout.addWidget(self.radio_without)
        self.occasion_layout.addWidget(self.radio_birthday)
        self.occasion_layout.addWidget(self.radio_anniversary)
        self.occasion_layout.addWidget(self.radio_honeymoon)

        self.occasion_group.setLayout(self.occasion_layout)
        self.layout.addWidget(self.occasion_group)

        #---------------------------------------Udogodnienia---------------------------------------
        self.amenities_group = QGroupBox("Udogodnienia, których potrzebujesz")
        self.amenities_layout = QVBoxLayout()

        # Checkboxy - wybór wielokrotny
        self.check_wheelchair_access = QCheckBox("Dostępność dla wózka inwalidzkiego")
        self.check_no_stairs = QCheckBox("Brak schodów w miejscach noclegu i atrakcji")
        self.check_pets_allowed = QCheckBox("Możliwość podróżowania ze zwierzętami")
        self.check_disabled_room = QCheckBox("Pokój hotelowy przystosowany dla osób z niepełnosprawnością")

        # Dodanie checkboxów do układu
        self.amenities_layout.addWidget(self.check_wheelchair_access)
        self.amenities_layout.addWidget(self.check_no_stairs)
        self.amenities_layout.addWidget(self.check_pets_allowed)
        self.amenities_layout.addWidget(self.check_disabled_room)

        self.amenities_group.setLayout(self.amenities_layout)
        self.layout.addWidget(self.amenities_group)


     #--------------------------------------------------------------------------------------------------------------------------       
        self.generate_button = QPushButton("Generuj plan podróży")
        self.generate_button.clicked.connect(self.generate_plan)
        self.layout.addWidget(self.generate_button)
        
        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        self.layout.addWidget(self.result_text)
        
        # Ustawienie układu w centralnym widżecie
        self.central_widget.setLayout(self.layout)
        self.scroll_area.setWidget(self.central_widget)


    #--------------------------------------------------------------------------------------------------------------------------
    def generate_plan(self):

        #miejsce skąd kroś wyjeższa jest OBOWIĄZKOWE
        if not self.departure_input.text().strip():
            QMessageBox.warning(self, "Błąd", "Proszę podać miejsce wyjazdu!")
            return

        form_data = {
            "destination": self.destination_input.text() if self.radio_specific.isChecked() else "Gdziekolwiek",
            "departure": self.departure_input.text(),
            "start_date": self.start_date_input.text(),
            "end_date": self.end_date_input.text(),
            "company": self.get_selected_company(),    # podpięcie dla wybory jednokrotnego
            "adults": self.adults_input.value(),
            "children": self.children_input.value(),
            "travel_style": self.get_selected_styles(),    # podpięcie dla wybory wielokrotnego
            "budget": self.budget_input.value(),
            "transport": self.get_selected_transport(),
            "local_transport": self.get_selected_local_transport(),
            "accommodation": self.get_selected_accommodation(),
            "interests": "",
            "food_preferences": self.get_selected_food_preferences(),
            "itinerary_detail": self.get_selected_itinerary_detail(),
            "special_occasions": self.get_selected_special_occasions(),
            "amenities": ""
        }
        
        response = generate_travel_plan(form_data)
        self.result_text.setText(response)

    #dla wyboru jednokrotnego -> Towarzystwo
    def get_selected_company(self):           
        if self.radio_family.isChecked():
            return self.radio_family.text()
        elif self.radio_partner.isChecked():
            return self.radio_partner.text()
        elif self.radio_friends.isChecked():
            return self.radio_friends.text()
        elif self.radio_group.isChecked():
            return self.radio_group.text()
        return self.radio_solo.text() #opcjia domyslna 

    #dla wyboru wielokrotnego -> Styl podróżowania
    def get_selected_styles(self):
        selected_styles = []
        if self.check_city.isChecked():
            selected_styles.append(self.check_city.text())
        if self.check_financial.isChecked():
            selected_styles.append(self.check_financial.text())
        if self.check_backpacking.isChecked():
            selected_styles.append(self.check_backpacking.text())
        if self.check_ecological.isChecked():
            selected_styles.append(self.check_ecological.text())
        if self.check_luxury.isChecked():
            selected_styles.append(self.check_luxury.text())
        return selected_styles if selected_styles else "dowolny"

    #dla wyboru wielokrotnego -> transport do miejsca
    def get_selected_transport(self):
        transport = []
        if self.check_car.isChecked():
            transport.append(self.check_car.text())
        if self.check_train.isChecked():
            transport.append(self.check_train.text())
        if self.check_bus.isChecked():
            transport.append(self.check_bus.text())
        if self.check_coach.isChecked():
            transport.append(self.check_coach.text())
        if self.check_bike.isChecked():
            transport.append(self.check_bike.text())
        if self.check_plane.isChecked():
            transport.append(self.check_plane.text())
        return transport if transport else ["dowolnym środkiem transportu"]

    #dla wyboru wielokrotnego -> transport na miejscu
    def get_selected_local_transport(self):
        local_transport = []
        if self.check_local_public.isChecked():
            local_transport.append(self.check_local_public.text())
        if self.check_local_foot.isChecked():
            local_transport.append(self.check_local_foot.text())
        if self.check_local_bike.isChecked():
            local_transport.append(self.check_local_bike.text())
        if self.check_local_car.isChecked():
            local_transport.append(self.check_local_car.text())
        return local_transport if local_transport else ["dowolnym środkiem transportu"]

    #dla wyboru jednokrotnego -> zakwaterowanie
    def get_selected_accommodation(self):
        if self.radio_hotel.isChecked():
            return self.radio_hotel.text()
        elif self.radio_hostel.isChecked():
            return self.radio_hostel.text()
        elif self.radio_apartment.isChecked():
            return self.radio_apartment.text()
        elif self.radio_camping.isChecked():
            return self.radio_camping.text()
        elif self.radio_airbnb.isChecked():
            return self.radio_airbnb.text()
        return self.radio_all.text()  #opcjia domyslna 

    #dla wyboru wielokrotnego -> zainteresowania
    def get_selected_interests(self):
        interests = []
        if self.check_culture.isChecked():
            interests.append(self.check_culture.text())
        if self.check_nature.isChecked():
            interests.append(self.check_nature.text())
        if self.check_water_sports.isChecked():
            interests.append(self.check_water_sports.text())
        if self.check_nightlife.isChecked():
            interests.append(self.check_nightlife.text())
        if self.check_shopping.isChecked():
            interests.append(self.check_shopping.text())
        if self.check_local_experience.isChecked():
            interests.append(self.check_local_experience.text())
        if self.check_kids.isChecked():
            interests.append(self.check_kids.text())
        if self.check_amusement_parks.isChecked():
            interests.append(self.check_amusement_parks.text())
        return interests if interests else ["brak preferencji"]

    #dla wyboru jednokrotnego -> jedzenie
    def get_selected_food_preferences(self):
        if self.radio_vege.isChecked():
            return self.radio_vege.text()
        elif self.radio_vegan.isChecked():
            return self.radio_vegan.text()
        return self.radio_none.text()

    #dla wyboru jednokrotnego -> szczegółowość planu
    def get_selected_itinerary_detail(self):
        return self.radio_detailed.text() if self.radio_detailed.isChecked() else self.radio_loose.text()

    ##dla wyboru jednokrotnego -> okazja
    def get_selected_special_occasions(self):
        if self.radio_birthday.isChecked():
            return self.radio_birthday.text()
        elif self.radio_anniversary.isChecked():
            return self.radio_anniversary.text()
        elif self.radio_honeymoon.isChecked():
            return self.radio_honeymoon.text()
        return self.radio_without.text()

    #dla wyboru wielokrotnego -> udogodnienia
    def get_selected_amenities(self):
        amenities = []
        if self.check_wheelchair_access.isChecked():
            amenities.append(self.check_wheelchair_access.text())
        if self.check_no_stairs.isChecked():
            amenities.append(self.check_no_stairs.text())
        if self.check_pets_allowed.isChecked():
            amenities.append(self.check_pets_allowed.text())
        if self.check_disabled_room.isChecked():
            amenities.append(self.check_disabled_room.text())
        return amenities if amenities else [""]
        



# Uruchomienie aplikacji
def main():
    app = QApplication(sys.argv)
    window = TravelPlanner()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
