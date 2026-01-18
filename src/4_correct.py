"""
Modul: 4_correct.py
Beschreibung: Regelbasierte Nachbearbeitung (Post-Processing) der klassifizierten Punktwolke.
Autor: Volker Becker
Datum: 2026-01-15

Funktionsweise:
1. Korrigiert Boden/Decke basierend auf einer Höhenanalyse (Z-Koordinate).
2. Bereinigt Stützen, die fälschlicherweise zu nah an Wänden detektiert wurden.
"""

import laspy
import numpy as np
from sklearn.neighbors import NearestNeighbors
import os

# --- KONFIGURATION ---
INPUT_FILE = os.path.join("output", "result_2og_final.las")
OUTPUT_FILE = os.path.join("output", "result_2og_corrected.las")

# Regeln
# Alles über Boden + 1.80m wird tendenziell dem Decken-Bereich zugeordnet (falls falsch klassifiziert)
# Alles unter Boden + 1.80m wird tendenziell dem Boden-Bereich zugeordnet
HEIGHT_THRESHOLD = 1.80 
MIN_DISTANCE_COLUMN_WALL = 0.60  # 60cm "Todeszone" um Wände, in der keine Stützen stehen dürfen

def main():
    """
    Hauptfunktion zur regelbasierten Korrektur.
    """
    print(f"[4_correct] Lade {INPUT_FILE}...")
    if not os.path.exists(INPUT_FILE):
        print("FEHLER: Input-Datei fehlt. Bitte Schritt 3 ausführen.")
        return

    las = laspy.read(INPUT_FILE)
    xyz = np.vstack((las.x, las.y, las.z)).transpose()
    # Kopie der Klassifizierung anlegen, um Änderungen vorzunehmen
    classification = np.array(las.classification)

    # --- HÖHEN-ANALYSE ---
    print("[4_correct] Analysiere Höhenverteilung...")
    z_values = xyz[:, 2]
    # Wir finden den "echten" Boden. 
    # Nutzung des 1. Perzentils statt min(), um einzelne Ausreißer nach unten (Rauschen) zu ignorieren.
    floor_level = np.percentile(z_values, 1)
    split_height = floor_level + HEIGHT_THRESHOLD
    print(f"   -> Boden-Niveau ca.: {floor_level:.2f} m")
    print(f"   -> Trennlinie (Threshold): {split_height:.2f} m")

    # --- REGEL 1a: FALSCHER BODEN (zu hoch) ---
    # Logik: Ein Punkt wurde als Boden (2) erkannt, schwebt aber weit oben (über split_height).
    # Maßnahme: Wird zur Decke (10) korrigiert.
    mask_fake_floor = (classification == 2) & (z_values > split_height)
    num_fake_floor = np.sum(mask_fake_floor)
    classification[mask_fake_floor] = 10  # Korrigiere zu Decke
    print(f"   -> {num_fake_floor} Punkte korrigiert (Boden -> Decke).")

    # --- REGEL 1b: FALSCHE DECKE (zu tief) ---
    # Logik: Ein Punkt wurde als Decke (10) erkannt, liegt aber tief unten (unter split_height).
    # Maßnahme: Wird zum Boden (2) korrigiert.
    mask_fake_ceiling = (classification == 10) & (z_values < split_height)
    num_fake_ceiling = np.sum(mask_fake_ceiling)
    classification[mask_fake_ceiling] = 2   # Korrigiere zu Boden
    print(f"   -> {num_fake_ceiling} Punkte korrigiert (Decke -> Boden).")

    # --- REGEL 2: STÜTZEN NAH AN WAND ---
    print(f"[4_correct] Regel 2: Stützen-Filter ({MIN_DISTANCE_COLUMN_WALL}m)...")
    idx_columns = np.where(classification == 4)[0] # Indices aller Stützen
    idx_walls = np.where(classification == 6)[0]   # Indices aller Wände

    if len(idx_columns) > 0 and len(idx_walls) > 0:
        # Erstelle einen KD-Tree für schnelle Nachbarschaftssuche nur auf den Wand-Punkten
        nbrs = NearestNeighbors(n_neighbors=1, algorithm='kd_tree', n_jobs=-1).fit(xyz[idx_walls])
        # Finde für jede Stütze den Abstand zur nächsten Wand
        distances, _ = nbrs.kneighbors(xyz[idx_columns])
        
        # Maske für Stützen, die zu nah an einer Wand stehen
        mask_too_close = distances.flatten() < MIN_DISTANCE_COLUMN_WALL
        idx_false_columns = idx_columns[mask_too_close]
        
        # Korrektur: Falsche Stützen werden zu Wand
        classification[idx_false_columns] = 6 
        print(f"   -> {len(idx_false_columns)} Stützen bereinigt (zu Wand).")
    else:
        print("   Keine Stützen/Wände gefunden.")

    # --- SPEICHERN ---
    print(f"[4_correct] Speichere {OUTPUT_FILE}...")
    new_las = laspy.create(point_format=las.header.point_format, file_version=las.header.version)
    new_las.header = las.header
    new_las.x = las.x
    new_las.y = las.y
    new_las.z = las.z
    new_las.classification = classification.astype(np.uint8)
    
    # Farben übertragen
    new_las.red = las.red
    new_las.green = las.green
    new_las.blue = las.blue
    if hasattr(las, 'intensity'):
        new_las.intensity = las.intensity

    new_las.write(OUTPUT_FILE)
    print("[4_correct] FERTIG.")

if __name__ == "__main__":
    main()