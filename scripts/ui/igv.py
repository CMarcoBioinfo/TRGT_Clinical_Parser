import os
import zipfile
import tempfile
import os
import zipfile
import tempfile
import subprocess
import PySimpleGUI as sg

SPANNING_ARCHIVE_SUFFIX = "spanning_BAM.zip"


def find_spanning_bam(zip_path, sample_internal):
    if not os.path.exists(zip_path):
        return None

    prefix = sample_internal.replace(".vcf.gz", "").replace(".vcf", "")
    bam = f"{prefix}.sorted.spanning.bam"
    bai = f"{bam}.bai"

    with zipfile.ZipFile(zip_path, "r") as z:
        names = z.namelist()
        if bam in names and bai in names:
            return zip_path, bam, bai

    return None


def open_igv(zip_path, bam_file, bai_file, chrom, start, end):
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
