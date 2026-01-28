from scripts.core.vcf_parser import parse_vcf_from_zip
from scripts.core.segmentation_parser import combine_mc, combine_ms
from scripts.core.segmentation_utils import remove_zero_repeats, sort_repeats, number_interruptions
from scripts.core.segmentation_interruptions import find_interruptions, extract_interruption_sequences, segmentation_complete
from scripts.bio.motifs_orientation import reverse_complement, rc_motifs, rc_segmentation
from scripts.core.motif_structure import build_motif
from scripts.core.clinical_thresholds_load import get_motif_properties
from scripts.bio.motifs_loader import load_motif_data
from scripts.ui.marking import mark_motifs, mark_segmentation
from scripts.ui.plots import get_available_plots


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

    r["Répétition1"] = remove_zero_repeats(r["Répétition1"])
    r["Répétition2"] = remove_zero_repeats(r["Répétition2"])

    # Choix de la segmentation selon présence d'interruptions
    seg1 = r["SegmentationComplete1"] if r.get("Interruptions1") else r["Segmentation1"]
    seg2 = r["SegmentationComplete2"] if r.get("Interruptions2") else r["Segmentation2"]

    r["Répétition1"] = build_motif(
        r["TRID"],
        r["Répétition1"],
        r.get("Interruptions1"),
        seg1,
        thresholds_data
    )

    r["Répétition2"] = build_motif(
        r["TRID"],
        r["Répétition2"],
        r.get("Interruptions2"),
        seg2,
        thresholds_data
    )

    r["Répétition1"] = sort_repeats(r["Répétition1"])
    r["Répétition2"] = sort_repeats(r["Répétition2"])

    return r


def process_interruptions(r):
    """Interruptions TRGT (entre segments)."""
    seq1 = r["_seq1"]
    seq2 = r["_seq2"]
    
    inter1 = find_interruptions(r["MS1"])
    inter2 = find_interruptions(r["MS2"])
    
    seqs1 = extract_interruption_sequences(seq1, inter1)
    seqs2 = extract_interruption_sequences(seq2, inter2)
    
    r["Interruptions1"] = sort_repeats(number_interruptions(seqs1))
    r["Interruptions2"] = sort_repeats(number_interruptions(seqs2))
    
    r["SegmentationComplete1"] = segmentation_complete(r["Segmentation1"], inter1, seqs1)
    r["SegmentationComplete2"] = segmentation_complete(r["Segmentation2"], inter2, seqs2)
    
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
    
    for r in rows:
        # Profondeur
        sd1 = r.get("SD1")
        sd2 = r.get("SD2")
        if sd1 is not None and sd2 is not None:
            warning = (int(sd1) < 50) or (int(sd2) < 50)
            r["Profondeur"] = f"⚠️ {sd1} / {sd2}" if warning else f"{sd1} / {sd2}"
        
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
        r = process_repeats(r)
        r = process_interruptions(r)
        r = process_marking(r, patho_motifs, uncertain_motifs, icons)
        r["Répétition1"] = sort_repeats(r["Répétition1"])
        r["Répétition2"] = sort_repeats(r["Répétition2"])
        r = process_plots(r, base_dir, prefix, sample_name)
        
    return rows


def process_plots(r, base_dir, prefix, sample_name):
    trid = r["TRID"]
    links = get_available_plots(base_dir, prefix, sample_name, trid)
    r["Plots_links"] = links if links else {}
    return r
