def motif_interruptions(motif_str, segmentation):
    if not motif_str or not segmentation:
        return None

    # Vérifier qu'il n'y a qu'un seul motif
    nb_motifs = motif_str.split("_")
    if len(nb_motifs) != 1:
        return motif_str

    # Extraire motif et répétitions pures
    motif = motif_str.split("(")[0]
    repetitions = int(motif_str.split("(")[1].split(")")[0])

    # Extraire start et end depuis la segmentation
    list_seq = segmentation.split("_")
    start = int(list_seq[0].split("(")[1].split("-")[0])
    end = int(list_seq[-1].split("-")[1].split(")")[0])

    # Calcul du total
    L = len(motif)
    total = (end - start) / L
    interruptions = int(round(total - repetitions))

    # Si aucune interruption
    if interruptions == 0:
        return f"{motif}({repetitions})"

    # Sinon motif(pures + i i)
    return f"{motif}({repetitions}+{interruptions}i)"
