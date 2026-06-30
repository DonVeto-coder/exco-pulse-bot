"""Build a fresh OEB Exco Action Tracker HTML from live workbook data,
by regenerating the data-critical sections inside the real template.
Usage: python build_html.py <tracker.xlsm> [YYYY-MM-DD]  ->  writes fresh.html
"""
import re, datetime, sys, os
from gen_data import build
from spark import spark_svg, company_strip_svg

HERE = os.path.dirname(os.path.abspath(__file__))
REF = open(os.path.join(HERE, "template.html"), encoding="utf-8").read()

PULSE = [
    ("Chief Executive Officer", "CEO delivery pulse"),
    ("Finance Manager",         "Finance Mgr delivery pulse"),
    ("Human Resources Manager", "Human Resources Mgr delivery pulse"),
    ("Innovation Manager",      "Innovation Mgr delivery pulse"),
    ("IT Manager",              "IT Mgr delivery pulse"),
    ("Marketing Manager",       "Marketing Mgr delivery pulse"),
    ("Production Manager",      "Production Mgr delivery pulse"),
    ("Sales Manager",           "Sales Mgr delivery pulse"),
    ("Strategy Manager",        "Strategy Mgr delivery pulse"),
]

def match_table(s, start):
    depth = 0
    for m in re.finditer(r'<table\b|</table>', s[start:]):
        if m.group(0).startswith('<table'): depth += 1
        else:
            depth -= 1
            if depth == 0: return start, start + m.end()
    return start, len(s)

def waffle_grid(open_n, todo, inprog, overdue):
    t = round(todo / open_n * 100) if open_n else 0
    p = round(inprog / open_n * 100) if open_n else 0
    o = 100 - t - p
    seq = ['#C3C9D4']*t + ['#00B2AD']*p + ['#1B2641']*o
    spacer = '<td style="width:2%;font-size:1px;">&nbsp;</td>'
    rowsep = '<tr><td colspan="19" style="height:4px;font-size:1px;">&nbsp;</td></tr>'
    rows = []
    for r in range(10):
        cells = [f'<td style="width:8.2%;height:26px;background:{seq[r*10+c]};border-radius:3px;font-size:1px;">&nbsp;</td>' for c in range(10)]
        rows.append('<tr>' + spacer.join(cells) + '</tr>')
    return ('<table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0" '
            'style="width:100%;border-collapse:collapse;table-layout:fixed;">' + rowsep.join(rows) + '</table>')

RANK_SHADES = ['#8E1A12','#A12A20','#C5564B','#D98B83','#E6ADA7','#EFC7C2','#F2D1CD','#F6DBD8','#FAE5E2']

def owner_bars(owners):
    rows = []
    for i, o in enumerate(owners):
        shade = RANK_SHADES[min(i, len(RANK_SHADES)-1)]
        rows.append(
            f'<tr><td style="background:{shade};border-radius:7px;padding:9px 12px;">'
            '<table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0" style="width:100%;border-collapse:collapse;"><tr>'
            f'<td align="left" style="font-size:12px;font-weight:700;color:#FFFFFF;white-space:nowrap;vertical-align:middle;">{o["dept"]} <span style="font-weight:400;">({o["who"]})</span></td>'
            '<td align="right" style="vertical-align:middle;white-space:nowrap;">'
            '<span style="font-size:8px;letter-spacing:.5px;text-transform:uppercase;color:#E7B4AE;">overdue&nbsp;</span>'
            f'<span style="font-size:16px;font-weight:700;color:#FFFFFF;">{o["overdue"]}</span>'
            '</td></tr></table></td></tr>')
    return ('<table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0" '
            'style="width:100%;border-collapse:separate;border-spacing:0 5px;">' + ''.join(rows) + '</table>')

def fmt_range(mon):
    sun = mon + datetime.timedelta(days=6)
    if mon.month == sun.month:
        return f"{mon.day:02d} - {sun.day:02d} {mon.strftime('%b')}"
    return f"{mon.day:02d} {mon.strftime('%b')} - {sun.day:02d} {sun.strftime('%b')}"

