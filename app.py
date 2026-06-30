from audit import audit_website
from report import print_report


def main():
    print("=" * 50)
    print("      BUSINESS DIGITAL AUDIT TOOL")
    print("=" * 50)

    business = input("Business Name : ")
    industry = input("Industry      : ")
    website = input("Website URL   : ")

    # Normalize simple inputs
    website = website.strip()
    if not website:
        print("Please provide a website URL.")
        return

    if not website.startswith("http://") and not website.startswith("https://"):
        website = "https://" + website

    try:
        report = audit_website(
            business,
            industry,
            website
        )

        print_report(report)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


if __name__ == "__main__":
    main()