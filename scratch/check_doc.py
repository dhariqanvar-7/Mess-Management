import docx

doc = docx.Document('report/Mess report.docx')
for i, p in enumerate(doc.paragraphs):
    for r in p.runs:
        if 'w:type="page"' in r._r.xml:
            print(f'P{i} has page break: {repr(p.text[:40])}')
            break
