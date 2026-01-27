import yaml
import os

def load_clinical_thresholds():
    """
    Charge clinical_thresholds.yaml et retourne un dictionnaire brut.
    Aucun post-traitement n'est appliqué : chaque locus garde sa structure.
    """
    base_dir = os.path.dirname(__file__)
    yaml_path = os.path.join(base_dir, "clinical_thresholds.yaml")

    with open(yaml_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    return data


def get_locus_config(trid, thresholds_data=None):
    """
    Retourne la configuration clinique d'un locus donné (ex: 'SCA2_ATXN2').
    """
    
    if thresholds_data is None:
        thresholds_data = load_clinical_thresholds()

    if trid not in thresholds_data:
        raise KeyError(f"Locus '{trid}' introuvable dans clinical_thresholds.yaml")

    return thresholds_data[trid]


def get_thresholds(trid, thresholds_data=None):
    """
    Retourne uniquement le bloc 'thresholds' d'un locus.
    """
    locus = get_locus_config(trid, thresholds_data)
    return locus.get("thresholds", {})


def get_structure_rules(trid, thresholds_data=None):
    """
    Retourne les règles structurelles d'un locus (liste ou vide).
    """
    locus = get_locus_config(trid, thresholds_data)
    return locus.get("structure_rules", [])


def get_motif_properties(trid, thresholds_data=None):
    """
    Retourne le bloc motif_properties d'un locus.
    """
    locus = get_locus_config(trid, thresholds_data)
    return locus.get("motif_properties", {})
