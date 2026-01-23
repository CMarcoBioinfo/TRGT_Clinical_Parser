def combine_mc(motifs, mc):
    """Combine motifs et MC en motif(nb)."""
    if not motifs or not mc:
        return ""

    motif_list = motifs.split(",")   
    mc_list = mc.split("_")

    result = []
    for i in range(min(len(motif_list), len(mc_list))):
        result.append(f"{motif_list[i]}({mc_list[i]})")

    return "_".join(result)


def combine_ms(motifs, ms):
    """Combine motifs and MS into motif(interval)."""
    if not motifs or not ms:
        return ""

    motif_list = motifs.split(",")
    blocks = ms.split("_")

    result = []

    for block in blocks:
        if "(" not in block:
            continue

        idx_str, interval = block.split("(", 1)
        interval = interval.rstrip(")")
        idx = int(idx_str)

        motif = motif_list[idx]
        result.append(f"{motif}({interval})")

    return "_".join(result)
