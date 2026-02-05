import os
import zipfile
import tempfile
import subprocess
import PySimpleGUI as sg
import glob

SPANNING_ARCHIVE_SUFFIX = "spanning_BAM.zip"


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
                    launcher = os.path.join(igv_dir, "igv_launcher.bat")

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
#  Extraction + lancement IGV
# ---------------------------------------------------------
def open_igv(zip_path, bam_file, bai_file, chrom, start, end):
    print("\n=== DEBUG open_igv ===")
    print("ZIP =", zip_path)
    print("BAM =", bam_file)
    print("BAI =", bai_file)
    print("REGION =", chrom, start, end)

    with tempfile.TemporaryDirectory() as tmpdir:
        with zipfile.ZipFile(zip_path, "r") as outer:
            print("Extraction dans :", tmpdir)
            outer.extract(bam_file, tmpdir)
            outer.extract(bai_file, tmpdir)

        bam_path = os.path.join(tmpdir, bam_file)
        region = f"{chrom}:{start}-{end}"

        print("BAM PATH =", bam_path)

        # Trouver IGV automatiquement
        launcher = find_igv_launcher()

        if launcher:
            print("LANCEMENT IGV AVEC :", launcher)
            try:
                subprocess.Popen([launcher, bam_path, region])
                print("IGV LANCÉ ✔")
                sg.popup("IGV a été lancé.")
                return
            except Exception as e:
                print("ERREUR IGV :", e)
                sg.popup(f"Erreur lors du lancement d'IGV :\n{e}")
                return

        print("IGV NON TROUVÉ ✘")
        sg.popup("Impossible de lancer IGV.\nIGV n'est pas installé ou pas détectable automatiquement.")


