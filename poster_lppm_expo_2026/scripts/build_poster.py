"""Re-flow the LPPM EXPO 2026 A0 poster template into a 60 x 180 cm X-banner.

PowerPoint caps slide size at 56 in (142.24 cm), so the slide is built at 1:2
scale (30 x 90 cm, same 1:3 ratio) and printed at 200 %. All geometry below is
written in PRINT centimetres / PRINT points and halved on the way out.

usage: build_poster.py <unpacked_dir> <penelitian|pengabdian> <header.png> <footer.png>
"""
import copy
import math
import re
import shutil
import sys
from pathlib import Path

from lxml import etree

NS = {
    "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
    "p": "http://schemas.openxmlformats.org/presentationml/2006/main",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
}
A = "{%s}" % NS["a"]
P = "{%s}" % NS["p"]

SCALE = 0.5                       # slide = print * SCALE
W, H = 60.0, 180.0                # print size, cm
M = 2.5                           # side margin, cm
CW = W - 2 * M
HEADER_H = W * 220 / 1356         # keeps header art aspect
FOOTER_H = W * 187 / 1354
BAND_H = 6.4
FOOTER_TOP = H - FOOTER_H

KINDS = {
    "penelitian": {
        "label": "PENELITIAN",
        "dark": "0B3A82",   # navy
        "tint": "E6EEF9",
        "figs": {
            "met": [
                dict(pics=["Picture 10", "Picture 14"], caption="TextBox 74", hmax=15),
                dict(pics=["Picture 27", "Picture 30"], labels=["TextBox 18", "TextBox 20"],
                     caption="TextBox 90", hmax=14),
            ],
            "has": [dict(pics=["Picture 46"], caption="TextBox 1033", hmax=21)],
        },
    },
    "pengabdian": {
        "label": "PENGABDIAN",
        "dark": "08502C",   # deep green
        "tint": "E4F3E9",
        "figs": {
            "met": [
                dict(pics=["Picture 4", "Picture 12"], caption="TextBox 7", hmax=15),
                dict(pics=["Picture 2"], caption="TextBox 11", hmax=14),
            ],
            "has": [dict(pics=["Picture 13", "Picture 15"], labels=["TextBox 22", "+TextBox 22"],
                         caption="TextBox 17", hmax=20)],
        },
    },
}

# section key, bar rectangle, title prefix, body text box, base text allotment (print cm)
SECTIONS = [
    ("lat", "Rectangle 1025", "Latar", "TextBox 73", 8.0),
    ("met", "Rectangle 61", "Metod", "TextBox 42", 9.0),
    ("has", "Rectangle 8", "Hasil", "TextBox 80", 10.5),
    ("kes", "Rectangle 76", "Kesimpulan", "TextBox 38", 7.5),
    ("lua", "Rectangle 26", "Luaran", "TextBox 40", 9.0),
]
DELETE = ["Rectangle 43", "Rectangle 58", "Rectangle 5", "AutoShape 2"]

GAP_SEC, GAP_BAR, GAP_FIG, GAP_IMG = 0.9, 0.6, 0.7, 1.5
BAR_H, CAP_H, LAB_H = 4.0, 3.4, 1.8
TITLE_H, SKEMA_H, AUTH_H = 9.0, 2.3, 6.2


def emu(cm):
    return int(round(cm * 360000 * SCALE))


def sz(pt):
    return str(int(round(pt * 100 * SCALE)))


def lum(hexc):
    def ch(v):
        v /= 255
        return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4
    r, g, b = (int(hexc[i:i + 2], 16) for i in (0, 2, 4))
    return 0.2126 * ch(r) + 0.7152 * ch(g) + 0.0722 * ch(b)


def contrast(c1, c2):
    l1, l2 = sorted([lum(c1), lum(c2)], reverse=True)
    return (l1 + 0.05) / (l2 + 0.05)


def load(path):
    return etree.parse(str(path), etree.XMLParser(remove_blank_text=False))


def save(tree, path):
    tree.write(str(path), xml_declaration=True, encoding="UTF-8", standalone=True)


def name_of(el):
    c = el.find(".//p:cNvPr", NS)
    return c.get("name") if c is not None else None


def text_of(el):
    return "".join(t.text or "" for t in el.iter(A + "t"))


def set_xfrm(el, x, y, w, h):
    xf = el.find(".//a:xfrm", NS)
    xf.find("a:off", NS).attrib.update({"x": str(emu(x)), "y": str(emu(y))})
    xf.find("a:ext", NS).attrib.update({"cx": str(emu(w)), "cy": str(emu(h))})


def ext_of(el):
    e = el.find(".//a:xfrm/a:ext", NS)
    return int(e.get("cx")), int(e.get("cy"))


