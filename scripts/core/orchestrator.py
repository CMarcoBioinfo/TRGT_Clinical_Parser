from scripts.core.vcf_parser import parse_vcf_from_zip
from scripts.core.segmentation_parser import combine_mc, combine_ms
from scripts.core.segmentation_utils import remove_zero_repeats, sort_repeats, number_interruptions
from scripts.core.segmentation_interruptions import find_interruptions, extract_interruption_sequences, segmentation_complete
from scripts.bio.motifs_orientation import reverse_complement, rc_motifs, rc_segmentation
from scripts.bio.motif_structure import build_motif
from scripts.bio.clinical_thresholds_loader import load_clinical_thresholds, get_motif_properties
from scripts.bio.motifs_loader import load_motif_data
from scripts.bio.genotype_compute import build_genotype
from scripts.bio.clinical_classifier import classify_allele
from scripts.ui.marking import mark_motifs, mark_segmentation
from scripts.ui.plots import get_available_plots
from scripts.ui.igv import get_available_spanning_bam


def process_orientation(r, orientation):
    """Gère l'orientation FW/RC."""
    trid = r["TRID"]
    stand = orientation.get(trid, "FW")

    if stand == "RC":
        motifs = rc_motifs(r["Motifs"])
        seq1 = reverse_complement(r["CONS1"])
        seq2 = reverse_complement(r["CONS2"])
        r["MS1"] = rc_segmentation(seq1, motifs)
        r["MS2"] = rc_segmentation(seq2, motifs)
    else:
        motifs = r["Motifs"]
        seq1 = r["CONS1"]
        seq2 = r["CONS2"]

    r["_motifs_used"] = motifs
    r["_seq1"] = seq1
    r["_seq2"] = seq2
    return r


def process_segmentation(r):
    """Combine MC/MS en répétitions et segmentation lisible.""" 
    motifs = r["_motifs_used"]
    
    r["Répétition1"] = combine_mc(motifs, r["MC1"])
    r["Répétition2"] = combine_mc(motifs, r["MC2"])
    r["Segmentation1"] = combine_ms(motifs, r["MS1"])
    r["Segmentation2"] = combine_ms(motifs, r["MS2"])
    
    return r


def process_repeats(r, thresholds_data):
    """Nettoyage et construction du motif TRGT final."""

    # --- Version brute (ancienne) ---
    rep1_raw = remove_zero_repeats(r["Répétition1"])
    rep2_raw = remove_zero_repeats(r["Répétition2"])

    # On les stocke pour les autres scripts
    r["RépétitionBrute1"] = rep1_raw
    r["RépétitionBrute2"] = rep2_raw

    # --- Choix segmentation selon interruptions ---
    seg1 = r["SegmentationComplete1"] if r.get("Interruptions1") not in (None, "", []) else r["Segmentation1"]
    seg2 = r["SegmentationComplete2"] if r.get("Interruptions2") not in (None, "", []) else r["Segmentation2"]

    # --- Version clinique (nouvelle logique TRGT) ---
    rep1_clin = build_motif(
        r["TRID"],
        rep1_raw,
        r.get("Interruptions1"),
        seg1,
        thresholds_data
    )

    rep2_clin = build_motif(
        r["TRID"],
        rep2_raw,
        r.get("Interruptions2"),
        seg2,
        thresholds_data
    )

    # On remplace les anciennes clés par la version clinique
    r["Répétition1"] = sort_repeats(rep1_clin)
    r["Répétition2"] = sort_repeats(rep2_clin)
    g1  = build_genotype(r["TRID"], r["Répétition1"], thresholds_data)
    g2 = build_genotype(r["TRID"], r["Répétition2"], thresholds_data)

    if g1 is not None and g2 is not None:
        r["Genotype"] = f"{g1} / {g2}"
    else:
        r["Genotype"] = None

    # Classification clinique
    c1 = classify_allele(r["TRID"], g1, r.get("Interruptions1"), thresholds_data)
    c2 = classify_allele(r["TRID"], g2, r.get("Interruptions2"), thresholds_data)
    
    r["Classification1"] = c1
    r["Classification2"] = c2
    r["Classification"] = f"{c1} / {c2}"

    return r


