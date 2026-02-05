import os
import zipfile
import tempfile
import subprocess
import shutil
import PySimpleGUI as sg

# Suffixe standard des archives TRGT contenant les spanning BAM
SPANNING_ARCHIVE_SUFFIX = "spanning_BAM.zip"


def igv_available():
    """Vérifie si IGV est installé sur le système."""
    return shutil.which("igv.sh") or shutil.which("igv.bat")


def find_spanning_bam(zip_path, sample):
    """
    Vérifie si {sample}.sorted.spanning.bam et .bai existent dans le ZIP.
    Exemple : patient1.trgt.sorted.spanning.bam
    """
    if not os.path.exists(zip_path):
        return None

    bam = f"{sample}.sorted.spanning.bam"
    bai = f"{sample}.sorted.spanning.bam.bai"

    with zipfile.ZipFile(zip_path, "r") as z:
        if bam in z.namelist() and bai in z.namelist():
            return bam, bai

    return None


def get_available_spanning_bam(base_dir, analyse_prefix, sample):
    """
    Retourne (zip_path, bam_file, bai_file) si le spanning BAM existe.
    """
    zip_path = os.path.join(base_dir, f"{analyse_prefix}{SPANNING_ARCHIVE_SUFFIX}")
    result = find_spanning_bam(zip_path, sample)

    if result:
        bam_file, bai_file = result
        return zip_path, bam_file, bai_file

    return None


def open_igv(zip_path, bam_file, bai_file, chrom, start, end):
    """
    Extrait le spanning BAM dans un dossier temporaire et ouvre IGV au locus donné.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        with zipfile.ZipFile(zip_path, "r") as z:
            z.extract(bam_file, tmpdir)
            z.extract(bai_file, tmpdir)

        bam_path = os.path.join(tmpdir, bam_file)
        region = f"{chrom}:{start}-{end}"

        igv_cmd = shutil.which("igv.sh") or shutil.which("igv.bat")
        if not igv_cmd:
            sg.popup("IGV n'est pas installé sur ce poste.")
            return

        subprocess.Popen([igv_cmd, bam_path, region])
        sg.popup("IGV a été lancé.")
