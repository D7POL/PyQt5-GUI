from PyQt5.QtWidgets import (
    QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QMessageBox,
    QHBoxLayout, QFrame, QSizePolicy, QComboBox, QCalendarWidget,
    QScrollArea, QCheckBox
)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QColor, QPalette
from gui.data_manager import speichere_daten, patienten, zahnaerzte, pfad_patienten, pfad_zahnaerzte

class SettingsManager:
    def __init__(self, main_window):
        self.main_window = main_window

    def show_einstellungen(self):
        if self.main_window.current_page:
            self.main_window.current_page.hide()
            self.main_window.current_page.deleteLater()

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

        # Scroll-Bereich für die Einstellungen
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: 5px solid #E8F4F8; }")
        
        scroll_content = QWidget()
        scroll_layout = QVBoxLayout(scroll_content)
        scroll_layout.setSpacing(15)

        if self.main_window.rolle == "Patient":
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
            
            self.main_window.neues_passwort = QLineEdit()
            self.main_window.neues_passwort.setPlaceholderText("Neues Passwort")
            self.main_window.neues_passwort.setEchoMode(QLineEdit.Password)
            passwort_layout.addWidget(self.main_window.neues_passwort)
            
            passwort_btn = QPushButton("🔒 Passwort aktualisieren")
            passwort_btn.clicked.connect(self.update_passwort)
            passwort_layout.addWidget(passwort_btn)
            
            scroll_layout.addWidget(passwort_group)

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
            
            self.main_window.kasse_box = QComboBox()
            self.main_window.kasse_box.addItems(["gesetzlich", "privat", "freiwillig gesetzlich"])
            self.main_window.kasse_box.setCurrentText(self.main_window.patient_data["krankenkasse"])
            kasse_layout.addWidget(self.main_window.kasse_box)
            
            kasse_btn = QPushButton("💉 Krankenkasse aktualisieren")
            kasse_btn.clicked.connect(self.update_krankenkasse)
            kasse_layout.addWidget(kasse_btn)
            
            scroll_layout.addWidget(kasse_group)

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
            
            self.main_window.problem_box = QComboBox()
            self.main_window.problem_box.addItems([
                "Karies klein", "Karies groß", "Teilkrone", "Krone", "Wurzelbehandlung"
            ])
            probleme_layout.addWidget(self.main_window.problem_box)
            
            self.main_window.problem_anzahl = QLineEdit()
            self.main_window.problem_anzahl.setPlaceholderText("Anzahl")
            probleme_layout.addWidget(self.main_window.problem_anzahl)
            
            problem_btn = QPushButton("➕ Behandlung hinzufügen")
            problem_btn.clicked.connect(self.add_problem)
            probleme_layout.addWidget(problem_btn)
            
            scroll_layout.addWidget(probleme_group)

        else:  # Zahnarzt Einstellungen
            # Finde den aktuellen Zahnarzt
            self.main_window.zahnarzt_data = None
            for z in zahnaerzte:
                if z["name"] == self.main_window.benutzername:
                    self.main_window.zahnarzt_data = z
                    break

            if self.main_window.zahnarzt_data:
                # Name ändern
                name_group = QFrame()
                name_group.setStyleSheet("""
                    QFrame {
                        background-color: #f8f9fa;
                        border-radius: 8px;
                        padding: 15px;
                        margin-bottom: 15px;
                    }
                """)
                name_layout = QVBoxLayout(name_group)
                
                name_label = QLabel("Name ändern")
                name_label.setStyleSheet("font-weight: bold; font-size: 16px; color: #2c3e50;")
                name_layout.addWidget(name_label)
                
                self.main_window.neuer_name = QLineEdit()
                self.main_window.neuer_name.setPlaceholderText("Neuer Name")
                self.main_window.neuer_name.setText(self.main_window.zahnarzt_data["name"])
                name_layout.addWidget(self.main_window.neuer_name)
                
                name_btn = QPushButton("👤 Name aktualisieren")
                name_btn.clicked.connect(self.update_zahnarzt_name)
                name_layout.addWidget(name_btn)
                
                scroll_layout.addWidget(name_group)

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
                
                self.main_window.neues_passwort = QLineEdit()
                self.main_window.neues_passwort.setPlaceholderText("Neues Passwort")
                self.main_window.neues_passwort.setEchoMode(QLineEdit.Password)
                passwort_layout.addWidget(self.main_window.neues_passwort)
                
                passwort_btn = QPushButton("🔒 Passwort aktualisieren")
                passwort_btn.clicked.connect(self.update_passwort)
                passwort_layout.addWidget(passwort_btn)
                
                scroll_layout.addWidget(passwort_group)

                # Krankenkassen
                kassen_group = QFrame()
                kassen_group.setStyleSheet("""
                    QFrame {
                        background-color: #f8f9fa;
                        border-radius: 8px;
                        padding: 15px;
                        margin-bottom: 15px;
                    }
                """)
                kassen_layout = QVBoxLayout(kassen_group)
                
                kassen_label = QLabel("Behandelt folgende Versicherungen:")
                kassen_label.setStyleSheet("font-weight: bold; font-size: 16px; color: #2c3e50;")
                kassen_layout.addWidget(kassen_label)
                
                self.main_window.kassen_checkboxes = {}
                for kasse in ["gesetzlich", "privat", "freiwillig gesetzlich"]:
                    cb = QCheckBox(kasse)
                    cb.setStyleSheet("color: #2c3e50; margin-left: 10px;")
                    cb.setChecked(kasse in self.main_window.zahnarzt_data["behandelt"])
                    self.main_window.kassen_checkboxes[kasse] = cb
                    kassen_layout.addWidget(cb)
                
                kassen_btn = QPushButton("💊 Krankenkassen aktualisieren")
                kassen_btn.clicked.connect(self.update_zahnarzt_kassen)
                kassen_layout.addWidget(kassen_btn)
                
                scroll_layout.addWidget(kassen_group)

                # Behandlungszeiten
                zeiten_group = QFrame()
                zeiten_group.setStyleSheet("""
                    QFrame {
                        background-color: #f8f9fa;
                        border-radius: 8px;
                        padding: 15px;
                    }
                """)
                zeiten_layout = QVBoxLayout(zeiten_group)
                
                zeiten_label = QLabel("Wöchentliche Behandlungszeiten:")
                zeiten_label.setStyleSheet("font-weight: bold; font-size: 16px; color: #2c3e50;")
                zeiten_layout.addWidget(zeiten_label)
                
                self.main_window.wochentage = {
                    "Mo": "Montag",
                    "Di": "Dienstag",
                    "Mi": "Mittwoch",
                    "Do": "Donnerstag",
                    "Fr": "Freitag"
                }
                
                self.main_window.zeiten_widgets = {}
                for tag_kurz, tag_lang in self.main_window.wochentage.items():
                    tag_frame = QFrame()
                    tag_layout = QVBoxLayout(tag_frame)
                    
                    # Checkbox für den Tag
                    tag_cb = QCheckBox(tag_lang)
                    tag_cb.setStyleSheet("color: #2c3e50; font-weight: bold;")
                    tag_cb.setChecked(tag_kurz in self.main_window.zahnarzt_data["zeiten"])
                    tag_layout.addWidget(tag_cb)
                    
                    # Container für Zeitslots
                    slots_frame = QFrame()
                    slots_layout = QVBoxLayout(slots_frame)
                    slots_frame.setVisible(tag_kurz in self.main_window.zahnarzt_data["zeiten"])
                    tag_cb.toggled.connect(slots_frame.setVisible)
                    
                    # Bestehende Zeitslots laden
                    self.main_window.zeiten_widgets[tag_kurz] = {
                        "checkbox": tag_cb,
                        "slots_frame": slots_frame,
                        "slots_layout": slots_layout,
                        "zeitslots": []
                    }
                    
                    if tag_kurz in self.main_window.zahnarzt_data["zeiten"]:
                        for zeitslot in self.main_window.zahnarzt_data["zeiten"][tag_kurz]:
                            von, bis = zeitslot.split("-")
                            
                            zeit_container = QFrame()
                            zeit_layout = QHBoxLayout(zeit_container)
                            
                            von_label = QLabel("Von:")
                            von_label.setStyleSheet("color: #2c3e50;")
                            zeit_layout.addWidget(von_label)
                            
                            von_zeit = QComboBox()
                            von_zeit.addItems([f"{h:02d}:00" for h in range(8, 19)])
                            von_zeit.setCurrentText(von)
                            zeit_layout.addWidget(von_zeit)
                            
                            bis_label = QLabel("Bis:")
                            bis_label.setStyleSheet("color: #2c3e50;")
                            zeit_layout.addWidget(bis_label)
                            
                            bis_zeit = QComboBox()
                            bis_zeit.addItems([f"{h:02d}:00" for h in range(8, 19)])
                            bis_zeit.setCurrentText(bis)
                            zeit_layout.addWidget(bis_zeit)
                            
                            # Entfernen-Button
                            remove_btn = QPushButton("×")
                            remove_btn.setStyleSheet("""
                                QPushButton {
                                    background-color: #e74c3c;
                                    color: white;
                                    border-radius: 10px;
                                    padding: 2px 6px;
                                    font-weight: bold;
                                }
                                QPushButton:hover {
                                    background-color: #c0392b;
                                }
                            """)
                            remove_btn.clicked.connect(lambda checked, c=zeit_container, t=tag_kurz: self.remove_zeitslot(t, c))
                            zeit_layout.addWidget(remove_btn)
                            
                            slots_layout.addWidget(zeit_container)
                            self.main_window.zeiten_widgets[tag_kurz]["zeitslots"].append({
                                "von": von_zeit,
                                "bis": bis_zeit
                            })
                    
                    # Button für zusätzliche Zeitslots
                    add_slot_btn = QPushButton("+ Zeitslot hinzufügen")
                    add_slot_btn.setStyleSheet("""
                        QPushButton {
                            background-color: transparent;
                            color: #3498db;
                            border: 1px solid #3498db;
                            padding: 5px;
                        }
                        QPushButton:hover {
                            background-color: #f0f9ff;
                        }
                    """)
                    add_slot_btn.clicked.connect(lambda checked, tag=tag_kurz: self.add_zeitslot(tag))
                    
                    self.main_window.zeiten_widgets[tag_kurz]["add_button"] = add_slot_btn
                    slots_layout.addWidget(add_slot_btn)
                    
                    tag_layout.addWidget(slots_frame)
                    zeiten_layout.addWidget(tag_frame)
                
                zeiten_btn = QPushButton("🕒 Behandlungszeiten aktualisieren")
                zeiten_btn.clicked.connect(self.update_zahnarzt_zeiten)
                zeiten_layout.addWidget(zeiten_btn)
                
                scroll_layout.addWidget(zeiten_group)

        scroll.setWidget(scroll_content)
        settings_layout.addWidget(scroll)
        self.main_window.inhalt_layout_inner.addWidget(settings_container)
        self.main_window.current_page = settings_container

    def update_zahnarzt_name(self):
        if not self.main_window.zahnarzt_data:
            return
            
        neuer_name = self.main_window.neuer_name.text().strip()
        if not neuer_name:
            QMessageBox.warning(self.main_window, "Fehler", "Bitte geben Sie einen Namen ein.")
            return
            
        # Prüfe ob der Name bereits existiert
        for arzt in zahnaerzte:
            if arzt["name"] == neuer_name and arzt != self.main_window.zahnarzt_data:
                QMessageBox.warning(
                    self.main_window,
                    "Fehler",
                    f"Ein Zahnarzt mit dem Namen '{neuer_name}' existiert bereits."
                )
                return
                
        self.main_window.zahnarzt_data["name"] = neuer_name
        speichere_daten(pfad_zahnaerzte, zahnaerzte)
        QMessageBox.information(self.main_window, "Erfolg", "Name wurde aktualisiert!")

    def update_zahnarzt_kassen(self):
        if not self.main_window.zahnarzt_data:
            return
            
        behandelt = [k for k, cb in self.main_window.kassen_checkboxes.items() if cb.isChecked()]
        if not behandelt:
            QMessageBox.warning(self.main_window, "Fehler", "Bitte mindestens eine Krankenkasse auswählen.")
            return
            
        self.main_window.zahnarzt_data["behandelt"] = behandelt
        speichere_daten(pfad_zahnaerzte, zahnaerzte)
        QMessageBox.information(self.main_window, "Erfolg", "Krankenkassen wurden aktualisiert!")

    def update_zahnarzt_zeiten(self):
        if not self.main_window.zahnarzt_data:
            return
            
        zeiten = {}
        hat_zeiten = False
        
        for tag_kurz, widgets in self.main_window.zeiten_widgets.items():
            if widgets["checkbox"].isChecked():
                zeiten[tag_kurz] = []
                for slot in widgets["zeitslots"]:
                    von = slot["von"].currentText()
                    bis = slot["bis"].currentText()
                    if von >= bis:
                        QMessageBox.warning(
                            self.main_window,
                            "Fehler",
                            f"Ungültige Zeitspanne am {self.main_window.wochentage[tag_kurz]}:\n"
                            f"'{von} - {bis}'"
                        )
                        return
                    zeiten[tag_kurz].append(f"{von}-{bis}")
                hat_zeiten = True
                
        if not hat_zeiten:
            QMessageBox.warning(self.main_window, "Fehler", "Bitte mindestens einen Tag mit Behandlungszeiten auswählen.")
            return
            
        self.main_window.zahnarzt_data["zeiten"] = zeiten
        speichere_daten(pfad_zahnaerzte, zahnaerzte)
        QMessageBox.information(self.main_window, "Erfolg", "Behandlungszeiten wurden aktualisiert!")

    def add_zeitslot(self, tag):
        widgets = self.main_window.zeiten_widgets[tag]
        slots_layout = widgets["slots_layout"]
        add_button = widgets["add_button"]
        
        # Entferne den Add-Button temporär
        slots_layout.removeWidget(add_button)
        
        # Erstelle neuen Zeitslot
        zeit_container = QFrame()
        zeit_layout = QHBoxLayout(zeit_container)
        
        von_label = QLabel("Von:")
        von_label.setStyleSheet("color: #2c3e50;")
        zeit_layout.addWidget(von_label)
        
        von_zeit = QComboBox()
        von_zeit.addItems([f"{h:02d}:00" for h in range(8, 19)])
        zeit_layout.addWidget(von_zeit)
        
        bis_label = QLabel("Bis:")
        bis_label.setStyleSheet("color: #2c3e50;")
        zeit_layout.addWidget(bis_label)
        
        bis_zeit = QComboBox()
        bis_zeit.addItems([f"{h:02d}:00" for h in range(8, 19)])
        bis_zeit.setCurrentText("18:00")
        zeit_layout.addWidget(bis_zeit)
        
        # Entfernen-Button
        remove_btn = QPushButton("×")
        remove_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border-radius: 10px;
                padding: 2px 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        remove_btn.clicked.connect(lambda: self.remove_zeitslot(tag, zeit_container))
        zeit_layout.addWidget(remove_btn)
        
        slots_layout.addWidget(zeit_container)
        slots_layout.addWidget(add_button)
        
        # Speichere neue Widgets
        widgets["zeitslots"].append({"von": von_zeit, "bis": bis_zeit})

    def remove_zeitslot(self, tag, container):
        widgets = self.main_window.zeiten_widgets[tag]
        
        # Finde den Index des zu entfernenden Zeitslots
        for i, slot in enumerate(widgets["zeitslots"]):
            if slot["von"].parent().parent() == container:
                widgets["zeitslots"].pop(i)
                break
        
        # Entferne Container
        container.deleteLater()

    def update_passwort(self):
        if not self.main_window.patient_data:
            return
            
        neues_passwort = self.main_window.neues_passwort.text().strip()
        if not neues_passwort:
            QMessageBox.warning(self.main_window, "Fehler", "Bitte geben Sie ein neues Passwort ein.")
            return
            
        self.main_window.patient_data["passwort"] = neues_passwort
        speichere_daten(pfad_patienten, patienten)
        QMessageBox.information(self.main_window, "Erfolg", "Passwort wurde aktualisiert!")
        self.main_window.neues_passwort.clear()

    def update_krankenkasse(self):
        if not self.main_window.patient_data:
            return
            
        neue_kasse = self.main_window.kasse_box.currentText()
        self.main_window.patient_data["krankenkasse"] = neue_kasse
        speichere_daten(pfad_patienten, patienten)
        QMessageBox.information(self.main_window, "Erfolg", "Krankenkasse wurde aktualisiert!")
        self.main_window.show_meine_daten()  # Aktualisiere die Analyse-Ansicht

    def add_problem(self):
        if not self.main_window.patient_data:
            return
            
        problem = self.main_window.problem_box.currentText()
        try:
            anzahl = int(self.main_window.problem_anzahl.text().strip())
            if anzahl <= 0:
                raise ValueError()
        except ValueError:
            QMessageBox.warning(self.main_window, "Fehler", "Bitte geben Sie eine gültige Anzahl ein.")
            return
            
        neues_problem = {
            "art": problem,
            "anzahl": anzahl,
            "material": "normal"
        }
        # Prüfe ob das Problem bereits existiert
        problem_existiert = False
        for p in self.main_window.patient_data["probleme"]:
            if p["art"] == problem:
                p["anzahl"] += anzahl
                problem_existiert = True
                break
        if not problem_existiert:
            self.main_window.patient_data["probleme"].append(neues_problem)
        speichere_daten(pfad_patienten, patienten)
        QMessageBox.information(self.main_window, "Erfolg", "Behandlung hinzugefügt!")
        self.main_window.show_meine_daten() 