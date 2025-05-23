import sys
import json
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton,
    QVBoxLayout, QMessageBox, QHBoxLayout, QFrame, QSizePolicy, QComboBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QIcon, QPixmap, QColor, QPalette

# Globale Stil-Definitionen
STYLE = """
QWidget {
    font-family: 'Segoe UI', Arial;
    font-size: 10pt;
}

QLabel {
    color: #2c3e50;
}

QLineEdit {
    padding: 8px;
    border: 2px solid #e0e0e0;
    border-radius: 5px;
    background-color: white;
    margin: 5px 0px;
}

QLineEdit:focus {
    border: 2px solid #3498db;
}

QPushButton {
    background-color: #3498db;
    color: white;
    border: none;
    padding: 10px 20px;
    border-radius: 5px;
    font-weight: bold;
    margin: 5px 0px;
}

QPushButton:hover {
    background-color: #2980b9;
}

QPushButton:pressed {
    background-color: #2472a4;
}

QComboBox {
    padding: 8px;
    border: 2px solid #e0e0e0;
    border-radius: 5px;
    background-color: white;
    margin: 5px 0px;
}

QComboBox:drop-down {
    border: none;
}

QComboBox:down-arrow {
    width: 12px;
    height: 12px;
}

QFrame[frameShape="4"] { /* Horizontale Linie */
    color: #e0e0e0;
    margin: 10px 0px;
}
"""

# JSON-Hilfsfunktionen
def lade_daten(pfad):
    with open(pfad, "r", encoding="utf-8") as f:
        daten = json.load(f)
        for eintrag in daten:
            if "passwort_geaendert" not in eintrag:
                eintrag["passwort_geaendert"] = False
        return daten

def speichere_daten(pfad, daten):
    with open(pfad, "w", encoding="utf-8") as f:
        json.dump(daten, f, ensure_ascii=False, indent=2)

# Datenpfade
pfad_patienten = "data/patienten.json"
pfad_zahnaerzte = "data/zahnaerzte.json"
patienten = lade_daten(pfad_patienten)
zahnaerzte = lade_daten(pfad_zahnaerzte)

# Preise und Zeitaufwand für Behandlungen
BEHANDLUNGEN = {
    "Karies klein": {"preis": 50, "zeit": 30, "einheit": "Minuten"},
    "Karies Groß": {"preis": 120, "zeit": 45, "einheit": "Minuten"},
    "Teilkrone": {"preis": 400, "zeit": 60, "einheit": "Minuten"},
    "Krone": {"preis": 600, "zeit": 90, "einheit": "Minuten"},
    "Wurzelbehandlung": {"preis": 300, "zeit": 120, "einheit": "Minuten"}
}

# Erstattungssätze nach Versicherung
ERSTATTUNG = {
    "gesetzlich": 0.7,  # 70% Erstattung
    "privat": 0.85,    # 85% Erstattung
    "freiwillig gesetzlich": 0.75  # 75% Erstattung
}

