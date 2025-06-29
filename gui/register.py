from PyQt5.QtWidgets import QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QMessageBox, QFrame, QComboBox, QCheckBox
from PyQt5.QtGui import QColor, QPalette
from PyQt5.QtCore import Qt
import os
import json

from gui.data_manager import patienten, zahnaerzte, speichere_daten, pfad_patienten, pfad_zahnaerzte, STYLE

# Registrierungsfenster neue Patienten
class RegistrierungsFenster(QWidget):
    def __init__(self, parent=None):
        super().__init__()
        self.setWindowTitle("BrightByte | Registrierung")
        self.setGeometry(700, 200, 400, 500)
        self.setStyleSheet(STYLE)

        # Hintergrundfarbe
        palette = self.palette()
        palette.setColor(QPalette.Window, QColor("#f5f6fa"))
        self.setPalette(palette)
        self.setAutoFillBackground(True)

        # Container Formular
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
            "Karies klein", "Karies groß", "Teilkrone", "Krone", "Wurzelbehandlung"
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

        # Prüft ob Name bereits existiert
        existierender_patient = None
        basis_name = name
        nummer = 1
        
        # Finde die höchste existierende Nummer
        for patient in patienten:
            if patient["name"] == name:
                existierender_patient = patient
                break
            elif patient["name"].startswith(name + "_"):
                try:
                    nr = int(patient["name"].split("_")[-1])
                    nummer = max(nummer, nr + 1)
                except ValueError:
                    continue

        if existierender_patient:
            msgbox = QMessageBox(self)
            msgbox.setWindowTitle("Patient existiert bereits")
            msgbox.setText(f"Ein Patient mit dem Namen '{name}' existiert bereits.\n\nSind Sie dieser Patient?")
            ja_btn = msgbox.addButton("Ja", QMessageBox.YesRole)
            nein_btn = msgbox.addButton("Nein", QMessageBox.NoRole)
            msgbox.setDefaultButton(ja_btn)
            msgbox.exec_()

            if msgbox.clickedButton() == ja_btn:
                # Aktualisiere existierenden Patienten
                existierender_patient["passwort"] = pw
                # Füge neue Beschwerden hinzu
                neues_problem = {
                    "art": beschwerde,
                    "anzahl": anzahl,
                    "material": "normal"
                }
                # Prüfe ob Problem bereits existiert
                problem_existiert = False
                for problem in existierender_patient["probleme"]:
                    if problem["art"] == beschwerde:
                        problem["anzahl"] += anzahl
                        problem_existiert = True
                        break
                if not problem_existiert:
                    existierender_patient["probleme"].append(neues_problem)
                speichere_daten(pfad_patienten, patienten)
                QMessageBox.information(
                    self,
                    "Erfolg",
                    "Patientendaten wurden aktualisiert!\n\nSie können sich jetzt mit Ihren Zugangsdaten anmelden."
                )
                self.close()
                return
            else:
                # Generiere neuen Namen mit Nummerierung
                while True:
                    name = f"{basis_name}_{nummer}"
                    # Prüfe ob dieser Name bereits existiert
                    name_existiert = False
                    for patient in patienten:
                        if patient["name"] == name:
                            name_existiert = True
                            nummer += 1
                            break
                    if not name_existiert:
                        break
                # Informiere Benutzer über den neuen Namen
                QMessageBox.information(
                    self,
                    "Neuer Benutzername",
                    f"Um Verwechslungen zu vermeiden, wurde Ihr Benutzername zu '{name}' geändert."
                )

        # Erstelle neuen Patienten
        neuer_patient = {
            "name": name,
            "passwort": pw,
            "krankenkasse": versicherung,
            "probleme": [
                {
                    "art": beschwerde,
                    "anzahl": anzahl,
                    "material": "normal"
                }
            ],
            "passwort_geaendert": True
        }

        patienten.append(neuer_patient)
        speichere_daten(pfad_patienten, patienten)

        QMessageBox.information(
            self,
            "Erfolg",
            f"Registrierung erfolgreich!\n\n"
            f"Ihr Benutzername: {name}\n"
            "Sie können sich jetzt mit Ihren Zugangsdaten anmelden."
        )
        self.close()

