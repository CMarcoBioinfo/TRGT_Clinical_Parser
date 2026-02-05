import os
import zipfile
import tempfile
import subprocess
import PySimpleGUI as sg

SPANNING_ARCHIVE_SUFFIX = "spanning_BAM.zip"

def find_spanning_bam(zip_path):
    """
    Trouve automatiquement le BAM TRGT dans le ZIP,
    sans dépendre du sample_name.
    """

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

    # On cherche n'importe quel fichier TRGT spanning
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


def get_available_spanning_bam(base_dir, analyse_prefix, sample_name=None):
    """
    sample_name n'est plus utilisé.
    """
    zip_path = os.path.join(base_dir, f"{analyse_prefix}spanning_BAM.zip")
    print("\n=== DEBUG get_available_spanning_bam ===")
    print("BASE DIR =", base_dir)
    print("ANALYSE PREFIX =", analyse_prefix)
    print("ZIP CONSTRUIT =", zip_path)

    return find_spanning_bam(zip_path)


def open_igv(zip_path, bam_file, bai_file, chrom, start, end):
    """
    Extraction + ouverture IGV
    """

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
        print("Commande IGV testée :")

        for cmd in ["igv.bat", "igv.exe", "igv.sh", "igv"]:
            print(" -", cmd)
            try:
                subprocess.Popen([cmd, bam_path, region])
                print("IGV LANCÉ ✔")
                sg.popup("IGV a été lancé.")
                return
            except FileNotFoundError:
                continue
            except Exception as e:
                print("ERREUR IGV :", e)
                sg.popup(f"Erreur lors du lancement d'IGV :\n{e}")
                return

        print("IGV NON TROUVÉ ✘")
        sg.popup("Impossible de lancer IGV.\nIGV n'est pas installé ou pas dans le PATH.")

