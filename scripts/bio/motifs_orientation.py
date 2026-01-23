def reverse_complement(seq):
    """
    Retourne le reverse-complement d'un motif TRGT.
    """
    seq = seq.upper()
    complement= {
        "A": "T",
        "T": "A",
        "C": "G",
        "G": "C",
        "N": "N"
    }
    return "".join(complement.get(base, "N") for base in reversed(seq))


def rc_motifs(motifs):
    if not motifs:
        return motifs
        
    parts = motifs.split(",")
    rc = []
    
    for m in parts:
        rc.append(reverse_complement(m))
        
    return ",".join(rc)


def rc_segmentation(seq, motifs_str):
    if not seq or not motifs_str:
        return ""

    # Liste TRGT (ordre original)
    motifs = motifs_str.split(",")

    # Liste triée pour matcher (mais on garde l’index TRGT)
    motifs_sorted = sorted(
        [(m, motifs.index(m)) for m in motifs],
        key=lambda x: len(x[0]),
        reverse=True
    )

    ms = []
    i = 0
    n = len(seq)

    while i < n:
        matched = False

        for motif, trgt_idx in motifs_sorted:
            m = len(motif)

            if seq.startswith(motif, i):
                start = i
                i += m

                while i < n and seq.startswith(motif, i):
                    i += m

                end = i
                ms.append((trgt_idx, start, end))
                matched = True
                break

        if not matched:
            i += 1

    if not ms:
        return ""

    return "_".join(f"{idx}({start}-{end})" for idx, start, end in ms)
