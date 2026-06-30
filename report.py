from html import escape


def as_list(value):
    if isinstance(value, list):
        return value
    if value in (None, ""):
        return []
    return [str(value)]


def status_label(passed):
    return "Pass" if passed else "Needs work"


def print_report(report):
    print("\n" + "=" * 60)
    print("          BUSINESS DIGITAL AUDIT REPORT")
    print("=" * 60)

    print(f"Business Name : {report.get('Business')}")
    print(f"Industry      : {report.get('Industry')}")
    print(f"Website       : {report.get('Website')}")
    print(f"Status        : {report.get('Status')}")
    print(f"HTTPS         : {report.get('HTTPS')}")
    print(f"Title         : {report.get('Title')}")
    print(f"Meta          : {report.get('Meta')}")
    print(f"H1            : {report.get('H1', 'Not Found')}")
    print(f"Social Media  : {', '.join(as_list(report.get('Social'))) or 'Not Found'}")
    print(f"Email         : {', '.join(as_list(report.get('Email'))) or 'Not Found'}")
    print(f"Phone         : {', '.join(as_list(report.get('Phone'))) or 'Not Found'}")
    print(f"Audit Score   : {report.get('Score', 0)}/100")

    print("\nCategory Scores")
    print("-" * 20)
    for category, score in report.get("Categories", {}).items():
        max_score = report.get("MaxScores", {}).get(category, 0)
        print(f"- {category}: {score}/{max_score}")

    print("\nAudit Checks")
    print("-" * 20)
    for check in report.get("Checks", []):
        print(f"- {status_label(check['passed'])}: {check['title']} ({check['detail']})")

    print("\nRecommendations")
    print("-" * 20)
    for item in report.get("Recommendations", []):
        print(f"- {item}")

    write_text_report(report)
    write_html_report(report)

    print("\nPlain text report saved as sample_report.txt")
    print("HTML report saved as sample_report.html")


def write_text_report(report, path="sample_report.txt"):
    with open(path, "w", encoding="utf-8") as file:
        file.write("BUSINESS DIGITAL AUDIT REPORT\n")
        file.write("=" * 60 + "\n\n")

        file.write(f"Business Name : {report.get('Business')}\n")
        file.write(f"Industry      : {report.get('Industry')}\n")
        file.write(f"Website       : {report.get('Website')}\n")
        file.write(f"Status        : {report.get('Status')}\n")
        file.write(f"HTTPS         : {report.get('HTTPS')}\n")
        file.write(f"Title         : {report.get('Title')}\n")
        file.write(f"Meta          : {report.get('Meta')}\n")
        file.write(f"H1            : {report.get('H1', 'Not Found')}\n")
        file.write(f"Social Media  : {', '.join(as_list(report.get('Social'))) or 'Not Found'}\n")
        file.write(f"Email         : {', '.join(as_list(report.get('Email'))) or 'Not Found'}\n")
        file.write(f"Phone         : {', '.join(as_list(report.get('Phone'))) or 'Not Found'}\n")
        file.write(f"Audit Score   : {report.get('Score', 0)}/100\n\n")

        file.write("Category Scores:\n")
        for category, score in report.get("Categories", {}).items():
            max_score = report.get("MaxScores", {}).get(category, 0)
            file.write(f"- {category}: {score}/{max_score}\n")

        file.write("\nAudit Checks:\n")
        for check in report.get("Checks", []):
            file.write(
                f"- {status_label(check['passed'])}: "
                f"{check['title']} ({check['detail']})\n"
            )

        file.write("\nRecommendations\n")
        file.write("-" * 20 + "\n")
        for item in report.get("Recommendations", []):
            file.write(f"- {item}\n")


