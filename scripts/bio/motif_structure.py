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
        return build_fxn_motif(list_repetitions, list_interruptions, list_segmentation, motif_props)


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
    counts = " + ".join(str(c) for _, c in groups)
    
    i_bp, i_count = compute_interruption_bp(segmentation, motif_groups)
    m = compute_m(i_bp, motif_len)
    if m > 0:
        counts = f"{counts} + {m}m"
    if i_count > 0:
        counts = f"{counts}, {i_count}i"
        
    if others:
        others_str = "_" + "_".join(f"{m}({c})" for m, c in others)
    else: 
        others_str = ""

    rep_string = f"{names}({counts}){others_str}"
    return rep_string


def build_fxn_motif(repetitions, interruptions, segmentation, motif_props):
    """
    Construit la notation FXN enrichie :
    GAA(total + units_GAAA (GAAA) + units_GAAGAAA (nGAAGAAA GAAGAAA) + m, i)_others
    """

    # Définition des motifs FXN
    main = "GAA"
    long1 = "GAAA"      # 4 bp → 1 unité
    long2 = "GAAGAAA"   # 7 bp → 2 unités

    motif_groups = motif_props["motif_groups"][0]
    if not motif_groups:
        return None

    motif_len = len(main)  # = 3 bp

    # 1) Extraction des motifs du groupe
    groups, others = extract_group_motifs(repetitions, interruptions, motif_groups)

    # Comptages initiaux
    n_GAA = 0
    n_GAAA = 0
    n_GAAGAAA = 0

    for motif, count in groups:
        if motif == main:
            n_GAA = count
        elif motif == long1:
            n_GAAA = count
        elif motif == long2:
            n_GAAGAAA = count

    # 2) Unités longues
    units_GAAA = n_GAAA * 1
    units_GAAGAAA = n_GAAGAAA * 2
    units_long = units_GAAA + units_GAAGAAA

    # 3) bp des motifs longs
    bp_GAAA = n_GAAA * len(long1)
    bp_GAAGAAA = n_GAAGAAA * len(long2)

    # 4) Interruptions réelles
    i_bp, i_count = compute_interruption_bp(segmentation, motif_groups)

    # 5) Total bp pour m = interruptions + motifs longs
    total_bp_for_m = i_bp + bp_GAAA + bp_GAAGAAA

    # 6) m total (en unités)
    m_total = compute_m(total_bp_for_m, motif_len)

    # 7) m résiduel (on retire les unités longues déjà comptées)
    m = m_total - units_long
    if m < 0:
        m = 0

    # 8) Total final en unités
    total_units = n_GAA + units_long + m

    # 9) Construction de la notation enrichie
    parts = [str(total_units)]

    if n_GAAA > 0:
        parts.append(f" + {units_GAAA} ({long1})")

    if n_GAAGAAA > 0:
        parts.append(f" + {units_GAAGAAA} ({n_GAAGAAA}{long2})")

    if m > 0:
        parts.append(f" + {m}m")

    counts = "".join(parts)

    if i_count > 0:
        counts += f", {i_count}i"

    # 10) Ajout des autres motifs
    if others:
        others_str = "_" + "_".join(f"{motif}({count})" for motif, count in others)
    else:
        others_str = ""

    rep_string = f"{main}({counts}){others_str}"
    return rep_string
