from audit import audit_website
from report import print_report

print("=" * 50)
print("      BUSINESS DIGITAL AUDIT TOOL")
print("=" * 50)

business = input("Business Name : ")
industry = input("Industry      : ")
website = input("Website URL   : ")

if not website.startswith("http://") and not website.startswith("https://"):
    website = "https://" + website

report = audit_website(
    business,
    industry,
    website
)

print_report(report)