def write_html_report(report, path="sample_report.html"):
    score = int(report.get("Score", 0) or 0)
    business = escape(str(report.get("Business") or "Business"))
    website = escape(str(report.get("Website") or "#"))
    status = escape(str(report.get("Status") or "Unknown"))

    category_cards = []
    for category, value in report.get("Categories", {}).items():
        max_score = report.get("MaxScores", {}).get(category, 1) or 1
        percent = int((value / max_score) * 100)
        category_cards.append(
            f"""
            <section class="metric">
              <div>
                <span>{escape(category)}</span>
                <strong>{value}/{max_score}</strong>
              </div>
              <div class="bar"><span style="width:{percent}%"></span></div>
            </section>
            """
        )

    check_rows = []
    for check in report.get("Checks", []):
        state_class = "pass" if check["passed"] else "fail"
        check_rows.append(
            f"""
            <tr>
              <td><span class="pill {state_class}">{status_label(check['passed'])}</span></td>
              <td>{escape(check['title'])}</td>
              <td>{escape(check['category'])}</td>
              <td>{escape(str(check['detail']))}</td>
            </tr>
            """
        )

    recommendations = "\n".join(
        f"<li>{escape(str(item))}</li>"
        for item in report.get("Recommendations", [])
    ) or "<li>No urgent recommendations.</li>"

    details = {
        "Title": report.get("Title"),
        "Meta description": report.get("Meta"),
        "H1": report.get("H1", "Not Found"),
        "Social links": ", ".join(as_list(report.get("Social"))) or "Not Found",
        "Email": ", ".join(as_list(report.get("Email"))) or "Not Found",
        "Phone": ", ".join(as_list(report.get("Phone"))) or "Not Found",
        "Images missing alt": ", ".join(as_list(report.get("MissingImages"))) or "None",
        "Missing Open Graph": ", ".join(as_list(report.get("MissingOG"))) or "None",
    }
    detail_rows = "\n".join(
        f"<tr><th>{escape(label)}</th><td>{escape(str(value))}</td></tr>"
        for label, value in details.items()
    )

    html = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>Audit Report - {business}</title>
  <style>
    :root {{
      color-scheme: light;
      --ink: #172033;
      --muted: #687385;
      --line: #dce3ec;
      --panel: #ffffff;
      --bg: #f3f6fa;
      --good: #14845f;
      --warn: #b64835;
      --accent: #255f85;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      font-family: Arial, Helvetica, sans-serif;
      background: var(--bg);
      color: var(--ink);
      line-height: 1.5;
    }}
    header {{
      background: #102235;
      color: #fff;
      padding: 32px clamp(18px, 5vw, 56px);
    }}
    header p {{ margin: 8px 0 0; color: #d2dbe5; }}
    main {{ max-width: 1120px; margin: 0 auto; padding: 24px 18px 40px; }}
    .summary {{
      display: grid;
      grid-template-columns: minmax(180px, 240px) 1fr;
      gap: 18px;
      align-items: stretch;
      margin-bottom: 18px;
    }}
    .score, .panel, .metric {{
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 18px;
    }}
    .score strong {{ display: block; font-size: 44px; line-height: 1; }}
    .score span, .metric span, th {{ color: var(--muted); font-size: 13px; }}
    .grid {{ display: grid; grid-template-columns: repeat(5, 1fr); gap: 12px; }}
    .metric div:first-child {{ display: flex; justify-content: space-between; gap: 8px; }}
    .bar {{ height: 10px; background: #e8edf3; border-radius: 999px; overflow: hidden; margin-top: 12px; }}
    .bar span {{ display: block; height: 100%; background: var(--accent); }}
    table {{ width: 100%; border-collapse: collapse; }}
    th, td {{ border-bottom: 1px solid var(--line); padding: 11px 8px; text-align: left; vertical-align: top; }}
    th {{ width: 210px; font-weight: 700; }}
    .pill {{ display: inline-block; min-width: 86px; border-radius: 999px; padding: 4px 9px; font-size: 12px; font-weight: 700; text-align: center; }}
    .pass {{ background: #dcf4eb; color: var(--good); }}
    .fail {{ background: #fbe3df; color: var(--warn); }}
    .section {{ margin-top: 18px; }}
    h1, h2 {{ margin: 0; }}
    h2 {{ font-size: 20px; margin-bottom: 12px; }}
    ul {{ margin: 0; padding-left: 20px; }}
    a {{ color: inherit; overflow-wrap: anywhere; }}
    @media (max-width: 780px) {{
      .summary, .grid {{ grid-template-columns: 1fr; }}
      th {{ width: auto; }}
      table, tbody, tr, th, td {{ display: block; }}
      th {{ border-bottom: 0; padding-bottom: 0; }}
      td {{ padding-top: 3px; }}
    }}
  </style>
</head>
<body>
  <header>
    <h1>Business Digital Audit Report</h1>
    <p>{business} | <a href="{website}">{website}</a></p>
  </header>
  <main>
    <section class="summary">
      <div class="score">
        <span>Audit Score</span>
        <strong>{score}/100</strong>
        <div class="bar"><span style="width:{score}%"></span></div>
      </div>
      <div class="panel">
        <h2>Audit Summary</h2>
        <table>
          <tr><th>Industry</th><td>{escape(str(report.get('Industry') or 'Not provided'))}</td></tr>
          <tr><th>Status</th><td>{status}</td></tr>
          <tr><th>HTTPS</th><td>{escape(str(report.get('HTTPS') or 'Unknown'))}</td></tr>
        </table>
      </div>
    </section>

    <section class="grid">
      {''.join(category_cards)}
    </section>

    <section class="panel section">
      <h2>Audit Checks</h2>
      <table>
        <thead>
          <tr><th>Status</th><th>Check</th><th>Category</th><th>Finding</th></tr>
        </thead>
        <tbody>{''.join(check_rows)}</tbody>
      </table>
    </section>

    <section class="panel section">
      <h2>Details</h2>
      <table>{detail_rows}</table>
    </section>

    <section class="panel section">
      <h2>Recommendations</h2>
      <ul>{recommendations}</ul>
    </section>
  </main>
</body>
</html>
"""

    with open(path, "w", encoding="utf-8") as file:
        file.write(html)
