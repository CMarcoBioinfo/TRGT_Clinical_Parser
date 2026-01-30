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
    """
    Retourne le nombre de répétitions
    """
    motif_groups = motif_props["motif_groups"][0]
    if not motif_groups:
        return None

    # motif principal patho
    block = extract_main_block(repetitions, motif_groups)
    if block == -1:
        return None

    # Contenu du motif avant la virgule
    inside = block.split(",", 1)[0].split("(", 1)[1]

    # enlever les ')' pour gérer les cas simples "8)"
    inside = inside.replace(")", "")

    number = inside.replace("+", " ").split()

    total = 0
    for n in number:
        # ignorer motifs longs "(GAAA" "(49GAAGAAA"
        if "(" in n:
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
        raw_motif = block.split("(", 1)[0]

        # on garde uniquement lettres et '+', on vire les icônes type "🔴"
        motif = "".join(c for c in raw_motif if c.isalpha() or c == "+")

        submotifs = motif.split("+")

        for m in submotifs:
            if m in motif_groups:
                return block

    return 0
