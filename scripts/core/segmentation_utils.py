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
