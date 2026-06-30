"""ECG-style 'delivery pulse' sparkline as inline SVG, matching the OEB email style.
Each month: a heartbeat 'beat' whose height ~ planned load.
 teal/flat = nothing expected; red = under-delivered; navy = current month; blue = met/exceeded."""

TEAL="#00B2AD"; RED="#E03A3A"; NAVY="#1B2641"; BLUE="#2F6BD8"; GREY="#9AA3B2"

def _beat(cx, base, amp, color):
    # an ECG QRS-ish complex centred on cx
    p = [(cx-26,base),(cx-10,base),(cx-7,base+amp*0.12),(cx-3,base-amp*0.20),
         (cx,base-amp),(cx+3,base+amp*0.28),(cx+7,base+amp*0.06),(cx+10,base),(cx+26,base)]
    return "M " + " L ".join(f"{x:.1f},{y:.1f}" for x,y in p)

def spark_svg(months):
    """months: list of dicts {label, delivered, planned, current}"""
    W,H=300,159; base=78; n=len(months)
    colw=W/n
    maxp=max([m["planned"] for m in months]+[1])
    segs=[]; labels=[]
    for i,m in enumerate(months):
        cx=colw*(i+0.5)
        d,p,cur=m["delivered"],m["planned"],m["current"]
        if p==0 and d==0:
            color=TEAL
            segs.append(f'<path d="M {cx-colw/2+6:.1f},{base} L {cx+colw/2-6:.1f},{base}" stroke="{TEAL}" stroke-width="2.2" fill="none"/>')
        else:
            amp=18+42*(p/maxp)
            color = NAVY if cur else (BLUE if d>=p else RED)
            segs.append(f'<path d="{_beat(cx,base,amp,color)}" stroke="{color}" stroke-width="2.2" fill="none" stroke-linejoin="round" stroke-linecap="round"/>')
        lc = NAVY if cur else GREY
        fw = "700" if cur else "400"
        labels.append(
            f'<text x="{cx:.1f}" y="120" text-anchor="middle" font-family="Segoe UI,Arial,sans-serif" '
            f'font-size="13" font-weight="{fw}" fill="{NAVY if cur else "#525252"}">{d} [{p}]</text>'
            f'<text x="{cx:.1f}" y="138" text-anchor="middle" font-family="Segoe UI,Arial,sans-serif" '
            f'font-size="10" letter-spacing="0.5" fill="{lc}">({m["label"]})</text>')
    grid=f'<line x1="6" y1="{base}" x2="{W-6}" y2="{base}" stroke="#E5E7EB" stroke-width="1"/>'
    return (f'<svg viewBox="0 0 {W} {H}" width="100%" xmlns="http://www.w3.org/2000/svg" '
            f'style="display:block;width:100%;height:auto;">{grid}{"".join(segs)}{"".join(labels)}</svg>')

def company_strip_svg(months):
    """Wide company-wide heartbeat strip on navy, matching the email header band."""
    W, H = 700, 98; base = 46; n = len(months)
    colw = W / n
    maxp = max([m["planned"] for m in months] + [1])
    parts = [f'<rect x="0" y="0" width="{W}" height="{H}" fill="#1B2641"/>']
    labels = []
    for i, m in enumerate(months):
        x0 = colw*i; x1 = colw*(i+1); cx = colw*(i+0.5)
        d, p, cur = m["delivered"], m["planned"], m["current"]
        color = "#FFFFFF" if cur else "#E03A3A"
        amp = (6 + 34*(p/maxp)) if p > 0 else 0
        if amp <= 0:
            path = f'M {x0:.1f},{base} L {x1:.1f},{base}'
        else:
            path = (f'M {x0:.1f},{base} L {cx-14:.1f},{base} '
                    f'L {cx-9:.1f},{base+amp*0.10:.1f} L {cx-4:.1f},{base-amp*0.22:.1f} '
                    f'L {cx:.1f},{base-amp:.1f} L {cx+4:.1f},{base+amp*0.30:.1f} '
                    f'L {cx+9:.1f},{base+amp*0.06:.1f} L {cx+14:.1f},{base} L {x1:.1f},{base}')
        parts.append(f'<path d="{path}" stroke="{color}" stroke-width="2" fill="none" '
                     'stroke-linejoin="round" stroke-linecap="round"/>')
        labels.append(f'<text x="{cx:.1f}" y="{base+30}" text-anchor="middle" '
                      f'font-family="Segoe UI,Arial,sans-serif" font-size="15" font-weight="700" fill="#FFFFFF">{d} [{p}]</text>')
        labels.append(f'<text x="{cx:.1f}" y="{base+46}" text-anchor="middle" '
                      f'font-family="Segoe UI,Arial,sans-serif" font-size="11" letter-spacing="0.5" fill="#AEB6C7">({m["label"]})</text>')
    return (f'<svg viewBox="0 0 {W} {H}" width="100%" xmlns="http://www.w3.org/2000/svg" '
            f'style="display:block;width:100%;height:auto;">' + "".join(parts) + "".join(labels) + '</svg>')