def clear_effects(el):
    sppr = el.find("p:spPr", NS)
    eff = sppr.find("a:effectLst", NS)
    if eff is not None:
        for c in list(eff):
            eff.remove(c)


def set_body(el, **attrs):
    bp = el.find(".//a:bodyPr", NS)
    bp.attrib.update(dict(attrs))
    return bp


def solid(hexc):
    f = etree.Element(A + "solidFill")
    etree.SubElement(f, A + "srgbClr", val=hexc)
    return f


def halve_text_units(root):
    """Font sizes, character spacing and point-based paragraph spacing -> 1:2 scale."""
    for el in root.iter():
        if el.tag in (A + "rPr", A + "endParaRPr", A + "defRPr"):
            if "sz" in el.attrib:
                el.set("sz", str(max(100, int(round(int(el.get("sz")) * SCALE)))))
            if "spc" in el.attrib:
                el.set("spc", str(int(round(int(el.get("spc")) * SCALE))))
        elif el.tag == A + "spcPts":
            el.set("val", str(int(round(int(el.get("val")) * SCALE))))


def shape_xml(sid, name, x, y, w, h, fill, paras, anchor="ctr", ins=None, txbox=False):
    ins = ins or {}
    ins_attr = "".join(f' {k}="{emu(v)}"' for k, v in ins.items())
    fill_xml = f'<a:solidFill><a:srgbClr val="{fill}"/></a:solidFill>' if fill else "<a:noFill/>"
    ps = []
    for p in paras:
        ps.append(
            f'<a:p><a:pPr algn="ctr"><a:lnSpc><a:spcPct val="{p.get("lnspc", 100000)}"/></a:lnSpc></a:pPr>'
            f'<a:r><a:rPr lang="id-ID" sz="{sz(p["pt"])}" b="1" spc="{p.get("spc", 0)}" dirty="0">'
            f'<a:solidFill><a:srgbClr val="{p["color"]}"/></a:solidFill>'
            f'<a:latin typeface="Arial" panose="020B0604020202020204" pitchFamily="34" charset="0"/>'
            f'<a:cs typeface="Arial" panose="020B0604020202020204" pitchFamily="34" charset="0"/>'
            f'</a:rPr><a:t>{p["text"]}</a:t></a:r></a:p>'
        )
    tx = "".join(ps) if paras else '<a:p><a:endParaRPr lang="id-ID"/></a:p>'
    xml = (
        f'<p:sp xmlns:p="{NS["p"]}" xmlns:a="{NS["a"]}"><p:nvSpPr><p:cNvPr id="{sid}" name="{name}"/>'
        f'<p:cNvSpPr{" txBox=\"1\"" if txbox else ""}/><p:nvPr userDrawn="1"/></p:nvSpPr>'
        f'<p:spPr><a:xfrm><a:off x="{emu(x)}" y="{emu(y)}"/><a:ext cx="{emu(w)}" cy="{emu(h)}"/></a:xfrm>'
        f'<a:prstGeom prst="rect"><a:avLst/></a:prstGeom>{fill_xml}<a:ln><a:noFill/></a:ln></p:spPr>'
        f'<p:txBody><a:bodyPr wrap="square" rtlCol="0" anchor="{anchor}"{ins_attr}><a:noAutofit/></a:bodyPr>'
        f'<a:lstStyle/>{tx}</p:txBody></p:sp>'
    )
    return etree.fromstring(xml)