# Registrierungsfenster für neue Zahnärzte
class ZahnarztRegistrierungsFenster(QWidget):
    def __init__(self, parent=None):
        super().__init__()
        self.setWindowTitle("BrightByte | Registrierung")
        self.setGeometry(700, 200, 400, 400)
        self.setStyleSheet(STYLE)

        # Hintergrundfarbe
        palette = self.palette()
        palette.setColor(QPalette.Window, QColor("#f5f6fa"))
        self.setPalette(palette)
        self.setAutoFillBackground(True)

        # Container Formular
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
        titel = QLabel("Zahnarzt Registrierung")
        titel.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            color: #2c3e50;
            margin-bottom: 10px;
        """)
        layout.addWidget(titel, alignment=Qt.AlignCenter)

        # Formularfelder
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("👤 Vollständiger Name")
        layout.addWidget(self.name_input)

        self.passwort_input = QLineEdit()
        self.passwort_input.setPlaceholderText("🔒 Passwort")
        self.passwort_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.passwort_input)

        # Behandelte Versicherungen
        kassen_label = QLabel("Behandelte Versicherungen:")
        kassen_label.setStyleSheet("color: #2c3e50; font-weight: bold;")
        layout.addWidget(kassen_label)
        
        self.kassen_checkboxes = {}
        for kasse in ["gesetzlich", "privat", "freiwillig gesetzlich"]:
            cb = QCheckBox(kasse)
            cb.setStyleSheet("color: #2c3e50; margin-left: 10px;")
            self.kassen_checkboxes[kasse] = cb
            layout.addWidget(cb)

        # Registrieren Button
        self.registrieren_button = QPushButton("✅ Registrierung abschließen")
        self.registrieren_button.clicked.connect(self.registriere_zahnarzt)
        layout.addWidget(self.registrieren_button)

        # Container Layout
        container_layout = QVBoxLayout(self)
        container_layout.addWidget(main_container)
        container_layout.setContentsMargins(20, 20, 20, 20)

    def registriere_zahnarzt(self):
        name = self.name_input.text().strip()
        passwort = self.passwort_input.text().strip()
        behandelt = [kasse for kasse, cb in self.kassen_checkboxes.items() if cb.isChecked()]

        if not name or not passwort:
            QMessageBox.warning(self, "Fehler", "Bitte Name und Passwort eingeben.")
            return
        if not behandelt:
            QMessageBox.warning(self, "Fehler", "Bitte mindestens eine Kasse auswählen.")
            return
        for zahnarzt in zahnaerzte:
            if zahnarzt["name"] == name:
                QMessageBox.warning(self, "Fehler", "Ein Zahnarzt mit diesem Namen existiert bereits.")
                return

        neuer_zahnarzt = {
            "name": name,
            "passwort": passwort,
            "behandelt": behandelt,
            "zeiten": {},  # Standard: keine Zeiten
            "passwort_geaendert": True
        }
        zahnaerzte.append(neuer_zahnarzt)
        speichere_daten(pfad_zahnaerzte, zahnaerzte)

        # Automatische Bildzuweisung
        bilder_dir = os.path.join(os.path.dirname(__file__), "..", "arzt_bilder")
        bilder_dir = os.path.abspath(bilder_dir)
        alle_bilder = [f"arzt_bilder/doc{i}.jpg" for i in range(1, 13)]
        bilder_json_path = os.path.join(os.path.dirname(__file__), "..", "data", "zahnaerzte_bilder.json")
        bilder_json_path = os.path.abspath(bilder_json_path)
        try:
            with open(bilder_json_path, "r", encoding="utf-8") as f:
                bilder_mapping = json.load(f)
        except Exception:
            bilder_mapping = {}
        vergebene_bilder = set(bilder_mapping.values())
        freies_bild = None
        for bild in alle_bilder:
            if bild not in vergebene_bilder:
                freies_bild = bild
                break
        if not freies_bild:
            # Falls alle vergeben, nimmt das erste Bild
            freies_bild = alle_bilder[0]
        bilder_mapping[name] = freies_bild
        with open(bilder_json_path, "w", encoding="utf-8") as f:
            json.dump(bilder_mapping, f, indent=2, ensure_ascii=False)

        QMessageBox.information(
            self,
            "Erfolg",
            f"Zahnarzt {name} wurde erfolgreich registriert."
        )
        self.close()
