import tempfile
import webbrowser
import os


def generate_html_table(headers, rows, sample_name):
    """Construit un tableau HTML complet."""
    html = f"""
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            table {{
                border-collapse: collapse;
                width: 100%;
                font-family: Arial;
            }}
            th, td {{
                border: 1px solid #444;
                padding: 6px;
                text-align: left;
            }}
            th {{
                background-color: #eee;
            }}
            h2 {{
                font-family: Arial;
            }}

            @media print {{
                table {{
                    width: 100%;
                    font-size: 10pt;
                }}
                th, td {{
                    padding: 4px;
                    word-break: break-word;
                }}
                body {{
                    margin: 0;
                }}
            }}
        </style>
    </head>
    <body>
        <h2>Résultats TRGT – {sample_name}</h2>
        <table>
    """

    # En-têtes
    html += "<tr>" + "".join(f"<th>{h}</th>" for h in headers) + "</tr>"

    # Lignes
    for r in rows:
        html += "<tr>" + "".join(f"<td>{r.get(h, '')}</td>" for h in headers) + "</tr>"

    html += "</table></body></html>"
    return html


def save_and_open_html(html_content):
    """Enregistre le HTML dans un fichier temporaire et l’ouvre."""
    tmp_path = os.path.join(tempfile.gettempdir(), "trgt_table.html")
    with open(tmp_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    webbrowser.open(f"file://{tmp_path}")
