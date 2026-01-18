# Scan-to-BIM Projekt - Installationsanleitung

## Voraussetzungen
* **Betriebssystem:** Windows 10/11 ODER macOS (10.13+) / Linux
* **Software:** Python 3.11 und CloudCompare (zur Visualisierung)

---

## A. Automatische Installation (Windows) - Empfohlen

1.  Navigieren in diesen Ordner.
2.  Führe das Skript `setup_windows.bat` (per Doppelklick) aus. 

> **Hinweis:** Das Skript prüft automatisch, ob Python 3.11 und CloudCompare installiert sind. Falls nicht, werden sie via `winget` nachgeladen. Anschließend wird die Entwicklungsumgebung (Virtual Environment) automatisch eingerichtet.

---

## B. Manuelle Installation (Windows)

Falls das automatische Skript nicht genutzt werden soll:

1.  **Python 3.11 installieren:**
    ```powershell
    winget install -e --id Python.Python.3.11
    ```
    

2.  **CloudCompare installieren:**
    ```powershell
    winget install -e --id CloudCompare.CloudCompare
    ```
    

3.  **Projekt einrichten** (in cmd oder PowerShell):
    ```powershell
    py -3.11 -m venv scan2bim_env
    scan2bim_env\Scripts\activate
    pip install --upgrade pip
    pip install -e .
    ```
    

---

## C. Anleitung für macOS (Apple Silicon / Intel)

1.  **Python 3.11 installieren:**
    Lade den Installer von [python.org](https://www.python.org/) herunter und führe ihn aus.

2.  **CloudCompare installieren:**
    Lade die `.dmg` Datei von [cloudcompare.org](https://www.cloudcompare.org/) herunter  oder nutze Homebrew:
    ```bash
    brew install --cask cloudcompare
    ```
    [cite: 7]

3.  **Projekt einrichten** (Terminal im Projektordner öffnen):
    ```bash
    python3.11 -m venv scan2bim_env
    source scan2bim_env/bin/activate
    pip install --upgrade pip
    pip install -e .
    ```

---

## D. Anleitung für Linux (Ubuntu/Debian)

1.  **Systempakete installieren:**
    ```bash
    sudo apt update
    sudo apt install python3.11 python3.11-venv python3.11-dev
    sudo snap install cloudcompare
    ```

2.  **Projekt einrichten:**
    ```bash
    python3.11 -m venv scan2bim_env
    source scan2bim_env/bin/activate
    pip install --upgrade pip
    pip install -e .
    ```

---

## E. Starten der Pipeline

Stelle sicher, dass das Environment aktiviert ist (erkennbar am `(scan2bim_env)` vor der Eingabezeile).

Starte den Prozess mit:
```bash
python main.py```


---

## F. Ergebnisse ansehen (CloudCompare)

Um die klassifizierten Punktwolken zu prüfen:

1.  Öffnen **CloudCompare**.
2.  Gehen auf `File` > `Open` und wähle eine Datei aus `output/` (z.B. `result_2og_corrected.las`).
3.  Im Dialog "Open LAS File": Klicken auf **Apply**.
    * *Falls gefragt wird "Global Shift/Scale": Bestätige mit **Yes**.*
4.  **WICHTIG - ANSICHT UMSTELLEN**:
    Damit die Klassifizierung sichtbar wird, muss die Ansicht umgestellt werden:
    * Klicken links im "DB Tree" auf die geladene Punktwolke.
    * Suchen unten links im Fenster "Properties" den Bereich **Colors**.
    * Stelle das Dropdown von "RGB" auf **Scalar Field** um.
    * Wähle im Dropdown "Current SF" das Feld **Classification** aus.

Nun werden die Bauteile farblich unterschieden (Wand, Boden, Fenster etc.).