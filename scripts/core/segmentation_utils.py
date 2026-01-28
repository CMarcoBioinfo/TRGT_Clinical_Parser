def number_interruptions(interruption_seqs):
    """
    Compte combien de fois chaque séquence d'interruption apparaît.
    Exemple :
        ["TTG", "TTGTTG", "TTG"] -> "TTG(2)_TTGTTG(1)"
    """
    if not interruption_seqs:
        return ""

    nb_inter = {}

    for seq in interruption_seqs:
        nb_inter[seq] = nb_inter.get(seq, 0) + 1

    # Construction du résultat non trié (le tri sera fait par sort_repeats)
    return "_".join(f"{seq}({count})" for seq, count in nb_inter.items())


def remove_zero_repeats(value):
    if not value:
        return value

    parts = value.split("_")
    cleaned = []

    for p in parts:
        if "(" in p and ")" in p:
            rep = int(p.split("(")[1].split(")")[0])
            if rep == 0:
                continue
        cleaned.append(p)

    return "_".join(cleaned)


def total_reps(p):
    """
    Extrait le nombre total de répétitions d'un motif TRGT.
    Compatible avec :
        CAG(27)
        CAG(27+1)
        CAG(27+1,2)
        CAG(20+2+1,3)
    """
    inside = p.split("(")[1].split(")")[0]

    # On enlève la partie ",i" s'il y en a une
    if "," in inside:
        inside = inside.split(",")[0]

    # inside est maintenant du type "20+2+1"
    parts = inside.split("+")

    total = 0
    for part in parts:
        # sécurité : ignorer les trucs non numériques
        try:
            total += int(part)
        except ValueError:
            pass

    return total



def sort_repeats(value):
    if not value or "_" not in value:
        return value

    parts = value.split("_")

    # tri décroissant sur le nombre total de répétitions
    parts_sorted = sorted(parts, key=total_reps, reverse=True)

    return "_".join(parts_sorted)
