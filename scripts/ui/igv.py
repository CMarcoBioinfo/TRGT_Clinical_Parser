import os
import zipfile
import tempfile
import subprocess
import PySimpleGUI as sg
import shutil

PADDING = 75
CURRENT_TMPDIR = None


# ---------------------------------------------------------
#  Nettoyage forcé du dossier temporaire
# ---------------------------------------------------------
def cleanup_tmpdir_force():
    global CURRENT_TMPDIR
    if CURRENT_TMPDIR:
        shutil.rmtree(CURRENT_TMPDIR, ignore_errors=True)
        CURRENT_TMPDIR = None


# ---------------------------------------------------------
#  Trouver automatiquement IGV (toutes versions)
# ---------------------------------------------------------
def find_igv_launcher():
    base_dirs = [
        r"C:\Program Files",
        r"C:\Program Files (x86)",
    ]

    for base in base_dirs:
        try:
            for entry in os.listdir(base):
                if entry.lower().startswith("igv"):
                    launcher = os.path.join(base, entry, "igv.bat")
                    if os.path.exists(launcher):
                        return launcher
        except PermissionError:
            continue

    return None


# ---------------------------------------------------------
#  Trouver le spanning BAM correspondant au sample dans le ZIP
# ---------------------------------------------------------
def find_spanning_bam(zip_path, sample_name=None):
    """
    Retourne (zip_path, bam, bai) si un BAM correspondant au sample existe.
    Sinon retourne None proprement.
    """
    if not os.path.exists(zip_path):
        return None

    with zipfile.ZipFile(zip_path, "r") as z:
        names = z.namelist()

    if sample_name:
        sample_lower = sample_name.lower()
        for n in names:
            if n.endswith(".sorted.spanning.bam") and sample_lower in n.lower():
                bam = n
                bai = bam + ".bai"
                if bai in names:
                    return zip_path, bam, bai

    return None


# ---------------------------------------------------------
#  Trouver le BAM correspondant au sample dans le ZIP
# ---------------------------------------------------------
def find_bam(zip_path, sample_name=None):
    """
    Retourne (zip_path, bam, bai) si un BAM correspondant au sample existe.
    Sinon retourne None proprement.
    """
    if not os.path.exists(zip_path):
        return None

    with zipfile.ZipFile(zip_path, "r") as z:
        names = z.namelist()

    if sample_name:
        sample_lower = sample_name.lower()
        for n in names:
            if n.endswith(".pbmm2.repeats.bam") and sample_lower in n.lower():
                bam = n
                bai = bam + ".bai"
                if bai in names:
                    return zip_path, bam, bai

    return None
    
# ---------------------------------------------------------
#  Trouver automatiquement le ZIP contenant les spanning BAM
# ---------------------------------------------------------
def get_available_spanning_bam(base_dir, sample_name=None):
    """
    Trouve le ZIP contenant les spanning BAM,
    puis cherche le BAM correspondant au sample_name.
    """
    for f in os.listdir(base_dir):
        if "spanning" in f.lower() and f.lower().endswith(".zip"):
            zip_path = os.path.join(base_dir, f)
            return find_spanning_bam(zip_path, sample_name)

    return None


# ---------------------------------------------------------
#  Trouver automatiquement le ZIP contenant les spanning BAM
# ---------------------------------------------------------
def get_available_bam(base_dir, sample_name=None):
    """
    Trouve le ZIP contenant les spanning BAM,
    puis cherche le BAM correspondant au sample_name.
    """
    for f in os.listdir(base_dir):
        if "repeat_reads" in f.lower() and f.lower().endswith(".zip"):
            zip_path = os.path.join(base_dir, f)
            return find_bam(zip_path, sample_name)

    return None
    
def open_igv(spanning_zip_path=None, spanning_bam_file=None, spanning_bai_file=None, mapped_zip_path=None, mapped_bam_file=None, mapped_bai_file=None, chrom=None, start=None, end=None):
    # --- Vérification du locus ---
    if chrom is None or start is None or end is None:
        sg.popup("Aucun locus sélectionné.\nVeuillez sélectionner un locus avant d’ouvrir IGV.")
        return
        
    global CURRENT_TMPDIR

    # --- Préparation région ---
    start_padded = max(0, start - PADDING)
    end_padded = end + PADDING
    region = f"{chrom}:{start_padded}-{end_padded}"

    # --- Liste des BAM à ouvrir ---
    bam_list = []

    # --- Dossier temporaire ---
    CURRENT_TMPDIR = tempfile.mkdtemp()

    # ---------------------------------------------------------
    # 1) Extraction du spanning BAM si présent
    # ---------------------------------------------------------
    if spanning_zip_path and spanning_bam_file and spanning_bai_file:
        try:
            with zipfile.ZipFile(spanning_zip_path, "r") as z:
                z.extract(spanning_bam_file, CURRENT_TMPDIR)
                z.extract(spanning_bai_file, CURRENT_TMPDIR)

            spanning_bam_path = os.path.join(CURRENT_TMPDIR, spanning_bam_file)
            bam_list.append(spanning_bam_path)

        except Exception as e:
            sg.popup(f"Erreur extraction spanning BAM :\n{e}")

    # ---------------------------------------------------------
    # 2) Extraction du mapped BAM si présent
    # ---------------------------------------------------------
    if mapped_zip_path and mapped_bam_file and mapped_bai_file:
        try:
            with zipfile.ZipFile(mapped_zip_path, "r") as z:
                z.extract(mapped_bam_file, CURRENT_TMPDIR)
                z.extract(mapped_bai_file, CURRENT_TMPDIR)

            mapped_bam_path = os.path.join(CURRENT_TMPDIR, mapped_bam_file)
            bam_list.append(mapped_bam_path)

        except Exception as e:
            sg.popup(f"Erreur extraction mapped BAM :\n{e}")

    # ---------------------------------------------------------
    # 3) Si aucun BAM → on ne lance rien
    # ---------------------------------------------------------
    if not bam_list:
        sg.popup("Aucun BAM disponible pour IGV.")
        return

    # ---------------------------------------------------------
    # 4) Lancement IGV
    # ---------------------------------------------------------
    launcher = find_igv_launcher()
    print(launcher)
    if not launcher:
        sg.popup("IGV introuvable sur cette machine.")
        return

    try:
        subprocess.Popen(
            [launcher] + bam_list + ["--locus", region],
            cwd=os.path.dirname(launcher)
        )
        sg.popup("IGV a été lancé avec :\n" + "\n".join(bam_list))

    except Exception as e:
        sg.popup(f"Erreur lors du lancement d'IGV :\n{e}")
