import os
import zipfile
import tempfile
import subprocess
import PySimpleGUI as sg

SPANNING_ARCHIVE_SUFFIX = "spanning_BAM.zip"


def extract_trgt_prefix(sample_internal):
    """
    Extrait le préfixe TRGT à partir du chemin interne du VCF.
    Gère .vcf, .vcf.gz, .trgt.vcf, .trgt.vcf.gz
    Exemple : folder/24071.trgt.vcf.gz -> 24071.trgt
    """
    base = os.path.basename(sample_internal)

    # enlever .gz
    if base.endswith(".gz"):
        base = base[:-3]

    # enlever .trgt.vcf
    if base.endswith(".trgt.vcf"):
        return base.replace(".trgt.vcf", "")

    # enlever .vcf
    if base.endswith(".vcf"):
        return base.replace(".vcf", "")

    return base


def find_spanning_bam(zip_path, sample_internal):
    """
    Version 'comme plots' : on reconstruit le nom exact du BAM TRGT.
    Aucun pattern matching, aucun startswith, aucun in.
    """
    if not os.path.exists(zip_path):
        return None

    # extraire le nom TRGT du sample
    sample_trgt = extract_trgt_prefix(sample_internal)

    # reconstruire le nom EXACT du BAM TRGT
    bam = f"{sample_trgt}.trgt.sorted.spanning.bam"
    bai = f"{bam}.bai"

    with zipfile.ZipFile(zip_path, "r") as z:
        names = z.namelist()

        if bam in names and bai in names:
            return bam, bai

    return None


def get_available_spanning_bam(base_dir, analyse_prefix, sample_internal):
    """
    Identique à plots : on reconstruit le nom exact du fichier interne.
    """
    zip_path = os.path.join(base_dir, f"{analyse_prefix}{SPANNING_ARCHIVE_SUFFIX}")
    return find_spanning_bam(zip_path, sample_internal)


def open_igv(zip_path, bam_file, bai_file, chrom, start, end):
    """
    Comme open_svg(), mais avec un seul niveau :
    - ouvrir le ZIP externe
    - extraire le fichier interne
    - l’ouvrir dans IGV
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
