import io
import time
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH


def _ensure_list(val) -> list:
    if isinstance(val, list):
        return val
    if isinstance(val, str):
        return [val]
    if val is None:
        return []
    return [val]


def _heading(doc: Document, text: str, level: int = 1):
    doc.add_heading(text, level=level)


def _bold_para(doc: Document, label: str, value: str):
    p = doc.add_paragraph()
    run = p.add_run(f"{label}: ")
    run.bold = True
    p.add_run(str(value) if value else "")


def _add_table(doc: Document, headers: list[str], rows: list[list[str]]):
    table = doc.add_table(rows=1, cols=len(headers))
    table.style = "Table Grid"
    hdr_cells = table.rows[0].cells
    for i, h in enumerate(headers):
        hdr_cells[i].text = h
        for run in hdr_cells[i].paragraphs[0].runs:
            run.bold = True
    for row in rows:
        row_cells = table.add_row().cells
        for i in range(len(row_cells)):
            row_cells[i].text = str(row[i]) if i < len(row) else ""
    doc.add_paragraph()


def generate_document(results: dict, class_num: str, subject: str, chapter: str) -> bytes:
    t0 = time.time()
    print(f"[DOCGEN] START")

    for k, v in results.items():
        print(f"[DOCGEN]   worker '{k}' result: {len(str(v))} chars")

    doc = Document()

    title = doc.add_heading(f"{chapter} — {subject} Class {class_num}", 0)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    doc.add_paragraph()

    # ── WORKER 1: Core Learning ──────────────────────────────────────────────
    print(f"[DOCGEN] Section: Core Learning (+{time.time()-t0:.1f}s)")
    w1 = results.get("core_learning", {})
    theory = w1.get("theory_core", {}) if isinstance(w1, dict) else {}

    _heading(doc, "Summary", 1)
    doc.add_paragraph(theory.get("summary", "") if isinstance(theory, dict) else str(theory))

    _heading(doc, "Concepts", 1)
    for concept in _ensure_list(theory.get("deep_dive", []) if isinstance(theory, dict) else []):
        if not isinstance(concept, dict):
            doc.add_paragraph(str(concept))
            continue
        _heading(doc, concept.get("concept_name", "Concept"), 2)
        _bold_para(doc, "Definition", concept.get("definition", ""))
        _bold_para(doc, "Explanation", concept.get("explanation", ""))
        _bold_para(doc, "Example", concept.get("example", ""))
        _bold_para(doc, "Analogy", concept.get("analogy", ""))
        misconception = concept.get("misconception", "")
        if misconception:
            _bold_para(doc, "Common Misconception", misconception)
        for app in _ensure_list(concept.get("applications", [])):
            doc.add_paragraph(str(app), style="List Bullet")

    # ── WORKER 2: Memory ─────────────────────────────────────────────────────
    print(f"[DOCGEN] Section: Memory (+{time.time()-t0:.1f}s)")
    memory = results.get("memory", {}).get("memory", {}) if isinstance(results.get("memory"), dict) else {}

    _heading(doc, "Flashcards", 1)
    flashcards = _ensure_list(memory.get("flashcards", []) if isinstance(memory, dict) else [])
    if flashcards and isinstance(flashcards[0], dict):
        _add_table(
            doc,
            ["Question", "Answer"],
            [[f.get("question", ""), f.get("answer", "")] for f in flashcards],
        )

    _heading(doc, "Key Terms", 1)
    key_terms = _ensure_list(memory.get("key_terms", []) if isinstance(memory, dict) else [])
    if key_terms and isinstance(key_terms[0], dict):
        _add_table(
            doc,
            ["Term", "Meaning", "Significance", "Example", "Memory Tip"],
            [
                [
                    t.get("term", ""),
                    t.get("meaning", ""),
                    t.get("significance", ""),
                    t.get("example", ""),
                    t.get("memory_tip", ""),
                ]
                for t in key_terms
            ],
        )

    _heading(doc, "Fun Facts", 1)
    for i, fact in enumerate(_ensure_list(memory.get("fun_facts", []) if isinstance(memory, dict) else []), 1):
        doc.add_paragraph(f"{i}. {fact}")

    # ── WORKERS 3a/3b/3c: Objective Questions ────────────────────────────────
    print(f"[DOCGEN] Section: Objective Questions (+{time.time()-t0:.1f}s)")
    mcqs = _ensure_list(results.get("mcqs", {}).get("mcqs", []) if isinstance(results.get("mcqs"), dict) else [])
    very_short = _ensure_list(results.get("very_short", {}).get("very_short", []) if isinstance(results.get("very_short"), dict) else [])
    short_answer = _ensure_list(results.get("short_answer", {}).get("short_answer", []) if isinstance(results.get("short_answer"), dict) else [])

    _heading(doc, "Multiple Choice Questions", 1)
    for i, q in enumerate(mcqs, 1):
        if not isinstance(q, dict):
            continue
        p = doc.add_paragraph()
        p.add_run(f"Q{i}. {q.get('question', '')}").bold = True
        opts = q.get("options", {})
        if isinstance(opts, dict):
            for key in ["A", "B", "C", "D"]:
                doc.add_paragraph(f"    ({key}) {opts.get(key, '')}")
        _bold_para(doc, "Answer", q.get("answer", ""))
        justification = q.get("justification", "")
        if justification:
            _bold_para(doc, "Justification", justification)
        doc.add_paragraph()

    _heading(doc, "Very Short Answer Questions", 1)
    for i, q in enumerate(very_short, 1):
        if not isinstance(q, dict):
            continue
        p = doc.add_paragraph()
        p.add_run(f"Q{i}. {q.get('question', '')}").bold = True
        _bold_para(doc, "Answer", q.get("answer", ""))

    _heading(doc, "Short Answer Questions (2 Marks)", 1)
    for i, q in enumerate(short_answer, 1):
        if not isinstance(q, dict):
            continue
        p = doc.add_paragraph()
        p.add_run(f"Q{i}. {q.get('question', '')}").bold = True
        _bold_para(doc, "Answer", q.get("answer", ""))

    # ── WORKERS 4a/4b/4c/4d: Analytical Questions ────────────────────────────
    print(f"[DOCGEN] Section: Analytical Questions (+{time.time()-t0:.1f}s)")
    medium_answer = _ensure_list(results.get("medium_answer", {}).get("medium_answer", []) if isinstance(results.get("medium_answer"), dict) else [])
    long_answer = _ensure_list(results.get("long_answer", {}).get("long_answer", []) if isinstance(results.get("long_answer"), dict) else [])
    assertion_reason = _ensure_list(results.get("assertion_reason", {}).get("assertion_reason", []) if isinstance(results.get("assertion_reason"), dict) else [])
    case_studies = _ensure_list(results.get("case_studies", {}).get("case_studies", []) if isinstance(results.get("case_studies"), dict) else [])

    _heading(doc, "Medium Answer Questions (3 Marks)", 1)
    for i, q in enumerate(medium_answer, 1):
        if not isinstance(q, dict):
            continue
        p = doc.add_paragraph()
        p.add_run(f"Q{i}. {q.get('question', '')}").bold = True
        doc.add_paragraph(str(q.get("answer", "")))
        doc.add_paragraph()

    _heading(doc, "Long Answer Questions (5 Marks)", 1)
    for i, q in enumerate(long_answer, 1):
        if not isinstance(q, dict):
            continue
        p = doc.add_paragraph()
        p.add_run(f"Q{i}. {q.get('question', '')}").bold = True
        doc.add_paragraph(str(q.get("answer", "")))
        doc.add_paragraph()

    _heading(doc, "Assertion-Reason Questions", 1)
    for i, q in enumerate(assertion_reason, 1):
        if not isinstance(q, dict):
            continue
        p = doc.add_paragraph()
        p.add_run(f"Q{i}. {q.get('question', '')}").bold = True
        opts = q.get("options", {})
        if isinstance(opts, dict):
            for key in ["i", "ii", "iii", "iv"]:
                doc.add_paragraph(f"    ({key}) {opts.get(key, '')}")
        _bold_para(doc, "Answer", q.get("answer", ""))
        explanation = q.get("explanation", "")
        if explanation:
            _bold_para(doc, "Explanation", explanation)
        doc.add_paragraph()

    _heading(doc, "Case Studies", 1)
    for i, cs in enumerate(case_studies, 1):
        if not isinstance(cs, dict):
            continue
        _heading(doc, f"Case Study {i}", 2)
        doc.add_paragraph(cs.get("case_study", ""))
        for sub in _ensure_list(cs.get("questions", [])):
            if not isinstance(sub, dict):
                continue
            p = doc.add_paragraph()
            p.add_run(f"({sub.get('sub_id', '')}) {sub.get('question', '')}").bold = True
            _bold_para(doc, "Answer", sub.get("answer", ""))
        doc.add_paragraph()

    # ── WORKER 10: Tests ─────────────────────────────────────────────────────
    print(f"[DOCGEN] Section: Tests (+{time.time()-t0:.1f}s)")
    tests = _ensure_list(results.get("tests", {}).get("tests", []) if isinstance(results.get("tests"), dict) else [])

    for test in tests:
        if not isinstance(test, dict):
            continue
        _heading(doc, f"Test: {test.get('test_id', '')}  ({test.get('total_marks', 25)} Marks)", 1)
        sections = test.get("sections", {})
        if not isinstance(sections, dict):
            continue

        _heading(doc, "Section A — MCQs (4 × 1 = 4 Marks)", 2)
        for i, q in enumerate(_ensure_list(sections.get("mcqs", [])), 1):
            if not isinstance(q, dict):
                continue
            p = doc.add_paragraph()
            p.add_run(f"Q{i}. {q.get('question', '')}").bold = True
            opts = q.get("options", {})
            if isinstance(opts, dict):
                for key in ["A", "B", "C", "D"]:
                    doc.add_paragraph(f"    ({key}) {opts.get(key, '')}")
            _bold_para(doc, "Answer", q.get("answer", ""))
            doc.add_paragraph()

        _heading(doc, "Section B — Assertion-Reason (3 × 1 = 3 Marks)", 2)
        for i, q in enumerate(_ensure_list(sections.get("assertion_reason", [])), 1):
            if not isinstance(q, dict):
                continue
            p = doc.add_paragraph()
            p.add_run(f"Q{i}. {q.get('question', '')}").bold = True
            opts = q.get("options", {})
            if isinstance(opts, dict):
                for key in ["i", "ii", "iii", "iv"]:
                    doc.add_paragraph(f"    ({key}) {opts.get(key, '')}")
            _bold_para(doc, "Answer", q.get("answer", ""))
            explanation = q.get("explanation", "")
            if explanation:
                _bold_para(doc, "Explanation", explanation)
            doc.add_paragraph()

        _heading(doc, "Section C — Short Answer (2 × 2 = 4 Marks)", 2)
        for i, q in enumerate(_ensure_list(sections.get("short_answer", [])), 1):
            if not isinstance(q, dict):
                continue
            p = doc.add_paragraph()
            p.add_run(f"Q{i}. {q.get('question', '')}").bold = True
            _bold_para(doc, "Answer", q.get("answer", ""))
            doc.add_paragraph()

        _heading(doc, "Section D — Medium Answer (3 × 3 = 9 Marks)", 2)
        for i, q in enumerate(_ensure_list(sections.get("medium_answer", [])), 1):
            if not isinstance(q, dict):
                continue
            p = doc.add_paragraph()
            p.add_run(f"Q{i}. {q.get('question', '')}").bold = True
            doc.add_paragraph(str(q.get("answer", "")))
            doc.add_paragraph()

        _heading(doc, "Section E — Long Answer (1 × 5 = 5 Marks)", 2)
        for i, q in enumerate(_ensure_list(sections.get("long_answer", [])), 1):
            if not isinstance(q, dict):
                continue
            p = doc.add_paragraph()
            p.add_run(f"Q{i}. {q.get('question', '')}").bold = True
            doc.add_paragraph(str(q.get("answer", "")))
            doc.add_paragraph()

    print(f"[DOCGEN] Saving to buffer (+{time.time()-t0:.1f}s)")
    buf = io.BytesIO()
    doc.save(buf)
    buf.seek(0)
    result = buf.read()
    print(f"[DOCGEN] DONE — {len(result)} bytes, total {time.time()-t0:.1f}s")
    return result
