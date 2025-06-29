from PyQt5.QtWidgets import (
    QWidget, QLabel, QVBoxLayout, QMessageBox,
    QHBoxLayout, QFrame, QScrollArea, QPushButton, QSizePolicy, QCalendarWidget, QTableWidget, QTableWidgetItem, QHeaderView
)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QColor, QTextCharFormat
from datetime import datetime, timedelta
import json
from components.calculator import berechne_kosten_und_zeit


def get_weekday(date_obj):
    """Get weekday name from a date object"""
    weekdays = ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag", "Sonntag"]
    return weekdays[date_obj.weekday()]


class ViewManager:
    def __init__(self, main_window):
        self.main_window = main_window

    def show_meine_daten(self):
        if self.main_window.current_page:
            self.main_window.current_page.hide()
            self.main_window.current_page.deleteLater()

        # Container Analyse
        analyse_container = QFrame()
        analyse_container.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 10px;
                padding: 20px;
            }
        """)
        analyse_layout = QVBoxLayout(analyse_container)

        if self.main_window.rolle == "Patient" and self.main_window.patient_data:
            # Analyse Patientendaten
            analyse_data = berechne_kosten_und_zeit(self.main_window.patient_data)

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
            versicherung_info = QLabel(f"Versicherung: {self.main_window.patient_data['krankenkasse']}")
            versicherung_info.setStyleSheet("font-size: 16px; color: #7f8c8d; margin-bottom: 10px;")
            analyse_layout.addWidget(versicherung_info)

            if not analyse_data["analyse"]:
                # Hinweistext außerhalb Box, ohne Scrollbereich
                hinweis = QLabel("Sie haben zurzeit keine Behandlungen, neue Behandlungen können Sie in den Einstellungen hinzufügen")
                hinweis.setStyleSheet("color: #7f8c8d; font-size: 15px; padding: 16px;")
                hinweis.setAlignment(Qt.AlignCenter)
                analyse_layout.addWidget(hinweis)
            else:
                # Container für Analyse-Details
                details_container = QFrame()
                details_container.setStyleSheet("""
                    QFrame {
                        background-color: #e8f4f8;
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

                # SCROLLBEREICH für Behandlungen
                details_scroll = QScrollArea()
                details_scroll.setWidgetResizable(True)
                details_scroll.setWidget(details_container)
                details_scroll.setMinimumHeight(300)
                details_scroll.setMaximumHeight(600)
                details_scroll.setStyleSheet("QScrollArea { margin-left: 0px; }")
                analyse_layout.addWidget(details_scroll)

            # Zusammenfassung Kosten
            zusammenfassung = QFrame()
            zusammenfassung.setStyleSheet("""
                QFrame {
                    background-color: #e8f4f8;
                    border-radius: 8px;
                    padding: 6px;
                    margin-top: 6px;
                    margin-left: 20px;
                    max-width: 1220px
                }
            """)
            zusammenfassung_layout = QVBoxLayout(zusammenfassung)
            zusammenfassung.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Maximum)

            gesamt_label = QLabel(f"Gesamtkosten: {analyse_data['gesamt_kosten']}€")
            gesamt_label.setStyleSheet("font-size: 22px; font-weight: bold; color: #2c3e50; line-height: 1.2;")
            zusammenfassung_layout.addWidget(gesamt_label)

            erstattung_label = QLabel(f"Erstattung durch Versicherung: {analyse_data['versicherung_anteil']:.2f}€")
            erstattung_label.setStyleSheet("color: #27ae60; font-size: 18px; line-height: 1.2;")
            zusammenfassung_layout.addWidget(erstattung_label)

            eigenanteil_label = QLabel(f"Ihr Eigenanteil: {analyse_data['eigenanteil']:.2f}€")
            eigenanteil_label.setStyleSheet("color: #e74c3c; font-size: 18px; line-height: 1.2;")
            zusammenfassung_layout.addWidget(eigenanteil_label)

            zeit_label = QLabel(f"Gesamter Zeitaufwand: {analyse_data['gesamt_zeit']} Minuten")
            zeit_label.setStyleSheet("color: #2c3e50; font-size: 18px; line-height: 1.2;")
            zusammenfassung_layout.addWidget(zeit_label)

            zusammenfassung.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
            analyse_layout.addWidget(zusammenfassung)

        self.main_window.inhalt_layout_inner.addWidget(analyse_container)
        self.main_window.current_page = analyse_container

    def show_meine_termine(self):
        if self.main_window.current_page:
            self.main_window.current_page.hide()
            self.main_window.current_page.deleteLater()

        # Container für Termine
        termine_container = QFrame()
        termine_container.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 10px;
                padding: 20px;
            }
        """)
        termine_layout = QVBoxLayout(termine_container)

        # Überschrift
        titel = QLabel("Meine Termine")
        titel.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            color: #2c3e50;
            margin-bottom: 20px;
        """)
        termine_layout.addWidget(titel)

        # Lade Termine
        with open("data/termine.json", "r", encoding="utf-8") as f:
            alle_termine = json.load(f)

        # Sammle alle Termine des Patienten
        meine_termine = []
        for arzt, arzt_termine in alle_termine.items():
            for datum, tag_termine in arzt_termine.items():
                for zeit, termin in tag_termine.items():
                    if termin["patient"] == self.main_window.benutzername:
                        meine_termine.append({
                            "arzt": arzt,
                            "datum": datum,
                            "zeit": zeit,
                            "behandlung": termin["behandlung"],
                            "dauer": termin["dauer"],
                            "anzahl": termin.get("anzahl")  # Lese Anzahl
                        })

        # Sortiert Termine nach Datum und Zeit
        meine_termine.sort(key=lambda x: (x["datum"], x["zeit"]))

        if not meine_termine:
            keine_termine = QLabel("Sie haben noch keine Termine gebucht.")
            keine_termine.setStyleSheet("color: #7f8c8d;")
            termine_layout.addWidget(keine_termine)
        else:
            # Erstellt ScrollArea für die Termine
            scroll = QScrollArea()
            scroll.setWidgetResizable(True)
            scroll.setStyleSheet("""
                QScrollArea {
                    border: 5px solid #E8F4F8;
                }
            """)

            scroll_content = QWidget()
            scroll_layout = QVBoxLayout(scroll_content)
            scroll_layout.setSpacing(10)  # Abstand zwischen Terminen

            # Gruppiere Termine nach Datum
            termine_nach_datum = {}
            for termin in meine_termine:
                datum = termin["datum"]
                if datum not in termine_nach_datum:
                    termine_nach_datum[datum] = []
                termine_nach_datum[datum].append(termin)

            for datum, termine in termine_nach_datum.items():
                # Datum Header
                datum_obj = datetime.strptime(datum, "%Y-%m-%d")
                datum_str = datum_obj.strftime("%d.%m.%Y")
                wochentag = get_weekday(datum_obj)  # Vollständiger Wochentag

                datum_frame = QFrame()
                datum_frame.setStyleSheet("""
                    QFrame {
                        background-color: #f8f9fa;
                        border-radius: 5px;
                        padding: 10px;
                        margin-bottom: 5px;
                    }
                """)
                datum_layout = QVBoxLayout(datum_frame)
                datum_layout.setSpacing(5)

                datum_label = QLabel(f"<b>{wochentag}, {datum_str}</b>")
                datum_label.setStyleSheet("color: #2c3e50; font-size: 14px;")
                datum_layout.addWidget(datum_label)

                for termin in termine:
                    termin_frame = QFrame()
                    termin_frame.setStyleSheet("""
                        QFrame {
                            background-color: white;
                            border: 1px solid #e0e0e0;
                            border-radius: 5px;
                            padding: 8px;
                        }
                    """)
                    termin_layout = QHBoxLayout(termin_frame)
                    termin_layout.setContentsMargins(10, 5, 10, 5)

                    # Linke Seite: Zeit und Dauer
                    zeit_container = QFrame()
                    zeit_layout = QVBoxLayout(zeit_container)
                    zeit_layout.setSpacing(2)
                    zeit_layout.setContentsMargins(0, 0, 0, 0)

                    zeit_label = QLabel(f"<b>{termin['zeit']} Uhr</b>")
                    zeit_label.setStyleSheet("color: #2c3e50;")
                    zeit_layout.addWidget(zeit_label)

                    dauer_label = QLabel(f"{termin['dauer']} Min.")
                    dauer_label.setStyleSheet("color: #7f8c8d; font-size: 15px;")
                    zeit_layout.addWidget(dauer_label)

                    termin_layout.addWidget(zeit_container)

                    # Vertikale Linie
                    linie = QFrame()
                    linie.setFrameShape(QFrame.VLine)
                    linie.setFrameShadow(QFrame.Sunken)
                    linie.setStyleSheet("color: #e0e0e0;")
                    termin_layout.addWidget(linie)

                    # Rechte Seite: Behandlung und Arzt
                    info_container = QFrame()
                    info_layout = QVBoxLayout(info_container)
                    info_layout.setSpacing(2)
                    info_layout.setContentsMargins(0, 0, 0, 0)

                    behandlung_label = QLabel(f"<b>{termin['behandlung']}</b>")
                    behandlung_label.setStyleSheet("color: #2c3e50;")
                    info_layout.addWidget(behandlung_label)

                    anzahl_str = f"Anzahl Zähne: {termin['anzahl']}"
                    anzahl_label = QLabel(anzahl_str)
                    anzahl_label.setStyleSheet("color: #7f8c8d; font-size: 13px;")
                    info_layout.addWidget(anzahl_label)

                    arzt_label = QLabel(f"{termin['arzt']}")
                    arzt_label.setStyleSheet("color: #34495e; font-size: 15px;")
                    info_layout.addWidget(arzt_label)

                    termin_layout.addWidget(info_container, stretch=1)

                    # Abbrechen-Button
                    abbrechen_btn = QPushButton("Termin absagen")
                    abbrechen_btn.setStyleSheet("""
                        QPushButton {
                            background-color: #e74c3c;
                            color: white;
                            border-radius: 5px;
                            padding: 5px 12px;
                            font-weight: bold;
                        }
                        QPushButton:hover {
                            background-color: #c0392b;
                        }
                    """)
                    abbrechen_btn.clicked.connect(lambda checked, arzt=termin['arzt'], datum=termin['datum'],
                                                         zeit=termin[
                                                             'zeit']: self.main_window.booking_manager.cancel_termin(
                        arzt, datum, zeit))
                    termin_layout.addWidget(abbrechen_btn)

                    datum_layout.addWidget(termin_frame)

                scroll_layout.addWidget(datum_frame)

            scroll_layout.addStretch()
            scroll.setWidget(scroll_content)
            termine_layout.addWidget(scroll)

        self.main_window.inhalt_layout_inner.addWidget(termine_container)
        self.main_window.current_page = termine_container

    def show_zahnarzt_dashboard(self):
        if self.main_window.current_page:
            self.main_window.current_page.hide()
            self.main_window.current_page.deleteLater()

        dashboard_container = QFrame()
        dashboard_container.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 10px;
                padding: 20px;
            }
        """)
        dashboard_layout = QVBoxLayout(dashboard_container)
        dashboard_layout.setSpacing(8)

        # Zahnarzt-Daten laden
        with open("data/zahnaerzte.json", "r", encoding="utf-8") as f:
            zahnaerzte_data = json.load(f)
        current_zahnarzt = next((a for a in zahnaerzte_data if a["name"] == self.main_window.benutzername), None)

        # Kompakter Kalender
        kalender_container = QFrame()
        kalender_container.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border-radius: 8px;
                padding: 4px 0 4px 0;
            }
        """)
        kalender_layout = QVBoxLayout(kalender_container)
        kalender_layout.setAlignment(Qt.AlignCenter)
        kalender_titel = QLabel("Termin-Kalender")
        kalender_titel.setStyleSheet("font-size: 16px; font-weight: bold; color: #2c3e50; margin-bottom: 4px;")
        kalender_layout.addWidget(kalender_titel, alignment=Qt.AlignCenter)
        self.main_window.zahnarzt_kalender = QCalendarWidget()
        self.main_window.zahnarzt_kalender.setMinimumHeight(320)
        self.main_window.zahnarzt_kalender.setMaximumHeight(340)
        self.main_window.zahnarzt_kalender.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.main_window.zahnarzt_kalender.setMinimumDate(QDate.currentDate())
        self.main_window.zahnarzt_kalender.setMaximumDate(QDate.currentDate().addMonths(3))
        self.main_window.zahnarzt_kalender.clicked.connect(self.show_zahnarzt_day_termine)
        kalender_layout.addWidget(self.main_window.zahnarzt_kalender)
        self.update_zahnarzt_calendar(current_zahnarzt)
        dashboard_layout.addWidget(kalender_container)

        self.main_window.terminliste_titel = QLabel("Termine - Klicken Sie auf einen Tag im Kalender")
        self.main_window.terminliste_titel.setStyleSheet(
            "font-size: 15px; font-weight: bold; color: #2c3e50; margin: 10px 0 6px 0;")
        dashboard_layout.addWidget(self.main_window.terminliste_titel)

        # Tabelle und Hinweistext vorbereiten
        self.main_window.termin_table = QTableWidget()
        self.main_window.termin_table.setColumnCount(6)
        self.main_window.termin_table.setRowCount(0)  # Keine Dummy-Zeile mehr
        self.main_window.termin_table.setHorizontalHeaderLabels(
            ["Uhrzeit", "Patient", "Behandlung", "Material", "Anzahl", "Dauer"])
        
        # Header ausblenden
        header = self.main_window.termin_table.horizontalHeader()
        header.setVisible(False)
        for i in range(6):
            self.main_window.termin_table.horizontalHeader().setSectionResizeMode(i, QHeaderView.Stretch)

        # Überschriftenzeile mit QLabel
        table_header_row = QFrame()
        table_header_layout = QHBoxLayout(table_header_row)
        table_header_layout.setContentsMargins(0, 0, 0, 0)
        table_header_layout.setSpacing(0)
        labels = [
            "Uhrzeit",
            "Patient",
            "Behandlung",
            "Material",
            "Anzahl",
            "Dauer"
        ]
        for text in labels:
            lbl = QLabel(text)
            lbl.setAlignment(Qt.AlignCenter)
            lbl.setStyleSheet("font-weight: bold; font-size: 15px; color: #2c3e50; border-bottom: 1px solid #d0d0d0; background: #f8f9fa; padding: 8px 2px;")
            table_header_layout.addWidget(lbl, 1)  # Stretch für Flexibilität

        # Überschriftenzeile und Tabelle in QVBoxLayout
        table_with_header = QFrame()
        table_with_header_layout = QVBoxLayout(table_with_header)
        table_with_header_layout.setContentsMargins(0, 0, 0, 0)
        table_with_header_layout.setSpacing(0)
        table_with_header_layout.addWidget(table_header_row)
        table_with_header_layout.addWidget(self.main_window.termin_table)

        # Speichert Überschriftenzeile als Attribut
        self.main_window.termin_table_header = table_header_row

        # Im dashboard_layout die Tabelle durch table_with_header ersetzen
        dashboard_layout.addWidget(table_with_header)

        # Header und Tabelle ausblenden
        self.main_window.termin_table_header.hide()
        self.main_window.termin_table.hide()

        self.main_window.termin_hinweis = QLabel("")
        self.main_window.termin_hinweis.setStyleSheet("color: #7f8c8d; font-size: 15px; padding: 16px;")
        self.main_window.termin_hinweis.hide()

        dashboard_layout.addWidget(self.main_window.termin_hinweis)

        self.main_window.inhalt_layout_inner.addWidget(dashboard_container)
        self.main_window.current_page = dashboard_container

    def update_zahnarzt_calendar(self, zahnarzt):
        """Aktualisiert die Kalender-Farben basierend auf Terminen und Arbeitszeiten"""
        if zahnarzt is None:
            return
        with open("data/termine.json", "r", encoding="utf-8") as f:
            termine = json.load(f)

        current = self.main_window.zahnarzt_kalender.minimumDate()
        today = QDate.currentDate()

        while current <= self.main_window.zahnarzt_kalender.maximumDate():
            weekday = current.toString("ddd")  # 'Mo', 'Di', ...
            format = QTextCharFormat()
            format.setForeground(QColor("#000000"))  # Immer schwarze Schrift

            # Prüfe ob Tag Termine hat
            date_str = current.toString("yyyy-MM-dd")
            arzt_termine = termine.get(zahnarzt["name"], {})
            tag_termine = arzt_termine.get(date_str, {})
            hat_termine = len(tag_termine) > 0

            if current < today:
                # Alle Tage vor heute: grau
                format.setBackground(QColor("#e0e0e0"))
            elif weekday == "Sa" or weekday == "So":
                # Samstag und Sonntag: rot
                format.setBackground(QColor("#ffb3b3"))
            elif weekday not in zahnarzt["zeiten"]:
                # Arzt arbeitet nicht: grau
                format.setBackground(QColor("#e0e0e0"))
            elif hat_termine:
                # Tag mit Terminen: orange
                format.setBackground(QColor("#ffd700"))
            else:
                # Verfügbare Tage ohne Termine: grün
                format.setBackground(QColor("#b9fbc0"))

            self.main_window.zahnarzt_kalender.setDateTextFormat(current, format)
            current = current.addDays(1)

    def show_zahnarzt_day_termine(self, date):
        with open("data/termine.json", "r", encoding="utf-8") as f:
            alle_termine = json.load(f)
        date_str = date.toString("yyyy-MM-dd")
        arzt_termine = alle_termine.get(self.main_window.benutzername, {})
        tag_termine = arzt_termine.get(date_str, {})
        datum_display = date.toString("dd.MM.yyyy")
        wochentag = get_weekday(date.toPyDate())
        self.main_window.terminliste_titel.setText(f"Termine am {wochentag}, {datum_display}")
        if not tag_termine:
            self.main_window.termin_table_header.hide()
            self.main_window.termin_table.setRowCount(0)
            self.main_window.termin_table.hide()
            self.main_window.termin_hinweis.setText("Keine Termine an diesem Tag.")
            self.main_window.termin_hinweis.show()
        else:
            self.main_window.termin_table_header.show()
            self.main_window.termin_hinweis.hide()
            sorted_termine = sorted(tag_termine.items(), key=lambda x: x[0])
            self.main_window.termin_table.setRowCount(len(sorted_termine))
            for row_idx, (zeit, termin_info) in enumerate(sorted_termine):
                self.main_window.termin_table.setItem(row_idx, 0, QTableWidgetItem(str(zeit)))
                self.main_window.termin_table.setItem(row_idx, 1, QTableWidgetItem(str(termin_info['patient'])))
                self.main_window.termin_table.setItem(row_idx, 2, QTableWidgetItem(str(termin_info['behandlung'])))
                self.main_window.termin_table.setItem(row_idx, 3,
                                                      QTableWidgetItem(str(termin_info.get('material', 'normal'))))
                anzahl = str(termin_info.get('anzahl', 'N/A')) + " Zähne" if isinstance(termin_info.get('anzahl'),
                                                                                        int) else "N/A"
                self.main_window.termin_table.setItem(row_idx, 4, QTableWidgetItem(anzahl))
                self.main_window.termin_table.setItem(row_idx, 5, QTableWidgetItem(str(termin_info['dauer']) + " Min."))
            self.main_window.termin_table.show()
            self.main_window.termin_table.updateGeometry()
            self.main_window.termin_table.repaint()