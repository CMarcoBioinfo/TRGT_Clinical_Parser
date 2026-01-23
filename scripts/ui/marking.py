def mark_motifs(value, trid, patho_motifs, uncertain_motifs, icons):
    if not value:
        return value

    patho = patho_motifs.get(trid, set())
    uncertain = uncertain_motifs.get(trid, set())

    RED = icons.get("patho", "")
    UNC = icons.get("uncertain", "")

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
            marked.append(f"{RED}{p}")
        elif motif in uncertain:
            marked.append(f"{UNC}{p}")
        else:
            marked.append(p)

    return sep.join(marked)


def mark_segmentation(segmentation, trid, patho_motifs, uncertain_motifs, icons):
    if not segmentation:
        return segmentation

    patho = patho_motifs.get(trid, set())
    uncertain = uncertain_motifs.get(trid, set())

    RED = icons.get("patho", "")
    UNC = icons.get("uncertain", "")

    parts = segmentation.split("_")
    marked = []

    for p in parts:
        motif = p.split("(")[0]

        if motif in patho:
            marked.append(f"{RED}{p}")
        elif motif in uncertain:
            marked.append(f"{UNC}{p}")
        else:
            marked.append(p)

    return "_".join(marked)
