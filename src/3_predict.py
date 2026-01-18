"""
Modul: 3_predict.py
Beschreibung: Klassifiziert eine neue, unbekannte Punktwolke mit dem trainierten Modell.
Autor: Volker Becker
Datum: 2026-01-15

Funktionsweise:
1. Lädt die Ziel-Punktwolke.
2. Führt ein Voxel-Downsampling durch, um Rechenzeit zu sparen.
3. Berechnet Features auf den Voxel-Zentren.
4. Wendet das ML-Modell an (Vorhersage).
5. Überträgt die Labels per Nearest-Neighbor (KNN) zurück auf die Original-Punktwolke.
"""

import laspy
import numpy as np
import pandas as pd
import open3d as o3d
import joblib
from jakteristics import compute_features
from sklearn.neighbors import KNeighborsClassifier
import os

# --- KONFIGURATION ---
INPUT_FILE_NAME = "2og_ausschnitt.las" 

# Pfade zusammenbauen
INPUT_FILE = os.path.join("data", INPUT_FILE_NAME)
MODEL_FILE = os.path.join("output", "scan_to_bim_model.pkl")
OUTPUT_FILE = os.path.join("output", "result_2og_final.las")

# Parameter
SEARCH_RADIUS = 0.4  # Muss synchron mit Schritt 1 (Training) sein!
VOXEL_SIZE = 0.05    # Kantenlänge der Voxel in Metern (5cm)

def main():
    """
    Hauptfunktion zur Klassifizierung neuer Daten.
    """
    print(f"[3_predict] Lade Datei: {INPUT_FILE}...")
    if not os.path.exists(INPUT_FILE):
        print(f"FEHLER: Datei {INPUT_FILE} nicht gefunden. Bitte in 'data/' ablegen.")
        return
    if not os.path.exists(MODEL_FILE):
        print(f"FEHLER: Modell {MODEL_FILE} fehlt. Bitte erst Schritt 2 ausführen.")
        return

    # Einlesen der Originaldaten
    las = laspy.read(INPUT_FILE)
    xyz_full = np.vstack((las.x, las.y, las.z)).transpose()
    
    # Farben laden & normalisieren (auf Bereich 0.0 - 1.0 für Open3D Verarbeitung)
    red = np.array(las.red)
    green = np.array(las.green)
    blue = np.array(las.blue)
    colors_full = np.vstack((red, green, blue)).transpose() / 65535.0

    # 2. VOXEL DOWNSAMPLING
    # Reduziert die Datenmenge signifikant für die Feature-Berechnung
    print("[3_predict] Voxel-Downsampling...", flush=True)
    pcd = o3d.geometry.PointCloud()
    pcd.points = o3d.utility.Vector3dVector(xyz_full)
    pcd.colors = o3d.utility.Vector3dVector(colors_full)
    
    # Fasst Punkte in einem 5cm Raster zusammen
    pcd_voxel = pcd.voxel_down_sample(voxel_size=VOXEL_SIZE)
    xyz_voxel = np.asarray(pcd_voxel.points)
    # Rückskalierung der Farben auf 16-Bit Integer Bereich für Konsistenz
    rgb_voxel = np.asarray(pcd_voxel.colors) * 65535.0 
    
    # 3. FEATURES
    # Berechnung der Geometrie nur für die reduzierten Voxel-Punkte
    print("[3_predict] Berechne Features...", flush=True)
    features = compute_features(xyz_voxel, 
                                search_radius=SEARCH_RADIUS, 
                                feature_names=['planarity', 'linearity', 'verticality', 'sphericity', 'omnivariance'],
                                num_threads=-1) 

    # 4. VORHERSAGE
    print("[3_predict] KI Klassifizierung...", flush=True)
    df = pd.DataFrame(features, columns=['planarity', 'linearity', 'verticality', 'sphericity', 'omnivariance'])
    df['red'] = rgb_voxel[:, 0]
    df['green'] = rgb_voxel[:, 1]
    df['blue'] = rgb_voxel[:, 2]
    # Fehlende Werte (z.B. bei isolierten Voxeln) mit 0 auffüllen
    df = df.fillna(0)

    # Laden des trainierten Modells
    model = joblib.load(MODEL_FILE)
    
    # Nur Spalten nutzen, die das Modell beim Training gesehen hat (Sicherheitscheck)
    valid_cols = [c for c in df.columns if c in model.feature_names_in_]
    pred_voxel = model.predict(df[valid_cols])

    # 5. HOCHRECHNEN (Upsampling)
    # Überträgt das Label des Voxels auf alle originalen Punkte in dessen Nähe
    print("[3_predict] Übertrage auf Originalwolke...", flush=True)
    knn = KNeighborsClassifier(n_neighbors=1, n_jobs=-1)
    # KNN lernt: Position der Voxel -> Label der Voxel
    knn.fit(xyz_voxel, pred_voxel)
    # KNN sagt vorher: Label für Originalpunkte basierend auf nächstem Voxel
    predictions_full = knn.predict(xyz_full)

    # 6. SPEICHERN
    print(f"[3_predict] Speichere {OUTPUT_FILE}...", flush=True)
    new_las = laspy.create(point_format=las.header.point_format, file_version=las.header.version)
    new_las.header = las.header
    new_las.x = las.x
    new_las.y = las.y
    new_las.z = las.z
    # Speichern der vorhergesagten Klasse (konvertiert zu uint8)
    new_las.classification = predictions_full.astype(np.uint8)
    
    # Originalfarben und Intensität beibehalten
    new_las.red = las.red
    new_las.green = las.green
    new_las.blue = las.blue
    if hasattr(las, 'intensity'):
        new_las.intensity = las.intensity
    
    new_las.write(OUTPUT_FILE)
    print("[3_predict] FERTIG.")

if __name__ == "__main__":
    main()