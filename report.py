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

    with open("sample_report.txt", "w", encoding="utf-8") as file:

        file.write("BUSINESS DIGITAL AUDIT REPORT\n")
        file.write("=" * 40 + "\n\n")

        file.write(f"Business Name : {report['Business']}\n")
        file.write(f"Industry      : {report['Industry']}\n")
        file.write(f"Website       : {report['Website']}\n")
        file.write(f"Status        : {report['Status']}\n")
        file.write(f"HTTPS         : {report['HTTPS']}\n")
        file.write(f"Title         : {report['Title']}\n")
        file.write(f"Meta          : {report['Meta']}\n")
        file.write(f"Social Media  : {', '.join(report['Social'])}\n")
        file.write(f"Email         : {', '.join(report['Email'])}\n")
        file.write(f"Phone         : {', '.join(report['Phone'])}\n")
        file.write(f"Audit Score   : {report['Score']}/100\n\n")

        file.write("Recommendations\n")
        file.write("-" * 20 + "\n")

        for item in report["Recommendations"]:
            file.write(f"- {item}\n")

    print("\n✔ Report saved as sample_report.txt")