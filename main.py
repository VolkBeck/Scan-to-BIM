"""
Modul: main.py
Beschreibung: Zentrales Steuerungsskript (Orchestrator) für die Scan-to-BIM Pipeline.
Autor: Volker Becker
Datum: 2026-01-15

Funktionsweise:
1. Prüft Ordnerstrukturen (data/output).
2. Führt die Prozess-Schritte (1 bis 4) nacheinander als Subprozesse aus.
3. Misst die Ausführungszeit jedes Schrittes.
4. Erstellt einen Abschlussbericht über die Gesamtlaufzeit.
"""

import subprocess
import os
import sys
import time

def run_step(script_name, description):
    """
    Führt ein einzelnes Python-Skript als Subprozess aus und misst die Zeit.

    Args:
        script_name (str): Name der Python-Datei (z.B. '1_extract.py').
        description (str): Kurzbeschreibung für die Konsolenausgabe.

    Returns:
        float: Benötigte Zeit in Sekunden (oder None bei Fehler).
    """
    print("="*60)
    print(f"STARTE SCHRITT: {description}")
    print(f"Skript: src/{script_name}")
    print("="*60)
    
    start_time = time.time()
    
    # Pfad zum Skript im src-Ordner bauen
    script_path = os.path.join("src", script_name)
    
    if not os.path.exists(script_path):
        print(f"FEHLER: Skript {script_path} nicht gefunden!")
        return None # Rückgabe None bei Fehler

    # Skript als eigener Prozess ausführen (sys.executable stellt sicher, dass derselbe Python-Interpreter genutzt wird)
    try:
        subprocess.run([sys.executable, script_path], check=True)
        duration = time.time() - start_time
        print(f"\n---> Schritt erfolgreich abgeschlossen in {duration:.1f} Sekunden.\n")
        return duration # Gib die Dauer zurück
    except subprocess.CalledProcessError:
        print(f"\n---> FEHLER in {script_name}. Abbruch.")
        return None

def main():
    """
    Hauptroutine: Definiert die Pipeline-Schritte und iteriert durch diese.
    """
    print("Scan-to-BIM AI Pipeline")
    print("Autor: Volker Becker")
    print("-" * 60)

    # Ordner erstellen falls nicht vorhanden
    os.makedirs("output", exist_ok=True)
    os.makedirs("data", exist_ok=True)

    total_machine_time = 0.0
    steps_run = 0

    # Liste der auszuführenden Skripte als Tupel (Dateiname, Beschreibung)
    steps = [
        ("1_extract.py", "Features aus Trainingsdaten extrahieren"),
        ("2_train.py", "Random Forest Modell trainieren"),
        ("3_predict.py", "Punktwolke klassifizieren (KI)"),
        ("4_correct.py", "Regelbasierte Fehlerkorrektur")
    ]

    # Iteration durch alle definierten Schritte
    for script, desc in steps:
        duration = run_step(script, desc)
        if duration is None:
            print("Abbruch der Pipeline aufgrund eines Fehlers.")
            return
        
        # Zeit aufaddieren
        total_machine_time += duration
        steps_run += 1

    # --- ABSCHLUSS-BERICHT FÜR DIE Bachelorarbeit ---
    minutes = total_machine_time / 60
    
    print("="*60)
    print("GESAMT-PIPELINE ERFOLGREICH BEENDET.")
    print(f"Ergebnisse liegen im Ordner 'output/'.")
    print("-" * 60)
    print(f"DATEN FÜR WIRTSCHAFTLICHKEITSANALYSE:")
    print(f"Anzahl Schritte: {steps_run}")
    print(f"Gesamte Maschinenzeit (Extract + Train + Predict + Correct):")
    print(f"   -> {total_machine_time:.2f} Sekunden")
    print(f"   -> {minutes:.2f} Minuten")
    print("="*60)

if __name__ == "__main__":
    main()