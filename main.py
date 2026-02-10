import PySimpleGUI as sg
import zipfile
import tempfile
import shutil
import os

from scripts.core.orchestrator import process_sample
from scripts.ui.plots import get_analysis_prefix, open_svg
from scripts.ui.html_export import generate_html_table, save_and_open_html
from scripts.ui.igv import get_available_spanning_bam, open_igv, cleanup_tmpdir_force


import ctypes
import sys

# def open_console():
#     # Ouvre une console Windows
#     ctypes.windll.kernel32.AllocConsole()
#     # Redirige stdout et stderr vers la console
#     sys.stdout = open("CONOUT$", "w")
#     sys.stderr = open("CONOUT$", "w")

# open_console()


# -------------------------
# CONFIGURATION UI
# -------------------------

DISEASES = {
    "FRDA (FXN)": "FRDA_FXN",
    "CANVAS (RFC1)": "CANVAS_RFC1",
    "SCA1": "SCA1_ATXN1",
    "SCA2": "SCA2_ATXN2",
    "SCA3": "SCA3_ATXN3",
    "SCA6 (CACNA1A)": "SCA6_CACNA1A",
    "SCA7": "SCA7_ATXN7",
    "SCA17 (TBP)": "SCA17_TBP",
    "SCA27B (FGF14)": "SCA27B_FGF14",
    "SCA36 (NOP56)": "SCA36_NOP56",
    "FXTAS (FMR1)": "FXS_FMR1",
    "C9orf72": "FTDALS1_C9orf72",
    "OPDM1 (LRP12)": "OPDM1_LRP12",
}

TRID_ORDER = { DISEASES[name]: i for i, name in enumerate(DISEASES) }

SCA_GROUP = [
    "SCA1",
    "SCA2",
    "SCA3",
    "SCA6 (CACNA1A)",
    "SCA7",
    "SCA17 (TBP)",
    "SCA27B (FGF14)",
    "SCA36 (NOP56)"
]

ATAXIE_GROUP = ["FRDA (FXN)", "CANVAS (RFC1)", "FXTAS (FMR1)"] + SCA_GROUP


def list_vcfs(zip_path):
    """Retourne la liste des fichiers VCF dans un ZIP."""
    with zipfile.ZipFile(zip_path, "r") as z:
        return [f for f in z.namelist() if f.lower().endswith((".vcf", ".vcf.gz"))]


# -------------------------
# MAIN UI
# -------------------------