# Hauptfenster
class MainFenster(QWidget):
    def __init__(self, benutzername, rolle):
        super().__init__()
        self.benutzername = benutzername
        self.rolle = rolle
        self.current_page = None  # Speichert die aktuelle Seite
        
        # Finde den aktuellen Patienten
        self.patient_data = None
        if rolle == "Patient":
            for p in patienten:
                if p["name"] == benutzername:
                    self.patient_data = p
                    break

        self.setWindowTitle("Dashboard")
        self.setGeometry(200, 200, 1200, 700)
        self.setStyleSheet(STYLE)
        
        # Setze Hintergrundfarbe
        palette = self.palette()
        palette.setColor(QPalette.Window, QColor("#f5f6fa"))
        self.setPalette(palette)
        self.setAutoFillBackground(True)

        self.init_ui()

    def logout(self):
        # Öffne das Login-Fenster
        self.login_fenster = LoginFenster()
        self.login_fenster.show()
        # Schließe das aktuelle Fenster
        self.close()

    def berechne_kosten_und_zeit(self, patient):
        if not patient:
            return None
            
        gesamt_kosten = 0
        gesamt_zeit = 0
        erstattung = ERSTATTUNG.get(patient["krankenkasse"], 0.7)
        
        analyse = []
        for problem in patient["probleme"]:
            behandlung = BEHANDLUNGEN.get(problem["art"])
            if behandlung:
                anzahl = problem["anzahl"]
                kosten = behandlung["preis"] * anzahl
                zeit = behandlung["zeit"] * anzahl
                
                analyse.append({
                    "art": problem["art"],
                    "anzahl": anzahl,
                    "kosten": kosten,
                    "zeit": zeit,
                    "einheit": behandlung["einheit"]
                })
                
                gesamt_kosten += kosten
                gesamt_zeit += zeit
        
        eigenanteil = gesamt_kosten * (1 - erstattung)
        versicherung_anteil = gesamt_kosten * erstattung
        
        return {
            "analyse": analyse,
            "gesamt_kosten": gesamt_kosten,
            "eigenanteil": eigenanteil,
            "versicherung_anteil": versicherung_anteil,
            "gesamt_zeit": gesamt_zeit
        }

    def show_meine_daten(self):
        if self.current_page:
            self.current_page.hide()
            self.current_page.deleteLater()
        
        # Container für die Analyse
        analyse_container = QFrame()
        analyse_container.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 10px;
                padding: 20px;
            }
        """)
        analyse_layout = QVBoxLayout(analyse_container)

        if self.rolle == "Patient" and self.patient_data:
            # Analyse der Patientendaten
            analyse_data = self.berechne_kosten_und_zeit(self.patient_data)
            
            # Überschrift
            titel = QLabel("Ihre persönliche Behandlungsanalyse")
            titel.setStyleSheet("""
                font-size: 24px;
                font-weight: bold;
                color: #2c3e50;
                margin-bottom: 20px;
            """)
            titel.setAlignment(Qt.AlignCenter)
            analyse_layout.addWidget(titel)

            # Versicherungsinformation
            versicherung_info = QLabel(f"Versicherung: {self.patient_data['krankenkasse']}")
            versicherung_info.setStyleSheet("font-size: 16px; color: #7f8c8d; margin-bottom: 10px;")
            analyse_layout.addWidget(versicherung_info)

            # Container für die Analyse-Details
            details_container = QFrame()
            details_container.setStyleSheet("""
                QFrame {
                    background-color: #f8f9fa;
                    border-radius: 8px;
                    padding: 15px;
                }
            """)
            details_layout = QVBoxLayout(details_container)

            # Einzelne Behandlungen
            for item in analyse_data["analyse"]:
                behandlung_frame = QFrame()
                behandlung_frame.setStyleSheet("""
                    QFrame {
                        background-color: white;
                        border-radius: 5px;
                        padding: 10px;
                        margin: 5px 0px;
                    }
                """)
                behandlung_layout = QVBoxLayout(behandlung_frame)
                
                art_label = QLabel(f"🦷 {item['art']} ({item['anzahl']}x)")
                art_label.setStyleSheet("font-weight: bold; color: #2c3e50;")
                behandlung_layout.addWidget(art_label)
                
                kosten_label = QLabel(f"Kosten: {item['kosten']}€")
                kosten_label.setStyleSheet("color: #2c3e50;")
                behandlung_layout.addWidget(kosten_label)
                
                zeit_label = QLabel(f"Zeitaufwand: {item['zeit']} {item['einheit']}")
                zeit_label.setStyleSheet("color: #2c3e50;")
                behandlung_layout.addWidget(zeit_label)
                
                details_layout.addWidget(behandlung_frame)

            analyse_layout.addWidget(details_container)

            # Zusammenfassung
            zusammenfassung = QFrame()
            zusammenfassung.setStyleSheet("""
                QFrame {
                    background-color: #e8f4f8;
                    border-radius: 8px;
                    padding: 15px;
                    margin-top: 20px;
                }
            """)
            zusammenfassung_layout = QVBoxLayout(zusammenfassung)

            gesamt_label = QLabel(f"Gesamtkosten: {analyse_data['gesamt_kosten']}€")
            gesamt_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #2c3e50;")
            zusammenfassung_layout.addWidget(gesamt_label)

            erstattung_label = QLabel(f"Erstattung durch Versicherung: {analyse_data['versicherung_anteil']:.2f}€")
            erstattung_label.setStyleSheet("color: #27ae60; font-size: 16px;")
            zusammenfassung_layout.addWidget(erstattung_label)

            eigenanteil_label = QLabel(f"Ihr Eigenanteil: {analyse_data['eigenanteil']:.2f}€")
            eigenanteil_label.setStyleSheet("color: #e74c3c; font-size: 16px;")
            zusammenfassung_layout.addWidget(eigenanteil_label)

            zeit_label = QLabel(f"Gesamter Zeitaufwand: {analyse_data['gesamt_zeit']} Minuten")
            zeit_label.setStyleSheet("color: #2c3e50; font-size: 16px;")
            zusammenfassung_layout.addWidget(zeit_label)

            analyse_layout.addWidget(zusammenfassung)

        self.inhalt_layout_inner.addWidget(analyse_container)
        self.current_page = analyse_container

    def show_einstellungen(self):
        if self.current_page:
            self.current_page.hide()
            self.current_page.deleteLater()

        # Container für Einstellungen
        settings_container = QFrame()
        settings_container.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 10px;
                padding: 20px;
            }
        """)
        settings_layout = QVBoxLayout(settings_container)

        # Überschrift
        titel = QLabel("Einstellungen")
        titel.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            color: #2c3e50;
            margin-bottom: 20px;
        """)
        titel.setAlignment(Qt.AlignCenter)
        settings_layout.addWidget(titel)

        if self.rolle == "Patient" and self.patient_data:
            # Passwort ändern
            passwort_group = QFrame()
            passwort_group.setStyleSheet("""
                QFrame {
                    background-color: #f8f9fa;
                    border-radius: 8px;
                    padding: 15px;
                    margin-bottom: 15px;
                }
            """)
            passwort_layout = QVBoxLayout(passwort_group)
            
            passwort_label = QLabel("Passwort ändern")
            passwort_label.setStyleSheet("font-weight: bold; font-size: 16px; color: #2c3e50;")
            passwort_layout.addWidget(passwort_label)
            
            self.neues_passwort = QLineEdit()
            self.neues_passwort.setPlaceholderText("Neues Passwort")
            self.neues_passwort.setEchoMode(QLineEdit.Password)
            passwort_layout.addWidget(self.neues_passwort)
            
            passwort_btn = QPushButton("🔒 Passwort aktualisieren")
            passwort_btn.clicked.connect(self.update_passwort)
            passwort_layout.addWidget(passwort_btn)
            
            settings_layout.addWidget(passwort_group)

            # Krankenkasse ändern
            kasse_group = QFrame()
            kasse_group.setStyleSheet("""
                QFrame {
                    background-color: #f8f9fa;
                    border-radius: 8px;
                    padding: 15px;
                    margin-bottom: 15px;
                }
            """)
            kasse_layout = QVBoxLayout(kasse_group)
            
            kasse_label = QLabel("Krankenkasse ändern")
            kasse_label.setStyleSheet("font-weight: bold; font-size: 16px; color: #2c3e50;")
            kasse_layout.addWidget(kasse_label)
            
            self.kasse_box = QComboBox()
            self.kasse_box.addItems(["gesetzlich", "privat", "freiwillig gesetzlich"])
            self.kasse_box.setCurrentText(self.patient_data["krankenkasse"])
            kasse_layout.addWidget(self.kasse_box)
            
            kasse_btn = QPushButton("💉 Krankenkasse aktualisieren")
            kasse_btn.clicked.connect(self.update_krankenkasse)
            kasse_layout.addWidget(kasse_btn)
            
            settings_layout.addWidget(kasse_group)

            # Neue Probleme hinzufügen
            probleme_group = QFrame()
            probleme_group.setStyleSheet("""
                QFrame {
                    background-color: #f8f9fa;
                    border-radius: 8px;
                    padding: 15px;
                }
            """)
            probleme_layout = QVBoxLayout(probleme_group)
            
            probleme_label = QLabel("Neue Behandlung hinzufügen")
            probleme_label.setStyleSheet("font-weight: bold; font-size: 16px; color: #2c3e50;")
            probleme_layout.addWidget(probleme_label)
            
            self.problem_box = QComboBox()
            self.problem_box.addItems([
                "Karies klein", "Karies Groß", "Teilkrone", "Krone", "Wurzelbehandlung"
            ])
            probleme_layout.addWidget(self.problem_box)
            
            self.problem_anzahl = QLineEdit()
            self.problem_anzahl.setPlaceholderText("Anzahl")
            probleme_layout.addWidget(self.problem_anzahl)
            
            problem_btn = QPushButton("➕ Behandlung hinzufügen")
            problem_btn.clicked.connect(self.add_problem)
            probleme_layout.addWidget(problem_btn)
            
            settings_layout.addWidget(probleme_group)

        self.inhalt_layout_inner.addWidget(settings_container)
        self.current_page = settings_container

    def update_passwort(self):
        if not self.patient_data:
            return
            
        neues_passwort = self.neues_passwort.text().strip()
        if not neues_passwort:
            QMessageBox.warning(self, "Fehler", "Bitte geben Sie ein neues Passwort ein.")
            return
            
        self.patient_data["passwort"] = neues_passwort
        speichere_daten(pfad_patienten, patienten)
        QMessageBox.information(self, "Erfolg", "Passwort wurde aktualisiert!")
        self.neues_passwort.clear()

    def update_krankenkasse(self):
        if not self.patient_data:
            return
            
        neue_kasse = self.kasse_box.currentText()
        self.patient_data["krankenkasse"] = neue_kasse
        speichere_daten(pfad_patienten, patienten)
        QMessageBox.information(self, "Erfolg", "Krankenkasse wurde aktualisiert!")
        self.show_meine_daten()  # Aktualisiere die Analyse-Ansicht

    def add_problem(self):
        if not self.patient_data:
            return
            
        problem = self.problem_box.currentText()
        try:
            anzahl = int(self.problem_anzahl.text().strip())
            if anzahl <= 0:
                raise ValueError()
        except ValueError:
            QMessageBox.warning(self, "Fehler", "Bitte geben Sie eine gültige Anzahl ein.")
            return
            
        neues_problem = {
            "art": problem,
            "anzahl": anzahl
        }
        
        self.patient_data["probleme"].append(neues_problem)
        speichere_daten(pfad_patienten, patienten)
        QMessageBox.information(self, "Erfolg", "Neue Behandlung wurde hinzugefügt!")
        self.problem_anzahl.clear()
        self.show_meine_daten()  # Aktualisiere die Analyse-Ansicht

    def init_ui(self):
        hauptlayout = QVBoxLayout()
        hauptlayout.setContentsMargins(20, 20, 20, 20)
        hauptlayout.setSpacing(20)

        # Begrüßung oben mit modernem Design
        begruessung_container = QFrame()
        begruessung_container.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 10px;
                padding: 20px;
            }
        """)
        begruessung_layout = QVBoxLayout(begruessung_container)
        
        begruessung = QLabel(f"Willkommen {self.benutzername}")
        begruessung.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            color: #2c3e50;
            margin-bottom: 5px;
        """)
        begruessung.setAlignment(Qt.AlignCenter)
        begruessung_layout.addWidget(begruessung)
        
        rolle_label = QLabel(f"Angemeldet als {self.rolle}")
        rolle_label.setStyleSheet("color: #7f8c8d;")
        rolle_label.setAlignment(Qt.AlignCenter)
        begruessung_layout.addWidget(rolle_label)
        
        hauptlayout.addWidget(begruessung_container)

        # Hauptbereich: horizontal geteilt
        inhalt_layout = QHBoxLayout()
        inhalt_layout.setSpacing(20)

        # Linkes Menü (Profilbereich) mit Schatten
        profil_container = QFrame()
        profil_container.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 10px;
                padding: 20px;
            }
        """)
        profil_layout = QVBoxLayout(profil_container)
        profil_layout.setSpacing(15)

        # Profilbild mit modernem Design
        profilbild = QLabel()
        profilbild.setFixedSize(100, 100)
        profilbild.setStyleSheet("""
            background-color: #3498db;
            border-radius: 50px;
            color: white;
            font-size: 36px;
            font-weight: bold;
        """)
        profilbild.setText(self.benutzername[0].upper())
        profilbild.setAlignment(Qt.AlignCenter)
        profil_layout.addWidget(profilbild, alignment=Qt.AlignCenter)

        # Trennlinie
        linie = QFrame()
        linie.setFrameShape(QFrame.HLine)
        linie.setFrameShadow(QFrame.Sunken)
        profil_layout.addWidget(linie)

        # Moderne Menü-Buttons mit Funktionalität
        menu_buttons = [
            ("Meine Daten", "📋", self.show_meine_daten),
            ("Termin buchen", "📅", None),
            ("Einstellungen", "⚙️", self.show_einstellungen)
        ]

        for text, icon, func in menu_buttons:
            btn = QPushButton(f"{icon} {text}")
            btn.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    color: #2c3e50;
                    text-align: left;
                    padding: 12px;
                    border-radius: 5px;
                    font-weight: normal;
                }
                QPushButton:hover {
                    background-color: #f0f0f0;
                }
            """)
            if func:
                btn.clicked.connect(func)
            profil_layout.addWidget(btn)

        profil_layout.addStretch()

        # Logout Button
        logout_btn = QPushButton("🚪 Abmelden")
        logout_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                text-align: center;
                padding: 12px;
                border-radius: 5px;
                font-weight: bold;
                margin-top: 10px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        logout_btn.clicked.connect(self.logout)
        profil_layout.addWidget(logout_btn)

        # Inhaltsbereich
        inhalt_container = QFrame()
        inhalt_container.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 10px;
                padding: 20px;
            }
        """)
        self.inhalt_layout_inner = QVBoxLayout(inhalt_container)

        # Layout zusammensetzen
        inhalt_layout.addWidget(profil_container, stretch=1)
        inhalt_layout.addWidget(inhalt_container, stretch=3)
        hauptlayout.addLayout(inhalt_layout)

        self.setLayout(hauptlayout)
        
        # Zeige initial die "Meine Daten" Seite
        if self.rolle == "Patient":
            self.show_meine_daten()

