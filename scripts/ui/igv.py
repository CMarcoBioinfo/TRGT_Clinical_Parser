import os
import zipfile
import tempfile
import subprocess
import PySimpleGUI as sg

SPANNING_ARCHIVE_SUFFIX = "spanning_BAM.zip"


def extract_trgt_prefix(sample_internal):
    """
    Extrait le préfixe TRGT à partir du chemin interne du VCF.
    Exemple : folder/patient1.trgt.vcf -> patient1.trgt
    """
    base = os.path.basename(sample_internal)
    if base.endswith(".trgt.vcf"):
        return base.replace(".trgt.vcf", "")
    if base.endswith(".vcf"):
        return base.replace(".vcf", "")
    return base


def find_spanning_bam(zip_path, trgt_prefix):
    """
    Trouve le BAM correspondant au sample TRGT.
    On cherche un fichier qui commence par le préfixe TRGT exact.
    """
    if not os.path.exists(zip_path):
        return None

    with zipfile.ZipFile(zip_path, "r") as z:
        names = z.namelist()

        for name in names:
            if name.startswith(trgt_prefix) and name.endswith(".sorted.spanning.bam"):
                bam = name
                bai = name + ".bai"
                if bai in names:
                    return bam, bai

    return None


def get_available_spanning_bam(base_dir, analyse_prefix, sample_internal):
    zip_path = os.path.join(base_dir, f"{analyse_prefix}{SPANNING_ARCHIVE_SUFFIX}")

    trgt_prefix = extract_trgt_prefix(sample_internal)

    result = find_spanning_bam(zip_path, trgt_prefix)

    if result:
        bam_file, bai_file = result
        return zip_path, bam_file, bai_file

    return None


def open_igv(zip_path, bam_file, bai_file, chrom, start, end):
    with tempfile.TemporaryDirectory() as tmpdir:
        with zipfile.ZipFile(zip_path, "r") as z:
            z.extract(bam_file, tmpdir)
            z.extract(bai_file, tmpdir)

        bam_path = os.path.join(tmpdir, bam_file)
        region = f"{chrom}:{start}-{end}"

        cmds = ["igv.bat", "igv.exe", "igv.sh", "igv"]

        for cmd in cmds:
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
