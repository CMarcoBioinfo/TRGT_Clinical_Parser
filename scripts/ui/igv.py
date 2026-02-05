import os
import zipfile
import tempfile
import subprocess
import PySimpleGUI as sg

SPANNING_ARCHIVE_SUFFIX = "spanning_BAM.zip"


def find_spanning_bam(zip_path, sample_internal):
    """
    Reconstruit le nom EXACT du BAM TRGT à partir du VCF interne.
    """
    if not os.path.exists(zip_path):
        return None

    # On enlève juste .vcf ou .vcf.gz
    prefix = sample_internal.replace(".vcf.gz", "").replace(".vcf", "")

    bam = f"{prefix}.sorted.spanning.bam"
    bai = f"{bam}.bai"

    with zipfile.ZipFile(zip_path, "r") as z:
        names = z.namelist()
        if bam in names and bai in names:
            return zip_path, bam, bai

    return None


def get_available_spanning_bam(base_dir, analyse_prefix, sample_internal):
    """
    Wrapper simple : construit le chemin du ZIP et appelle find_spanning_bam().
    Permet de garder main.py propre.
    """
    zip_path = os.path.join(base_dir, f"{analyse_prefix}{SPANNING_ARCHIVE_SUFFIX}")
    return find_spanning_bam(zip_path, sample_internal)


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