def main():
    sg.theme("SystemDefault")

    layout = [
        [sg.Text("Sélection du fichier TRGT (trgt_vcf.zip)")],
        [sg.Input(key="-ZIP-", enable_events=True), sg.FileBrowse("Parcourir")],
        [sg.Text("Sample à analyser")],
        [sg.Input(key="-SEARCH-", enable_events=True, size=(40,1))],
        [sg.Combo([], key="-SAMPLE-", size=(40,1), readonly=True)],
        [sg.Text("Maladies à analyser")],
    ]

    for disease in DISEASES:
        layout.append([sg.Checkbox(disease, key=f"-{disease}-")])

    layout += [
        [sg.Frame("Raccourcis", [
            [sg.Button("SCA"), sg.Button("Ataxies"), sg.Button("Décocher")]
        ])],
        [sg.Button("Lancer l'analyse")],
        [sg.Text("", key="-STATUS-", text_color="blue")],
        [sg.Text("by Corentin Marco", justification="right", font=("Helvetica", 8), text_color="gray")]
    ]

    window = sg.Window("TRGT Clinical Parser", layout)

    # -------------------------
    # ÉVÉNEMENTS
    # -------------------------

    while True:
        event, values = window.read()
        if event == sg.WINDOW_CLOSED:
            break

        # Raccourcis
        if event == "SCA":
            for d in DISEASES:
                window[f"-{d}-"].update(False)
            for d in SCA_GROUP:
                window[f"-{d}-"].update(True)

        if event == "Ataxies":
            for d in DISEASES:
                window[f"-{d}-"].update(False)
            for d in ATAXIE_GROUP:
                window[f"-{d}-"].update(True)

        if event == "Décocher":
            for d in DISEASES:
                window[f"-{d}-"].update(False)

        # Charger les VCF du ZIP
        if event == "-ZIP-":
            zip_path = values["-ZIP-"]
            if zip_path:
                samples = list_vcfs(zip_path)
                display = [os.path.basename(s) for s in samples]
                window.metadata = dict(zip(display, samples))
                window.metadata["all_samples"] = display
                window["-SAMPLE-"].update(values=display)

        if event == "-SEARCH-":
            query = values["-SEARCH-"].lower()
            all_samples = window.metadata.get("all_samples", [])
        
            if query:
                filtered = [s for s in all_samples if query in s.lower()]
            else:
                filtered = all_samples
        
            window["-SAMPLE-"].update(values=filtered)
        
            if len(filtered) == 1:
                window["-SAMPLE-"].update(filtered[0])

        # Lancer l'analyse
        if event == "Lancer l'analyse":
            zip_path = values["-ZIP-"]
            sample_display = values["-SAMPLE-"]

            if not zip_path or not sample_display:
                window["-STATUS-"].update("Veuillez sélectionner un ZIP et un sample", text_color="red")
                continue

            sample_internal = window.metadata[sample_display]

            selected_trids = [
                DISEASES[name]
                for name in DISEASES
                if values[f"-{name}-"]
            ]

            if not selected_trids:
                window["-STATUS-"].update("Veuillez sélectionner au moins une maladie", text_color="red")
                continue

            # Préparation
            analyse_prefix = get_analysis_prefix(zip_path)
            base_dir = os.path.dirname(zip_path)
            sample_name = sample_display.replace(".trgt.vcf", "")

            # -------------------------
            # APPEL AU PIPELINE TRGT
            # -------------------------
            rows = process_sample(
                zip_path,
                sample_internal,
                selected_trids,
                base_dir,
                analyse_prefix,
                sample_name
            )

            # -------------------------
            # AFFICHAGE DES RÉSULTATS
            # -------------------------

            headers = [
                "TRID", "Gene", "Profondeur",
                "Taille (bp)", "Motifs", "Genotype", "Classification",
                "Répétition1", "Répétition2",
                "Segmentation1", "Segmentation2"
            ]


            rows.sort(key=lambda r: TRID_ORDER.get(r["TRID"], 999))
            table_data = [[r.get(h, "") for h in headers] for r in rows]

            col_widths = [14, 8, 10, 20, 12, 10, 14, 20, 20, 30, 30]

            table_layout = [
                [sg.Table(
                    values=table_data,
                    headings=headers,
                    auto_size_columns=False,
                    col_widths=col_widths,
                    justification="left",
                    num_rows=min(20, len(table_data)),
                    key="-TABLE-",
                    enable_events=True,
                    expand_x=True,
                    expand_y=True
                )],
                [sg.Frame("Détails", [
                    [sg.Multiline("", key="-DETAILS-", size=(300, 40), disabled=True, expand_x=True, expand_y=True)],
                    [sg.Text("Plots disponibles :"), sg.Combo([], key="-PLOTCHOICE-", size=(40,1))],
                    [sg.Button("Ouvrir plot"), sg.Button("Copier")],
                    [sg.Button("Ouvrir IGV", key="-IGV-", disabled=True)]
                ])],
                [sg.Button("Imprimer le tableau"), sg.Button("Fermer")]
            ]

            table_window = sg.Window(f"Résultats pour {sample_display}", table_layout, resizable=True, finalize=True)
            table_window.maximize()

            # -------------------------
            # ÉVÉNEMENTS TABLEAU
            # -------------------------

            while True:
                ev, vals = table_window.read()

                if ev in (sg.WINDOW_CLOSED, "Fermer"):
                    cleanup_tmpdir_force()
                    table_window.close()
                    window.bring_to_front()
                    break

                if ev == "-TABLE-":
                    idx = vals["-TABLE-"][0]
                    row = rows[idx]

                    table_window["-IGV-"].update(disabled=False)
                    
                    details = [f"{h} : {row.get(h, '')}" for h in headers]
                    details.append(f"Pureté : {row.get('Pureté', '')}")
                    details.append(f"Methylation : {row.get('Methylation', '')}")

                    # Interruptions
                    if row.get("Interruptions1") or row.get("Interruptions2"):
                        details.append("")
                        if row.get("Interruptions1"):
                            details.append(f"Interruptions1 : {row['Interruptions1']}")
                        if row.get("Interruptions2"):
                            details.append(f"Interruptions2 : {row['Interruptions2']}")
                        if row.get("SegmentationComplete1"):
                            details.append(f"SegmentationComplète1 : {row['SegmentationComplete1']}")
                        if row.get("SegmentationComplete2"):
                            details.append(f"SegmentationComplète2 : {row['SegmentationComplete2']}")

                    table_window["-DETAILS-"].update("\n".join(details))

                    available = [label for label in row["Plots_links"] if row["Plots_links"][label]]
                    table_window["-PLOTCHOICE-"].update(values=available)

                if ev == "Ouvrir plot":
                    idx = vals["-TABLE-"][0]
                    row = rows[idx]
                    choice = vals["-PLOTCHOICE-"]
                    if choice:
                        zip_path, inner_zip, svg_file = row["Plots_links"][choice]
                        open_svg(zip_path, inner_zip, svg_file)

                if ev == "Copier":
                    sg.clipboard_set(table_window["-DETAILS-"].get())

                if ev == "Imprimer le tableau":
                    html = generate_html_table(headers, rows, sample_name)
                    save_and_open_html(html)

                if ev == "-IGV-":
                    links = row.get("IGV_links")
                
                    if not links:
                        sg.popup("Aucun spanning BAM disponible pour cet échantillon.")
                        continue
                
                    zip_path, bam_file, bai_file = links
                
                    open_igv(zip_path, bam_file, bai_file, row["CHROM"], row["START"], row["END"])

    window.close()

if __name__ == "__main__":
    main()
