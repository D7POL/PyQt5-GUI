import sys
import json
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QMessageBox
)
from PyQt5.QtCore import Qt

# Hilfsfunktionen für JSON-Zugriff
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

# Daten laden
pfad_patienten = "data/patienten.json"
pfad_zahnaerzte = "data/zahnaerzte.json"
patienten = lade_daten(pfad_patienten)
zahnaerzte = lade_daten(pfad_zahnaerzte)

class PasswortAendernFenster(QWidget):
    def __init__(self, benutzer, rolle):
        super().__init__()
        self.benutzer = benutzer
        self.rolle = rolle
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
        self.close()


class LoginFenster(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Login Zahnarztpraxis")
        self.setGeometry(100, 100, 400, 250)

        layout = QVBoxLayout()

        self.label_benutzer = QLabel("Benutzername:")
        self.eingabe_benutzer = QLineEdit()

        self.label_passwort = QLabel("Passwort:")
        self.eingabe_passwort = QLineEdit()
        self.eingabe_passwort.setEchoMode(QLineEdit.Password)

        self.login_button = QPushButton("Login")
        self.login_button.clicked.connect(self.pruefe_login)

        layout.addWidget(self.label_benutzer)
        layout.addWidget(self.eingabe_benutzer)
        layout.addWidget(self.label_passwort)
        layout.addWidget(self.eingabe_passwort)
        layout.addWidget(self.login_button)

        self.setLayout(layout)

    def pruefe_login(self):
        benutzername = self.eingabe_benutzer.text().strip()
        passwort = self.eingabe_passwort.text().strip()

        # Patienten prüfen
        for p in patienten:
            if p["name"] == benutzername and p["passwort"] == passwort:
                if not p.get("passwort_geaendert", False):
                    QMessageBox.information(self, "Erstlogin", f"Willkommen Patient {benutzername}! Bitte Passwort ändern.")
                    self.passwortfenster = PasswortAendernFenster(p, "Patient")
                    self.passwortfenster.show()
                else:
                    QMessageBox.information(self, "Login", f"Willkommen zurück, Patient {benutzername}!")
                return

        # Zahnärzte prüfen
        for z in zahnaerzte:
            if z["name"] == benutzername and z["passwort"] == passwort:
                if not z.get("passwort_geaendert", False):
                    QMessageBox.information(self, "Erstlogin", f"Willkommen Zahnarzt {benutzername}! Bitte Passwort ändern.")
                    self.passwortfenster = PasswortAendernFenster(z, "Zahnarzt")
                    self.passwortfenster.show()
                else:
                    QMessageBox.information(self, "Login", f"Willkommen zurück, Zahnarzt {benutzername}!")
                return

        QMessageBox.warning(self, "Fehler", "Benutzername oder Passwort falsch!")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    fenster = LoginFenster()
    fenster.show()
    sys.exit(app.exec_())
