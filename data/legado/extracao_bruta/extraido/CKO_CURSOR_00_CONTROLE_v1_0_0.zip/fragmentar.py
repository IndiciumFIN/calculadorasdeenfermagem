#!/usr/bin/env python3
"""CKO — fracionamento reproduzível e não destrutivo de PDFs/arquivos.
SOMENTE saídas locais; não lê/grava Drive, Supabase ou GitHub.

Autoridade: PDF de origem. Transcrições servem a navegação, não homologação.
"""
import argparse
import csv
import hashlib
import json
import os
import re
from pathlib import Path
import shutil
import sys

BLOCK=1024*1024

def sha256(path):
    h=hashlib.sha256()
    with open(path,'rb') as f:
        for block in iter(lambda:f.read(BLOCK),b''):
            h.update(block)
    return h.hexdigest()

def sha_bytes(buf):
    return hashlib.sha256(buf).hexdigest()

def write_json(path, obj):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(obj,ensure_ascii=False,indent=2,sort_keys=True)+'\n',encoding='utf-8')

def fragment_pdf(src, out, pages_per=25, compare_pix=False, engine='pymupdf'):
    import fitz
    src=Path(src);out=Path(out)
    if pages_per<=0:raise ValueError('pages_per > 0')
    doc=fitz.open(str(src)); n=len(doc)
    if n==0:raise ValueError('PDF vazio')
    slug=out.name
    out.mkdir(parents=True, exist_ok=True)
    entries=[];pages=[];sum_chars=0;low=[];whitespace_normalized_pages=[]
    for start in range(0,n,pages_per):
        end=min(n,start+pages_per)
        stem=f'{slug}__P{start+1:04d}-P{end:04d}'
        p_pdf=out/(stem+'.pdf');p_txt=out/(stem+'.pages.jsonl')
        if engine=='pypdf':
            from pypdf import PdfReader, PdfWriter
            if start==0: reader=PdfReader(str(src))
            writer=PdfWriter()
            for page_index in range(start,end): writer.add_page(reader.pages[page_index])
            writer.write(str(p_pdf))
        elif engine=='pymupdf':
            sub=fitz.open();sub.insert_pdf(doc,from_page=start,to_page=end-1,annots=True,links=True)
            sub.save(str(p_pdf),garbage=3,deflate=True)
            sub.close()
        else: raise ValueError('engine deve ser pypdf ou pymupdf')
        with p_txt.open('w',encoding='utf-8',newline='\n') as f:
            for pi in range(start,end):
                t=doc[pi].get_text(sort=False)
                data={'original_page_1_based':pi+1,'fragment_page_1_based':pi-start+1,'text':t,
                      'text_sha256':sha_bytes(t.encode('utf-8')),'chars':len(t),'extraction':'pymupdf.get_text(sort=False)'}
                f.write(json.dumps(data,ensure_ascii=False)+'\n');sum_chars+=len(t)
                if len(t)<100: low.append(pi+1)
        frag=fitz.open(str(p_pdf))
        assert len(frag)==end-start
        pix_ok=True
        for i in range(end-start):
            txt=frag[i].get_text(sort=False)
            orig=doc[start+i].get_text(sort=False)
            if txt!=orig:
                if re.sub(r'\s+',' ',txt).strip()!=re.sub(r'\s+',' ',orig).strip():
                    raise RuntimeError(f'Divergência NÃO trivial de texto p. {start+i+1}: {stem}')
                whitespace_normalized_pages.append(start+i+1)
        if compare_pix:
            for i in sorted(set([0,(end-start)-1])):
                # Renderiza a mesma página, detecta conteúdo visual perdido.
                ma=fitz.Matrix(0.85,0.85)
                a=doc[start+i].get_pixmap(matrix=ma,alpha=False,annots=True)
                b=frag[i].get_pixmap(matrix=ma,alpha=False,annots=True)
                if a.width!=b.width or a.height!=b.height or a.samples!=b.samples: pix_ok=False
        frag.close()
        if not pix_ok: raise RuntimeError(f'Divergência visual nas páginas extremas de {stem}')
        entries.append({'id':stem,'start_page_1_based':start+1,'end_page_1_based':end,'pages':end-start,
                        'pdf_file':p_pdf.name,'pdf_sha256':sha256(p_pdf),'pdf_bytes':p_pdf.stat().st_size,
                        'transcript_file':p_txt.name,'transcript_sha256':sha256(p_txt),
                        'transcript_bytes':p_txt.stat().st_size,'page_text_equality':'PASS_OR_WHITESPACE_ONLY',
                        'visual_compare_first_last':'PASS' if compare_pix else 'NOT_RUN'})
    assert sum(e['pages'] for e in entries)==n
    man={'schema':'cko.cursor.pdf_fragments.v1','status':'CANDIDATE_SOURCE_SNAPSHOT','type':'PDF_ANALYSIS_PARTS',
         'source_name':src.name,'source_sha256':sha256(src),'source_bytes':src.stat().st_size,
         'source_total_pages':n,'pages_per_part':pages_per,'total_parts':len(entries),'pdf_split_engine':engine,
         'total_extracted_chars':sum_chars,'low_text_pages_lt_100_chars':low,
         'whitespace_only_differences':whitespace_normalized_pages,
         'integrity_method':['original byte SHA-256','continuous PDF page coverage','text equality each page',
                             'fragment file SHA-256','first and last page pixel compare' if compare_pix else 'pixel compare not run'],
         'disclaimer':'Paginação original é 1-based. PDFs originais são fonte da verdade. Partes reencodificadas não se concatenam byte a byte para recuperar o PDF original. OCR não executado; texto extraído é apenas índice de apoio.',
         'fragments':entries}
    write_json(out/'MANIFEST.json',man)
    doc.close();return man

