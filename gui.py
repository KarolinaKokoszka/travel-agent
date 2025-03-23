from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QSlider, QWidget, QTabWidget, QVBoxLayout, QLabel, QPushButton,
    QRadioButton, QLineEdit,
    QTextEdit, QCheckBox, QGroupBox, QDialog, QHBoxLayout, QScrollArea, QMessageBox,  QCompleter, QCalendarWidget
)
import sys
from travel_agent import generate_travel_plan
from PyQt6.QtCore import Qt, QDate, pyqtSlot, QObject
from PyQt6.QtWidgets import QLineEdit, QCompleter
from PyQt6.QtGui import QColor, QTextCharFormat
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebChannel import QWebChannel
import re

#-----------------------------do mapki -------------------------------------------------------
class MapHandler(QObject):
    def __init__(self, window):
        super().__init__()
        self.window = window  # Zapisujemy referencję do okna głównego

    @pyqtSlot(float, float)
    def receive_coordinates(self, lat, lng):
        print(f"Otrzymano współrzędne: {lat}, {lng}")
        self.window.departure_input.setText(f"{lat}, {lng}")  # Używamy referencji do okna
        self.window.map_dialog.accept()

class MapDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Wybierz miejsce na mapie")
        self.setGeometry(100, 100, 600, 400)

        self.layout = QVBoxLayout()
        self.map_view = QWebEngineView()
        self.layout.addWidget(self.map_view)
        self.setLayout(self.layout)

        # Przekazujemy referencję do window w MapHandler
        self.channel = QWebChannel()
        self.map_handler = MapHandler(parent)  # Przekazujemy okno główne
        self.channel.registerObject("handler", self.map_handler)

        self.map_view.page().setWebChannel(self.channel)
        self.map_view.setHtml(self.generate_map())
    
    def generate_map(self):
        return '''
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8" />
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <script src="https://unpkg.com/leaflet@1.7.1/dist/leaflet.js"></script>
            <link rel="stylesheet" href="https://unpkg.com/leaflet@1.7.1/dist/leaflet.css" />
            <script src="qrc:///qtwebchannel/qwebchannel.js"></script>
        </head>
        <body>
            <div id="map" style="width: 100%; height: 100vh;"></div>
            <script>
                var map = L.map('map').setView([52.2298, 21.0118], 6);
                L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png').addTo(map);
                var marker;

                new QWebChannel(qt.webChannelTransport, function(channel) {
                    window.pyHandler = channel.objects.handler;
                });

                map.on('click', function(e) {
                    if (marker) {
                        map.removeLayer(marker);
                    }
                    marker = L.marker([e.latlng.lat, e.latlng.lng]).addTo(map);
                    window.pyHandler.receive_coordinates(e.latlng.lat, e.latlng.lng);
                });
            </script>
        </body>
        </html>
        '''
