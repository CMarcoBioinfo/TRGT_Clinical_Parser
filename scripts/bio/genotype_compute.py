from scripts.bio.clinical_thresholds_loader import get_motif_properties


def build_genotype(trid, repetitions, thresholds_data):
    """
    Prépare les doénnes et lance le calcul de genotype
    """
    if not trid or not repetitions:
        return None

    motif_props = get_motif_properties(trid, thresholds_data)

    if trid == "CANVAS_RFC1":
        return compute_canvas_genotype(repetitions, motif_props)

    return compute_genotype(repetitions, motif_props)


def compute_genotype(repetitions, motif_props):
    motif_groups = motif_props["motif_groups"][0]
    if not motif_groups:
        return None

    block = extract_main_block(repetitions, motif_groups)
    if block in (None, -1):
        return None

    try:
        inside = block.split(",", 1)[0].split("(", 1)[1]
    except Exception:
        return None

    inside = inside.replace(")", "")
    number = inside.replace("+", " ").split()

    total = 0
    for n in number:

        if "(" in n:
            continue

        if n.endswith("i") and n[:-1].isdigit():
            continue

        if n.endswith("m") and n[:-1].isdigit():
            total += int(n[:-1])
            continue

        if n.isdigit():
            total += int(n)
            continue

        if any(c.isalpha() for c in n):
            continue

    return total


def compute_canvas_genotype(repetitions, motif_props):
    """
    Pour CANVAS : on prend le motif majoritaire et son nombre.
    """
    blocks = repetitions.split("_")

    # extraire tous les motifs pathogènes possibles
    patho_motifs = motif_props["pathogenic_motifs"]

    best_motif = None
    best_count = -1

    for block in blocks:
        # block = "AAGGG(620)" ou "AAAAG(12)"
        if "(" not in block:
            continue

        motif, rest = block.split("(", 1)
        motif = motif.strip()
        count = rest.split(")", 1)[0]

        if not count.isdigit():
            continue

        count = int(count)

        # on garde le motif majoritaire
        if count > best_count:
            best_count = count
            best_motif = motif

    if best_motif is None:
        return None
        
    icon_patho = "\U0001F534" if best_motif in patho_motifs else ""
        
    return f"{best_count} ({icon_patho}{best_motif})"


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
