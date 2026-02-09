from scripts.bio.clinical_thresholds_loader import get_locus_config


# -------------------------
# FAMILLES DE LOCI
# -------------------------

SIMPLE_LOCI = {
    "SCA2_ATXN2", "SCA3_ATXN3", "SCA6_CACNA1A",
    "SCA7_ATXN7", "SCA17_TBP", "SCA36_NOP56", "FTDALS1_C9orf72",
    "FXS_FMR1", "OPDM1_LRP12", "FRDA_FXN"
}

STRUCTURAL_LOCI = {
    "SCA1_ATXN1", "SCA27B_FGF14"
}

MOTIF_DEPENDENT_LOCI = {
    "CANVAS_RFC1"
}

# -------------------------
# CLASSIFICATION PRINCIPALE
# -------------------------

def classify_allele(trid, genotype, interruptions, thresholds_data):
    """
    Classification clinique d'un allèle TRGT.
    """

    if genotype is None:
        return None

    locus = get_locus_config(trid, thresholds_data)

    # 1) Cas simples : seuils uniquement
    if trid in SIMPLE_LOCI:
        return classify_simple(genotype, locus["thresholds"])

    # 2) Cas structurels simples : interruptions influencent la classification
    if trid in STRUCTURAL_LOCI:
        return classify_structural(genotype, interruptions, locus)

    # 3) Cas structurel avancé : FXN
    if trid in ADVANCED_STRUCTURAL:
        return classify_fxn(genotype, interruptions, locus)

    # 4) Cas motif-dépendant : CANVAS
    if trid in MOTIF_DEPENDENT_LOCI:
        return classify_canvas(genotype, locus)

    # 4) RFC1 sera ajouté plus tard
    return "unclassified"


# -------------------------
# FAMILLE A : SEUILS SIMPLES
# -------------------------

def classify_simple(genotype, thresholds):
    for label, (low, high) in thresholds.items():
        if genotype >= low and (high is None or genotype <= high):
            return label
    return "unclassified"


# -------------------------
# FAMILLE B : STRUCTURAL (SCA1, FGF14)
# -------------------------

def classify_structural(genotype, interruptions, locus):
    rules = locus.get("structure_rules", [])
    has_interruptions = bool(interruptions)

    for rule in rules:
        cond = rule["conditions"]

        rr = cond.get("repeat_range")
        if rr:
            low, high = rr
            if genotype < low:
                continue
            if high is not None and genotype > high:
                continue

        if "interruptions" in cond:
            if cond["interruptions"] != has_interruptions:
                continue

        # classification est dans cond, pas dans rule
        return cond["classification"]

    return classify_simple(genotype, locus["thresholds"])


# -------------------------------------
# FAMILLE C : CANVAS (Motif dependance)
# -------------------------------------

def classify_canvas(genotype, locus):
    """
    Classification clinique pour CANVAS :
    - génotype = "620 (AAGGG)"
    - on extrait le motif et le nombre
    - on applique le seuil correspondant au motif
    """

    if genotype is None:
        return None

    # exemple : "620 (AAGGG)"
    parts = genotype.split()
    if len(parts) < 2:
        return None

    # nombre
    try:
        count = int(parts[0])
    except:
        return None

    # motif entre parenthèses
    motif = parts[1].strip("()")
    motif = motif.lstrip("\U0001F534")

    thresholds = locus["thresholds"]

    # si le motif a un seuil dédié
    if motif in thresholds:
        low, high = thresholds[motif]["pathogenic"]
        if count >= low:
            return "pathogenic"
        else:
            return "normal"

    # sinon → motif non pathogène
    return "normal"
