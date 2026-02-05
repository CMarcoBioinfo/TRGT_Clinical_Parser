import os
import zipfile
import tempfile
import subprocess
import PySimpleGUI as sg

SPANNING_ARCHIVE_SUFFIX = "spanning_BAM.zip"


def find_spanning_bam(zip_path, sample):
    """
    Trouve automatiquement le BAM TRGT correspondant au sample,
    en appliquant la même logique que plots.py :
    - on ne devine rien
    - on parcourt le ZIP
    - on cherche un fichier qui commence par {sample}
      et finit par .sorted.spanning.bam
    """
    if not os.path.exists(zip_path):
        return None

    with zipfile.ZipFile(zip_path, "r") as z:
        for name in z.namelist():
            if name.startswith(sample) and name.endswith(".sorted.spanning.bam"):
                bam = name
                bai = name + ".bai"
                if bai in z.namelist():
                    return bam, bai
            
        print("DEBUG — sample recherché :", sample) 
        print("DEBUG — contenu du ZIP :", z.namelist())

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
    Extrait le spanning BAM dans un dossier temporaire et tente de lancer IGV.
    Si IGV n'est pas trouvé → message propre.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        # Extraction des fichiers
        with zipfile.ZipFile(zip_path, "r") as z:
            z.extract(bam_file, tmpdir)
            z.extract(bai_file, tmpdir)

        bam_path = os.path.join(tmpdir, bam_file)
        region = f"{chrom}:{start}-{end}"

        # Commandes possibles selon OS
        possible_cmds = [
            "igv.bat",   # Windows
            "igv.exe",   # Windows
            "igv.sh",    # Linux/Mac
            "igv"        # fallback
        ]

        # Essayer chaque commande
        for cmd in possible_cmds:
            try:
                subprocess.Popen([cmd, bam_path, region])
                sg.popup("IGV a été lancé.")
                return
            except FileNotFoundError:
                continue
            except Exception as e:
                sg.popup(f"Erreur lors du lancement d'IGV :\n{e}")
                return

        # Si aucune commande n'a fonctionné
        sg.popup(
            "Impossible de lancer IGV.\n\n"
            "IGV n'est pas installé ou n'est pas dans le PATH.\n"
            "Essayez d'ajouter IGV au PATH ou lancez-le manuellement."
        )
