from PyQt5.QtWidgets import QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QMessageBox, QFrame
from PyQt5.QtGui import QColor, QPalette
from PyQt5.QtCore import Qt
from gui.data_manager import speichere_daten, patienten, zahnaerzte, pfad_patienten, pfad_zahnaerzte, STYLE
from components.main_window import MainFenster

class PasswortAendernFenster(QWidget):
    def __init__(self, benutzer, rolle, parent=None):
        super().__init__()
        self.benutzer = benutzer
        self.rolle = rolle
        self.parent_fenster = parent
        self.setWindowTitle("BrightByte | Passwort ändern")
        self.setGeometry(700, 200, 400, 300)
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
