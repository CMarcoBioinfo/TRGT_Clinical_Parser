def parse_motif_counts(m: str):
    """
    Transforme 'CAG(2)_CAA(3)' en [('CAG', 2), ('CAA', 3)].
    """
    if not m:
        return []

    result = []
    parts = m.split("_")

    for part in parts:
        i = part.index("(")
        motif = part[:i]
        count = int(part[i+1:-1])  # enlève "(" et ")"
        result.append((motif, count))

    return result



def parse_segmentation(seg: str):
    """
    Transforme 'CAG(2-5)_T_CAG(6-9)_CAT' en liste (motif, start, end).
    """
    parts = seg.split("_")
    segments = []
    current_pos = None

    for part in parts:
        if "(" in part:
            motif, coords = part.split("(")
            coords = coords[:-1]  # enlever ")"
            start, end = map(int, coords.split("-"))
            segments.append((motif, start, end))
            current_pos = end
        else:
            motif = part
            motif_len = len(motif)
            start = current_pos
            end = current_pos + motif_len
            segments.append((motif, start, end))
            current_pos = end

    return segments
