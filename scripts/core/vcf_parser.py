# parse_vcf.py
import zipfile

# Dictionnaire TRID -> gène (issu de ton BED)
TRID_TO_GENE = {
    "SCA1_ATXN1": "ATXN1",
    "SCA2_ATXN2": "ATXN2",
    "SCA3_ATXN3": "ATXN3",
    "SCA6_CACNA1A": "CACNA1A",
    "SCA7_ATXN7": "ATXN7",
    "SCA17_TBP": "TBP",
    "CANVAS_RFC1": "RFC1",
    "FRDA_FXN": "FXN",
    "FTDALS1_C9orf72": "C9orf72",
    "SCA27B_FGF14": "FGF14",
    "FXS_FMR1": "FMR1",
    "OPDM1_LRP12": "LRP12",
}


def parse_info(info_str):
    """Parse the INFO field of a VCF line."""
    info = {}
    for item in info_str.split(";"):
        if "=" in item:
            key, value = item.split("=", 1)
            info[key] = value
    return info


def split_two(value):
    """Sépare un champ 'x,y' en (x, y)."""
    if not value:
        return "", ""
    parts = value.split(",")
    if len(parts) == 1:
        return parts[0], ""
    return parts[0], parts[1]


def get_consensus_sequences(ref, alt, gt):
    """
    Retourne la séquence consensus des deux allèles selon GT.
    TRGT ajoute toujours une base de padding en tête : on la retire.
    """    
    a1, a2 = gt.split("/")

    alt_list = [] if alt == "." else alt.split(",")

    def allele_seq(a):
        idx = int(a)

        # Allèle 0 = REF
        if idx == 0:
            seq = ref
        else:
            if not alt_list:
                seq = ref
            else:
                seq = alt_list[idx - 1]

        # TRGT : toujours une base de padding en tête → on l'enlève
        return seq[1:] if len(seq) > 1 else ""

    return allele_seq(a1), allele_seq(a2)



def parse_vcf_from_zip(zip_path, vcf_filename, selected_trids):
    """Parse un VCF TRGT dans un ZIP et renvoie une liste de dictionnaires."""
    results = []

    with zipfile.ZipFile(zip_path, "r") as z:
        with z.open(vcf_filename) as f:
            for raw in f:
                line = raw.decode("utf-8").strip()

                # Ignorer les lignes d'en-tête
                if line.startswith("#"):
                    continue

                cols = line.split("\t")
                chrom, pos, vid, ref, alt, qual, flt, info_str, fmt, sample_data = cols
                
                info = parse_info(info_str)
                trid = info.get("TRID")

                # Filtrer sur les maladies sélectionnées
                if trid not in selected_trids:
                    continue
                    
                # Coordonnées du locus TRGT
                start = int(pos)
                end = int(info.get("END", start))
                
                # FORMAT fields
                fmt_fields = fmt.split(":")
                sample_fields = sample_data.split(":")
                data = dict(zip(fmt_fields, sample_fields))
                gt = data.get("GT")
            
                # Séparer les champs à deux allèles
                al1, al2 = split_two(data.get("AL"))
                allr1, allr2 = split_two(data.get("ALLR"))
                sd1, sd2 = split_two(data.get("SD"))
                mc1, mc2 = split_two(data.get("MC"))
                ms1, ms2 = split_two(data.get("MS"))
                ap1, ap2 = split_two(data.get("AP"))
                am1, am2 = split_two(data.get("AM"))
                cons1, cons2 = get_consensus_sequences(ref, alt, gt)

                # Ajouter la ligne formatée
                results.append({
                    "TRID": trid,
                    "Gene": TRID_TO_GENE.get(trid),
                    "Motifs": info.get("MOTIFS"),
                    "GT": gt,
                    
                    "CHROM": chrom,
                    "START": start,
                    "END": end,

                    # Champs séparés A1 / A2
                    "AL1": al1,
                    "AL2": al2,
                    "ALLR1": allr1,
                    "ALLR2": allr2,
                    "SD1": sd1,
                    "SD2": sd2,
                    "MC1": mc1,
                    "MC2": mc2,
                    "MS1": ms1,
                    "MS2": ms2,
                    "AP1": ap1,
                    "AP2": ap2,
                    "AM1": am1,
                    "AM2": am2,
                    "CONS1": cons1,
                    "CONS2": cons2,
                })

    return results