#-------------------------------------------------- PLANER PODRÓŻY---------------------------------------------
class TravelPlanner(QMainWindow):
    def __init__(self):
        super().__init__()
        self.load_styles()
        
        self.setWindowTitle("Planer Podróży")
        self.setGeometry(100, 100, 1100, 1000)

    
        # Tworzenie głównego widgetu przewijania
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.setCentralWidget(self.scroll_area)
        
        # Główny widget i układ
        self.central_widget = QWidget()
        self.layout = QVBoxLayout()

        self.header = QLabel("PLANER PODRÓŻY", self)
        self.header.setStyleSheet("""
            background-image: url('background.jpg');
            background-position: center;
            color: white;
            font-size: 36px;
            font-weight: bold;
            padding: 10px;
            border: 2px solid black; 

        """)
        self.header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.header.setFixedHeight(160)
        # Dodanie nagłówka do głównego układu
        self.layout.addWidget(self.header)
        
        #---------------------------------------Miejsce docelowe---------------------------------------
        self.destination_group = QGroupBox("Dokąd chcesz jechać?")
        self.destination_layout = QVBoxLayout()

        # Przyciski radiowe - jednokrotny wybór
        self.radio_anywhere = QRadioButton("Gdziekolwiek")
        self.radio_specific = QRadioButton("Konkretne miejsce")
        self.radio_anywhere.setChecked(True)  # Opcja pierwsza domyślnie zaznaczona


        self.destination_input = QLineEdit()
        self.destination_input.setPlaceholderText("Podaj miejsce docelowe")
        self.destination_input.setEnabled(False)  # Początkowo wyłączone

        # Lista miast do podpowiedzi
        cities = ["Warszawa", "Gdańsk", "Zakopane", "Wrocław", "Kraków", "Łódź", "Poznań", "Szczecin", "Białystok", "Lublin"]

        self.completer = QCompleter(cities)
        self.completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.destination_input.setCompleter(self.completer)

        # Dodanie przycisków do układu
        self.destination_layout.addWidget(self.radio_anywhere)
        self.destination_layout.addWidget(self.radio_specific)
        self.destination_layout.addWidget(self.destination_input)

        self.destination_group.setLayout(self.destination_layout)
        self.layout.addWidget(self.destination_group)


        # Zdarzenie - wywołanie listy podpowiedzi po kliknięciu w pole tekstowe
        self.radio_anywhere.toggled.connect(self.update_destination_input_state)
        self.radio_specific.toggled.connect(self.update_destination_input_state)

        self.destination_input.focusInEvent = self.show_suggestions_on_focus

        # Obsługa wyboru miasta z listy
        self.completer.activated.connect(self.on_city_selected)

        #---------------------------------------Miejsce wyjazdu---------------------------------------
      # Miejsce wyjazdu (Skąd wyjeżdżasz?)
        self.layout.addWidget(QLabel("Skąd wyjeżdżasz?"))

        # Tworzymy QGroupBox, który będzie zawierał pole tekstowe oraz przycisk
        group_box = QGroupBox(self)
        group_box.setTitle("")  # Usuwamy tytuł, aby zachować czysty wygląd
        group_box.setStyleSheet("""
            QGroupBox {
                border: 2px solid rgb(0, 41, 0);  /* Ciemnozielona obramówka */
                border-radius: 5px;  /* Zaokrąglone rogi */
                padding: 10px;  /* Padding w środku */
            }
        """)

        # Tworzymy layout w obrębie QGroupBox
        map_layout = QHBoxLayout(group_box)

        # Pole tekstowe
        self.departure_input = QLineEdit()
        map_layout.addWidget(self.departure_input)

        # Przycisk "Wybierz na mapie"
        self.map_button = QPushButton("Wybierz na mapie")
        self.map_button.clicked.connect(self.open_map_dialog)
        map_layout.addWidget(self.map_button)
        self.layout.addWidget(group_box)

          # --------------------------------------- Kalendarz ---------------------------------------
        self.start_date = None
        self.end_date = None

        # Przycisk do wyboru daty
        self.travel_date_button = QPushButton("Wybierz termin podróży")
        self.travel_date_button.clicked.connect(self.show_calendar)
        self.layout.addWidget(self.travel_date_button)

        # Layout na daty rozpoczęcia i zakończenia podróży
        self.date_layout = QHBoxLayout()
        self.layout.addLayout(self.date_layout)

        # Data rozpoczęcia podróży
        self.start_date_input = QLineEdit(self)
        self.start_date_input.setPlaceholderText("Data rozpoczęcia")
        self.start_date_input.setReadOnly(False) 
        self.date_layout.addWidget(self.start_date_input)

        # Data zakończenia podróży
        self.end_date_input = QLineEdit(self)
        self.end_date_input.setPlaceholderText("Data zakończenia")
        self.end_date_input.setReadOnly(False)
        self.date_layout.addWidget(self.end_date_input)

        # Strzałki do zmiany miesięcy
        self.nav_layout = QHBoxLayout()
        self.prev_button = QPushButton("◄")
        self.next_button = QPushButton("►")
        self.nav_layout.addWidget(self.prev_button)
        self.nav_layout.addWidget(self.next_button)

        # Layout poziomy na kalendarz
        self.calendars_layout = QHBoxLayout()
        self.layout.addLayout(self.calendars_layout)

        # Kalendarz rozpoczęcia podróży
        self.start_calendar = QCalendarWidget()
        self.start_calendar.setSelectedDate(QDate.currentDate())  
        self.start_calendar.setMinimumDate(QDate.currentDate()) 
        self.start_calendar.setFirstDayOfWeek(Qt.DayOfWeek.Monday)  
        self.start_calendar.clicked.connect(self.handle_date_selection)
        self.start_calendar.setGridVisible(True)
        self.calendars_layout.addWidget(self.start_calendar)

        # Kalendarz zakończenia podróży
        self.end_calendar = QCalendarWidget()
        self.end_calendar.setSelectedDate(QDate.currentDate().addMonths(1))  
        self.end_calendar.setMinimumDate(QDate.currentDate()) 
        self.start_calendar.setFirstDayOfWeek(Qt.DayOfWeek.Monday)  
        self.end_calendar.clicked.connect(self.handle_date_selection)
        self.end_calendar.setGridVisible(True)
        self.calendars_layout.addWidget(self.end_calendar)
        
        # Początkowo ukrywamy okienka, kalendarze oraz strzałki
        self.set_widgets_visibility(False)

        self.update_calendar_height(self.start_calendar)
        self.update_calendar_height(self.end_calendar)

        

      
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
        
        #---------------------------------- Ilość dorosłych ----------------------------------
        self.adult_layout = QHBoxLayout()        
        self.layout.addWidget(QLabel("Ilość dorosłych:"), 0, Qt.AlignmentFlag.AlignLeft)

        # Okienko do wyboru liczby dorosłych (read-only)
        self.adults_input = QLineEdit()
        self.adults_input.setText("1")  # Domyślnie 1 dorosły
        self.adults_input.setAlignment(Qt.AlignmentFlag.AlignCenter)  
        self.adults_input.setReadOnly(True) 

        # Przycisk do zmniejszenia liczby dorosłych
        self.decrease_adults_button = QPushButton("-")
        self.decrease_adults_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.decrease_adults_button.clicked.connect(self.decrease_adults)

        # Przycisk do zwiększenia liczby dorosłych
        self.increase_adults_button = QPushButton("+")
        self.increase_adults_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.increase_adults_button.clicked.connect(self.increase_adults)

        # Dodanie do layoutu
        self.adult_layout.addWidget(self.decrease_adults_button)
        self.adult_layout.addWidget(self.adults_input)
        self.adult_layout.addWidget(self.increase_adults_button)

        # Dodanie layoutu do głównego layoutu
        self.layout.addLayout(self.adult_layout)

        #----------------------------------- Ilość dzieci -----------------------------------
        # Layout dla liczby dzieci
        self.children_layout = QHBoxLayout()

        # Etykieta
        self.layout.addWidget(QLabel("Ilość dzieci:"), 0, Qt.AlignmentFlag.AlignLeft)

        # Okienko do wyboru liczby dzieci (read-only)
        self.children_input = QLineEdit()
        self.children_input.setText("0")  # Domyślnie 0 dzieci
        self.children_input.setAlignment(Qt.AlignmentFlag.AlignCenter)  # Centrowanie wartości
        self.children_input.setReadOnly(True)  # Okienko jest tylko do odczytu, nie można edytować wartości

        # Przycisk do zmniejszenia liczby dzieci
        self.decrease_children_button = QPushButton("-")
        self.decrease_children_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.decrease_children_button.clicked.connect(self.decrease_children)

        # Przycisk do zwiększenia liczby dzieci
        self.increase_children_button = QPushButton("+")
        self.increase_children_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.increase_children_button.clicked.connect(self.increase_children)

        # Dodanie do layoutu
        self.children_layout.addWidget(self.decrease_children_button)
        self.children_layout.addWidget(self.children_input)
        self.children_layout.addWidget(self.increase_children_button)

        # Dodanie layoutu do głównego layoutu
        self.layout.addLayout(self.children_layout)




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

        self.layout.addWidget(QLabel("Jaki masz budżet na osobę?"))

        # Tworzymy layout dla suwaka i etykiety
        self.budget_layout = QHBoxLayout()

        # Tworzymy suwak
        self.budget_slider = QSlider(Qt.Orientation.Horizontal)
        self.budget_slider.setMinimum(100)
        self.budget_slider.setMaximum(10000)
        self.budget_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.budget_slider.setTickInterval(500)
        self.budget_slider.setSingleStep(50)  # Krok co 50 jednostek
        self.budget_slider.setPageStep(50)  # Skok o 50 jednostek
      
        self.budget_label = QLabel("100")

        # Zmieniamy wygląd suwaka
        self.budget_slider.setStyleSheet("""
            QSlider {
                height: 20px;
            }
            QSlider::handle {
                background: rgb(0, 41, 0);
                border: 2px solid #5c4d7d;
                width: 20px;
                height: 20px;
                border-radius: 10px;
            }
        """)

        # Funkcja aktualizująca etykietę po przesunięciu suwaka
        self.budget_slider.valueChanged.connect(self.update_budget)

        self.budget_slider.setAttribute(Qt.WidgetAttribute.WA_OpaquePaintEvent)  # Sprawia, że nie będzie odbierał zdarzeń z kółka myszy

        # Dodajemy suwak i etykietę do layoutu
        self.budget_layout.addWidget(self.budget_slider)
        self.budget_layout.addWidget(self.budget_label)

        # Dodajemy layout do głównego layoutu
        self.layout.addLayout(self.budget_layout)


        #---------------------------------pasek menu-----------------------------------------  
       # Tworzenie paska menu z zakładkami
        self.layout.addWidget(QLabel("PODAJ NAM WIĘCEJ SZCZEGÓŁÓW"))

        # Tworzenie paska menu z zakładkami
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabBarAutoHide(False) 
        self.layout.addWidget(self.tab_widget)

        # Tworzenie poszczególnych sekcji formularza
        self.tab_widget.addTab(self.create_transport_section(), "Transport")
        self.tab_widget.addTab(self.create_local_transport_section(), "Transport lokalny")
        self.tab_widget.addTab(self.create_accommodation_section(), "Nocleg")
        self.tab_widget.addTab(self.create_interests_section(), "Zainteresowania")
        self.tab_widget.addTab(self.create_food_section(), "Preferencje kulinarne")
        self.tab_widget.addTab(self.create_occasion_section(), "Okazja")
        self.tab_widget.addTab(self.create_amenities_section(), "Udogodnienia")

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


    #----------------------------------METODY---------------------------------------
    def load_styles(self):
        with open("styles.qss", "r") as f:
            style = f.read()
            self.setStyleSheet(style)
   
    def update_destination_input_state(self):
        """
        Funkcja ta jest wywoływana przy każdej zmianie stanu przycisków radiowych.
        Jeśli wybrano "Konkretne miejsce", pole tekstowe staje się aktywne.
        Jeśli wybrano "Gdziekolwiek", pole tekstowe staje się nieaktywne.
        """
        if self.radio_specific.isChecked():
            self.destination_input.setEnabled(True)
        else:
            self.destination_input.setEnabled(False)
            self.destination_input.clear()  # Czyści pole tekstowe, gdy opcja "Gdziekolwiek" jest wybrana

    def show_suggestions_on_focus(self, event):
        """
        Funkcja ta jest wywoływana, gdy pole tekstowe zyskuje fokus (po kliknięciu w nie).
        Powoduje wyświetlenie listy podpowiedzi natychmiast po kliknięciu.
        """
        super(QLineEdit, self.destination_input).focusInEvent(event)
        self.completer.complete()  # Wywołanie `complete()` aktywuje listę podpowiedzi

    def on_city_selected(self, city):
        """
        Funkcja wywoływana po kliknięciu na miasto z listy podpowiedzi.
        Wstawia wybrane miasto do pola tekstowego.
        """
        self.destination_input.setText(city)  # Ustawia wybrane miasto w polu tekstowym
    
    #---------------------skad wyjezdzasz ---------------------------------------

    def open_map_dialog(self):
        self.map_dialog = MapDialog(self)
        self.map_dialog.exec()
   

    #------------------------- menu pasek-----------------------------------
    def create_transport_section(self):
        transport_group = QGroupBox("Jak chcesz dotrzeć?")
        transport_layout = QVBoxLayout()

        # Funkcja do tworzenia checkboxa z emotką i tekstem
        def create_checkbox_with_emoji(label_text, emoji, checked=False):
            checkbox = QCheckBox(f"{label_text} {emoji}")
            checkbox.setChecked(checked)
            checkbox.setStyleSheet("QCheckBox { font-size: 16px; }")  # Zwiększenie rozmiaru czcionki, aby była wyraźniejsza
            return checkbox

        # Tworzenie checkboxów z emotkami
        self.check_car = create_checkbox_with_emoji("Samochodem", "🚗")
        self.check_bike = create_checkbox_with_emoji("Rowerem", "🚴‍♂️")
        self.check_train = create_checkbox_with_emoji("Pociągiem", "🚂")
        self.check_bus = create_checkbox_with_emoji("Autobusem", "🚌")
        self.check_coach = create_checkbox_with_emoji("Autokarem", "🚍")
        self.check_plane = create_checkbox_with_emoji("Samolotem", "✈️")

        # Dodanie checkboxów do układu
        transport_layout.addWidget(self.check_car)
        transport_layout.addWidget(self.check_bike)
        transport_layout.addWidget(self.check_train)
        transport_layout.addWidget(self.check_bus)
        transport_layout.addWidget(self.check_coach)
        transport_layout.addWidget(self.check_plane)

        transport_group.setLayout(transport_layout)
        return transport_group
   


    def create_local_transport_section(self):
        local_transport_group = QGroupBox("Jak chcesz się poruszać na miejscu?")
        local_transport_layout = QVBoxLayout()

        # Checkboxy - wybór wielokrotny
        self.check_local_public = QCheckBox("Komunikacją miejską")
        self.check_local_foot = QCheckBox("Pieszo")
        self.check_local_bike = QCheckBox("Rowerem")
        self.check_local_car = QCheckBox("Samochodem")

        # Dodanie checkboxów do układu
        local_transport_layout.addWidget(self.check_local_public)
        local_transport_layout.addWidget(self.check_local_foot)
        local_transport_layout.addWidget(self.check_local_bike)
        local_transport_layout.addWidget(self.check_local_car)

        local_transport_group.setLayout(local_transport_layout)
        return local_transport_group

    def create_accommodation_section(self):
        accommodation_group = QGroupBox("Rodzaj noclegu")
        accommodation_layout = QVBoxLayout()

        # Przyciski radiowe - jednokrotny wybór
        self.radio_hotel = QRadioButton("🏨 Hotel")
        self.radio_hostel = QRadioButton("🛌 Hostel")
        self.radio_apartment = QRadioButton("🏠 Apartament")
        self.radio_camping = QRadioButton("⛺ Camping")
        self.radio_airbnb = QRadioButton("🏡 Airbnb")
        self.radio_all = QRadioButton("🎲 Bez różnicy")
        self.radio_all.setChecked(True)  # ostatnia opcja domyślnie

        # Dodanie przycisków do układu
        accommodation_layout.addWidget(self.radio_hotel)
        accommodation_layout.addWidget(self.radio_hostel)
        accommodation_layout.addWidget(self.radio_apartment)
        accommodation_layout.addWidget(self.radio_camping)
        accommodation_layout.addWidget(self.radio_airbnb)
        accommodation_layout.addWidget(self.radio_all)

        accommodation_group.setLayout(accommodation_layout)
        return accommodation_group

    def create_interests_section(self):
        interests_group = QGroupBox("Zainteresowania i aktywności")
        interests_layout = QVBoxLayout()

        # Checkboxy - wybór wielokrotny
        self.check_culture = QCheckBox("🏛️ Kultura i historia")
        self.check_nature = QCheckBox("🌲Przyroda i trekking")
        self.check_water_sports = QCheckBox("🏄 Sporty wodne")
        self.check_nightlife = QCheckBox("🎉 Życie nocne")
        self.check_shopping = QCheckBox("🛍️ Shopping")
        self.check_local_experience = QCheckBox("🧑‍🍳 Lokalne doświadczenia (warsztaty, gotowanie)")
        self.check_kids = QCheckBox("🎡 Atrakcje dla dzieci")
        self.check_amusement_parks = QCheckBox("🎢 Parki rozrywki")

        # Dodanie checkboxów do układu
        interests_layout.addWidget(self.check_culture)
        interests_layout.addWidget(self.check_nature)
        interests_layout.addWidget(self.check_water_sports)
        interests_layout.addWidget(self.check_nightlife)
        interests_layout.addWidget(self.check_shopping)
        interests_layout.addWidget(self.check_local_experience)
        interests_layout.addWidget(self.check_kids)
        interests_layout.addWidget(self.check_amusement_parks)

        interests_group.setLayout(interests_layout)
        return interests_group

    def create_food_section(self):
        food_group = QGroupBox("Preferencje kulinarne")
        food_layout = QVBoxLayout()

        # Przyciski radiowe - jednokrotny wybór
        self.radio_none = QRadioButton("Nie mam ograniczeń")
        self.radio_vege = QRadioButton("Kuchnia wegetariańska")
        self.radio_vegan = QRadioButton("Kuchnia wegańska")
        self.radio_none.setChecked(True)  # pierwsza opcja domyślnie

        # Dodanie przycisków do układu
        food_layout.addWidget(self.radio_none)
        food_layout.addWidget(self.radio_vege)
        food_layout.addWidget(self.radio_vegan)

        food_group.setLayout(food_layout)
        return food_group

    def create_occasion_section(self):
        occasion_group = QGroupBox("Czy jest jakaś specjalna okazja związana z wyjazdem?")
        occasion_layout = QVBoxLayout()

        # Przyciski radiowe - jednokrotny wybór
        self.radio_without = QRadioButton("Bez okazji")
        self.radio_birthday = QRadioButton("Z okazji urodzin")
        self.radio_anniversary = QRadioButton("Z okazji rocznicy")
        self.radio_honeymoon = QRadioButton("Na podróż poślubną")
        self.radio_without.setChecked(True)  # pierwsza opcja domyślnie

        # Dodanie przycisków do układu
        occasion_layout.addWidget(self.radio_without)
        occasion_layout.addWidget(self.radio_birthday)
        occasion_layout.addWidget(self.radio_anniversary)
        occasion_layout.addWidget(self.radio_honeymoon)

        occasion_group.setLayout(occasion_layout)
        return occasion_group

    def create_amenities_section(self):
        amenities_group = QGroupBox("Udogodnienia, których potrzebujesz")
        amenities_layout = QVBoxLayout()

        # Checkboxy - wybór wielokrotny
        self.check_wheelchair_access = QCheckBox("Dostępność dla wózka inwalidzkiego")
        self.check_no_stairs = QCheckBox("Brak schodów w miejscach noclegu i atrakcji")
        self.check_pets_allowed = QCheckBox("Możliwość podróżowania ze zwierzętami")
        self.check_disabled_room = QCheckBox("Pokój hotelowy przystosowany dla osób z niepełnosprawnością")

        # Dodanie checkboxów do układu
        amenities_layout.addWidget(self.check_wheelchair_access)
        amenities_layout.addWidget(self.check_no_stairs)
        amenities_layout.addWidget(self.check_pets_allowed)
        amenities_layout.addWidget(self.check_disabled_room)

        amenities_group.setLayout(amenities_layout)
        return amenities_group


    #-------------------kalendarz-----------------------------------

    def set_widgets_visibility(self, visible):
        """
        Funkcja do ustawiania widoczności widgetów w layoutach.
        """
        # Ukrywanie lub pokazywanie wszystkich widgetów w date_layout
        for widget in self.date_layout.children():
            widget.setVisible(visible)

        # Ukrywanie lub pokazywanie wszystkich widgetów w nav_layout
        for widget in self.nav_layout.children():
            widget.setVisible(visible)

        # Ukrywanie lub pokazywanie kalendarzy
        self.start_calendar.setVisible(visible)
        self.end_calendar.setVisible(visible)

    def show_calendar(self):
        """
        Wyświetla kalendarz oraz okienka dat po kliknięciu na przycisk 'Wybierz termin podróży'
        """
        self.set_widgets_visibility(True)
    def handle_start_date_input(self):
        """
        Obsługuje ręczne wpisywanie daty rozpoczęcia podróży.
        """
        date_str = self.start_date_input.text()
        if self.is_valid_date(date_str):
            self.start_date = QDate.fromString(date_str, "dd.MM.yyyy")
            self.start_date_input.setStyleSheet("background-color: #8DB600;")  # Zgniły jasny zielony
        else:
            self.start_date_input.setStyleSheet("background-color: lightcoral;")  # Kolor błędu

    def handle_end_date_input(self):
        """
        Obsługuje ręczne wpisywanie daty zakończenia podróży.
        """
        date_str = self.end_date_input.text()
        if self.is_valid_date(date_str):
            self.end_date = QDate.fromString(date_str, "dd.MM.yyyy")
            self.end_date_input.setStyleSheet("background-color: #8DB600;")  # Zgniły jasny zielony
        else:
            self.end_date_input.setStyleSheet("background-color: lightcoral;")  # Kolor błędu

    def is_valid_date(self, date_str):
        """
        Sprawdza, czy data jest w poprawnym formacie dd.MM.yyyy oraz czy nie jest wcześniejsza niż dzisiejsza data.
        """
        # Sprawdzanie, czy data pasuje do wzorca "dd.MM.yyyy"
        date_pattern = r"^\d{2}\.\d{2}\.\d{4}$"
        if not re.match(date_pattern, date_str):
            return False 

        # Parsowanie daty z tekstu
        date = QDate.fromString(date_str, "dd.MM.yyyy")

        # Sprawdzanie, czy konwersja do QDate się powiodła
        if not date.isValid():
            return False  

        # Sprawdzanie, czy data nie jest wcześniejsza niż dzisiaj
        today = QDate.currentDate()
        if date < today:
            return False  

        return True  

    def handle_date_selection(self, date):
        """
        Obsługuje kliknięcia na kalendarzu.
        Zaznacza początkową i końcową datę, a także podświetla wszystkie dni między nimi.
        """
        if self.start_date is None:  # Jeśli nie ma jeszcze daty początkowej
            self.start_date = date
            self.start_date_input.setText(self.start_date.toString("dd.MM.yyyy"))
            self.start_date_input.setStyleSheet("background-color: rgb(115, 157, 115);")
        elif self.end_date is None and date > self.start_date:  # Jeśli nie ma jeszcze daty końcowej i data jest po dacie początkowej
            self.end_date = date
            self.end_date_input.setText(self.end_date.toString("dd.MM.yyyy"))
            self.end_date_input.setStyleSheet("background-color: rgb(115, 157, 115);")
            self.highlight_range()  # Podświetl dni pomiędzy startową a końcową datą
            self.update_calendar_height(self.start_calendar)
            self.update_calendar_height(self.end_calendar)
        elif date == self.start_date or date == self.end_date:  # Kliknięcie na już wybraną datę, aby ją odznaczyć
            self.clear_selection()

    def highlight_range(self):
        """
        Podświetlanie zakresu dat od start_date do end_date.
        """
        if self.start_date is not None and self.end_date is not None:
            format = QTextCharFormat()
            format.setBackground(QColor("pink"))

            # Podświetlenie dni pomiędzy datą początkową a końcową
            current_date = self.start_date.addDays(1)
            while current_date < self.end_date:
                self.start_calendar.setDateTextFormat(current_date, format)
                self.end_calendar.setDateTextFormat(current_date, format)
                current_date = current_date.addDays(1)

            # Podświetlenie daty początkowej i końcowej
            format.setBackground(QColor("gray"))
            self.start_calendar.setDateTextFormat(self.start_date, format)
            self.end_calendar.setDateTextFormat(self.start_date, format)
            self.start_calendar.setDateTextFormat(self.end_date, format)
            self.end_calendar.setDateTextFormat(self.end_date, format)

    def clear_selection(self):
        """
        Wyczyść zaznaczenie (start_date i end_date).
        """
        self.start_date = None
        self.end_date = None
        self.start_calendar.setDateTextFormat(QDate(), QTextCharFormat())
        self.end_calendar.setDateTextFormat(QDate(), QTextCharFormat())
        self.start_calendar.update()
        self.end_calendar.update()

    def next_month(self):
        """
        Funkcja do zmiany na następny miesiąc.
        """
        self.start_calendar.showNextMonth()
        self.end_calendar.showNextMonth()
        self.update_calendar_height(self.start_calendar)
        self.update_calendar_height(self.end_calendar)

    def previous_month(self):
        """
        Funkcja do zmiany na poprzedni miesiąc.
        """
        self.start_calendar.showPreviousMonth()
        self.end_calendar.showPreviousMonth()
        self.update_calendar_height(self.start_calendar)
        self.update_calendar_height(self.end_calendar)
    
    #--------DO POPRAWY, nie wiem jak naprawic wysokosc kalendarza, narazie ustawione po prostu na 6 tyg automatycznie + 1 tydzien (pon,wt)
    def update_calendar_height(self, calendar):
        """
        Uaktualnia wysokość kalendarza, aby zawsze wyświetlał pełny miesiąc (6 tygodni).
        """
        current_date = calendar.selectedDate()
        
        # Zakładając, że kalendarz to 6 tygodni
        calendar.setMinimumHeight(7 * 40)  # Każdy tydzień to około 40px


    # ---------------------------------- ilosc doroslych/dzieci -----------------------------
    def decrease_adults(self):
        """Zmniejsza liczbę dorosłych"""
        current_value = int(self.adults_input.text())  
        if current_value > 1:
            self.adults_input.setText(str(current_value - 1))  

    def increase_adults(self):
        """Zwiększa liczbę dorosłych"""
        current_value = int(self.adults_input.text())  
        self.adults_input.setText(str(current_value + 1))  

    def decrease_children(self):
        """Zmniejsza liczbę dzieci"""
        current_value = int(self.children_input.text())  
        if current_value > 0:
            self.children_input.setText(str(current_value - 1))

    def increase_children(self):
        """Zwiększa liczbę dzieci"""
        current_value = int(self.children_input.text()) 
        self.children_input.setText(str(current_value + 1)) 
        


    #-----------------------Budżet----------------------------------
    def update_budget(self):
        # Aktualizuje etykietę na podstawie wartości suwaka
        budget = round(self.budget_slider.value() / 50) * 50  # Zaokrąglanie do 50
        self.budget_slider.setValue(budget)
        self.budget_label.setText(str(budget))
    


    def setup_budget_slider(self):
        # Konfiguruje suwak
        self.budget_slider.setMinimum(100)
        self.budget_slider.setMaximum(10000)
        self.budget_slider.setTickInterval(500)
        self.budget_slider.setSingleStep(50)  # Krok co 50 jednostek
        self.budget_slider.setPageStep(50)  # Skok o 50 jednostek
        self.budget_slider.wheelEvent = lambda event: None 

    def setup_budget_ui(self):
        # Tworzy interfejs suwaka i etykiety
        self.budget_layout.addWidget(self.budget_slider)
        self.budget_layout.addWidget(self.budget_label)
        self.layout.addLayout(self.budget_layout)


    #--------------------------------------------------------------------------------------------------------------------------
    def generate_plan(self):

         # Sprawdzenie, czy miejsce wyjazdu zostało wprowadzone
        departure_text = self.departure_input.text().strip()
        if not departure_text:
            QMessageBox.warning(self, "Błąd", "Proszę podać miejsce wyjazdu!")
            return

        # Sprawdzenie, czy miejsce wyjazdu to współrzędne, czy nazwa miejscowości
        departure_coords = None
        if ',' in departure_text: 
            try:
                lat, lng = map(float, departure_text.split(','))
                departure_coords = (lat, lng)  # Przekształcamy tekst na krotkę współrzędnych
            except ValueError:
                QMessageBox.warning(self, "Błąd", "Proszę podać prawidłowe współrzędne (lat, lng)!")
                return
        else:
            # Jeśli nie są to współrzędne, traktujemy to jako nazwę miejscowości
            departure_coords = None  # W takim przypadku miejsce wyjazdu to tylko nazwa miejscowości


        form_data = {
            "destination": self.destination_input.text() if self.radio_specific.isChecked() else "Gdziekolwiek",
            "departure": departure_text,
            "departure_coords": departure_coords, 
            "start_date": self.start_date_input.text(),
            "end_date": self.end_date_input.text(),
            "company": self.get_selected_company(), 
            "adults": int(self.adults_input.text()) if self.adults_input.text().isdigit() else 1,  # Sprawdzanie liczby dorosłych
            "children": int(self.children_input.text()) if self.children_input.text().isdigit() else 0,  # Sprawdzanie liczby dzieci
            "travel_style": self.get_selected_styles(),  
            "budget": self.budget_slider.value(),
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