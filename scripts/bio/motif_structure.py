from scripts.bio.clinical_thresholds_loader import get_motif_properties
from scripts.ui.formatters import parse_motif_counts, parse_segmentation
from scripts.core.motif_utils import extract_group_motifs, compute_interruption_bp, compute_m

def build_motif(trid, repetitions, interruptions, segmentation, thresholds_data):
    """
    Prépare les données et lance la construction du motif selon le locus.
    """
    if not trid or not repetitions or not segmentation:
        return None

    #      Parsing propre
    list_repetitions = parse_motif_counts(repetitions)
    list_interruptions = parse_motif_counts(interruptions) if interruptions else []
    list_segmentation = parse_segmentation(segmentation)
                             
    motif_props = get_motif_properties(trid, thresholds_data)

    if trid == "FRDA_FXN":
        return repetitions

    if trid == "CANVAS_RFC1":
        return repetitions

    else:
        return build_simple_motif(list_repetitions, list_interruptions, list_segmentation, motif_props)


def build_simple_motif(repetitions, interruptions, segmentation, motif_props):
    """ Construit le motif TRGT final pour les loci simples.
    - repetitions : [('CAG', 27), ('CAA', 3)]
    - interruptions : [('CAT', 2), ('T', 2)]
    - segmentation : [('CAG', 2,5), ('T',5,6), ...]
    - motif_props : dict du locus """
    
    motif_groups = motif_props["motif_groups"][0]
    if not motif_groups:
        return None
    motif_len = len(motif_groups[0])

    groups, others = extract_group_motifs(repetitions, interruptions, motif_groups)
    # Construction de la partie répétition pure
    names = "+".join(m for m, _ in groups)
    counts = "+".join(str(c) for _, c in groups)
    
    i = compute_interruption_bp(segmentation, motif_groups)
    m = compute_m(i, motif_len)
    if m > 0:
        counts = f"{counts}+{m}m"
    if i > 0:
        counts = f"{counts},{i}i"
        
    if others:
        others_str = "_" + "_".join(f"{m}({c})" for m, c in others)
    else: 
        others_str = ""

    rep_string = f"{names}({counts}){others_str}"
    return rep_string
