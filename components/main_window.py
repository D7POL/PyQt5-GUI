from PyQt5.QtWidgets import (
    QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QMessageBox,
    QHBoxLayout, QFrame, QSizePolicy, QComboBox, QCalendarWidget,
    QScrollArea, QCheckBox
)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QColor, QPalette
from datetime import datetime, timedelta
import json

from Login.data_manager import (
    patienten, zahnaerzte, BEHANDLUNGEN, speichere_daten,
    pfad_patienten, pfad_zahnaerzte, STYLE
)
from components.helper import get_weekday, CALENDAR_TODAY_OVERRIDE
from components.calculator import berechne_kosten_und_zeit
from components.settings_manager import SettingsManager
from components.booking_manager import BookingManager
from components.view_manager import ViewManager

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

        self.setWindowTitle("BrightByte")
        self.setGeometry(300, 50, 1200, 600)
        self.setStyleSheet(STYLE)
        
        # Setze Hintergrundfarbe
        palette = self.palette()
        palette.setColor(QPalette.Window, QColor("#f5f6fa"))
        self.setPalette(palette)
        self.setAutoFillBackground(True)

        # Initialisiere Behandlungsvariablen
        self.selected_problem = None
        self.selected_anzahl = None
        self.selected_material = None
        self.selected_zahnarzt = None
        self.selected_date = None
        self.selected_time = None

        self.settings_manager = SettingsManager(self)
        self.booking_manager = BookingManager(self)
        self.view_manager = ViewManager(self)
        self.init_ui()

    def logout(self):
        # Öffne das Login-Fenster
        from Login.Login import LoginFenster
        self.login_fenster = LoginFenster()
        self.login_fenster.show()
        # Schließe das aktuelle Fenster
        self.close()

    def show_meine_daten(self):
        self.view_manager.show_meine_daten()

    def show_einstellungen(self):
        self.settings_manager.show_einstellungen()

    def update_passwort(self):
        self.settings_manager.update_passwort()

    def update_krankenkasse(self):
        self.settings_manager.update_krankenkasse()

    def add_problem(self):
        self.settings_manager.add_problem()

    def show_meine_termine(self):
        self.view_manager.show_meine_termine()

    def cancel_termin(self, arzt, datum, zeit):
        self.booking_manager.cancel_termin(arzt, datum, zeit)

    def show_termin_buchen(self):
        self.booking_manager.show_termin_buchen()

    def update_anzahl_box(self):
        self.booking_manager.update_anzahl_box()
            
    def update_kosten(self):
        self.booking_manager.update_kosten()

    def show_arzt_selection(self):
        self.booking_manager.show_arzt_selection()

    def show_kalender(self):
        self.booking_manager.show_kalender()
        
    def update_calendar(self):
        self.booking_manager.update_calendar()
        
    def show_time_slots(self, date):
        self.booking_manager.show_time_slots(date)
            
    def select_time(self, time):
        self.booking_manager.select_time(time)
        
    def show_zahnarzt_dashboard(self):
        self.view_manager.show_zahnarzt_dashboard()

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
                padding: 12px;
            }
        """)
        begruessung_layout = QVBoxLayout(begruessung_container)
        begruessung_layout.setAlignment(Qt.AlignCenter)
        
        begruessung = QLabel(f"Willkommen {self.benutzername}")
        begruessung.setStyleSheet("""
            font-size: 26px;
            font-weight: bold;
            color: #2c3e50;
            margin: 0px;
        """)
        begruessung.setAlignment(Qt.AlignCenter)
        begruessung_layout.addWidget(begruessung)
        
        rolle_label = QLabel(f"Angemeldet als {self.rolle}")
        rolle_label.setStyleSheet("color: #7f8c8d; margin: 0px;")
        rolle_label.setAlignment(Qt.AlignCenter)
        begruessung_layout.addWidget(rolle_label)
        
        begruessung_layout.addStretch(1)

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

        # Unterschiedliche Menü-Buttons je nach Rolle
        if self.rolle == "Patient":
            menu_buttons = [
                ("Meine Daten", "📋", self.show_meine_daten),
                ("Termin buchen", "📅", self.show_termin_buchen),
                ("Meine Termine", "📆", self.show_meine_termine),
                ("Einstellungen", "⚙️", self.show_einstellungen)
            ]
        else:  # Zahnarzt
            menu_buttons = [
                ("Dashboard", "📊", self.show_zahnarzt_dashboard),
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
        
        # Zeige initial die passende Seite
        if self.rolle == "Patient":
            self.show_meine_daten()
        else:
            self.show_zahnarzt_dashboard()