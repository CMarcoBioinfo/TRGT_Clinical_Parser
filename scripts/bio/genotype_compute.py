def build_genotype(trid, repetitions, thresolds_data):
    """
    Prépare les doénnes et lance le calcul de genotype
    """
    if not trid or not repetitions or not segmentation:
        return None

    motif_props = get_motif_properties(trid, thresholds_data)

    if trid == "CANVAS_RFC":
        return "complexe"

    return compute_genotype(repetitions, motif_props)


def compute_genotype(repetitions, motif_props):
    """
    Retourne les nombre de répétition
    """
    motif_groups = motif_props["motif_groups"][0]
    if not motif_groups:
        return None

    # motif principal patho
    block = extract_main_block(repetitions, motif_groups)

    # Contenu du motif avant la virgule
    inside = block.split(",", 1)[0].split("(", 1)[1]
    number = inside.replace("+", " ").split()

    total = 0
    for n in number:
        # ignorer motifs longs "(GAAA)" "(49GAAGAAA)"
        if "(" in n or ")" in n:
            continue

        # ignorer "49GAAGAAA"
        if any(c.isalpha() for c in n):
            continue

        # cas "642"
        if n.isdigit():
            total += int(n)
            continue

        # cas "65m"
        if n.endswith("m") and n[:-1].isdigit():
            total += int(n[:-1])
            continue

    return total


def extract_main_block(repetitions, motif_groups):
    """
    Retourne le bloc contenant un des motifs principaux
    """
    blocks = repetitions.split("_")

    for block in blocks:
        motif = block.split("(", 1)[0]
        submotifs = motif.split("+")

        for m in submotifs:
            if m in motif_groups:
                return block

    return -1
