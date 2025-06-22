import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit, QPushButton,
    QVBoxLayout, QMessageBox, QHBoxLayout, QFrame, QCheckBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QPalette

from Login.passwort import PasswortAendernFenster
from components.main_window import MainFenster
from Login.Register import RegistrierungsFenster, ZahnarztRegistrierungsFenster
from Login.data_manager import patienten, zahnaerzte, STYLE

class LoginFenster(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("BrightByte")
        self.setGeometry(700, 200, 400, 500)
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

        # Buttons Container
        button_container = QFrame()
        button_container.setStyleSheet("""
            QFrame {
                background-color: transparent;
                border: none;
            }
        """)
        button_layout = QVBoxLayout(button_container)
        button_layout.setSpacing(10)
        
        # Login Button
        self.login_button = QPushButton("🔑 Anmelden")
        self.login_button.clicked.connect(self.pruefe_login)
        button_layout.addWidget(self.login_button)
        
        # Registrierungs-Buttons
        reg_label = QLabel("Neu hier? Registrieren Sie sich als:")
        reg_label.setStyleSheet("color: #7f8c8d; margin-top: 10px;")
        reg_label.setAlignment(Qt.AlignCenter)
        button_layout.addWidget(reg_label)
        
        reg_buttons_layout = QHBoxLayout()
        
        self.patient_reg_button = QPushButton("🏥 Patient")
        self.patient_reg_button.clicked.connect(self.zeige_patienten_registrierung)
        self.patient_reg_button.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
        """)
        reg_buttons_layout.addWidget(self.patient_reg_button)
        
        self.arzt_reg_button = QPushButton("👨‍⚕️ Zahnarzt")
        self.arzt_reg_button.clicked.connect(self.zeige_zahnarzt_registrierung)
        self.arzt_reg_button.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        reg_buttons_layout.addWidget(self.arzt_reg_button)
        
        button_layout.addLayout(reg_buttons_layout)
        layout.addWidget(button_container)

        # Container Layout
        container_layout = QVBoxLayout(self)
        container_layout.addWidget(main_container)
        container_layout.setContentsMargins(20, 20, 20, 20)

    def zeige_patienten_registrierung(self):
        self.regfenster = RegistrierungsFenster(self)
        self.regfenster.show()

    def zeige_zahnarzt_registrierung(self):
        self.zahnarzt_regfenster = ZahnarztRegistrierungsFenster(self)
        self.zahnarzt_regfenster.show()

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