def build(root_dir, kind, header_png, footer_png):
    cfg = KINDS[kind]
    dark, tint = cfg["dark"], cfg["tint"]
    print(f"{kind}: white-on-dark {contrast('FFFFFF', dark):.1f}:1, dark-on-tint {contrast(dark, tint):.1f}:1")
    d = Path(root_dir)

    # --- slide size ---------------------------------------------------------------
    pres = d / "ppt/presentation.xml"
    t = load(pres)
    old = t.find("p:sldSz", NS)
    ow, oh = int(old.get("cx")), int(old.get("cy"))
    old.attrib.clear()
    old.attrib.update({"cx": str(emu(W)), "cy": str(emu(H))})
    save(t, pres)
    sx, sy = emu(W) / ow, emu(H) / oh

    # --- theme: accent1 follows the category colour --------------------------------
    th = d / "ppt/theme/theme1.xml"
    s = th.read_text(encoding="utf8")
    s = re.sub(r"<a:accent1>.*?</a:accent1>", f'<a:accent1><a:srgbClr val="{dark}"/></a:accent1>', s, count=1)
    th.write_text(s, encoding="utf8")

    # --- layouts: rescale placeholder frames so nothing sits off-slide ------------
    for lay in sorted((d / "ppt/slideLayouts").glob("slideLayout*.xml")):
        lt = load(lay)
        for xf in lt.iter(A + "xfrm"):
            o, e = xf.find("a:off", NS), xf.find("a:ext", NS)
            o.set("x", str(int(int(o.get("x")) * sx))); o.set("y", str(int(int(o.get("y")) * sy)))
            e.set("cx", str(int(int(e.get("cx")) * sx))); e.set("cy", str(int(int(e.get("cy")) * sy)))
        save(lt, lay)

    # --- master: header / footer art, tint backgrounds, live event text, category band
    mp = d / "ppt/slideMasters/slideMaster1.xml"
    mt = load(mp)
    tree = mt.find(".//p:cSld/p:spTree", NS)
    for el in list(tree):
        if el.tag == P + "sp" and el.find(".//p:ph", NS) is not None:
            xf = el.find(".//a:xfrm", NS)
            if xf is not None:
                o, e = xf.find("a:off", NS), xf.find("a:ext", NS)
                o.set("x", str(int(int(o.get("x")) * sx))); o.set("y", str(int(int(o.get("y")) * sy)))
                e.set("cx", str(int(int(e.get("cx")) * sx))); e.set("cy", str(int(int(e.get("cy")) * sy)))
        if el.tag == P + "pic":
            n = name_of(el)
            if n == "Picture 9":
                set_xfrm(el, 0, 0, W, HEADER_H)
            elif n == "Picture 11":
                set_xfrm(el, 0, FOOTER_TOP, W, FOOTER_H)
    grp = tree.find("p:grpSpPr", NS)
    hdr_bg = shape_xml(201, "Header Background", 0, 0, W, HEADER_H, tint, [])
    ftr_bg = shape_xml(202, "Footer Background", 0, FOOTER_TOP, W, FOOTER_H, tint, [])
    grp.addnext(ftr_bg)
    grp.addnext(hdr_bg)
    tree.append(shape_xml(
        203, "Event Title", 0.6, 2.2, 15.0, 5.4, None,
        [dict(text="LPPM EXPO 2026", pt=46, color=dark, lnspc=95000),
         dict(text="INOVASI &amp; KOLABORASI", pt=29, color=dark, lnspc=105000),
         dict(text="UNTUK NEGRI", pt=29, color=dark, lnspc=95000)],
        ins=dict(lIns=0, rIns=0), txbox=True))
    tree.append(shape_xml(
        204, "Category Band", 0, HEADER_H, W, BAND_H, dark,
        [dict(text=cfg["label"], pt=150, color="FFFFFF", spc=int(1500 * SCALE))],
        ins=dict(lIns=0, rIns=0, tIns=0, bIns=0)))
    save(mt, mp)
    shutil.copyfile(header_png, d / "ppt/media/image1.png")
    shutil.copyfile(footer_png, d / "ppt/media/image2.png")

    # --- slide --------------------------------------------------------------------
    sp_path = d / "ppt/slides/slide1.xml"
    st = load(sp_path)
    sroot = st.getroot()
    tree = sroot.find(".//p:cSld/p:spTree", NS)
    halve_text_units(sroot)
    shapes = [el for el in tree if el.tag in (P + "sp", P + "pic")]

    def by_name(n):
        hits = [el for el in shapes if name_of(el) == n]
        assert len(hits) == 1, (n, len(hits))
        return hits[0]

    def by_text(prefix, name=None):
        hits = [el for el in shapes if text_of(el).strip().startswith(prefix) and (name is None or name_of(el) == name)]
        assert len(hits) == 1, (prefix, len(hits))
        return hits[0]

    for n in DELETE:
        el = by_name(n)
        tree.remove(el)
        shapes.remove(el)

    # "+Name" = clone of Name (used to split the single "(a)   (b)" label box)
    max_id = max(int(c.get("id")) for c in sroot.iter(P + "cNvPr"))
    clones = {}
    for kind_figs in cfg["figs"].values():
        for row in kind_figs:
            for lab in row.get("labels", []):
                if lab.startswith("+"):
                    src = by_name(lab[1:])
                    cl = copy.deepcopy(src)
                    max_id += 1
                    c = cl.find(".//p:cNvPr", NS)
                    c.set("id", str(max_id)); c.set("name", lab[1:] + "b")
                    for ext in c.findall("a:extLst", NS):
                        c.remove(ext)
                    src.addnext(cl)
                    clones[lab] = cl

    def get(n):
        return clones[n] if n in clones else by_name(n)

    def set_label(el, txt):
        runs = el.findall(".//a:p/a:r", NS)
        runs[0].find("a:t", NS).text = txt
        for r_ in runs[1:]:
            r_.getparent().remove(r_)

    # category colour on bars, crisp text (no glow / shadow)
    title = by_text("JUDUL")
    clear_effects(title)
    for rpr in title.iter(A + "rPr", A + "endParaRPr"):
        if rpr.get("sz"):
            rpr.set("sz", sz(80))
        f = rpr.find("a:solidFill", NS)
        if f is not None:
            rpr.replace(f, solid(dark))
    bp = set_body(title, wrap="square", anchor="ctr", lIns="0", rIns="0")
    for c in list(bp):
        bp.remove(c)
    etree.SubElement(bp, A + "normAutofit")

    skema = by_text("Skema", "Text Box 7")
    authors = by_text("Nama", "Text Box 7")

    def layout(extra):
        pos = {}
        y = HEADER_H + BAND_H + 0.7
        pos["title"] = (M, y, CW, TITLE_H); y += TITLE_H + 0.2
        pos["skema"] = (M, y, CW, SKEMA_H); y += SKEMA_H
        pos["authors"] = (M, y, CW, AUTH_H); y += AUTH_H
        for key, bar, _, body, allot in SECTIONS:
            y += GAP_SEC
            pos[bar] = (0, y, W, BAR_H); y += BAR_H + GAP_BAR
            pos[body] = (M, y, CW, allot + extra); y += allot + extra
            for row in cfg["figs"].get(key, []):
                y += GAP_FIG
                pics = [get(n) for n in row["pics"]]
                aspects = [ext_of(p_)[0] / ext_of(p_)[1] for p_ in pics]
                n = len(pics)
                h = min(row["hmax"], (CW - GAP_IMG * (n - 1)) / sum(aspects))
                total = h * sum(aspects) + GAP_IMG * (n - 1)
                x = (W - total) / 2
                xs = []
                for nm, a in zip(row["pics"], aspects):
                    pos[nm] = (x, y, h * a, h); xs.append((x, h * a)); x += h * a + GAP_IMG
                y += h
                if row.get("labels"):
                    for lab, (lx, lw) in zip(row["labels"], xs):
                        pos[lab] = (lx, y, lw, LAB_H)
                    y += LAB_H
                pos[row["caption"]] = (M, y, CW, CAP_H); y += CAP_H
        return pos, y

    _, end = layout(0)
    limit = FOOTER_TOP - 0.6
    slack = limit - end
    assert slack >= 0, f"overflow by {-slack:.2f} cm"
    pos, end = layout(slack / len(SECTIONS))
    print(f"{kind}: content ends {end:.2f} cm, footer at {FOOTER_TOP:.2f} cm, extra/section {slack/len(SECTIONS):.2f} cm")

    set_xfrm(title, *pos["title"])
    set_xfrm(skema, *pos["skema"])
    set_xfrm(authors, *pos["authors"])
    for key, bar, prefix, body, _ in SECTIONS:
        b = by_name(bar)
        set_xfrm(b, *pos[bar])
        sppr = b.find("p:spPr", NS)
        g = sppr.find("a:gradFill", NS)
        if g is None:
            g = sppr.find("a:solidFill", NS)
        sppr.replace(g, solid(dark))
        tt = by_text(prefix, "Title 1")
        set_xfrm(tt, *pos[bar])
        clear_effects(tt)
        set_body(tt, wrap="square", anchor="ctr")
        set_xfrm(by_name(body), *pos[body])
        for row in cfg["figs"].get(key, []):
            for nm in row["pics"]:
                set_xfrm(get(nm), *pos[nm])
            for i, lab in enumerate(row.get("labels", [])):
                el = get(lab)
                set_xfrm(el, *pos[lab])
                set_label(el, "(%s)" % "ab"[i])
            cap = get(row["caption"])
            set_xfrm(cap, *pos[row["caption"]])
            for para in cap.iter(A + "p"):
                ppr = para.find("a:pPr", NS)
                if ppr is None:
                    ppr = etree.Element(A + "pPr")
                    para.insert(0, ppr)
                ppr.set("algn", "ctr")
    save(st, sp_path)

    # --- speaker note for authors / print shop -----------------------------------
    np_ = d / "ppt/notesSlides/notesSlide1.xml"
    s = np_.read_text(encoding="utf8")
    note = ("UKURAN CETAK 60 x 180 cm. Slide ini dibuat skala 1:2 (30 x 90 cm) karena PowerPoint "
            "membatasi ukuran slide maksimal 142 cm. Ekspor ke PDF, lalu cetak 200% (fit to 60 x 180 cm). "
            "Ukuran huruf di layar = setengah ukuran cetak (isi 20 pt = 40 pt saat dicetak). "
            "Gambar/foto sebaiknya minimal 150 dpi pada ukuran cetak.")
    s = s.replace('<a:p><a:endParaRPr lang="en-ID" dirty="0"/></a:p>',
                  f'<a:p><a:r><a:rPr lang="id-ID" dirty="0"/><a:t>{note}</a:t></a:r></a:p>', 1)
    np_.write_text(s, encoding="utf8")


if __name__ == "__main__":
    build(*sys.argv[1:5])
