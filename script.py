import sys
import pandas as pd
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QPushButton,
    QVBoxLayout, QHBoxLayout, QStackedWidget, QFrame
)
from PyQt5.QtCore import Qt

# --- Excel-Daten laden ---
file_path = "Patienten_Zahnärzte_Kosten.xlsx"
df_patienten = pd.read_excel(file_path, sheet_name="Stamm-Patienten", skiprows=3)
df_zahnaerzte = pd.read_excel(file_path, sheet_name="Zahnärzte", skiprows=2)

class HauptDashboard(QMainWindow):
    def __init__(self, benutzername, rolle):
        super().__init__()
        self.benutzername = benutzername
        self.rolle = rolle

        self.setWindowTitle("Zahnarztpraxis")
        self.setGeometry(100, 100, 1200, 700)

        # ----------------- TOP BAR -----------------
        oben_layout = QHBoxLayout()

        # Logo links
        logo = QLabel("🦷 KIEFERORTHOPÄDIE\nDr. Katz & Partner")
        logo.setStyleSheet("font-size: 18px; font-weight: bold;")
        oben_layout.addWidget(logo, alignment=Qt.AlignLeft)

        oben_layout.addStretch()

        # Impressum & Datenschutz rechts
        rechts_label = QLabel("Impressum   Datenschutz")
        rechts_label.setStyleSheet("font-size: 12px;")
        oben_layout.addWidget(rechts_label, alignment=Qt.AlignRight)

        oben_widget = QWidget()
        oben_widget.setLayout(oben_layout)

        # ----------------- NAVIGATION -----------------
        nav_layout = QHBoxLayout()

        self.leistungen_btn = QPushButton("Leistungen")
        self.praxis_btn = QPushButton("Praxis")
        self.ueberuns_btn = QPushButton("Über uns")
        self.kontakt_btn = QPushButton("Kontakt / Anfahrt")

        for btn in [self.leistungen_btn, self.praxis_btn, self.ueberuns_btn, self.kontakt_btn]:
            btn.setFixedHeight(40)
            btn.setStyleSheet("font-size: 14px; padding: 10px;")

        self.leistungen_btn.clicked.connect(self.seite_leistungen)
        self.praxis_btn.clicked.connect(self.seite_praxis)
        self.ueberuns_btn.clicked.connect(self.seite_ueberuns)
        self.kontakt_btn.clicked.connect(self.seite_kontakt)

        nav_layout.addStretch()
        nav_layout.addWidget(self.leistungen_btn)
        nav_layout.addWidget(self.praxis_btn)
        nav_layout.addWidget(self.ueberuns_btn)
        nav_layout.addWidget(self.kontakt_btn)
        nav_layout.addStretch()

        nav_widget = QWidget()
        nav_widget.setLayout(nav_layout)

        # ----------------- INHALT -----------------
        self.seiten = QStackedWidget()

        self.startseite = QLabel(f"Willkommen {self.benutzername} ({self.rolle}) auf der Startseite!")
        self.startseite.setAlignment(Qt.AlignCenter)

        self.leistungen = QLabel("Leistungen: Zahnreinigung, Kariesbehandlung, etc.")
        self.leistungen.setAlignment(Qt.AlignCenter)

        self.praxis = QLabel("Unsere Praxis: Modern ausgestattet, zentral gelegen.")
        self.praxis.setAlignment(Qt.AlignCenter)

        self.ueber_uns = QLabel("Über uns: Unser erfahrenes Team stellt sich vor.")
        self.ueber_uns.setAlignment(Qt.AlignCenter)

        self.kontakt = QLabel("Kontakt / Anfahrt: Hier finden Sie uns.")
        self.kontakt.setAlignment(Qt.AlignCenter)

        # Seiten hinzufügen
        self.seiten.addWidget(self.startseite)  # Index 0
        self.seiten.addWidget(self.leistungen)  # Index 1
        self.seiten.addWidget(self.praxis)      # Index 2
        self.seiten.addWidget(self.ueber_uns)   # Index 3
        self.seiten.addWidget(self.kontakt)     # Index 4

        # ----------------- FOOTER -----------------
        footer = QLabel("© 2025 Zahnarztpraxis. Alle Rechte vorbehalten.")
        footer.setAlignment(Qt.AlignCenter)
        footer.setStyleSheet("font-size: 12px; color: gray;")

        # ----------------- HAUPTLAYOUT -----------------
        haupt_layout = QVBoxLayout()
        haupt_layout.addWidget(oben_widget)
        haupt_layout.addWidget(self.erstelle_trennlinie())
        haupt_layout.addWidget(nav_widget)
        haupt_layout.addWidget(self.erstelle_trennlinie())
        haupt_layout.addWidget(self.seiten)
        haupt_layout.addWidget(self.erstelle_trennlinie())
        haupt_layout.addWidget(footer)

        container = QWidget()
        container.setLayout(haupt_layout)
        self.setCentralWidget(container)

    def erstelle_trennlinie(self):
        linie = QFrame()
        linie.setFrameShape(QFrame.HLine)
        linie.setFrameShadow(QFrame.Sunken)
        return linie

    def seite_leistungen(self):
        self.seiten.setCurrentIndex(1)

    def seite_praxis(self):
        self.seiten.setCurrentIndex(2)

    def seite_ueberuns(self):
        self.seiten.setCurrentIndex(3)

    def seite_kontakt(self):
        self.seiten.setCurrentIndex(4)

### Login-Fenster ###
from PyQt5.QtWidgets import QLineEdit, QMessageBox

class LoginFenster(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Zahnarztpraxis - Login")
        self.setGeometry(100, 100, 800, 600)

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)

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

        patient = df_patienten[
            (df_patienten['Patient'] == benutzername) &
            (df_patienten['initiales Passwort'] == passwort)
        ]

        if not patient.empty:
            self.dashboard = HauptDashboard(benutzername, "Patient")
            self.dashboard.show()
            self.close()
            return

        zahnarzt = df_zahnaerzte[
            (df_zahnaerzte['Zahnarzt'] == benutzername) &
            (df_zahnaerzte['ID/Passwort'] == passwort)
        ]

        if not zahnarzt.empty:
            self.dashboard = HauptDashboard(benutzername, "Zahnarzt")
            self.dashboard.show()
            self.close()
            return

        QMessageBox.warning(self, "Fehler", "Benutzername oder Passwort falsch!")

### App starten ###
if __name__ == "__main__":
    app = QApplication(sys.argv)
    fenster = LoginFenster()
    fenster.show()
    sys.exit(app.exec_())
