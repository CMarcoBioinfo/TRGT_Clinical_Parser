import os
import zipfile
import io
import webbrowser
import tempfile
import threading
import time


# Les suffixes des archives de plots
PLOT_ARCHIVES = {
    "Motifs allele": "_motifs_allele.zip",
    "Motifs waterfall": "_motifs_waterfall.zip",
    "Meth allele": "_meth_allele.zip",
    "Meth waterfall": "_meth_waterfall.zip"
}

def get_analysis_prefix(vcfs_zip):
    """
    Extrait le préfixe d'analyse à partir du fichier vcfs.zip
    Exemple : analysis-[multiple]-48-trgt_vcfs.zip -> analysis-[multiple]-48-trgt
    """
    base = os.path.basename(vcfs_zip)
    return base.replace("_vcfs.zip", "")

def find_svg(outer_zip, sample, specificity, trid):
    if not os.path.exists(outer_zip):
        return None
    with zipfile.ZipFile(outer_zip, "r") as outer:
        inner_name = f"{sample}_{specificity}.trvz_alleles.zip"
        if inner_name not in outer.namelist():
            return None
        with outer.open(inner_name) as inner_file:
            inner_bytes = inner_file.read()
            with zipfile.ZipFile(io.BytesIO(inner_bytes)) as inner:
                target = f"{trid}.trvz.svg"
                if target in inner.namelist():
                    return (inner_name, target)
    return None


def get_available_plots(base_dir, analyse_prefix, sample, trid):
    results = {}
    for label, suffix in PLOT_ARCHIVES.items():
        zip_path = os.path.join(base_dir, f"{analyse_prefix}{suffix}")
        specificity = suffix.replace(".zip", "").lstrip("_")
        internal = find_svg(zip_path, sample, specificity, trid)
        if internal:
            inner_zip, svg_file = internal
            results[label] = (zip_path, inner_zip, svg_file)
        else:
            results[label] = None
    return results
    

def open_svg(zip_path, inner_zip, svg_file):
    """
    Extrait un SVG dans un dossier temporaire caché, l'ouvre dans le navigateur,
    puis supprime le fichier après un délai.
    """
    with zipfile.ZipFile(zip_path, "r") as outer:
        with outer.open(inner_zip) as inner_file:
            inner_bytes = inner_file.read()
            with zipfile.ZipFile(io.BytesIO(inner_bytes)) as inner:
                svg_bytes = inner.read(svg_file)

                # Créer un dossier caché pour les fichiers temporaires
                tmp_dir = os.path.join(tempfile.gettempdir(), ".tmp_plots")
                os.makedirs(tmp_dir, exist_ok=True)

                tmp_path = os.path.join(tmp_dir, svg_file)
                with open(tmp_path, "wb") as f:
                    f.write(svg_bytes)

                # Ouvrir dans le navigateur
                webbrowser.open(f"file://{tmp_path}")

                # Supprimer automatiquement après un délai (ex: 30s)
                def cleanup(path):
                    time.sleep(30)
                    try:
                        os.remove(path)
                    except FileNotFoundError:
                        pass

                threading.Thread(target=cleanup, args=(tmp_path,), daemon=True).start()