# Passwort ändern Fenster
class PasswortAendernFenster(QWidget):
    def __init__(self, benutzer, rolle, parent=None):
        super().__init__()
        self.benutzer = benutzer
        self.rolle = rolle
        self.parent_fenster = parent
        self.setWindowTitle("Passwort ändern")
        self.setGeometry(150, 150, 400, 300)
        self.setStyleSheet(STYLE)

        # Setze Hintergrundfarbe
        palette = self.palette()
        palette.setColor(QPalette.Window, QColor("#f5f6fa"))
        self.setPalette(palette)
        self.setAutoFillBackground(True)

        # Container für das gesamte Formular
        main_container = QFrame(self)
        main_container.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 10px;
                padding: 20px;
            }
        """)
        
        layout = QVBoxLayout(main_container)
        layout.setSpacing(15)

        # Überschrift
        self.label_info = QLabel(f"Passwort ändern für {self.benutzer['name']}")
        self.label_info.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
            color: #2c3e50;
            margin-bottom: 10px;
        """)
        layout.addWidget(self.label_info, alignment=Qt.AlignCenter)

        # Rolle Label
        rolle_label = QLabel(f"Angemeldet als {rolle}")
        rolle_label.setStyleSheet("color: #7f8c8d;")
        rolle_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(rolle_label)

        # Passwort Felder
        self.neues_passwort = QLineEdit()
        self.neues_passwort.setEchoMode(QLineEdit.Password)
        self.neues_passwort.setPlaceholderText("Neues Passwort eingeben")
        layout.addWidget(self.neues_passwort)

        self.bestaetigen_passwort = QLineEdit()
        self.bestaetigen_passwort.setEchoMode(QLineEdit.Password)
        self.bestaetigen_passwort.setPlaceholderText("Passwort bestätigen")
        layout.addWidget(self.bestaetigen_passwort)

        # Button mit Icon
        self.speichern_button = QPushButton("🔒 Passwort ändern")
        layout.addWidget(self.speichern_button)
        self.speichern_button.clicked.connect(self.passwort_aendern)

        # Container Layout
        container_layout = QVBoxLayout(self)
        container_layout.addWidget(main_container)
        container_layout.setContentsMargins(20, 20, 20, 20)

    def passwort_aendern(self):
        neues = self.neues_passwort.text().strip()
        bestaetigung = self.bestaetigen_passwort.text().strip()

        if not neues or not bestaetigung:
            QMessageBox.warning(self, "Fehler", "Bitte beide Felder ausfüllen.")
            return
        if neues != bestaetigung:
            QMessageBox.warning(self, "Fehler", "Passwörter stimmen nicht überein.")
            return

        self.benutzer["passwort"] = neues
        self.benutzer["passwort_geaendert"] = True

        if self.rolle == "Patient":
            speichere_daten(pfad_patienten, patienten)
        else:
            speichere_daten(pfad_zahnaerzte, zahnaerzte)

        QMessageBox.information(self, "Erfolg", "Passwort erfolgreich geändert.")
        self.mainfenster = MainFenster(self.benutzer["name"], self.rolle)
        self.mainfenster.show()
        self.close()
        if self.parent_fenster:
            self.parent_fenster.close()

