import os
import zipfile
import tempfile
import subprocess
import PySimpleGUI as sg

SPANNING_ARCHIVE_SUFFIX = "spanning_BAM.zip"


def find_spanning_bam(zip_path, sample_name):
    if not os.path.exists(zip_path):
        return None

    with zipfile.ZipFile(zip_path, "r") as z:
        names = z.namelist()

    # On cherche un fichier qui commence par sample_name et finit par .bam
    for n in names:
        if n.startswith(sample_name) and n.endswith(".bam"):
            bam = n
            bai = bam + ".bai"
            if bai in names:
                return zip_path, bam, bai

    return None



def get_available_spanning_bam(base_dir, analyse_prefix, sample_name):
    """
    Wrapper simple : construit le chemin du ZIP et appelle find_spanning_bam().
    Permet de garder orchestrator et main propres.
    """
    zip_path = os.path.join(base_dir, f"{analyse_prefix}{SPANNING_ARCHIVE_SUFFIX}")
    return find_spanning_bam(zip_path, sample_name)


def open_igv(zip_path, bam_file, bai_file, chrom, start, end):
    """
    Extraction + ouverture IGV
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        with zipfile.ZipFile(zip_path, "r") as outer:
            outer.extract(bam_file, tmpdir)
            outer.extract(bai_file, tmpdir)

        bam_path = os.path.join(tmpdir, bam_file)
        region = f"{chrom}:{start}-{end}"

        for cmd in ["igv.bat", "igv.exe", "igv.sh", "igv"]:
            try:
                subprocess.Popen([cmd, bam_path, region])
                sg.popup("IGV a été lancé.")
                return
            except FileNotFoundError:
                continue
            except Exception as e:
                sg.popup(f"Erreur lors du lancement d'IGV :\n{e}")
                return

        sg.popup("Impossible de lancer IGV.\nIGV n'est pas installé ou pas dans le PATH.")
