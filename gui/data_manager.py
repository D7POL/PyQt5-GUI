import json

# Stil-Definition
STYLE = """
QWidget {
    font-family: 'Segoe UI', Arial;
    font-size: 10pt;
}

QLabel {
    color: #2c3e50;
}

QLineEdit {
    padding: 8px;
    border: 2px solid #e0e0e0;
    border-radius: 5px;
    background-color: white;
    margin: 5px 0px;
    color: black;
}

QLineEdit:focus {
    border: 2px solid #3498db;
}

QPushButton {
    background-color: #3498db;
    color: white;
    border: none;
    padding: 10px 20px;
    border-radius: 5px;
    font-weight: bold;
    margin: 5px 0px;
}

QPushButton:hover {
    background-color: #2980b9;
}

QPushButton:pressed {
    background-color: #2472a4;
}

QComboBox {
    padding: 8px;
    border: 2px solid #e0e0e0;
    border-radius: 5px;
    background-color: white;
    margin: 5px 0px;
}

QComboBox:drop-down {
    border: none;
}

QComboBox:down-arrow {
    width: 12px;
    height: 12px;
}

QFrame[frameShape="4"] { /* Horizontale Linie */
    color: #e0e0e0;
    margin: 10px 0px;
}
"""

# JSON-Hilfsfunktionen
def lade_daten(pfad):
    with open(pfad, "r", encoding="utf-8") as f:
        daten = json.load(f)
        # Nur für Patienten- und Zahnarztdateien das Feld setzen
        if "patienten" in pfad or "zahnaerzte" in pfad:
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
pfad_behandlungen = "data/kosten_behandlungen.json"

# Daten laden
patienten = lade_daten(pfad_patienten)
zahnaerzte = lade_daten(pfad_zahnaerzte)
behandlungen_liste = lade_daten(pfad_behandlungen)
BEHANDLUNGEN = {b["art"]: b for b in behandlungen_liste} 