# Registrierungsfenster für neue Patienten
class RegistrierungsFenster(QWidget):
    def __init__(self, parent=None):
        super().__init__()
        self.setWindowTitle("Registrierung")
        self.setGeometry(150, 150, 400, 500)
        self.setStyleSheet(STYLE)

        # Setze Hintergrundfarbe
        palette = self.palette()
        palette.setColor(QPalette.Window, QColor("#f5f6fa"))
        self.setPalette(palette)
        self.setAutoFillBackground(True)

        # Container für das gesamte Formular
        main_container = QFrame(self)
        main_container.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 10px;
                padding: 20px;
            }
        """)

        layout = QVBoxLayout(main_container)
        layout.setSpacing(15)

        # Überschrift
        titel = QLabel("Neue Registrierung")
        titel.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            color: #2c3e50;
            margin-bottom: 10px;
        """)
        layout.addWidget(titel, alignment=Qt.AlignCenter)

        # Untertitel
        untertitel = QLabel("Bitte füllen Sie alle Felder aus")
        untertitel.setStyleSheet("color: #7f8c8d;")
        untertitel.setAlignment(Qt.AlignCenter)
        layout.addWidget(untertitel)

        # Formularfelder
        self.eingabe_name = QLineEdit()
        self.eingabe_name.setPlaceholderText("👤 Vollständiger Name")
        layout.addWidget(self.eingabe_name)

        self.eingabe_passwort = QLineEdit()
        self.eingabe_passwort.setPlaceholderText("🔒 Passwort")
        self.eingabe_passwort.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.eingabe_passwort)

        # Versicherung
        versicherung_label = QLabel("Versicherung:")
        versicherung_label.setStyleSheet("color: #2c3e50; font-weight: bold;")
        layout.addWidget(versicherung_label)
        
        self.versicherung_box = QComboBox()
        self.versicherung_box.addItems(["gesetzlich", "privat", "freiwillig gesetzlich"])
        layout.addWidget(self.versicherung_box)

        # Beschwerden
        probleme_label = QLabel("Beschwerde:")
        probleme_label.setStyleSheet("color: #2c3e50; font-weight: bold;")
        layout.addWidget(probleme_label)
        
        self.probleme_box = QComboBox()
        self.probleme_box.addItems([
            "Karies klein", "Karies Groß", "Teilkrone", "Krone", "Wurzelbehandlung"
        ])
        layout.addWidget(self.probleme_box)

        self.eingabe_anzahl = QLineEdit()
        self.eingabe_anzahl.setPlaceholderText("🔢 Anzahl (optional, Standard = 1)")
        layout.addWidget(self.eingabe_anzahl)

        # Registrieren Button
        self.registrieren_button = QPushButton("✅ Registrierung abschließen")
        self.registrieren_button.clicked.connect(self.registriere)
        layout.addWidget(self.registrieren_button)

        # Container Layout
        container_layout = QVBoxLayout(self)
        container_layout.addWidget(main_container)
        container_layout.setContentsMargins(20, 20, 20, 20)

    def registriere(self):
        name = self.eingabe_name.text().strip()
        pw = self.eingabe_passwort.text().strip()
        versicherung = self.versicherung_box.currentText()
        beschwerde = self.probleme_box.currentText()
        anzahl_text = self.eingabe_anzahl.text().strip()

        if not name or not pw or not versicherung or not beschwerde:
            QMessageBox.warning(self, "Fehler", "Bitte alle Pflichtfelder ausfüllen.")
            return

        try:
            anzahl = int(anzahl_text) if anzahl_text else 1
        except ValueError:
            QMessageBox.warning(self, "Fehler", "Anzahl muss eine Zahl sein.")
            return

        neuer_patient = {
            "name": name,
            "passwort": pw,
            "krankenkasse": versicherung,
            "probleme": [
                {
                    "art": beschwerde,
                    "anzahl": anzahl
                }
            ],
            "passwort_geaendert": True
        }

        patienten.append(neuer_patient)
        speichere_daten(pfad_patienten, patienten)

        QMessageBox.information(self, "Erfolg", "Registrierung erfolgreich!")
        self.close()