def build_html(xlsm_path, report_date):
    d = build(xlsm_path, report_date)
    w = d['waffle']; owners = d['owners_overdue']
    h = REF

    h = re.sub(r'Data as at:[^<]*', f"Data as at: {report_date.strftime('%d %b %Y')} &middot; 07:00", h)

    cur_mon = report_date - datetime.timedelta(days=report_date.weekday())
    prv_mon = cur_mon - datetime.timedelta(days=7)
    new_cmp = f"week {prv_mon.isocalendar()[1]} ({fmt_range(prv_mon)}) - week {cur_mon.isocalendar()[1]} ({fmt_range(cur_mon)})"
    h = re.sub(r'week \d+ \([^)]*\) - week \d+ \([^)]*\)', new_cmp, h)

    h = h.replace("1% of 318 open actions", f"1% of {w['open']} open actions")
    h = re.sub(r'To be done \(\d+\)', f"To be done ({w['todo']})", h)
    h = re.sub(r'In progress \(\d+\)', f"In progress ({w['inprog']})", h)
    h = re.sub(r'Overdue \(\d+\)', f"Overdue ({w['overdue']})", h)
    anchor = h.find(f"Overdue ({w['overdue']})")
    tstart = h.find("<table", anchor)
    s, e = match_table(h, tstart)
    h = h[:s] + waffle_grid(w['open'], w['todo'], w['inprog'], w['overdue']) + h[e:]

    oanchor = h.find("High overdue")
    btstart = h.rfind("<table", 0, h.find("border-spacing:0 5px", oanchor))
    s2, e2 = match_table(h, btstart)
    h = h[:s2] + owner_bars(owners) + h[e2:]

    pulses = d["pulses"]; open_by = d["owner_open"]; total_by = d["owner_total"]
    over_by = {o["role"]: o["overdue"] for o in owners}
    for role, alt in PULSE:
        svg = spark_svg(pulses[role])
        h = re.sub(r'<img[^>]*alt="' + re.escape(alt) + r'[^"]*"[^>]*>', lambda m: svg, h, count=1)

    rkeys = list(pulses.keys())
    comp = [{
        "label":     pulses[rkeys[0]][idx]["label"],
        "current":   pulses[rkeys[0]][idx]["current"],
        "delivered": sum(pulses[r][idx]["delivered"] for r in rkeys),
        "planned":   sum(pulses[r][idx]["planned"] for r in rkeys),
    } for idx in range(len(pulses[rkeys[0]]))]
    strip = company_strip_svg(comp)
    h = re.sub(r'<img[^>]*alt="Delivery pulse[^"]*"[^>]*>', lambda m: strip, h, count=1)

    roles = [role for role, _ in PULSE]
    ip = iter(open_by.get(r, 0) for r in roles)
    def _inplay(m):
        try: v = next(ip)
        except StopIteration: return m.group(0)
        return m.group(1) + str(v) + m.group(2)
    h = re.sub(r'(font-size:30px;font-weight:700;color:#1B2641;line-height:1;">)\d+'
               r'(</div><div style="font-size:8px;[^>]*>In play)', _inplay, h)
    to = iter((total_by.get(r, 0), over_by.get(r, 0)) for r in roles)
    def _to(m):
        try: t, o = next(to)
        except StopIteration: return m.group(0)
        return f'{t} total &middot; <strong{m.group(1)}>{o} overdue</strong>'
    h = re.sub(r'\d+ total &middot; <strong([^>]*)>\d+ overdue</strong>', _to, h)

    return h, d

if __name__ == "__main__":
    xlsm = sys.argv[1] if len(sys.argv) > 1 else "tracker.xlsm"
    rd = datetime.date.fromisoformat(sys.argv[2]) if len(sys.argv) > 2 else datetime.date.today()
    html, data = build_html(xlsm, rd)
    open("fresh.html", "w", encoding="utf-8").write(html)
    print(f"report_date={rd.isoformat()} waffle={data['waffle']} -> wrote fresh.html ({len(html)} bytes)")
