import sys
import json
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton,
    QVBoxLayout, QMessageBox
)
from PyQt5.QtCore import Qt

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

# Hauptfenster
class MainFenster(QWidget):
    def __init__(self, benutzername, rolle):
        super().__init__()
        self.setWindowTitle(f"Hauptseite - {rolle} {benutzername}")
        self.setGeometry(200, 200, 600, 400)
        self.setStyleSheet("background-color: white;")

# Passwort ändern Fenster
class PasswortAendernFenster(QWidget):
    def __init__(self, benutzer, rolle, parent=None):
        super().__init__()
        self.benutzer = benutzer
        self.rolle = rolle
        self.parent_fenster = parent
        self.setWindowTitle("Passwort ändern")
        self.setGeometry(150, 150, 400, 250)

        layout = QVBoxLayout()
        self.label_info = QLabel(f"Passwort ändern für {self.benutzer['name']} ({rolle})")
        layout.addWidget(self.label_info, alignment=Qt.AlignCenter)

        self.neues_passwort = QLineEdit()
        self.neues_passwort.setEchoMode(QLineEdit.Password)
        self.neues_passwort.setPlaceholderText("Neues Passwort eingeben")
        layout.addWidget(self.neues_passwort)

        self.bestaetigen_passwort = QLineEdit()
        self.bestaetigen_passwort.setEchoMode(QLineEdit.Password)
        self.bestaetigen_passwort.setPlaceholderText("Passwort bestätigen")
        layout.addWidget(self.bestaetigen_passwort)

        self.speichern_button = QPushButton("Passwort ändern")
        self.speichern_button.clicked.connect(self.passwort_aendern)
        layout.addWidget(self.speichern_button)

        self.setLayout(layout)

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
from PyQt5.QtWidgets import QComboBox
class RegistrierungsFenster(QWidget):
    def __init__(self, parent=None):
        super().__init__()
        self.setWindowTitle("Registrierung")
        self.setGeometry(150, 150, 400, 350)

        layout = QVBoxLayout()

        self.eingabe_name = QLineEdit()
        self.eingabe_name.setPlaceholderText("Vollständiger Name")
        layout.addWidget(self.eingabe_name)

        self.eingabe_passwort = QLineEdit()
        self.eingabe_passwort.setPlaceholderText("Passwort")
        self.eingabe_passwort.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.eingabe_passwort)

        # Drop-down für Versicherung
        self.versicherung_box = QComboBox()
        self.versicherung_box.addItems(["gesetzlich", "privat", "freiwillig gesetzlich"])
        layout.addWidget(QLabel("Versicherung:"))
        layout.addWidget(self.versicherung_box)

        # Drop-down für Beschwerden
        self.probleme_box = QComboBox()
        self.probleme_box.addItems([
            "Karies klein", "Karies Groß", "Teilkrone", "Krone", "Wurzelbehandlung"
        ])
        layout.addWidget(QLabel("Beschwerde:"))
        layout.addWidget(self.probleme_box)

        self.eingabe_anzahl = QLineEdit()
        self.eingabe_anzahl.setPlaceholderText("Anzahl (optional, Standard = 1)")
        layout.addWidget(self.eingabe_anzahl)

        self.registrieren_button = QPushButton("Registrieren")
        self.registrieren_button.clicked.connect(self.registriere)
        layout.addWidget(self.registrieren_button)

        self.setLayout(layout)

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
        self.setWindowTitle("Login Zahnarztpraxis")
        self.setGeometry(100, 100, 400, 300)

        layout = QVBoxLayout()

        self.label_benutzer = QLabel("Benutzername:")
        self.eingabe_benutzer = QLineEdit()

        self.label_passwort = QLabel("Passwort:")
        self.eingabe_passwort = QLineEdit()
        self.eingabe_passwort.setEchoMode(QLineEdit.Password)

        self.login_button = QPushButton("Login")
        self.login_button.clicked.connect(self.pruefe_login)

        self.registrieren_button = QPushButton("Registrieren")
        self.registrieren_button.clicked.connect(self.zeige_registrierung)

        layout.addWidget(self.label_benutzer)
        layout.addWidget(self.eingabe_benutzer)
        layout.addWidget(self.label_passwort)
        layout.addWidget(self.eingabe_passwort)
        layout.addWidget(self.login_button)
        layout.addWidget(self.registrieren_button)

        self.setLayout(layout)

    def zeige_registrierung(self):
        self.regfenster = RegistrierungsFenster(self)
        self.regfenster.show()

    def pruefe_login(self):
        benutzername = self.eingabe_benutzer.text().strip()
        passwort = self.eingabe_passwort.text().strip()

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