# Login Fenster
class LoginFenster(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Zahnarztpraxis Login")
        self.setGeometry(100, 100, 400, 500)
        self.setStyleSheet(STYLE)

        # Setze Hintergrundfarbe
        palette = self.palette()
        palette.setColor(QPalette.Window, QColor("#f5f6fa"))
        self.setPalette(palette)
        self.setAutoFillBackground(True)

        # Container für das gesamte Login-Formular
        main_container = QFrame(self)
        main_container.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 10px;
                padding: 20px;
            }
        """)

        layout = QVBoxLayout(main_container)
        layout.setSpacing(15)

        # Willkommens-Header
        welcome_label = QLabel("Willkommen")
        welcome_label.setStyleSheet("""
            font-size: 28px;
            font-weight: bold;
            color: #2c3e50;
            margin-bottom: 10px;
        """)
        welcome_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(welcome_label)

        # Untertitel
        subtitle_label = QLabel("Bitte melden Sie sich an")
        subtitle_label.setStyleSheet("color: #7f8c8d;")
        subtitle_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(subtitle_label)

        # Eingabefelder
        self.benutzername = QLineEdit()
        self.benutzername.setPlaceholderText("👤 Benutzername")
        layout.addWidget(self.benutzername)

        self.passwort = QLineEdit()
        self.passwort.setPlaceholderText("🔒 Passwort")
        self.passwort.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.passwort)

        # Buttons
        button_layout = QHBoxLayout()
        
        self.login_button = QPushButton("🔑 Anmelden")
        self.login_button.clicked.connect(self.pruefe_login)
        button_layout.addWidget(self.login_button)
        
        self.registrieren_button = QPushButton("✨ Registrieren")
        self.registrieren_button.clicked.connect(self.zeige_registrierung)
        self.registrieren_button.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
        """)
        button_layout.addWidget(self.registrieren_button)
        
        layout.addLayout(button_layout)

        # Container Layout
        container_layout = QVBoxLayout(self)
        container_layout.addWidget(main_container)
        container_layout.setContentsMargins(20, 20, 20, 20)

    def zeige_registrierung(self):
        self.regfenster = RegistrierungsFenster(self)
        self.regfenster.show()

    def pruefe_login(self):
        benutzername = self.benutzername.text().strip()
        passwort = self.passwort.text().strip()

        for p in patienten:
            if p["name"] == benutzername and p["passwort"] == passwort:
                if not p.get("passwort_geaendert", False):
                    QMessageBox.information(self, "Erstlogin", f"Willkommen Patient {benutzername}! Bitte Passwort ändern.")
                    self.passwortfenster = PasswortAendernFenster(p, "Patient", parent=self)
                    self.passwortfenster.show()
                else:
                    self.mainfenster = MainFenster(p["name"], "Patient")
                    self.mainfenster.show()
                    self.close()
                return

        for z in zahnaerzte:
            if z["name"] == benutzername and z["passwort"] == passwort:
                if not z.get("passwort_geaendert", False):
                    QMessageBox.information(self, "Erstlogin", f"Willkommen Zahnarzt {benutzername}! Bitte Passwort ändern.")
                    self.passwortfenster = PasswortAendernFenster(z, "Zahnarzt", parent=self)
                    self.passwortfenster.show()
                else:
                    self.mainfenster = MainFenster(z["name"], "Zahnarzt")
                    self.mainfenster.show()
                    self.close()
                return

        QMessageBox.warning(self, "Fehler", "Benutzername oder Passwort falsch!")

# Start der App
if __name__ == "__main__":
    app = QApplication(sys.argv)
    fenster = LoginFenster()
    fenster.show()
    sys.exit(app.exec_())
