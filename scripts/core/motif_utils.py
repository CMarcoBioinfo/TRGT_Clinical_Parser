def extract_group_motifs(repetitions, interruptions, motif_group):
    """
    Sépare et trie les motifs appartenant au motif_group
    de ceux qui n'en font pas partie.
    """

    # Motifs du groupe
    group_reps = [(m, c) for m, c in repetitions if m in motif_group]
    group_inters = [(m, c) for m, c in interruptions if m in motif_group]

    # Motifs hors groupe
    other_reps = [(m, c) for m, c in repetitions if m not in motif_group]
    
    # Fusion + tri décroissant par count
    groups = sorted(group_reps + group_inters, key=lambda x: x[1], reverse=True)
    others = sorted(other_reps, key=lambda x: x[1], reverse=True)

    return groups, others


def compute_interruption_bp(segmentation, motif_group):
    """
    Calcule la taille totale des interruptions internes (i) en bp.
    """
    interruption_bp = 0

    for motif, start, end in segmentation:
        if motif not in motif_group:
            interruption_bp += (end - start)

    return interruption_bp


def compute_m(interruption_bp, motif_len):
    """
    Calcule m = nombre de motifs compensés.
    """
    if motif_len <= 0:
        return 0
    return interruption_bp // motif_len
