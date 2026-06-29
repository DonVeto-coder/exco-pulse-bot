"""Weekly job: download workbook -> render full dashboard PNG -> upload to SharePoint.
The existing Power Automate flow then attaches that pulse.png and sends it.
"""
import datetime, subprocess, sys
import graph
from build_html import build_html

XLSM_PATH = "Action Tracker - Exco/Executive Action Tracker/Exco_Action_Tracker.xlsm"
PNG_PATH  = "Action Tracker - Exco/Executive Action Tracker/pulse.png"

def main():
    report_date = datetime.date.today()
    if len(sys.argv) > 1:
        report_date = datetime.date.fromisoformat(sys.argv[1])

    token = graph.get_token()
    graph.download(XLSM_PATH, "tracker.xlsm", token)

    html, data = build_html("tracker.xlsm", report_date)
    open("fresh.html", "w", encoding="utf-8").write(html)
    print("report_date:", report_date.isoformat(), "waffle:", data["waffle"])

    subprocess.run(["node", "render.js"], check=True)

    graph.upload("pulse.png", PNG_PATH, token)
    print("done - pulse.png published to SharePoint")

if __name__ == "__main__":
    main()
