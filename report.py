def print_report(report):

    print("\n" + "=" * 60)
    print("          BUSINESS DIGITAL AUDIT REPORT")
    print("=" * 60)

    print(f"Business Name : {report['Business']}")
    print(f"Industry      : {report['Industry']}")
    print(f"Website       : {report['Website']}")
    print(f"Status        : {report['Status']}")
    print(f"HTTPS         : {report['HTTPS']}")
    print(f"Title         : {report['Title']}")
    print(f"Meta          : {report['Meta']}")
    print(f"Social Media  : {', '.join(report['Social'])}")
    print(f"Email         : {', '.join(report['Email'])}")
    print(f"Phone         : {', '.join(report['Phone'])}")
    print(f"Audit Score   : {report['Score']}/100")

    print("\nRecommendations")
    print("-" * 20)

    for item in report["Recommendations"]:
        print(f"• {item}")

    # Plain text export
    with open("sample_report.txt", "w", encoding="utf-8") as file:

        file.write("BUSINESS DIGITAL AUDIT REPORT\n")
        file.write("=" * 60 + "\n\n")

        file.write(f"Business Name : {report.get('Business')}\n")
        file.write(f"Industry      : {report.get('Industry')}\n")
        file.write(f"Website       : {report.get('Website')}\n")
        file.write(f"Status        : {report.get('Status')}\n")
        file.write(f"HTTPS         : {report.get('HTTPS')}\n")
        file.write(f"Title         : {report.get('Title')}\n")
        file.write(f"Meta          : {report.get('Meta')}\n")
        file.write(f"H1            : {report.get('H1','Not Found')}\n")
        file.write(f"Social Media  : {', '.join(report.get('Social',[]))}\n")
        file.write(f"Email         : {', '.join(report.get('Email',[]))}\n")
        file.write(f"Phone         : {', '.join(report.get('Phone',[]))}\n")
        file.write(f"Audit Score   : {report.get('Score')}/100\n\n")

        file.write("Category Scores:\n")
        for k, v in report.get('Categories', {}).items():
            file.write(f"- {k}: {v}\n")

        file.write("\nRecommendations\n")
        file.write("-" * 20 + "\n")

        for item in report.get("Recommendations", []):
            file.write(f"- {item}\n")

    print("\n✔ Plain text report saved as sample_report.txt")

    # HTML export
    html = []
    html.append("<!doctype html>")
    html.append("<html lang=\"en\">")
    html.append("<head>")
    html.append("<meta charset=\"utf-8\">")
    html.append(f"<title>Audit Report - {report.get('Business')}</title>")
    html.append("<meta name=\"viewport\" content=\"width=device-width,initial-scale=1\">")
    html.append("<style>")
    html.append("body{font-family:Arial,Helvetica,sans-serif;padding:20px;background:#f7f9fb}")
    html.append(".card{background:#fff;padding:20px;border-radius:8px;box-shadow:0 2px 8px rgba(0,0,0,0.06);margin-bottom:16px}")
    html.append(".score{font-size:28px;font-weight:700}")
    html.append(".bar{height:14px;background:#e6eef8;border-radius:7px;overflow:hidden}")
    html.append(".fill{height:100%;background:#2b7df7}")
    html.append("table{width:100%;border-collapse:collapse}")
    html.append("td,th{padding:8px;border-bottom:1px solid #eee;text-align:left}")
    html.append("</style>")
    html.append("</head>")
    html.append("<body>")

    html.append(f"<h1>Audit Report — {report.get('Business')}</h1>")

    html.append("<div class=\"card\">")
    html.append(f"<div><strong>Website:</strong> <a href=\"{report.get('Website')}\">{report.get('Website')}</a></div>")
    html.append(f"<div><strong>Status:</strong> {report.get('Status')}</div>")
    html.append(f"<div style=\"margin-top:8px\"><span class=\"score\">{report.get('Score')}/100</span></div>")
    html.append("<div class=\"bar\" style=\"margin-top:8px\"><div class=\"fill\" style=\"width:" + str(report.get('Score')) + "%\"></div></div>")
    html.append("</div>")

    # Category scores
    html.append("<div class=\"card\">")
    html.append("<h2>Category Scores</h2>")
    for k, v in report.get('Categories', {}).items():
        html.append(f"<div style=\"margin-bottom:10px\"><strong>{k}</strong> — {v}/" + ("30" if k=="SEO" else "20" if k in ("Contact","Social","Technical") else "10") + "")
        html.append("<div class=\"bar\"><div class=\"fill\" style=\"width:" + str(int((v/ (30 if k=="SEO" else 20 if k in ("Contact","Social","Technical") else 10)) * 100)) + "%\"></div></div></div>")
    html.append("</div>")

    # Details
    html.append("<div class=\"card\">")
    html.append("<h2>Details</h2>")
    html.append("<table>")
    html.append(f"<tr><th>Title</th><td>{report.get('Title')}</td></tr>")
    html.append(f"<tr><th>Meta</th><td>{report.get('Meta')}</td></tr>")
    html.append(f"<tr><th>H1</th><td>{report.get('H1','Not Found')}</td></tr>")
    html.append(f"<tr><th>Social</th><td>{', '.join(report.get('Social',[]))}</td></tr>")
    html.append(f"<tr><th>Email</th><td>{', '.join(report.get('Email',[]))}</td></tr>")
    html.append(f"<tr><th>Phone</th><td>{', '.join(report.get('Phone',[]))}</td></tr>")
    html.append(f"<tr><th>Missing Images ALT</th><td>{', '.join(report.get('MissingImages',[])) or 'None'}</td></tr>")
    html.append(f"<tr><th>Missing OG tags</th><td>{', '.join(report.get('MissingOG',[])) or 'None'}</td></tr>")
    html.append("</table>")
    html.append("</div>")

    # Recommendations
    html.append("<div class=\"card\">")
    html.append("<h2>Recommendations</h2>")
    html.append("<ul>")
    for item in report.get('Recommendations', []):
        html.append(f"<li>{item}</li>")
    html.append("</ul>")
    html.append("</div>")

    html.append("</body></html>")

    with open("sample_report.html", "w", encoding="utf-8") as f:
        f.write('\n'.join(html))

    print("✔ HTML report saved as sample_report.html")