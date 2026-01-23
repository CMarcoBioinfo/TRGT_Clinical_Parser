def mark_motifs(value, trid):
    if not value:
        return value

    patho = PATHO_MOTIFS.get(trid, set())
    uncertain = UNCERTAIN_MOTIFS.get(trid, set())

    if "_" in value:
        parts = value.split("_")
        sep = "_"
    elif "," in value:
        parts = value.split(",")
        sep = ","
    else:
        parts = [value]
        sep = ""

    patho_list = []
    uncertain_list = []
    normal_list = []

    for p in parts:
        motif = p.split("(")[0]
        if motif in patho:
            patho_list.append(p)
        elif motif in uncertain:
            uncertain_list.append(p)
        else:
            normal_list.append(p)

    ordered = patho_list + uncertain_list + normal_list
    
    marked = []
    for p in ordered:
        motif = p.split("(")[0]
        if motif in patho:
            marked.append(f"{RED_DOT_ICON}{p}")
        elif motif in uncertain:
            marked.append(f"{UNCERTAIN_ICON}{p}")
        else:
            marked.append(p)
            
    return sep.join(marked)


def mark_segmentation(segmentation, trid):
    """
    Marquer les motifs de segmentation
    """
    if not segmentation:
        return segmentation

    patho = PATHO_MOTIFS.get(trid, set())
    uncertain = UNCERTAIN_MOTIFS.get(trid, set())

    parts = segmentation.split("_")
    marked = []

    for p in parts:
        motif = p.split("(")[0]

        if motif in patho:
            marked.append(f"{RED_DOT_ICON}{p}")
        elif motif in uncertain:
            marked.append(f"{UNCERTAIN_ICON}{p}")
        else:
            marked.append(p)

    return "_".join(marked)
