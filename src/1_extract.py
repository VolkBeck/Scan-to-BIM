"""
Modul: 1_extract.py
Beschreibung: Extrahiert geometrische Merkmale und Farbinformationen aus einer gelabelten
              Trainings-Punktwolke (.las).
Autor: Volker Becker
Datum: 2026-01-15

Funktionsweise:
1. Lädt eine .las Datei.
2. Berechnet geometrische Features (Linearität, Planarität, etc.) mittels 'jakteristics'.
3. Speichert die Ergebnisse als CSV für das Modell-Training.
"""

import laspy
import numpy as np
import pandas as pd
from jakteristics import compute_features
import os

# --- PFAD KONFIGURATION (Automatisch) ---
# Wir gehen davon aus, dass das Skript vom Hauptordner aus gestartet wird
INPUT_FILE = os.path.join("data", "training_labeled.las")
OUTPUT_CSV = os.path.join("output", "training_features.csv")

# Parameter
# SEARCH_RADIUS definiert die Nachbarschaftsgröße für die Berechnung der geometrischen Features.
# Ein Wert von 0.4m wurde gewählt, um auch bei geringer Punktdichte robuste Ergebnisse zu erzielen.
SEARCH_RADIUS = 0.4  # Erhöht wegen geringer Dichte (wie besprochen)

def main():
    """
    Hauptfunktion zur Extraktion der Trainingsdaten.
    Liest die Punktwolke, berechnet Features und speichert sie als CSV.
    """
    print(f"[1_extract] Lade {INPUT_FILE}...")
    
    # Überprüfung, ob die Eingabedatei existiert
    if not os.path.exists(INPUT_FILE):
        print(f"FEHLER: Datei {INPUT_FILE} fehlt! Bitte in den 'data' Ordner legen.")
        return

    # Einlesen der LAS-Datei
    las = laspy.read(INPUT_FILE)
    # Konvertierung der x, y, z Koordinaten in ein NumPy Array (N x 3)
    xyz = np.vstack((las.x, las.y, las.z)).transpose()
    # Laden der Klassifizierung (Labels), die zum Trainieren benötigt werden
    labels = np.array(las.classification)

    print(f"[1_extract] Anzahl Punkte: {len(xyz)}")

    # 1. FARBEN LADEN (RGB Fix)
    print("[1_extract] Extrahiere RGB-Farben...")
    # LAS speichert Farben oft als 16-Bit Integer. Wir laden sie hier als Rohdaten.
    red = np.array(las.red)
    green = np.array(las.green)
    blue = np.array(las.blue)

    # 2. GEOMETRIE BERECHNEN
    print(f"[1_extract] Berechne Geometrie (Radius {SEARCH_RADIUS}m)...")
    
    # Definition der zu berechnenden geometrischen Eigenheiten
    feature_names = ['planarity', 'linearity', 'verticality', 'sphericity', 'omnivariance']
    
    # compute_features nutzt Multi-Threading (num_threads=-1), um die Berechnung zu beschleunigen
    features = compute_features(xyz, 
                                search_radius=SEARCH_RADIUS, 
                                feature_names=feature_names,
                                num_threads=-1)

    # 3. DATAFRAME ZUSAMMENBAUEN
    # Erstellen eines Pandas DataFrame für einfache Handhabung und Export
    df = pd.DataFrame(features, columns=feature_names)
    
    # Farben hinzufügen
    df['red'] = red
    df['green'] = green
    df['blue'] = blue
    
    # Label (Zielvariable) hinzufügen
    df['label'] = labels
    
    # z_norm speichern (optional) - normalisierte Höhe relativ zum tiefsten Punkt
    df['z_norm'] = (xyz[:, 2] - np.min(xyz[:, 2]))

    # Bereinigen von NaN Werten, die bei der Feature-Berechnung entstehen können
    df = df.dropna()
    # Entfernen von unklassifizierten Punkten (Label 0 ist oft "Rauschen" oder "Unclassified")
    df = df[df['label'] > 0] 
    
    print(f"[1_extract] Speichere {len(df)} Punkte in {OUTPUT_CSV}...")
    # Export ohne Index, um Speicherplatz zu sparen und das Format sauber zu halten
    df.to_csv(OUTPUT_CSV, index=False)
    print("[1_extract] FERTIG.")

if __name__ == "__main__":
    main()