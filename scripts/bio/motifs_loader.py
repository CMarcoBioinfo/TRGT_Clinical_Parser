import yaml
import os

def load_motif_data():
    """Charge motifs_data.yaml et retourne un dictionnaire structuré."""
    base_dir = os.path.dirname(__file__)
    yaml_path = os.path.join(base_dir, "motifs_data.yaml")

    with open(yaml_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    # Variables explicites
    pathologic_motifs_raw = data["patho_motifs"]
    uncertain_motifs_raw = data["uncertain_motifs"]
    orientation_map = data["orientation"]
    icons = data["icons"]

    # Conversion en sets pour un accès rapide
    pathologic_motifs = {
        trid: set(motif_list)
        for trid, motif_list in pathologic_motifs_raw.items()
    }

    uncertain_motifs = {
        trid: set(motif_list)
        for trid, motif_list in uncertain_motifs_raw.items()
    }

    return {
        "patho_motifs": pathologic_motifs,
        "uncertain_motifs": uncertain_motifs,
        "orientation": orientation_map,
        "icons": icons,
    }
