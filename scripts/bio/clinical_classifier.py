from scripts.bio.clinical_thresholds_loader import get_locus_config

def classify_allele(trid, genotype, interruptions, thresholds_data):
    """
    Classification clinique d'un allèle selon :
    - les règles structurelles (structure_rules)
    - les seuils (thresholds)
    - les interruptions TRGT biologiques (pas les 'i' de la répétition clinique)

    Paramètres :
        trid : nom du locus (ex: "SCA1_ATXN1")
        genotype : nombre total de répétitions (int)
        interruptions : liste de motifs TRGT biologiques (ex: ["CAT(2)", "CAA(1)"])
        thresholds_data : dictionnaire YAML chargé

    Retour :
        string : normal / intermediate / premutation / pathogenic_complete / etc.
    """

    if genotype is None:
        return None

    locus = get_locus_config(trid, thresholds_data)
    thresholds = locus.get("thresholds", {})
    rules = locus.get("structure_rules", [])

    has_interruptions = bool(interruptions)

    # ---------------------------------------------------------
    # 1) APPLICATION DES RÈGLES STRUCTURELLES (si présentes)
    # ---------------------------------------------------------
    for rule in rules:
        cond = rule.get("conditions", {})

        # repeat_range
        rr = cond.get("repeat_range")
        if rr:
            low, high = rr
            if genotype < low:
                continue
            if high is not None and genotype > high:
                continue

        # interruptions: true/false
        if "interruptions" in cond:
            if cond["interruptions"] != has_interruptions:
                continue

        # interruption_type (FXN)
        if "interruption_type" in cond:
            if not interruptions:
                continue

            motifs = [m.split("(")[0] for m in interruptions]

            if cond["interruption_type"] == "triplet":
                if not all(len(m) == 3 for m in motifs):
                    continue
            else:  # nontriplet
                if not any(len(m) != 3 for m in motifs):
                    continue

        # Si toutes les conditions matchent → classification trouvée
        return rule["classification"]

    # ---------------------------------------------------------
    # 2) APPLICATION DES SEUILS SIMPLES
    # ---------------------------------------------------------
    for label, rng in thresholds.items():
        low, high = rng
        if genotype >= low and (high is None or genotype <= high):
            return label

    return "unclassified"
