from PyQt5.QtWidgets import (
    QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QMessageBox,
    QHBoxLayout, QFrame, QSizePolicy, QComboBox, QCalendarWidget, QScrollArea
)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QColor, QTextCharFormat, QPixmap
from datetime import datetime, timedelta
import json
from gui.data_manager import BEHANDLUNGEN, zahnaerzte, patienten, speichere_daten, pfad_patienten

class BookingManager:
    def __init__(self, main_window):
        self.main_window = main_window

    def show_termin_buchen(self):
        if self.main_window.rolle == "Patient":
            if self.main_window.current_page:
                self.main_window.current_page.hide()
                self.main_window.current_page.deleteLater()
            
            # Container für die Terminbuchung
            self.main_window.termin_container = QFrame()
            self.main_window.termin_container.setStyleSheet("""
                QFrame {
                    background-color: white;
                    border-radius: 10px;
                    padding: 20px;
                }
            """)
            termin_layout = QVBoxLayout(self.main_window.termin_container)

            # Überschrift
            titel = QLabel("Termin buchen")
            titel.setStyleSheet("""
                font-size: 24px;
                font-weight: bold;
                color: #2c3e50;
                margin-bottom: 20px;
            """)
            titel.setAlignment(Qt.AlignCenter)
            termin_layout.addWidget(titel)

            # Prüfe ob Patient Probleme hat
            if not self.main_window.patient_data["probleme"]:
                keine_probleme = QLabel("Sie haben aktuell keine Behandlungen, für die Sie einen Termin buchen können.")
                keine_probleme.setStyleSheet("color: #7f8c8d;")
                keine_probleme.setWordWrap(True)
                termin_layout.addWidget(keine_probleme)
                
                # Hinweis zum Hinzufügen von Behandlungen
                hinweis = QLabel("Sie können in den Einstellungen neue Behandlungen hinzufügen.")
                hinweis.setStyleSheet("color: #3498db;")
                hinweis.setWordWrap(True)
                termin_layout.addWidget(hinweis)
                
                # Button zu den Einstellungen
                einstellungen_btn = QPushButton("Zu den Einstellungen")
                einstellungen_btn.clicked.connect(self.main_window.show_einstellungen)
                termin_layout.addWidget(einstellungen_btn)
            else:
                # Schritt 1: Behandlungsauswahl
                self.main_window.problem_box = QComboBox()
                for problem in self.main_window.patient_data["probleme"]:
                    self.main_window.problem_box.addItem(f"{problem['art']} ({problem['anzahl']} Zähne)")
                termin_layout.addWidget(QLabel("Behandlung:"))
                termin_layout.addWidget(self.main_window.problem_box)

                # Anzahl der Zähne
                termin_layout.addWidget(QLabel("Anzahl der Zähne für diese Behandlung:"))
                self.main_window.anzahl_box = QComboBox()
                self.update_anzahl_box()
                termin_layout.addWidget(self.main_window.anzahl_box)

                # Füllmaterial
                termin_layout.addWidget(QLabel("Füllmaterial:"))
                self.main_window.material_box = QComboBox()
                self.main_window.material_box.addItems(["normal", "hochwertig", "höchstwertig"])
                termin_layout.addWidget(self.main_window.material_box)

                # Kostenübersicht
                self.main_window.kosten_label = QLabel()
                self.main_window.kosten_label.setStyleSheet("""
                    background-color: #f8f9fa;
                    padding: 10px;
                    border-radius: 5px;
                    margin-top: 10px;
                """)
                termin_layout.addWidget(self.main_window.kosten_label)

                # Event-Handler verbinden
                self.main_window.problem_box.currentIndexChanged.connect(self.update_anzahl_box)
                self.main_window.anzahl_box.currentIndexChanged.connect(self.update_kosten)
                self.main_window.material_box.currentIndexChanged.connect(self.update_kosten)

                # Kostenberechnung
                self.update_kosten()

                # Weiter-Button
                self.main_window.weiter_btn = QPushButton("Weiter zur Arztwahl")
                self.main_window.weiter_btn.clicked.connect(self.show_arzt_selection)
                termin_layout.addWidget(self.main_window.weiter_btn)

            self.main_window.inhalt_layout_inner.addWidget(self.main_window.termin_container)
            self.main_window.current_page = self.main_window.termin_container

    def update_anzahl_box(self):
        self.main_window.anzahl_box.clear()
        current_problem = self.main_window.patient_data["probleme"][self.main_window.problem_box.currentIndex()]
        for i in range(1, current_problem["anzahl"] + 1):
            self.main_window.anzahl_box.addItem(str(i))
            
    def update_kosten(self):
        if self.main_window.problem_box.currentIndex() < 0 or self.main_window.anzahl_box.currentIndex() < 0:
            return
        problem = self.main_window.patient_data["probleme"][self.main_window.problem_box.currentIndex()]
        anzahl = int(self.main_window.anzahl_box.currentText())
        material = self.main_window.material_box.currentText()
        # Speichere ausgewählte Werte für spätere nutzung
        self.main_window.selected_problem = problem
        self.main_window.selected_anzahl = anzahl
        self.main_window.selected_material = material
        # Grundkosten und Zeit aus BEHANDLUNGEN
        behandlung = BEHANDLUNGEN[problem["art"]]["materialien"].get(material, BEHANDLUNGEN[problem["art"]]["materialien"]["normal"])
        grundkosten = behandlung["preis"]
        grundzeit = behandlung["zeit"]
        versicherung = self.main_window.patient_data["krankenkasse"]
        erstattung = behandlung["erstattung"].get(versicherung, 0.0)
        # Berechnung
        gesamtkosten = grundkosten * anzahl
        eigenanteil = gesamtkosten * (1 - erstattung)
        versicherung_anteil = gesamtkosten * erstattung
        # Kostenübersicht aktualisieren
        self.main_window.kosten_label.setText(f"""
            <h3>Kostenübersicht:</h3>
            <p>Gesamtkosten: {gesamtkosten:.2f}€</p>
            <p>Erstattung durch Versicherung: {versicherung_anteil:.2f}€</p>
            <p>Ihr Eigenanteil: {eigenanteil:.2f}€</p>
        """)

    def show_arzt_selection(self):
        # Container für Arztwahl
        self.main_window.arzt_container = QFrame()
        self.main_window.arzt_container.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 10px;
                padding: 20px;
            }
        """)
        arzt_layout = QVBoxLayout(self.main_window.arzt_container)
        
        titel = QLabel("Zahnarzt auswählen")
        titel.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            color: #2c3e50;
            margin-bottom: 20px;
        """)
        arzt_layout.addWidget(titel)
        
        # Lade Zahnärzte
        with open("data/zahnaerzte.json", "r", encoding="utf-8") as f:
            zahnaerzte_data = json.load(f)
            
        # Filtere Zahnärzte nach Krankenkasse
        versicherung = self.main_window.patient_data["krankenkasse"]
        self.main_window.verfuegbare_aerzte = [
            arzt for arzt in zahnaerzte_data
            if versicherung in arzt["behandelt"]
        ]
        
        if not self.main_window.verfuegbare_aerzte:
            QMessageBox.warning(self.main_window, "Keine Ärzte verfügbar", "Leider wurden keine Ärzte gefunden, die Ihre Versicherung akzeptieren.")
            return
        
        # Initialisiere Variablen für Kartenauswahl
        self.arzt_card_frames = []
        self.selected_arzt_index = None
        
        # Verwende Kartenansicht
        self.show_arzt_cards()
        arzt_layout.addWidget(self.main_window.arzt_cards_container)
        
        # Weiter-Button (anfangs deaktiviert)
        self.main_window.kalender_btn = QPushButton("Weiter zur Terminauswahl")
        self.main_window.kalender_btn.setEnabled(False)  # Erst aktivieren wenn Arzt ausgewählt
        self.main_window.kalender_btn.clicked.connect(self.show_kalender)
        arzt_layout.addWidget(self.main_window.kalender_btn)
        
        # Zurück-Button
        zurueck_btn = QPushButton("Zurück zur Behandlungsauswahl")
        zurueck_btn.clicked.connect(self.show_termin_buchen)
        arzt_layout.addWidget(zurueck_btn)
        
        # Aktualisiere UI
        if self.main_window.current_page:
            self.main_window.current_page.hide()
            self.main_window.current_page.deleteLater()
        self.main_window.inhalt_layout_inner.addWidget(self.main_window.arzt_container)
        self.main_window.current_page = self.main_window.arzt_container

    def show_kalender(self):
        # Prüfe ob ein Arzt ausgewählt wurde
        if self.selected_arzt_index is None:
            QMessageBox.warning(self.main_window, "Fehler", "Bitte wählen Sie zuerst einen Zahnarzt aus.")
            return
            
        # Verwende ausgewählten
        self.main_window.selected_zahnarzt = self.main_window.verfuegbare_aerzte[self.selected_arzt_index]
        
        # Container für Kalender
        self.main_window.kalender_container = QFrame()
        self.main_window.kalender_container.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 10px;
                padding: 20px;
            }
        """)
        self.main_window.kalender_container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        kalender_layout = QVBoxLayout(self.main_window.kalender_container)
        kalender_layout.setAlignment(Qt.AlignVCenter)
        
        titel = QLabel("Termin auswählen")
        titel.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            color: #2c3e50;
            margin-bottom: 20px;
        """)
        titel.setAlignment(Qt.AlignCenter)
        kalender_layout.addWidget(titel)
        
        # Kalender-Widget
        self.main_window.kalender = QCalendarWidget()
        self.main_window.kalender.setMinimumHeight(350)
        self.main_window.kalender.setMinimumWidth(600)
        self.main_window.kalender.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.main_window.kalender.setMinimumDate(QDate.currentDate())
        self.main_window.kalender.setMaximumDate(QDate.currentDate().addMonths(3))
        self.main_window.kalender.clicked.connect(self.show_time_slots)
        kalender_layout.addWidget(self.main_window.kalender, alignment=Qt.AlignCenter)
        
        # Container für Zeitauswahl
        time_container = QFrame()
        time_container.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border-radius: 5px;
                padding: 10px;
                margin-top: 10px;
            }
        """)
        time_layout = QHBoxLayout(time_container)
        time_label = QLabel("Uhrzeit:")
        time_layout.addWidget(time_label)
        self.main_window.time_box = QComboBox()
        self.main_window.time_box.setStyleSheet("""
            QComboBox {
                padding: 5px;
                border: 1px solid #e0e0e0;
                border-radius: 3px;
                min-width: 100px;
            }
        """)
        time_layout.addWidget(self.main_window.time_box)
        self.main_window.confirm_btn = QPushButton("✓ Termin bestätigen")
        self.main_window.confirm_btn.setEnabled(False)
        self.main_window.confirm_btn.clicked.connect(lambda: self.select_time(self.main_window.time_box.currentText()))
        self.main_window.confirm_btn.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71;
                color: white;
                border: none;
                padding: 8px 15px;
                border-radius: 3px;
            }
            QPushButton:disabled {
                background-color: #bdc3c7;
            }
            QPushButton:hover:!disabled {
                background-color: #27ae60;
            }
        """)
        time_layout.addWidget(self.main_window.confirm_btn)
        kalender_layout.addWidget(time_container, alignment=Qt.AlignCenter)
        kalender_layout.addStretch(1)
        
        # Zurück-Button
        zurueck_btn = QPushButton("Zurück zur Arztwahl")
        zurueck_btn.clicked.connect(self.show_arzt_selection)
        kalender_layout.addWidget(zurueck_btn)
        
        # Aktualisiere UI
        if self.main_window.current_page:
            self.main_window.current_page.hide()
            self.main_window.current_page.deleteLater()
        self.main_window.inhalt_layout_inner.addWidget(self.main_window.kalender_container)
        self.main_window.current_page = self.main_window.kalender_container
        
        # Deaktiviert Tage, an denen der Arzt nicht arbeitet
        self.update_calendar()

    def update_calendar(self):
        with open("data/termine.json", "r", encoding="utf-8") as f:
            termine = json.load(f)

        current = self.main_window.kalender.minimumDate()
        today = QDate.currentDate()
        while current <= self.main_window.kalender.maximumDate():
            weekday = current.toString("ddd")  # 'Mo', 'Di', ...
            format = QTextCharFormat()
            format.setForeground(QColor("#000000"))  # Immer schwarze Schrift

            if current < today:
                # Alle Tage vor heute: grau
                format.setBackground(QColor("#e0e0e0"))
            elif weekday == "Sa" or weekday == "So":
                # Samstag und Sonntag: rot
                format.setBackground(QColor("#ffb3b3"))
            elif weekday not in self.main_window.selected_zahnarzt["zeiten"]:
                # Arzt arbeitet nicht: grau
                format.setBackground(QColor("#e0e0e0"))
            else:
                # Verfügbare Tage: grün
                format.setBackground(QColor("#b9fbc0"))

            self.main_window.kalender.setDateTextFormat(current, format)
            current = current.addDays(1)
        
    def show_time_slots(self, date):
        self.main_window.selected_date = date
        weekday = date.toString("ddd")
        
        # Lösche alte Zeitslots
        self.main_window.time_box.clear()
        self.main_window.confirm_btn.setEnabled(False)
        
        if weekday not in self.main_window.selected_zahnarzt["zeiten"]:
            return
            
        # Lade bereits gebuchte Termine
        with open("data/termine.json", "r", encoding="utf-8") as f:
            termine = json.load(f)
            
        arzt_termine = termine.get(self.main_window.selected_zahnarzt["name"], {})
        tag_termine = arzt_termine.get(date.toString("yyyy-MM-dd"), {})
        
        # Behandlungsdauer in Minuten
        mat_info = BEHANDLUNGEN[self.main_window.selected_problem["art"]]["materialien"].get(self.main_window.selected_material, BEHANDLUNGEN[self.main_window.selected_problem["art"]]["materialien"]["normal"])
        behandlungsdauer = mat_info["zeit"]
        
        # Erstellt Liste aller blockierten Zeiten basierend auf bestehenden Terminen
        blockierte_zeiten = []
        for termin_zeit, termin_info in tag_termine.items():
            start_zeit = datetime.strptime(termin_zeit, "%H:%M")
            end_zeit = start_zeit + timedelta(minutes=termin_info["dauer"])
            
            # Blockiere alle 30-Minuten-Intervalle während der Behandlung
            current_block = start_zeit
            while current_block < end_zeit:
                blockierte_zeiten.append(current_block.strftime("%H:%M"))
                current_block += timedelta(minutes=30)
        
        # Zeige verfügbare Zeitslots
        for zeitfenster in self.main_window.selected_zahnarzt["zeiten"][weekday]:
            start, end = zeitfenster.split("-")
            current_time = datetime.strptime(start, "%H:%M")
            end_time = datetime.strptime(end, "%H:%M")
            
            while current_time <= end_time - timedelta(minutes=behandlungsdauer):
                time_str = current_time.strftime("%H:%M")
                
                # Prüfe ob Zeitslot verfügbar ist
                is_available = True
                
                # Prüfe ob gesamte Behandlungsdauer verfügbar ist
                test_time = current_time
                while test_time < current_time + timedelta(minutes=behandlungsdauer):
                    if test_time.strftime("%H:%M") in blockierte_zeiten:
                        is_available = False
                        break
                    test_time += timedelta(minutes=30)
                
                if is_available:
                    self.main_window.time_box.addItem(time_str)
                    
                current_time += timedelta(minutes=30)
        
        if self.main_window.time_box.count() > 0:
            self.main_window.confirm_btn.setEnabled(True)
            
    def select_time(self, time):
        self.main_window.selected_time = time
        
        # Speichere Termin
        with open("data/termine.json", "r", encoding="utf-8") as f:
            termine = json.load(f)
            
        # Erstelle Einträge wenn sie noch nicht existieren
        if self.main_window.selected_zahnarzt["name"] not in termine:
            termine[self.main_window.selected_zahnarzt["name"]] = {}
            
        date_str = self.main_window.selected_date.toString("yyyy-MM-dd")
        if date_str not in termine[self.main_window.selected_zahnarzt["name"]]:
            termine[self.main_window.selected_zahnarzt["name"]][date_str] = {}
            
        # Füge Termin hinzu
        mat_info = BEHANDLUNGEN[self.main_window.selected_problem["art"]]["materialien"].get(self.main_window.selected_material, BEHANDLUNGEN[self.main_window.selected_problem["art"]]["materialien"]["normal"])
        termine[self.main_window.selected_zahnarzt["name"]][date_str][time] = {
            "patient": self.main_window.patient_data["name"],
            "behandlung": self.main_window.selected_problem["art"],
            "material": self.main_window.selected_material,
            "dauer": mat_info["zeit"],
            "anzahl": self.main_window.selected_anzahl
        }
        
        with open("data/termine.json", "w", encoding="utf-8") as f:
            json.dump(termine, f, indent=2)
            
        # Aktualisiere Patientendaten
        for i, problem in enumerate(self.main_window.patient_data["probleme"]):
            if problem["art"] == self.main_window.selected_problem["art"]:
                if problem["anzahl"] > self.main_window.selected_anzahl:
                    problem["anzahl"] -= self.main_window.selected_anzahl
                else:
                    del self.main_window.patient_data["probleme"][i]
                break
                
        with open("data/patienten.json", "r", encoding="utf-8") as f:
            patienten_data = json.load(f)
            
        for patient in patienten_data:
            if patient["name"] == self.main_window.patient_data["name"]:
                patient["probleme"] = self.main_window.patient_data["probleme"]
                break
                
        with open("data/patienten.json", "w", encoding="utf-8") as f:
            json.dump(patienten_data, f, indent=2)
            
        msg = QMessageBox(self.main_window)
        msg.setWindowTitle("Erfolg")
        msg.setIcon(QMessageBox.Information)
        msg.setTextFormat(Qt.PlainText)
        msg.setText(
            f"Termin erfolgreich gebucht!\n\n"
            f"Datum: {self.main_window.selected_date.toString('dd.MM.yyyy')}\n"
            f"Uhrzeit: {time}\n"
            f"Zahnarzt: {self.main_window.selected_zahnarzt['name']}\n"
            f"Behandlung: {self.main_window.selected_problem['art']}\n"
            f"Anzahl Zähne: {self.main_window.selected_anzahl}\n"
            f"Material: {self.main_window.selected_material}"
        )
        msg.setStyleSheet("QLabel{ text-align: left; }")
        msg.exec_()
        
        # Zeige die Terminübersicht
        self.main_window.show_meine_termine()

    def cancel_termin(self, arzt, datum, zeit):
        msg_box = QMessageBox(self.main_window)
        msg_box.setIcon(QMessageBox.Question)
        msg_box.setWindowTitle("Termin absagen")
        # Datum deutsche Format
        try:
            datum_dt = datetime.strptime(datum, "%Y-%m-%d")
            datum_de = datum_dt.strftime("%d.%m.%Y")
        except Exception:
            datum_de = datum  # Fallback falls Format schon passt
        msg_box.setText(f"Möchten Sie den Termin am {datum_de} um {zeit} Uhr bei {arzt} wirklich absagen?")
        ja_btn = msg_box.addButton("Ja", QMessageBox.YesRole)
        nein_btn = msg_box.addButton("Nein", QMessageBox.NoRole)
        msg_box.setDefaultButton(ja_btn)
        msg_box.exec_()
        if msg_box.clickedButton() == ja_btn:
            # Lade alle Termine
            with open("data/termine.json", "r", encoding="utf-8") as f:
                alle_termine = json.load(f)
            # Termin-Infos merken, bevor gelöscht wird
            termin_info = None
            if arzt in alle_termine and datum in alle_termine[arzt] and zeit in alle_termine[arzt][datum]:
                termin_info = alle_termine[arzt][datum][zeit]
                del alle_termine[arzt][datum][zeit]
                if not alle_termine[arzt][datum]:
                    del alle_termine[arzt][datum]
            # Speichere zurück
            with open("data/termine.json", "w", encoding="utf-8") as f:
                json.dump(alle_termine, f, indent=2, ensure_ascii=False)
            # Entferne Termin auch aus Patientenakte (Problem wieder hinzufügen)
            if termin_info is not None:
                with open("data/patienten.json", "r", encoding="utf-8") as f:
                    patienten_data = json.load(f)
                for patient in patienten_data:
                    if patient["name"] == self.main_window.benutzername:
                        # Problem wieder hinzufügen (art, anzahl=1, material)
                        art = termin_info.get("behandlung")
                        material = termin_info.get("material", "normal")
                        anzahl = termin_info.get("anzahl", 1) # Verwende die gespeicherte Anzahl
                        # Prüfe, ob Problem schon existiert (mit gleichem Material)
                        gefunden = False
                        for p in patient["probleme"]:
                            if p["art"] == art and p.get("material", "normal") == material:
                                p["anzahl"] = p.get("anzahl", 1) + anzahl
                                gefunden = True
                                break
                        if not gefunden:
                            patient["probleme"].append({"art": art, "anzahl": anzahl, "material": material})
                        # Aktualisiere self.main_window.patient_data sofort
                        self.main_window.patient_data = patient
                        break
                with open("data/patienten.json", "w", encoding="utf-8") as f:
                    json.dump(patienten_data, f, indent=2, ensure_ascii=False)
            QMessageBox.information(self.main_window, "Termin abgesagt", "Der Termin wurde erfolgreich abgesagt.")
        self.main_window.show_meine_termine()

    def show_arzt_cards(self):
        # Scrollbereich für Arztkarten
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setStyleSheet("QScrollArea { border: none; background: transparent; }")

        # Container für Karten (Widget im Scrollbereich)
        cards_widget = QWidget()
        cards_layout = QHBoxLayout(cards_widget)
        cards_layout.setContentsMargins(15, 0, 0, 0)  # 10px links, Rest 0
        cards_layout.setSpacing(20)
        cards_layout.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        # Lade Bilder
        try:
            with open("data/zahnaerzte_bilder.json", "r", encoding="utf-8") as f:
                arzt_bilder = json.load(f)
        except FileNotFoundError:
            arzt_bilder = {}

        verfuegbare_aerzte = self.main_window.verfuegbare_aerzte
        self.arzt_card_frames = []
        for idx, arzt in enumerate(verfuegbare_aerzte):
            card = QFrame()
            card.setObjectName(f"arzt_card_{idx}")
            card.setCursor(Qt.PointingHandCursor)
            card.setFixedSize(230, 340)
            card.setStyleSheet("""
                QFrame {
                    background: white;
                    border-radius: 18px;
                    border: 2px solid #e0e0e0;
                }
            """)
            card_layout = QVBoxLayout(card)
            card_layout.setContentsMargins(0, 0, 0, 0)
            card_layout.setSpacing(0)
            card_layout.setAlignment(Qt.AlignTop)
            # Bild oben, zentriert, nicht verzerrt
            bild_label = QLabel()
            bild_label.setFixedSize(180, 180)
            bild_label.setStyleSheet("background-color: #f8f9fa; border-radius: 10px; margin: 0px; padding: 0px;")
            bild_label.setAlignment(Qt.AlignCenter)
            bild_label.setScaledContents(True)
            if arzt["name"] in arzt_bilder:
                bild_path = arzt_bilder[arzt["name"]]
                pixmap = QPixmap(bild_path).scaled(180, 180, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
                bild_label.setPixmap(pixmap)
            else:
                bild_label.setText(arzt["name"][0].upper())
                bild_label.setStyleSheet("""
                    background-color: #3498db;
                    color: white;
                    border-radius: 10px;
                    font-size: 48px;
                    font-weight: bold;
                    margin: 0px;
                    padding: 0px;
                """)
            card_layout.addWidget(bild_label, alignment=Qt.AlignHCenter)
            card_layout.addSpacing(18)
            name_label = QLabel(arzt["name"])
            name_label.setStyleSheet("font-weight: bold; font-size: 18px; color: #2c3e50;")
            name_label.setAlignment(Qt.AlignCenter)
            card_layout.addWidget(name_label)
            card_layout.addStretch(1)
            self.arzt_card_frames.append((card, name_label))
            def make_click_handler(global_idx):
                return lambda event: self.select_arzt_card(global_idx)
            card.mousePressEvent = make_click_handler(idx)
            cards_layout.addWidget(card)
        cards_widget.setLayout(cards_layout)
        scroll_area.setWidget(cards_widget)
        self.main_window.arzt_cards_container = scroll_area

    def select_arzt_card(self, idx):
        self.selected_arzt_index = idx
        self.main_window.selected_zahnarzt = self.main_window.verfuegbare_aerzte[idx]
        
        # Farbliche Markierung wenn ausgewählt
        for i, (card, name_label) in enumerate(self.arzt_card_frames):
            if i == idx:
                card.setStyleSheet("background: white; border-radius: 18px; border: 3px solid #217dbb;")
                name_label.setStyleSheet("font-weight: bold; font-size: 18px; color: #217dbb;")
            else:
                card.setStyleSheet("background: white; border-radius: 18px; border: 2px solid #e0e0e0;")
                name_label.setStyleSheet("font-weight: bold; font-size: 18px; color: #2c3e50;")
        
        # Aktiviere den Weiter-Button
        if hasattr(self.main_window, 'kalender_btn'):
            self.main_window.kalender_btn.setEnabled(True) 