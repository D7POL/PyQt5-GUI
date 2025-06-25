from gui.data_manager import BEHANDLUNGEN

def berechne_kosten_und_zeit(patient):
    if not patient:
        return None
    
    gesamt_kosten = 0
    gesamt_zeit = 0
    versicherung = patient["krankenkasse"]
    
    analyse = []
    for problem in patient["probleme"]:
        behandlung = BEHANDLUNGEN.get(problem["art"])
        if behandlung:
            anzahl = problem["anzahl"]
            # Füllmaterial berücksichtigen (default: normal)
            material = problem.get("material", "normal")
            mat_info = behandlung["materialien"].get(material, behandlung["materialien"]["normal"])
            kosten = mat_info["preis"] * anzahl
            zeit = mat_info["zeit"] * anzahl
            einheit = behandlung["einheit"]
            erstattung = mat_info["erstattung"].get(versicherung, 0.0)
            eigenanteil = kosten * (1 - erstattung)
            versicherung_anteil = kosten * erstattung
            analyse.append({
                "art": problem["art"],
                "anzahl": anzahl,
                "material": material,
                "kosten": kosten,
                "zeit": zeit,
                "einheit": einheit,
                "eigenanteil": eigenanteil,
                "versicherung_anteil": versicherung_anteil
            })
            gesamt_kosten += kosten
            gesamt_zeit += zeit
    gesamt_eigenanteil = sum(item["eigenanteil"] for item in analyse)
    gesamt_versicherung_anteil = sum(item["versicherung_anteil"] for item in analyse)
    return {
        "analyse": analyse,
        "gesamt_kosten": gesamt_kosten,
        "eigenanteil": gesamt_eigenanteil,
        "versicherung_anteil": gesamt_versicherung_anteil,
        "gesamt_zeit": gesamt_zeit
    } 