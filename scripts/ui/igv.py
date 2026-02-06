import os
import zipfile
import tempfile
import subprocess
import PySimpleGUI as sg
import shutil

SPANNING_ARCHIVE_SUFFIX = "spanning_BAM.zip"
PADDING = 100

CURRENT_TMPDIR = None


# ---------------------------------------------------------
#  Nettoyage forcé du dossier temporaire
# ---------------------------------------------------------
def cleanup_tmpdir_force():
    global CURRENT_TMPDIR
    if CURRENT_TMPDIR:
        print("Nettoyage forcé du dossier temporaire")
        shutil.rmtree(CURRENT_TMPDIR, ignore_errors=True)
        CURRENT_TMPDIR = None


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

    print("AUCUN igv_launcher.bat trouvé automatiquement.")
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

    for n in names:
        if n.endswith(".sorted.spanning.bam"):
            bam = n
            bai = bam + ".bai"
            if bai in names:
                return zip_path, bam, bai

    return None


# ---------------------------------------------------------
#  Trouver automatiquement le ZIP spanning_BAM.zip
# ---------------------------------------------------------
def get_available_spanning_bam(base_dir, analyse_prefix, sample_name=None):
    for f in os.listdir(base_dir):
        if "spanning" in f.lower() and f.lower().endswith(".zip"):
            zip_path = os.path.join(base_dir, f)
            return find_spanning_bam(zip_path)
    return None


# ---------------------------------------------------------
#  Extraction + lancement IGV (mode CLI, fiable)
# ---------------------------------------------------------
def open_igv(zip_path, bam_file, bai_file, chrom, start, end):
    global CURRENT_TMPDIR

    print("\n=== DEBUG open_igv ===")
    print("ZIP =", zip_path)
    print("BAM =", bam_file)
    print("BAI =", bai_file)
    print("REGION =", chrom, start, end)

    # Padding
    start_padded = max(0, start - PADDING)
    end_padded = end + PADDING
    region = f"{chrom}:{start_padded}-{end_padded}"

    # Nouveau dossier temporaire
    CURRENT_TMPDIR = tempfile.mkdtemp()
    print("Extraction dans :", CURRENT_TMPDIR)

    with zipfile.ZipFile(zip_path, "r") as outer:
        outer.extract(bam_file, CURRENT_TMPDIR)
        outer.extract(bai_file, CURRENT_TMPDIR)

    bam_path = os.path.join(CURRENT_TMPDIR, bam_file)
    print("BAM PATH =", bam_path)

    launcher = find_igv_launcher()

    if launcher:
        print("LANCEMENT IGV AVEC :", launcher)
        try:
            subprocess.Popen(
                [launcher, bam_path, region],
                cwd=os.path.dirname(launcher)
            )
            print("IGV LANCÉ ✔")
            sg.popup("IGV a été lancé.")
            return
        except Exception as e:
            print("ERREUR IGV :", e)
            sg.popup(f"Erreur lors du lancement d'IGV :\n{e}")
            return

    print("IGV NON TROUVÉ ✘")
    sg.popup("Impossible de lancer IGV.\nIGV n'est pas installé ou pas détectable automatiquement.")
