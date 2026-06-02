"""Search 2019-2024 board PDFs for any TCRWP-related contract approval, motion, or vote.
Writes hits + progress to tcrwp_post2018_results.txt (line-buffered)."""
import os, re, sys
from pathlib import Path
import pdfplumber, pypdf

ROOT = Path(r'C:\Dev\TroySD')
folders = [f for f in ROOT.iterdir() if f.is_dir() and re.match(r'^(2019|2020|2021|2022|2023|2024)', f.name)]
folders.sort()

ANY_TCRWP = re.compile(r'(Teachers College|Reading and Writing Project|Reading Writing Project|TCRWP|Lucy Calkins)', re.I)
MOTION_CONTEXT = re.compile(r'(BE IT THEREFORE RESOLVED|RESOLUTION|It was moved by|moved by .{0,80} seconded|approve.{0,300}contract|approve.{0,300}professional|authorization|adopt.{0,200}curriculum|approved the .{0,120}contract)', re.I)

OUT = Path(__file__).parent / 'tcrwp_post2018_results.txt'
out = open(OUT, 'w', buffering=1, encoding='utf-8')

def log(msg):
    out.write(msg + '\n')
    print(msg, flush=True)

pdf_count = 0
hit_count = 0
folder_count = 0
results = []

log(f'Folders to scan: {len(folders)}')
for folder in folders:
    folder_count += 1
    pdfs = list(folder.glob('*.pdf'))
    if folder_count % 10 == 0:
        log(f'[progress] folder {folder_count}/{len(folders)}: {folder.name} (pdfs={pdf_count}, hits={hit_count})')
    for pdf in pdfs:
        pdf_count += 1
        try:
            text = ''
            try:
                with pdfplumber.open(pdf) as p:
                    text = '\n'.join(page.extract_text() or '' for page in p.pages)
            except Exception:
                with open(pdf, 'rb') as f:
                    r = pypdf.PdfReader(f)
                    text = '\n'.join(p.extract_text() or '' for p in r.pages)

            if not ANY_TCRWP.search(text):
                continue
            for m in ANY_TCRWP.finditer(text):
                start = max(0, m.start() - 1500)
                end = min(len(text), m.end() + 1500)
                window = text[start:end]
                if MOTION_CONTEXT.search(window):
                    hit_count += 1
                    log('=' * 80)
                    log(f'HIT: {folder.name} / {pdf.name}')
                    log(f'TCRWP keyword: {m.group()}')
                    log('--- window ---')
                    log(window[:2000])
                    log('--- end ---')
                    break
        except Exception as e:
            log(f'ERR {pdf.name}: {e}')

log(f'\n=== DONE ===')
log(f'Folders scanned: {len(folders)}')
log(f'PDFs scanned: {pdf_count}')
log(f'Motion-near-TCRWP hits: {hit_count}')
out.close()
