"""
Modul: 2_train.py
Beschreibung: Trainiert einen Random Forest Klassifikator basierend auf den extrahierten Features.
Autor: Volker Becker
Datum: 2026-01-15

Funktionsweise:
1. Lädt die Feature-Matrix (CSV) aus Schritt 1.
2. Führt eine 5-Fold Cross-Validation durch, um die Modellgüte zu prüfen.
3. Trainiert das finale Modell auf dem gesamten Datensatz.
4. Speichert das Modell als .pkl Datei via joblib.
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import StratifiedKFold, cross_val_predict
from sklearn.metrics import classification_report, confusion_matrix
import joblib
import os

# --- PFAD KONFIGURATION ---
INPUT_CSV = os.path.join("output", "training_features.csv")
MODEL_FILE = os.path.join("output", "scan_to_bim_model.pkl")

def main():
    """
    Hauptfunktion für das Training und die Evaluierung des Random Forest Modells.
    """
    print("="*50)
    print(f"[2_train] START: Random Forest Training mit 5-Fold CV")
    print("="*50)

    # 1. DATEN LADEN
    print(f"[2_train] Lade Daten von {INPUT_CSV}...")
    if not os.path.exists(INPUT_CSV):
        print("FEHLER: CSV fehlt. Bitte erst Schritt 1 ausführen.")
        return

    df = pd.read_csv(INPUT_CSV)
    
    # Features definieren
    # Wir nutzen eine Kombination aus Farbinformationen (RGB) und geometrischen Features.
    feature_cols = ['planarity', 'linearity', 'verticality', 'sphericity', 'omnivariance', 'red', 'green', 'blue']
    
    X = df[feature_cols] # Feature Matrix
    y = df['label']      # Target Vector (Klassen)

    print(f"[2_train] Datensatz geladen: {len(df)} Punkte.")
    print(f"[2_train] Features: {feature_cols}")

    # 2. RANDOM FOREST KONFIGURIEREN
    # n_estimators=500: Anzahl der Bäume im Wald (höher = oft besser, aber langsamer)
    # n_jobs=-1: Nutzt alle verfügbaren CPU-Kerne
    # random_state=42: Sorgt für Reproduzierbarkeit der Ergebnisse (Wissenschaftlicher Standard)
    clf = RandomForestClassifier(n_estimators=500, n_jobs=-1, random_state=42)

    # 3. K-FOLD CROSS VALIDATION DURCHFÜHREN
    # Wir nutzen "Stratified", damit in jedem Fold das Verhältnis der Klassen gleich bleibt 
    # (Wichtig, da Klassen wie Fenster oft unterrepräsentiert sind)
    print("\n[2_train] Starte 5-Fold Cross-Validation (das kann kurz dauern)...")
    
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    
    # cross_val_predict liefert für jeden Punkt im Datensatz eine Vorhersage, 
    # die gemacht wurde, als dieser Punkt im Test-Set (Validation Set) war.
    y_pred_cv = cross_val_predict(clf, X, y, cv=cv, n_jobs=-1)

    # 4. EVALUIERUNG (Auf Basis des gesamten Datensatzes!)
    print("\n" + "="*50)
    print("ERGEBNISSE DER KREUZVALIDIERUNG (5-Fold)")
    print("="*50)
    
    # Classification Report: Zeigt Precision, Recall und F1-Score pro Klasse
    print("Klassifizierungsbericht:")
    print(classification_report(y, y_pred_cv))

    # Confusion Matrix: Zeigt Verwechslungen zwischen Klassen
    print("\nConfusion Matrix (Alle Daten):")
    cm = confusion_matrix(y, y_pred_cv)
    print(cm)
    
    # Klassen-Legende
    print("\nLegende (Klassen-IDs):")
    print(clf.classes_ if hasattr(clf, "classes_") else np.unique(y))
    print("="*50)

    # 5. FINALES MODELL SPEICHERN
    # CV war nur zum Testen der Qualität. Jetzt trainieren wir das Modell auf 100% der Daten,
    # damit es für die neue Punktwolke (Schritt 3) maximales Wissen besitzt.
    print(f"\n[2_train] Trainiere finales Modell auf allen {len(df)} Punkten...")
    clf.fit(X, y)

    print(f"[2_train] Speichere Modell in {MODEL_FILE}...")
    joblib.dump(clf, MODEL_FILE)
    print("[2_train] FERTIG.")

if __name__ == "__main__":
    main()