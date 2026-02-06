from scripts.bio.clinical_thresholds_loader import get_locus_config


# -------------------------
# FAMILLES DE LOCI
# -------------------------

SIMPLE_LOCI = {
    "SCA2_ATXN2", "SCA3_ATXN3", "SCA6_CACNA1A",
    "SCA7_ATXN7", "SCA17_TBP", "SCA36_NOP56", "FTDALS1_C9orf72",
    "FXS_FMR1", "OPDM1_LRP12"
}

STRUCTURAL_LOCI = {
    "SCA1_ATXN1", "SCA27B_FGF14"
}

ADVANCED_STRUCTURAL = {
    "FRDA_FXN"
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


# -------------------------
# FAMILLE C : FXN (structure_rules + interruption_type)
# -------------------------

def classify_fxn(genotype, interruptions, locus):
    rules = locus.get("structure_rules", [])

    if interruptions:
        motifs = [m.split("(")[0] for m in interruptions]
        all_triplet = all(len(m) == 3 for m in motifs)
        interruption_type = "triplet" if all_triplet else "nontriplet"
    else:
        interruption_type = None

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
            if cond["interruptions"] != bool(interruptions):
                continue

        if "interruption_type" in cond:
            if cond["interruption_type"] != interruption_type:
                continue

        # 🔴 ici la correction :
        return cond["classification"]

    return classify_simple(genotype, locus["thresholds"])
