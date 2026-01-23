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
    inside = p.split("(")[1].split(")")[0]

    if "+" in inside:
        pure, inter = inside.split("+")
        inter = inter.replace("i", "")
        return int(pure) + int(inter)
    else:
        return int(inside)


def sort_repeats(value):
    if not value or "_" not in value:
        return value

    parts = value.split("_")

    # tri décroissant sur le nombre total de répétitions
    parts_sorted = sorted(parts, key=total_reps, reverse=True)

    return "_".join(parts_sorted)