def verify_pdf(out, src=None, render=False):
    import fitz
    out=Path(out)
    j=json.loads((out/'MANIFEST.json').read_text(encoding='utf-8'))
    assert j['schema']=='cko.cursor.pdf_fragments.v1'
    if src is not None:
        src=Path(src)
        assert sha256(src)==j['source_sha256']
        doc=fitz.open(str(src))
        assert len(doc)==j['source_total_pages']
    else:doc=None
    expect=1
    for x in j['fragments']:
        assert x['start_page_1_based']==expect, (out,x['start_page_1_based'],expect)
        assert x['end_page_1_based']==expect+x['pages']-1
        p=out/x['pdf_file']; t=out/x['transcript_file']
        assert sha256(p)==x['pdf_sha256']
        assert sha256(t)==x['transcript_sha256']
        d=fitz.open(str(p)); assert len(d)==x['pages']
        lines=t.read_text(encoding='utf-8').splitlines();assert len(lines)==x['pages']
        for i,line in enumerate(lines):
            o=json.loads(line)
            assert o['original_page_1_based']==expect+i
            assert o['fragment_page_1_based']==i+1
            assert o['text_sha256']==sha_bytes(o['text'].encode('utf-8'))
            segtext=d[i].get_text(sort=False)
            assert re.sub(r'\s+',' ',segtext).strip()==re.sub(r'\s+',' ',o['text']).strip()
            if doc is not None:
                assert doc[expect+i-1].get_text(sort=False)==o['text']
        d.close();expect+=x['pages']
    assert expect-1==j['source_total_pages']
    if doc:doc.close()
    return {'status':'PASS','pages':expect-1,'fragments':len(j['fragments'])}

def fragment_bytes(src,out,max_bytes=7_000_000):
    """Cortes binários exatos, adequados a qualquer arquivo, com reconstrução bit a bit."""
    src=Path(src);out=Path(out);out.mkdir(parents=True,exist_ok=True)
    if not 0<max_bytes<10_000_000:raise ValueError('max_bytes deve ser de 1 a 9.999.999')
    parts=[]
    with src.open('rb') as r:
        index=0
        while True:
            b=r.read(max_bytes)
            if not b:break
            index+=1
            name=f'{src.name}.part{index:04d}'
            p=out/name;p.write_bytes(b)
            parts.append({'index':index,'file':name,'bytes':len(b),'sha256':sha256(p)})
    man={'schema':'cko.cursor.exact_binary_parts.v1','source_name':src.name,'source_sha256':sha256(src),
         'source_bytes':src.stat().st_size,'method':'BYTE_EXACT_CONTIGUOUS','parts':parts}
    write_json(out/'REBUILD_MANIFEST.json',man)
    return man

def verify_bytes(folder, destination=None):
    folder=Path(folder)
    man=json.loads((folder/'REBUILD_MANIFEST.json').read_text(encoding='utf-8'))
    h=hashlib.sha256();total=0
    if destination:
        destination=Path(destination);destination.parent.mkdir(parents=True,exist_ok=True)
        fd=destination.open('wb')
    else:fd=None
    try:
        for i,p in enumerate(man['parts'],1):
            assert p['index']==i
            path=folder/p['file'];assert path.stat().st_size==p['bytes']
            assert sha256(path)==p['sha256']
            with path.open('rb') as f:
                for b in iter(lambda:f.read(BLOCK),b''):
                    h.update(b);total+=len(b)
                    if fd:fd.write(b)
    finally:
        if fd:fd.close()
    assert h.hexdigest()==man['source_sha256'] and total==man['source_bytes']
    return {'status':'PASS','bytes':total,'sha256':h.hexdigest()}

def main():
    p=argparse.ArgumentParser(description=__doc__)
    sub=p.add_subparsers(dest='command',required=True)
    for name in ['pdf','binary']:
        x=sub.add_parser(name);x.add_argument('source');x.add_argument('output')
        if name=='pdf':x.add_argument('--pages',type=int,default=25);x.add_argument('--render',action='store_true');x.add_argument('--engine',choices=['pymupdf','pypdf'],default='pymupdf')
        else:x.add_argument('--max-bytes',type=int,default=7_000_000)
    v=sub.add_parser('verify-pdf');v.add_argument('output');v.add_argument('--source')
    b=sub.add_parser('verify-binary');b.add_argument('output');b.add_argument('--rebuild')
    a=p.parse_args()
    if a.command=='pdf':result=fragment_pdf(a.source,a.output,a.pages,a.render,a.engine)
    elif a.command=='binary':result=fragment_bytes(a.source,a.output,a.max_bytes)
    elif a.command=='verify-pdf':result=verify_pdf(a.output,a.source)
    else:result=verify_bytes(a.output,a.rebuild)
    print(json.dumps({k:v for k,v in result.items() if k not in ['fragments','parts']},ensure_ascii=False,indent=2))

if __name__=='__main__':main()
