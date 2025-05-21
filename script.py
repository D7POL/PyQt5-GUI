import sys
import pandas as pd
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout,
    QMessageBox, QSpacerItem, QSizePolicy
)
from PyQt5.QtCore import Qt

# Excel-Datei und Daten laden
file_path = "Patienten_Zahnärzte_Kosten.xlsx"
df_patienten = pd.read_excel(file_path, sheet_name="Stamm-Patienten", skiprows=3)
df_zahnaerzte = pd.read_excel(file_path, sheet_name="Zahnärzte", skiprows=2)

class PasswortAendernFenster(QWidget):
    def __init__(self, benutzername, rolle):
        super().__init__()
        self.benutzername = benutzername
        self.rolle = rolle  # 'Patient' oder 'Zahnarzt'
        self.setWindowTitle("Passwort ändern")
        self.setGeometry(150, 150, 400, 300)

        layout = QVBoxLayout()

        self.label_info = QLabel(f"Passwort ändern für {self.benutzername} ({self.rolle})")
        layout.addWidget(self.label_info, alignment=Qt.AlignCenter)

        self.neues_passwort = QLineEdit()
        self.neues_passwort.setEchoMode(QLineEdit.Password)
        self.neues_passwort.setPlaceholderText("Neues Passwort eingeben")
        layout.addWidget(self.neues_passwort, alignment=Qt.AlignCenter)

        self.bestaetigen_passwort = QLineEdit()
        self.bestaetigen_passwort.setEchoMode(QLineEdit.Password)
        self.bestaetigen_passwort.setPlaceholderText("Passwort bestätigen")
        layout.addWidget(self.bestaetigen_passwort, alignment=Qt.AlignCenter)

        self.speichern_button = QPushButton("Passwort ändern")
        self.speichern_button.clicked.connect(self.passwort_aendern)
        layout.addWidget(self.speichern_button, alignment=Qt.AlignCenter)

        self.setLayout(layout)

    def passwort_aendern(self):
        neues = self.neues_passwort.text().strip()
        bestaetigung = self.bestaetigen_passwort.text().strip()

        if neues != bestaetigung:
            QMessageBox.warning(self, "Fehler", "Passwörter stimmen nicht überein.")
            return

        global df_patienten, df_zahnaerzte

        if self.rolle == "Patient":
            df_patienten.loc[df_patienten['Patient'] == self.benutzername, 'initiales Passwort'] = neues
        else:
            df_zahnaerzte.loc[df_zahnaerzte['Zahnarzt'] == self.benutzername, 'ID/Passwort'] = neues

        # Speichern zurück in Excel
        with pd.ExcelWriter(file_path, engine="openpyxl", mode="a", if_sheet_exists="overlay") as writer:
            df_patienten.to_excel(writer, sheet_name="Stamm-Patienten", index=False, startrow=3)
            df_zahnaerzte.to_excel(writer, sheet_name="Zahnärzte", index=False, startrow=2)

        QMessageBox.information(self, "Erfolg", "Passwort erfolgreich geändert.")
        self.close()

class LoginFenster(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Zahnarztpraxis - Login")
        self.setGeometry(100, 100, 800, 600)

        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignCenter)

        self.label_benutzer = QLabel("Benutzername:")
        self.eingabe_benutzer = QLineEdit()
        self.eingabe_benutzer.setFixedWidth(300)

        self.label_passwort = QLabel("Passwort:")
        self.eingabe_passwort = QLineEdit()
        self.eingabe_passwort.setEchoMode(QLineEdit.Password)
        self.eingabe_passwort.setFixedWidth(300)

        self.login_button = QPushButton("Login")
        self.login_button.setFixedWidth(150)
        self.login_button.clicked.connect(self.pruefe_login)

        form_layout = QVBoxLayout()
        form_layout.setSpacing(15)
        form_layout.addWidget(self.label_benutzer, alignment=Qt.AlignCenter)
        form_layout.addWidget(self.eingabe_benutzer, alignment=Qt.AlignCenter)
        form_layout.addWidget(self.label_passwort, alignment=Qt.AlignCenter)
        form_layout.addWidget(self.eingabe_passwort, alignment=Qt.AlignCenter)
        form_layout.addWidget(self.login_button, alignment=Qt.AlignCenter)

        main_layout.addSpacerItem(QSpacerItem(20, 100, QSizePolicy.Minimum, QSizePolicy.Expanding))
        main_layout.addLayout(form_layout)
        main_layout.addSpacerItem(QSpacerItem(20, 100, QSizePolicy.Minimum, QSizePolicy.Expanding))

        self.setLayout(main_layout)

    def pruefe_login(self):
        benutzername = self.eingabe_benutzer.text().strip()
        passwort = self.eingabe_passwort.text().strip()

        patient = df_patienten[
            (df_patienten['Patient'] == benutzername) &
            (df_patienten['initiales Passwort'] == passwort)
        ]

        if not patient.empty:
            QMessageBox.information(self, "Erfolg", f"Willkommen Patient {benutzername}!")
            self.passwortfenster = PasswortAendernFenster(benutzername, "Patient")
            self.passwortfenster.show()
            return

        zahnarzt = df_zahnaerzte[
            (df_zahnaerzte['Zahnarzt'] == benutzername) &
            (df_zahnaerzte['ID/Passwort'] == passwort)
        ]

        if not zahnarzt.empty:
            QMessageBox.information(self, "Erfolg", f"Willkommen Zahnarzt {benutzername}!")
            self.passwortfenster = PasswortAendernFenster(benutzername, "Zahnarzt")
            self.passwortfenster.show()
            return

        QMessageBox.warning(self, "Fehler", "Benutzername oder Passwort falsch!")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    fenster = LoginFenster()
    fenster.show()
    sys.exit(app.exec_())