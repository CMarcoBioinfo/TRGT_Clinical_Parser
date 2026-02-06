import os
import zipfile
import tempfile
import subprocess
import PySimpleGUI as sg
import urllib.request
import urllib.error
import shutil
import time

SPANNING_ARCHIVE_SUFFIX = "spanning_BAM.zip"
PADDING = 50  # marge autour de la région TRGT

CURRENT_TMPDIR = None
CURRENT_BAM = None


# ---------------------------------------------------------
#  API IGV : détecter si IGV est ouvert
# ---------------------------------------------------------
def igv_is_running():
    try:
        urllib.request.urlopen("http://localhost:60151/status", timeout=0.2)
        return True
    except:
        return False


# ---------------------------------------------------------
#  API IGV : charger un BAM
# ---------------------------------------------------------
def igv_load(bam_path):
    url = f"http://localhost:60151/load?file={bam_path}"
    try:
        urllib.request.urlopen(url)
    except Exception as e:
        print("Erreur IGV LOAD :", e)


# ---------------------------------------------------------
#  API IGV : aller à une région (avec padding)
# ---------------------------------------------------------
def igv_goto(chrom, start, end, padding=PADDING):
    start_padded = max(0, start - padding)
    end_padded = end + padding
    region = f"{chrom}:{start_padded}-{end_padded}"
    url = f"http://localhost:60151/goto?locus={region}"
    try:
        urllib.request.urlopen(url)
    except Exception as e:
        print("Erreur IGV GOTO :", e)


# ---------------------------------------------------------
#  Trouver automatiquement IGV (toutes versions)
# ---------------------------------------------------------
def find_igv_launcher():
    print("\n=== DEBUG find_igv_launcher ===")

    base_dirs = [
        r"C:\Program Files",
        r"C:\Program Files (x86)",
    ]

    for base in base_dirs:
        print("Recherche dans :", base)

        try:
            for entry in os.listdir(base):
                if entry.lower().startswith("igv"):
                    igv_dir = os.path.join(base, entry)
                    launcher = os.path.join(igv_dir, "igv.bat")

                    print("Test :", launcher)

                    if os.path.exists(launcher):
                        print("IGV trouvé :", launcher)
                        return launcher
        except PermissionError:
            continue

    print("AUCUN lanceur IGV trouvé automatiquement.")
    return None


# ---------------------------------------------------------
#  Trouver le BAM TRGT dans le ZIP
# ---------------------------------------------------------
def find_spanning_bam(zip_path):
    print("\n=== DEBUG IGV ===")
    print("ZIP PATH =", zip_path)

    if not os.path.exists(zip_path):
        print("ERREUR : Le ZIP n'existe pas.")
        return None

    with zipfile.ZipFile(zip_path, "r") as z:
        names = z.namelist()

    print("CONTENU DU ZIP :")
    for n in names:
        print(" -", n)

    for n in names:
        if n.endswith(".sorted.spanning.bam"):
            bam = n
            bai = bam + ".bai"

            print("BAM TROUVÉ :", bam)
            print("BAI ATTENDU :", bai)

            if bai in names:
                print("BAI TROUVÉ ✔")
                return zip_path, bam, bai
            else:
                print("BAI MANQUANT ✘")

    print("AUCUN BAM TRGT TROUVÉ DANS LE ZIP.")
    return None


# ---------------------------------------------------------
#  Trouver automatiquement le ZIP spanning_BAM.zip
# ---------------------------------------------------------
def get_available_spanning_bam(base_dir, analyse_prefix, sample_name=None):
    print("\n=== DEBUG get_available_spanning_bam ===")
    print("BASE DIR =", base_dir)
    print("ANALYSE PREFIX =", analyse_prefix)

    for f in os.listdir(base_dir):
        if "spanning" in f.lower() and f.lower().endswith(".zip"):
            zip_path = os.path.join(base_dir, f)
            print("ZIP TROUVÉ AUTOMATIQUEMENT :", zip_path)
            return find_spanning_bam(zip_path)

    print("AUCUN ZIP SPANNING TROUVÉ DANS LE DOSSIER.")
    return None


# ---------------------------------------------------------
#  Suppression du dossier temporaire si IGV est fermé
# ---------------------------------------------------------
def cleanup_tmp_if_igv_closed():
    global CURRENT_TMPDIR

    if CURRENT_TMPDIR and not igv_is_running():
        print("IGV fermé → suppression du dossier temporaire")
        shutil.rmtree(CURRENT_TMPDIR, ignore_errors=True)
        CURRENT_TMPDIR = None


# ---------------------------------------------------------
#  Extraction + lancement IGV (intelligent)
# ---------------------------------------------------------
def open_igv(zip_path, bam_file, bai_file, chrom, start, end):
    global CURRENT_TMPDIR, CURRENT_BAM

    print("\n=== DEBUG open_igv ===")
    print("ZIP =", zip_path)
    print("BAM =", bam_file)
    print("BAI =", bai_file)
    print("REGION =", chrom, start, end)

    # 1) IGV déjà ouvert → juste déplacement
    if igv_is_running():
        print("IGV déjà ouvert → déplacement uniquement")
        igv_goto(chrom, start, end)
        return

    # 2) IGV fermé → extraction + lancement
    CURRENT_TMPDIR = tempfile.mkdtemp()
    print("Extraction dans :", CURRENT_TMPDIR)

    with zipfile.ZipFile(zip_path, "r") as outer:
        outer.extract(bam_file, CURRENT_TMPDIR)
        outer.extract(bai_file, CURRENT_TMPDIR)

    bam_path = os.path.join(CURRENT_TMPDIR, bam_file)
    CURRENT_BAM = bam_path

    launcher = find_igv_launcher()

    if not launcher:
        sg.popup("Impossible de trouver IGV.")
        return

    print("LANCEMENT IGV AVEC :", launcher)
    subprocess.Popen([launcher], cwd=os.path.dirname(launcher))

    # On laisse IGV démarrer
    time.sleep(2)

    # Charger le BAM + aller à la région
    igv_load(bam_path)
    igv_goto(chrom, start, end)

    sg.popup("IGV a été lancé.")