def process_interruptions(r):
    seq1 = r["_seq1"]
    seq2 = r["_seq2"]
    
    inter1 = find_interruptions(r["MS1"])
    inter2 = find_interruptions(r["MS2"])
    
    seqs1 = extract_interruption_sequences(seq1, inter1)
    seqs2 = extract_interruption_sequences(seq2, inter2)
    
    # Allèle 1
    if inter1:
        r["Interruptions1"] = sort_repeats(number_interruptions(seqs1))
        r["SegmentationComplete1"] = segmentation_complete(r["Segmentation1"], inter1, seqs1)
    else:
        r["Interruptions1"] = None

    # Allèle 2
    if inter2:
        r["Interruptions2"] = sort_repeats(number_interruptions(seqs2))
        r["SegmentationComplete2"] = segmentation_complete(r["Segmentation2"], inter2, seqs2)
    else:
        r["Interruptions2"] = None

    return r


def process_marking(r, patho_motifs, uncertain_motifs, icons):
    """Marquage UI (patho, incertain)."""
    trid = r["TRID"]
    
    r["Motifs"] = mark_motifs(r["_motifs_used"], trid, patho_motifs, uncertain_motifs, icons)
    r["Répétition1"] = mark_motifs(r["Répétition1"], trid, patho_motifs, uncertain_motifs, icons)
    r["Répétition2"] = mark_motifs(r["Répétition2"], trid, patho_motifs, uncertain_motifs, icons)
    
    r["Segmentation1"] = mark_segmentation(r["Segmentation1"], trid, patho_motifs, uncertain_motifs, icons)
    r["Segmentation2"] = mark_segmentation(r["Segmentation2"], trid, patho_motifs, uncertain_motifs, icons)
    
    return r

def process_sample(zip_path, vcf_filename, selected_trids, base_dir, prefix, sample_name):
    """Pipeline TRGT complet pour un sample."""
    rows = parse_vcf_from_zip(zip_path, vcf_filename, selected_trids)
    
    motif_data = load_motif_data()
    patho_motifs = motif_data["patho_motifs"]
    uncertain_motifs = motif_data["uncertain_motifs"]
    orientation = motif_data["orientation"]
    icons = motif_data["icons"]
    thresholds_data = load_clinical_thresholds()
    
    for r in rows:
        # Profondeur
        sd1 = r.get("SD1")
        sd2 = r.get("SD2")
        if sd1 is not None and sd2 is not None:
            warning = (int(sd1) < 50) or (int(sd2) < 50)
            r["Profondeur"] = f"\U000026A0 {sd1} / {sd2}" if warning else f"{sd1} / {sd2}"
        
        # Taille (bp)
        al1 = r.get("AL1")
        al2 = r.get("AL2")
        allr1 = r.get("ALLR1")
        allr2 = r.get("ALLR2")
        
        if al1 is not None and al2 is not None:
            t1 = f"{al1} ({allr1})" if allr1 else al1
            t2 = f"{al2} ({allr2})" if allr2 else al2
            r["Taille (bp)"] = f"{t1} / {t2}"
        
        # Pureté
        ap1 = r.get("AP1")
        ap2 = r.get("AP2")
        if ap1 is not None and ap2 is not None:
            r["Pureté"] = f"{ap1} / {ap2}"
        
        # Methylation
        am1 = r.get("AM1")
        am2 = r.get("AM2")
        if am1 is not None and am2 is not None:
            r["Methylation"] = f"{am1} / {am2}"

        r = process_orientation(r, orientation)
        r = process_segmentation(r)
        r = process_interruptions(r)
        r = process_repeats(r, thresholds_data)
        r = process_marking(r, patho_motifs, uncertain_motifs, icons)
        r["Répétition1"] = sort_repeats(r["Répétition1"])
        r["Répétition2"] = sort_repeats(r["Répétition2"])
        r = process_plots(r, base_dir, prefix, sample_name)
        r = process_igv(r, base_dir, prefix, sample_name)

        
    return rows


def process_plots(r, base_dir, prefix, sample_name):
    trid = r["TRID"]
    links = get_available_plots(base_dir, prefix, sample_name, trid)
    r["Plots_links"] = links if links else {}
    return r

def process_igv(r, base_dir, prefix, sample_name):
    spanning = get_available_spanning_bam(base_dir, prefix, sample_name)
    r["IGV_links"] = spanning if spanning else None
    return r
