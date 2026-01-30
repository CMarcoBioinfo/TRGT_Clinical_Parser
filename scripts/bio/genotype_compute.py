from scripts.bio.clinical_thresholds_loader import get_motif_properties


def build_genotype(trid, repetitions, thresholds_data):
    """
    Prépare les doénnes et lance le calcul de genotype
    """
    if not trid or not repetitions:
        return None

    motif_props = get_motif_properties(trid, thresholds_data)

    if trid == "CANVAS_RFC1":
        return "complexe"

    return compute_genotype(repetitions, motif_props)


def compute_genotype(repetitions, motif_props):
    motif_groups = motif_props["motif_groups"][0]
    if not motif_groups:
        return None

    block = extract_main_block(repetitions, motif_groups)
    if block == -1:
        return None

    inside = block.split(",", 1)[0].split("(", 1)[1]

    # enlever les ")" pour éviter de perdre "2m)"
    inside = inside.replace(")", "")

    number = inside.replace("+", " ").split()

    total = 0
    for n in number:

        # motifs longs "(GAAA" "(49GAAGAAA"
        if "(" in n:
            continue

        # interruptions "2i"
        if n.endswith("i") and n[:-1].isdigit():
            continue

        # résidus "2m"
        if n.endswith("m") and n[:-1].isdigit():
            total += int(n[:-1])
            continue

        # nombres simples
        if n.isdigit():
            total += int(n)
            continue

        # ignorer tout le reste
        if any(c.isalpha() for c in n):
            continue

    return total


def extract_main_block(repetitions, motif_groups):
    """
    Retourne le bloc contenant un des motifs principaux
    """
    blocks = repetitions.split("_")

    for block in blocks:
        raw_motif = block.split("(", 1)[0]

        # on garde uniquement lettres et '+', on vire les icônes type "🔴"
        motif = "".join(c for c in raw_motif if c.isalpha() or c == "+")

        submotifs = motif.split("+")

        for m in submotifs:
            if m in motif_groups:
                return block

    return 0
