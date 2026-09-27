import os
import sys
from rapidocr_onnxruntime import RapidOCR

img_dir = r'C:\Users\应轩旸\Desktop\math\images'
output_dir = r'c:\Users\应轩旸\Documents\trae_projects\001\ocr_output'
os.makedirs(output_dir, exist_ok=True)

print("Loading OCR engine...", flush=True)
engine = RapidOCR()
print("Engine loaded.", flush=True)

# Get all image files
img_files = sorted([f for f in os.listdir(img_dir) if f.endswith('.png')])

# Group by PDF
pdf_groups = {}
for f in img_files:
    base = f.split('_page_')[0]
    if base not in pdf_groups:
        pdf_groups[base] = []
    pdf_groups[base].append(f)

for base, files in pdf_groups.items():
    print(f"Processing {base} ({len(files)} pages)...", flush=True)
    all_text = ''
    for i, f in enumerate(files):
        img_path = os.path.join(img_dir, f)
        try:
            result, elapse = engine(img_path)
            text = ''
            if result:
                for line in result:
                    text += line[1] + '\n'
            page_num = f.split('_page_')[1].replace('.png', '')
            all_text += f'--- Page {page_num} ---\n{text}\n'
            if (i+1) % 5 == 0:
                print(f"  {base}: {i+1}/{len(files)} pages done", flush=True)
        except Exception as e:
            page_num = f.split('_page_')[1].replace('.png', '')
            all_text += f'--- Page {page_num} ---\n[OCR ERROR: {e}]\n\n'
            print(f"  Error on {f}: {e}", flush=True)
    
    out_path = os.path.join(output_dir, f'{base}_ocr.txt')
    with open(out_path, 'w', encoding='utf-8') as fout:
        fout.write(all_text)
    print(f"  Saved {base}: {len(all_text)} chars", flush=True)

print("OCR complete!", flush=True)
