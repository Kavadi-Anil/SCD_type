import os

def create_notebook_html():
    html_code = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>How AI Has Changed Data Engineering in 2026 - Handwritten Spiral Notebook Notes</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Architects+Daughter&family=Caveat:wght@500;700&family=Gochi+Hand&family=Kalam:wght@300;400;700&family=Patrick+Hand&family=Schoolbell&display=swap" rel="stylesheet">
<style>
  @page {
    size: A4 portrait;
    margin: 10mm;
  }

  * {
    box-sizing: border-box;
    -webkit-print-color-adjust: exact;
    print-color-adjust: exact;
  }

  body {
    margin: 0;
    padding: 20px 0;
    background: #e8e4dc;
    font-family: 'Kalam', 'Patrick Hand', cursive, sans-serif;
    color: #1a365d;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 30px;
    overflow-x: auto;
  }

  /* Notebook Page (A4 Realistic Styling) */
  .notebook-page {
    position: relative;
    width: 210mm;
    min-height: 297mm;
    background-color: #fdfcf7;
    background-image: 
      radial-gradient(#f0ede4 15%, transparent 16%),
      radial-gradient(#f0ede4 15%, transparent 16%);
    background-size: 60px 60px;
    background-position: 0 0, 30px 30px;
    box-shadow: 
      0 10px 35px rgba(0, 0, 0, 0.18),
      0 2px 8px rgba(0, 0, 0, 0.08),
      inset 0 0 80px rgba(220, 210, 195, 0.25);
    border-radius: 4px 14px 14px 4px;
    padding: 22mm 20mm 20mm 34mm; /* Left padding for spiral margin */
    overflow: visible;
    page-break-after: always;
    break-after: page;
  }

  @media print {
    body {
      background: none;
      padding: 0;
      gap: 0;
    }
    .notebook-page {
      box-shadow: none;
      border-radius: 0;
      margin: 0;
      page-break-after: always;
      break-after: page;
      width: 210mm;
      height: 297mm;
      min-height: 297mm;
      max-height: 297mm;
    }
  }

  /* Spiral Binding Track & Rings */
  .spiral-track {
    position: absolute;
    left: 0;
    top: 0;
    bottom: 0;
    width: 30mm;
    pointer-events: none;
  }

  .spiral-spine-shadow {
    position: absolute;
    left: 20mm;
    top: 0;
    bottom: 0;
    width: 8px;
    background: linear-gradient(to right, rgba(0,0,0,0.12), transparent);
  }

  .spiral-hole {
    position: absolute;
    left: 10mm;
    width: 6.5mm;
    height: 6.5mm;
    border-radius: 50%;
    background: #4a453f;
    box-shadow: 
      inset 0 2px 4px rgba(0,0,0,0.8),
      0 1px 1px rgba(255,255,255,0.8);
  }

  .spiral-ring {
    position: absolute;
    left: 4.5mm;
    width: 14mm;
    height: 7mm;
    border: 2.2mm solid #9e9e9e;
    border-color: #b0bec5 #546e7a #37474f #cfd8dc;
    border-radius: 40% 60% 60% 40% / 50% 50% 50% 50%;
    box-shadow: 
      0 3px 5px rgba(0,0,0,0.35),
      inset 0 1px 2px rgba(255,255,255,0.7);
    transform: rotate(-12deg);
  }

  /* Page Top Header / Notebook Meta */
  .page-header {
    display: flex;
    justify-content: space-between;
    align-items: baseline;
    border-bottom: 2px dashed #d1c7b7;
    padding-bottom: 6px;
    margin-bottom: 16px;
    font-family: 'Patrick Hand', cursive;
    font-size: 14px;
    color: #5c6b73;
    break-after: avoid;
    page-break-after: avoid;
  }

  .page-number {
    font-weight: bold;
    color: #c62828;
    background: rgba(255, 235, 59, 0.3);
    padding: 2px 10px;
    border-radius: 12px;
    border: 1px dashed #fbc02d;
  }

  /* Handwriting Typography */
  h1, h2, h3, h4 {
    font-family: 'Architects Daughter', 'Caveat', cursive;
    color: #b71c1c; /* Red handwritten headings */
    margin: 12px 0 8px 0;
    line-height: 1.25;
    letter-spacing: 0.3px;
    break-after: avoid;
    page-break-after: avoid;
  }

  h1 {
    font-size: 26px;
    text-decoration: none;
    display: inline-block;
    border-bottom: 2.5px solid #d32f2f;
    padding-bottom: 4px;
    transform: rotate(-0.5deg);
  }

  h2 {
    font-size: 21px;
    transform: rotate(0.3deg);
    border-bottom: 1.5px dashed rgba(183, 28, 28, 0.4);
    padding-bottom: 3px;
  }

  h3 {
    font-size: 18px;
    color: #c62828;
  }

  p, li, td, th, div {
    font-family: 'Kalam', 'Patrick Hand', cursive;
    font-size: 15px;
    line-height: 1.5;
    color: #0f3460; /* Blue handwritten text */
  }

  ul, ol {
    margin: 8px 0 12px 20px;
    padding: 0;
  }

  li {
    margin-bottom: 5px;
  }

  /* Yellow Highlighter */
  .hl {
    background: linear-gradient(104deg, rgba(255,245,157,0) 0.9%, rgba(255,238,88,0.85) 2.4%, rgba(255,241,118,0.75) 96%, rgba(255,245,157,0) 98.5%);
    border-radius: 3px;
    padding: 1px 5px;
    box-decoration-break: clone;
    -webkit-box-decoration-break: clone;
    color: #0d2137;
    font-weight: 700;
  }

  .hl-red {
    background: linear-gradient(104deg, rgba(255,205,210,0) 0.9%, rgba(255,205,210,0.85) 2.4%, rgba(255,205,210,0.75) 96%, rgba(255,205,210,0) 98.5%);
    padding: 1px 5px;
    color: #b71c1c;
    font-weight: bold;
    border-radius: 3px;
  }

  .hl-green {
    background: linear-gradient(104deg, rgba(200,230,201,0) 0.9%, rgba(165,214,167,0.85) 2.4%, rgba(200,230,201,0.75) 96%, rgba(200,230,201,0) 98.5%);
    padding: 1px 5px;
    color: #1b5e20;
    font-weight: bold;
    border-radius: 3px;
  }

  /* Callout Badges */
  .badge {
    display: inline-block;
    padding: 2px 8px;
    border-radius: 4px;
    font-family: 'Architects Daughter', cursive;
    font-size: 13px;
    font-weight: bold;
    letter-spacing: 0.5px;
    margin-right: 6px;
    box-shadow: 1px 2px 4px rgba(0,0,0,0.1);
  }

  .badge-imp {
    background: #ffcdd2;
    color: #b71c1c;
    border: 1.5px solid #e57373;
    transform: rotate(-1.5deg);
  }

  .badge-memory {
    background: #fff9c4;
    color: #f57f17;
    border: 1.5px solid #fbc02d;
    transform: rotate(1.2deg);
  }

  .badge-faq {
    background: #e1bee7;
    color: #4a148c;
    border: 1.5px solid #ba68c8;
    transform: rotate(-1deg);
  }

  .badge-shortcut {
    background: #b2dfdb;
    color: #004d40;
    border: 1.5px solid #4db6ac;
    transform: rotate(1deg);
  }

  /* Handwritten Boxes */
  .note-box {
    position: relative;
    background: rgba(255, 253, 231, 0.7);
    border: 2px solid #546e7a;
    border-radius: 8px 16px 6px 14px;
    padding: 12px 14px;
    margin: 12px 0;
    box-shadow: 2px 3px 8px rgba(0,0,0,0.06);
    break-inside: avoid;
    page-break-inside: avoid;
  }

  .note-box-red {
    background: rgba(255, 235, 238, 0.6);
    border: 2px solid #d32f2f;
  }

  .note-box-blue {
    background: rgba(227, 242, 253, 0.6);
    border: 2px solid #1976d2;
  }

  /* Handwritten Tape Effect */
  .tape {
    position: absolute;
    top: -8px;
    left: 25px;
    width: 60px;
    height: 16px;
    background: rgba(255, 255, 255, 0.7);
    border-left: 2px dashed rgba(0,0,0,0.15);
    border-right: 2px dashed rgba(0,0,0,0.15);
    box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    transform: rotate(-2deg);
  }

  /* Handwritten Tables */
  .hand-table {
    width: 100%;
    border-collapse: collapse;
    margin: 12px 0;
    break-inside: avoid;
    page-break-inside: avoid;
  }

  .hand-table th {
    font-family: 'Architects Daughter', cursive;
    color: #b71c1c;
    border-bottom: 2.5px solid #c62828;
    padding: 6px 10px;
    text-align: left;
    font-size: 15px;
  }

  .hand-table td {
    border-bottom: 1px dashed #b0bec5;
    padding: 6px 10px;
    font-size: 14px;
    color: #0f3460;
  }

  .hand-table tr:last-child td {
    border-bottom: 2px solid #90a4ae;
  }

  /* Diagram & Mind Map Containers */
  .diagram-container {
    width: 100%;
    margin: 12px 0;
    text-align: center;
    break-inside: avoid;
    page-break-inside: avoid;
  }

  svg.hand-drawn {
    max-width: 100%;
    height: auto;
    filter: drop-shadow(1px 2px 3px rgba(0,0,0,0.08));
  }

  /* Handwritten Underline */
  .pen-underline {
    position: relative;
    display: inline-block;
  }
  .pen-underline::after {
    content: '';
    position: absolute;
    left: 0;
    bottom: -2px;
    width: 100%;
    height: 3px;
    background: #d32f2f;
    border-radius: 2px;
    transform: rotate(-0.6deg);
  }

  .quote-statement {
    font-size: 17px;
    font-family: 'Caveat', cursive;
    font-weight: 700;
    color: #b71c1c;
    border-left: 4px solid #d32f2f;
    padding-left: 12px;
    margin: 10px 0;
    font-style: italic;
  }

  .d-flex {
    display: flex;
    gap: 12px;
  }
  .col-half {
    flex: 1;
  }
</style>
</head>
<body>

<!-- ========================================================================= -->
<!-- PAGE 1: INTRODUCTION, CREDIBILITY, GROUND TRUTH VS HYPE                  -->
<!-- ========================================================================= -->
<div class="notebook-page" id="page-1">
  <div class="spiral-track">
    <div class="spiral-spine-shadow"></div>
    <!-- 20 Spiral Rings -->
    <script>
      /* Ring injector in pure inline CSS for exact rendering */
    </script>
    <div style="top: 15mm;" class="spiral-hole"></div><div style="top: 14mm;" class="spiral-ring"></div>
    <div style="top: 28mm;" class="spiral-hole"></div><div style="top: 27mm;" class="spiral-ring"></div>
    <div style="top: 41mm;" class="spiral-hole"></div><div style="top: 40mm;" class="spiral-ring"></div>
    <div style="top: 54mm;" class="spiral-hole"></div><div style="top: 53mm;" class="spiral-ring"></div>
    <div style="top: 67mm;" class="spiral-hole"></div><div style="top: 66mm;" class="spiral-ring"></div>
    <div style="top: 80mm;" class="spiral-hole"></div><div style="top: 79mm;" class="spiral-ring"></div>
    <div style="top: 93mm;" class="spiral-hole"></div><div style="top: 92mm;" class="spiral-ring"></div>
    <div style="top: 106mm;" class="spiral-hole"></div><div style="top: 105mm;" class="spiral-ring"></div>
    <div style="top: 119mm;" class="spiral-hole"></div><div style="top: 118mm;" class="spiral-ring"></div>
    <div style="top: 132mm;" class="spiral-hole"></div><div style="top: 131mm;" class="spiral-ring"></div>
    <div style="top: 145mm;" class="spiral-hole"></div><div style="top: 144mm;" class="spiral-ring"></div>
    <div style="top: 158mm;" class="spiral-hole"></div><div style="top: 157mm;" class="spiral-ring"></div>
    <div style="top: 171mm;" class="spiral-hole"></div><div style="top: 170mm;" class="spiral-ring"></div>
    <div style="top: 184mm;" class="spiral-hole"></div><div style="top: 183mm;" class="spiral-ring"></div>
    <div style="top: 197mm;" class="spiral-hole"></div><div style="top: 196mm;" class="spiral-ring"></div>
    <div style="top: 210mm;" class="spiral-hole"></div><div style="top: 209mm;" class="spiral-ring"></div>
    <div style="top: 223mm;" class="spiral-hole"></div><div style="top: 222mm;" class="spiral-ring"></div>
    <div style="top: 236mm;" class="spiral-hole"></div><div style="top: 235mm;" class="spiral-ring"></div>
    <div style="top: 249mm;" class="spiral-hole"></div><div style="top: 248mm;" class="spiral-ring"></div>
    <div style="top: 262mm;" class="spiral-hole"></div><div style="top: 261mm;" class="spiral-ring"></div>
    <div style="top: 275mm;" class="spiral-hole"></div><div style="top: 274mm;" class="spiral-ring"></div>
  </div>

  <div class="page-header">
    <span>TOPIC: HOW AI CHANGED DATA ENGINEERING (2026)</span>
    <span>CHAPTER 1: GROUND TRUTH</span>
    <span class="page-number">PAGE 01</span>
  </div>

  <h1>How AI Has Changed Data Engineering in 2026</h1>
  <div style="font-size: 16px; margin: 4px 0 12px; color: #546e7a;">
    <i>Sub-title: The Ground Truth, Real Market Shifts & The Future</i>
  </div>

  <div class="note-box note-box-blue">
    <div class="tape"></div>
    <span class="badge badge-imp">SPEAKER PROFILE</span>
    <h3 style="margin-top:2px;">Narendra Kumar (Senior Data Architect)</h3>
    <ul>
      <li><span class="hl">12+ Years in IT</span>: Delivered 10+ end-to-end enterprise projects on Databricks & Azure.</li>
      <li>Currently driving <span class="hl">2-3 live cutting-edge projects</span> in active production.</li>
      <li><span class="hl">Databricks MVP</span>: Regular direct touchbase with Databricks engineering teams & product roadmaps.</li>
      <li>Active mentor guiding corporate mentees through real enterprise shifts.</li>
    </ul>
  </div>

  <h2>Chapter 1: The 2026 Ground Reality vs. Hype</h2>
  <p>The market in 2026 is filled with extreme noise and social media exaggeration:</p>
  
  <div class="d-flex" style="margin: 10px 0;">
    <div class="note-box note-box-red col-half" style="margin:0;">
      <h4 style="color:#b71c1c; margin:0 0 6px 0;">❌ The AI Hype Myth</h4>
      <p style="margin:0; font-size:14px;">"AI writes all code now. Data engineering is 100% automated and dead. Freshers cannot get jobs."</p>
    </div>
    <div class="note-box col-half" style="background:rgba(232, 245, 233, 0.7); border:2px solid #2e7d32; margin:0;">
      <h4 style="color:#2e7d32; margin:0 0 6px 0;">✔ The Ground Reality</h4>
      <p style="margin:0; font-size:14px;">"AI transforms <span class="hl-green">productivity & interfaces</span>. Core distributed data fundamentals remain mandatory for hiring!"</p>
    </div>
  </div>

  <div class="quote-statement">
    "The fundamentals of data engineering get you in; building AI skills keeps you relevant and promoted."
  </div>

  <h2>The 3 Pillars of AI Impact</h2>
  <p>Narendra Kumar categorizes the entire 2026 transformation into <span class="hl">3 Core Areas</span>:</p>

  <div class="diagram-container">
    <svg class="hand-drawn" width="540" height="130" viewBox="0 0 540 130">
      <!-- Area 1 -->
      <rect x="10" y="15" width="160" height="95" rx="8" fill="#fff9c4" stroke="#fbc02d" stroke-width="2.2" stroke-dasharray="2,1"/>
      <text x="90" y="40" font-family="Architects Daughter" font-size="14" font-weight="bold" fill="#b71c1c" text-anchor="middle">AREA 1: PRODUCTIVITY</text>
      <text x="90" y="62" font-family="Kalam" font-size="12" fill="#0f3460" text-anchor="middle">• Code & Pipeline Gen</text>
      <text x="90" y="80" font-family="Kalam" font-size="12" fill="#0f3460" text-anchor="middle">• Auto Test & Living Docs</text>
      <text x="90" y="98" font-family="Kalam" font-size="12" fill="#0f3460" text-anchor="middle">• Reusable "AI Skills"</text>

      <!-- Area 2 -->
      <rect x="190" y="15" width="160" height="95" rx="8" fill="#e1f5fe" stroke="#0288d1" stroke-width="2.2"/>
      <text x="270" y="40" font-family="Architects Daughter" font-size="14" font-weight="bold" fill="#b71c1c" text-anchor="middle">AREA 2: AI-READY</text>
      <text x="270" y="62" font-family="Kalam" font-size="12" fill="#0f3460" text-anchor="middle">• Table/Col Metadata</text>
      <text x="270" y="80" font-family="Kalam" font-size="12" fill="#0f3460" text-anchor="middle">• Metric Views (Semantics)</text>
      <text x="270" y="98" font-family="Kalam" font-size="12" fill="#0f3460" text-anchor="middle">• Enterprise Ontology</text>

      <!-- Area 3 -->
      <rect x="370" y="15" width="160" height="95" rx="8" fill="#f3e5f5" stroke="#7b1fa2" stroke-width="2.2" stroke-dasharray="3,1"/>
      <text x="450" y="40" font-family="Architects Daughter" font-size="14" font-weight="bold" fill="#b71c1c" text-anchor="middle">AREA 3: APPLICATIONS</text>
      <text x="450" y="62" font-family="Kalam" font-size="12" fill="#0f3460" text-anchor="middle">• RAG Architectures</text>
      <text x="450" y="80" font-family="Kalam" font-size="12" fill="#0f3460" text-anchor="middle">• Unstructured Parsing</text>
      <text x="450" y="98" font-family="Kalam" font-size="12" fill="#0f3460" text-anchor="middle">• Natural Language Q&A</text>
    </svg>
  </div>

  <div class="note-box" style="margin-top:6px;">
    <span class="badge badge-shortcut">KEY LESSON</span>
    <b>Pre-AI DE</b> ended at Silver/Gold tables for BI reports. <b>2026 AI DE</b> builds structured semantic platforms consumed by autonomous AI agents & humans alike!
  </div>
</div>

<!-- ========================================================================= -->
<!-- PAGE 2: AREA 1 (PRODUCTIVITY) & AREA 2 (AI-READY DATA PLATFORMS)         -->
<!-- ========================================================================= -->
<div class="notebook-page" id="page-2">
  <div class="spiral-track">
    <div class="spiral-spine-shadow"></div>
    <div style="top: 15mm;" class="spiral-hole"></div><div style="top: 14mm;" class="spiral-ring"></div>
    <div style="top: 28mm;" class="spiral-hole"></div><div style="top: 27mm;" class="spiral-ring"></div>
    <div style="top: 41mm;" class="spiral-hole"></div><div style="top: 40mm;" class="spiral-ring"></div>
    <div style="top: 54mm;" class="spiral-hole"></div><div style="top: 53mm;" class="spiral-ring"></div>
    <div style="top: 67mm;" class="spiral-hole"></div><div style="top: 66mm;" class="spiral-ring"></div>
    <div style="top: 80mm;" class="spiral-hole"></div><div style="top: 79mm;" class="spiral-ring"></div>
    <div style="top: 93mm;" class="spiral-hole"></div><div style="top: 92mm;" class="spiral-ring"></div>
    <div style="top: 106mm;" class="spiral-hole"></div><div style="top: 105mm;" class="spiral-ring"></div>
    <div style="top: 119mm;" class="spiral-hole"></div><div style="top: 118mm;" class="spiral-ring"></div>
    <div style="top: 132mm;" class="spiral-hole"></div><div style="top: 131mm;" class="spiral-ring"></div>
    <div style="top: 145mm;" class="spiral-hole"></div><div style="top: 144mm;" class="spiral-ring"></div>
    <div style="top: 158mm;" class="spiral-hole"></div><div style="top: 157mm;" class="spiral-ring"></div>
    <div style="top: 171mm;" class="spiral-hole"></div><div style="top: 170mm;" class="spiral-ring"></div>
    <div style="top: 184mm;" class="spiral-hole"></div><div style="top: 183mm;" class="spiral-ring"></div>
    <div style="top: 197mm;" class="spiral-hole"></div><div style="top: 196mm;" class="spiral-ring"></div>
    <div style="top: 210mm;" class="spiral-hole"></div><div style="top: 209mm;" class="spiral-ring"></div>
    <div style="top: 223mm;" class="spiral-hole"></div><div style="top: 222mm;" class="spiral-ring"></div>
    <div style="top: 236mm;" class="spiral-hole"></div><div style="top: 235mm;" class="spiral-ring"></div>
    <div style="top: 249mm;" class="spiral-hole"></div><div style="top: 248mm;" class="spiral-ring"></div>
    <div style="top: 262mm;" class="spiral-hole"></div><div style="top: 261mm;" class="spiral-ring"></div>
    <div style="top: 275mm;" class="spiral-hole"></div><div style="top: 274mm;" class="spiral-ring"></div>
  </div>

  <div class="page-header">
    <span>TOPIC: HOW AI CHANGED DATA ENGINEERING</span>
    <span>CHAPTER 2 & 3: ARCHITECTURE</span>
    <span class="page-number">PAGE 02</span>
  </div>

  <h2>Chapter 2: Boosting DE Productivity</h2>
  <p>AI has fundamentally transformed the developer's daily inner loop:</p>

  <ul>
    <li><b>Code & Pipeline Generation:</b> Drafting complex PySpark transforms, window functions, and SQL pipelines using Genie Code / Copilots.</li>
    <li><b>Automated Testing:</b> Synthesizing edge-case DataFrames, mock tables, and Delta Live Table quality expectations automatically.</li>
    <li><b>Automated Living Documentation:</b> Lineage graphs, data dictionaries, and architectural READMEs generated directly from schemas.</li>
    <li><b>Packaging Work as "AI Skills":</b> Bundling reusable enterprise guidelines (e.g. Medallion patterns, error logging) into modular skills for consistent execution.</li>
  </ul>

  <h2>Chapter 3: Building AI-Ready Data Platforms</h2>
  <div class="note-box note-box-red">
    <div class="tape"></div>
    <span class="badge badge-imp">PARADIGM SHIFT</span>
    <p style="margin:2px 0 0 0; font-size:15px;">
      <b>Pre-AI Goal:</b> Prepare Silver/Gold tables → BI teams prepare charts.<br>
      <b>2026 Goal:</b> <span class="hl">AI agents are now direct consumers of data!</span> If the platform lacks rich context, AI agents hallucinate and fail.
    </p>
  </div>

  <h3>The 4 Core Elements of an AI-Ready Platform:</h3>

  <div class="diagram-container">
    <svg class="hand-drawn" width="540" height="230" viewBox="0 0 540 230">
      <!-- Box 1 -->
      <rect x="15" y="10" width="245" height="95" rx="6" fill="#fffde7" stroke="#fbc02d" stroke-width="2"/>
      <text x="30" y="32" font-family="Architects Daughter" font-size="14" font-weight="bold" fill="#c62828">1. Rich Metadata & Relationships</text>
      <text x="30" y="52" font-family="Kalam" font-size="12" fill="#0f3460">• Detailed table & column descriptions.</text>
      <text x="30" y="70" font-family="Kalam" font-size="12" fill="#0f3460">• Explicit Primary Key (PK) & Foreign Key (FK)</text>
      <text x="30" y="88" font-family="Kalam" font-size="12" fill="#0f3460">  constraints in Unity Catalog.</text>

      <!-- Box 2 -->
      <rect x="280" y="10" width="245" height="95" rx="6" fill="#e8f5e9" stroke="#43a047" stroke-width="2"/>
      <text x="295" y="32" font-family="Architects Daughter" font-size="14" font-weight="bold" fill="#2e7d32">2. Governed Metric Views</text>
      <text x="295" y="52" font-family="Kalam" font-size="12" fill="#0f3460">• Centralized business metric definitions.</text>
      <text x="295" y="70" font-family="Kalam" font-size="12" fill="#0f3460">• Standard facts & dimensions.</text>
      <text x="295" y="88" font-family="Kalam" font-size="12" fill="#0f3460">• Prevents AI calculating wrong numbers.</text>

      <!-- Box 3 -->
      <rect x="15" y="115" width="245" height="100" rx="6" fill="#e3f2fd" stroke="#1976d2" stroke-width="2"/>
      <text x="30" y="137" font-family="Architects Daughter" font-size="14" font-weight="bold" fill="#1565c0">3. Business Data Ontology</text>
      <text x="30" y="157" font-family="Kalam" font-size="12" fill="#0f3460">• Clear domain boundaries (Sales, HR, Supply).</text>
      <text x="30" y="175" font-family="Kalam" font-size="12" fill="#0f3460">• Proper asset tagging & certifications.</text>
      <text x="30" y="193" font-family="Kalam" font-size="12" fill="#0f3460">• Connects tables, notebooks & Genie agents.</text>

      <!-- Box 4 -->
      <rect x="280" y="115" width="245" height="100" rx="6" fill="#fce4ec" stroke="#c2185b" stroke-width="2"/>
      <text x="295" y="137" font-family="Architects Daughter" font-size="14" font-weight="bold" fill="#880e4f">4. Certified Semantic Layer</text>
      <text x="295" y="157" font-family="Kalam" font-size="12" fill="#0f3460">• AI agents prioritize "Certified: Gold" assets.</text>
      <text x="295" y="175" font-family="Kalam" font-size="12" fill="#0f3460">• Eliminates ambiguity in business models.</text>
      <text x="295" y="193" font-family="Kalam" font-size="12" fill="#0f3460">• Enables seamless NL-to-SQL translation.</text>
    </svg>
  </div>

  <div class="note-box">
    <span class="badge badge-memory">MEMORY TRICK: M-E-T-A</span>
    Make your Lakehouse <span class="hl">M-E-T-A</span> ready:<br>
    <b>M</b>etric Views (Gov. Math) | <b>E</b>xplicit Constraints (PK/FK) | <b>T</b>able/Col Descriptions | <b>A</b>sset Certifications.
  </div>
</div>

<!-- ========================================================================= -->
<!-- PAGE 3: AREA 3 (AI APPS: RAG & NL) & SKILL MATRIX                        -->
<!-- ========================================================================= -->
<div class="notebook-page" id="page-3">
  <div class="spiral-track">
    <div class="spiral-spine-shadow"></div>
    <div style="top: 15mm;" class="spiral-hole"></div><div style="top: 14mm;" class="spiral-ring"></div>
    <div style="top: 28mm;" class="spiral-hole"></div><div style="top: 27mm;" class="spiral-ring"></div>
    <div style="top: 41mm;" class="spiral-hole"></div><div style="top: 40mm;" class="spiral-ring"></div>
    <div style="top: 54mm;" class="spiral-hole"></div><div style="top: 53mm;" class="spiral-ring"></div>
    <div style="top: 67mm;" class="spiral-hole"></div><div style="top: 66mm;" class="spiral-ring"></div>
    <div style="top: 80mm;" class="spiral-hole"></div><div style="top: 79mm;" class="spiral-ring"></div>
    <div style="top: 93mm;" class="spiral-hole"></div><div style="top: 92mm;" class="spiral-ring"></div>
    <div style="top: 106mm;" class="spiral-hole"></div><div style="top: 105mm;" class="spiral-ring"></div>
    <div style="top: 119mm;" class="spiral-hole"></div><div style="top: 118mm;" class="spiral-ring"></div>
    <div style="top: 132mm;" class="spiral-hole"></div><div style="top: 131mm;" class="spiral-ring"></div>
    <div style="top: 145mm;" class="spiral-hole"></div><div style="top: 144mm;" class="spiral-ring"></div>
    <div style="top: 158mm;" class="spiral-hole"></div><div style="top: 157mm;" class="spiral-ring"></div>
    <div style="top: 171mm;" class="spiral-hole"></div><div style="top: 170mm;" class="spiral-ring"></div>
    <div style="top: 184mm;" class="spiral-hole"></div><div style="top: 183mm;" class="spiral-ring"></div>
    <div style="top: 197mm;" class="spiral-hole"></div><div style="top: 196mm;" class="spiral-ring"></div>
    <div style="top: 210mm;" class="spiral-hole"></div><div style="top: 209mm;" class="spiral-ring"></div>
    <div style="top: 223mm;" class="spiral-hole"></div><div style="top: 222mm;" class="spiral-ring"></div>
    <div style="top: 236mm;" class="spiral-hole"></div><div style="top: 235mm;" class="spiral-ring"></div>
    <div style="top: 249mm;" class="spiral-hole"></div><div style="top: 248mm;" class="spiral-ring"></div>
    <div style="top: 262mm;" class="spiral-hole"></div><div style="top: 261mm;" class="spiral-ring"></div>
    <div style="top: 275mm;" class="spiral-hole"></div><div style="top: 274mm;" class="spiral-ring"></div>
  </div>

  <div class="page-header">
    <span>TOPIC: HOW AI CHANGED DATA ENGINEERING</span>
    <span>CHAPTER 4 & 5: SKILLS DYNAMICS</span>
    <span class="page-number">PAGE 03</span>
  </div>

  <h2>Chapter 4: Emerging AI Applications</h2>
  <div class="note-box note-box-blue">
    <div class="tape"></div>
    <h3 style="margin-top:0;">1. RAG on Unstructured Data (PDFs, Images, Text)</h3>
    <p>Before AI, processing unstructured data required complex dedicated ML research teams. Now, multimodal LLMs make parsing invoices, contracts, and audio a <span class="hl">standard data engineering ingestion pipeline</span> using Vector Search & Delta Lake.</p>
    
    <h3 style="margin-top:8px;">2. Serving Business Users via Natural Language</h3>
    <p>Instead of clicking through 30 dashboard filters, business users ask questions in plain English: <span class="hl">"Show revenue churn in EMEA for Q3."</span> AI agents query the AI-ready platform and synthesize verified answers with source citations.</p>
  </div>

  <h2>Chapter 5: Outdating vs. Rising Skills</h2>
  <p>The market is ruthlessly devaluing syntax memorization and rewarding architectural context:</p>

  <table class="hand-table">
    <thead>
      <tr>
        <th style="width: 48%;">❌ OUTDATING SKILLS (Declining Value)</th>
        <th style="width: 52%;">✔ RISING SKILLS (High Value in 2026)</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td><b>Handwriting boilerplate code:</b> Typing basic PySpark / SQL transforms by hand.</td>
        <td><b>Generating <span class="hl-green">GOOD</span> code via AI:</b> Crafting high-context prompts with schema DDL & constraints.</td>
      </tr>
      <tr>
        <td><b>Developing pipelines from scratch:</b> Manually scripting orchestration plumbing.</td>
        <td><b>Declarative Pipelines:</b> Managing Lakeflow Connect & DLT declarative graphs.</td>
      </tr>
      <tr>
        <td><b>Memorizing syntax & APIs:</b> Storing library signatures in your head.</td>
        <td><b>Reviewing & Testing AI Code:</b> Catching subtle hallucinations, logic traps, and data leaks.</td>
      </tr>
      <tr>
        <td><b>Manual Testing:</b> Typing repetitive assert statements.</td>
        <td><b>Automated AI Quality Gates:</b> Synthesizing edge-case tests & automated quality suites.</td>
      </tr>
      <tr>
        <td><b>Manual Documentation:</b> Writing data dictionaries by hand.</td>
        <td><b>Automated Living Documentation:</b> Setting up CI/CD auto-doc generation.</td>
      </tr>
      <tr>
        <td><b>Tabular-Only Workloads:</b> Only touching CSVs and relational DBs.</td>
        <td><b>RAG & Unstructured Ingestion:</b> Embeddings, chunking, and Vector Search indexing.</td>
      </tr>
    </tbody>
  </table>

  <div class="note-box note-box-red" style="margin-top:6px;">
    <span class="badge badge-imp">NOTEBOOK TAKEAWAY</span>
    <b>Why is "GOOD" in all caps?</b> Anyone can prompt an LLM to spit out code. The true high-paying skill is giving AI exact context to generate robust, production-grade pipelines without bugs.
  </div>
</div>

<!-- ========================================================================= -->
<!-- PAGE 4: HIRING REALITY (THE 3-TIER HIERARCHY)                            -->
<!-- ========================================================================= -->
<div class="notebook-page" id="page-4">
  <div class="spiral-track">
    <div class="spiral-spine-shadow"></div>
    <div style="top: 15mm;" class="spiral-hole"></div><div style="top: 14mm;" class="spiral-ring"></div>
    <div style="top: 28mm;" class="spiral-hole"></div><div style="top: 27mm;" class="spiral-ring"></div>
    <div style="top: 41mm;" class="spiral-hole"></div><div style="top: 40mm;" class="spiral-ring"></div>
    <div style="top: 54mm;" class="spiral-hole"></div><div style="top: 53mm;" class="spiral-ring"></div>
    <div style="top: 67mm;" class="spiral-hole"></div><div style="top: 66mm;" class="spiral-ring"></div>
    <div style="top: 80mm;" class="spiral-hole"></div><div style="top: 79mm;" class="spiral-ring"></div>
    <div style="top: 93mm;" class="spiral-hole"></div><div style="top: 92mm;" class="spiral-ring"></div>
    <div style="top: 106mm;" class="spiral-hole"></div><div style="top: 105mm;" class="spiral-ring"></div>
    <div style="top: 119mm;" class="spiral-hole"></div><div style="top: 118mm;" class="spiral-ring"></div>
    <div style="top: 132mm;" class="spiral-hole"></div><div style="top: 131mm;" class="spiral-ring"></div>
    <div style="top: 145mm;" class="spiral-hole"></div><div style="top: 144mm;" class="spiral-ring"></div>
    <div style="top: 158mm;" class="spiral-hole"></div><div style="top: 157mm;" class="spiral-ring"></div>
    <div style="top: 171mm;" class="spiral-hole"></div><div style="top: 170mm;" class="spiral-ring"></div>
    <div style="top: 184mm;" class="spiral-hole"></div><div style="top: 183mm;" class="spiral-ring"></div>
    <div style="top: 197mm;" class="spiral-hole"></div><div style="top: 196mm;" class="spiral-ring"></div>
    <div style="top: 210mm;" class="spiral-hole"></div><div style="top: 209mm;" class="spiral-ring"></div>
    <div style="top: 223mm;" class="spiral-hole"></div><div style="top: 222mm;" class="spiral-ring"></div>
    <div style="top: 236mm;" class="spiral-hole"></div><div style="top: 235mm;" class="spiral-ring"></div>
    <div style="top: 249mm;" class="spiral-hole"></div><div style="top: 248mm;" class="spiral-ring"></div>
    <div style="top: 262mm;" class="spiral-hole"></div><div style="top: 261mm;" class="spiral-ring"></div>
    <div style="top: 275mm;" class="spiral-hole"></div><div style="top: 274mm;" class="spiral-ring"></div>
  </div>

  <div class="page-header">
    <span>TOPIC: HOW AI CHANGED DATA ENGINEERING</span>
    <span>CHAPTER 6: HIRING REALITY</span>
    <span class="page-number">PAGE 04</span>
  </div>

  <h2>Chapter 6: What It Takes to Get Hired in 2026</h2>
  <p>Hiring standards follow a strict, realistic 3-tier hierarchy based on experience:</p>

  <div class="diagram-container">
    <svg class="hand-drawn" width="540" height="180" viewBox="0 0 540 180">
      <!-- Pyramid Tier 3 -->
      <polygon points="270,10 180,60 360,60" fill="#f8bbd0" stroke="#c2185b" stroke-width="2"/>
      <text x="270" y="38" font-family="Architects Daughter" font-size="12" font-weight="bold" fill="#880e4f" text-anchor="middle">TIER 3: ADVANCED / ARCHITECT</text>
      <text x="270" y="52" font-family="Kalam" font-size="10" fill="#4a148c" text-anchor="middle">Vector Search • DABs • AI Skills • MCP Servers</text>

      <!-- Pyramid Tier 2 -->
      <polygon points="180,60 360,60 430,115 110,115" fill="#ffe082" stroke="#ffa000" stroke-width="2"/>
      <text x="270" y="82" font-family="Architects Daughter" font-size="13" font-weight="bold" fill="#e65100" text-anchor="middle">TIER 2: TRENDING & IMMINENT (3-6 MONTHS)</text>
      <text x="270" y="100" font-family="Kalam" font-size="11" fill="#bf360c" text-anchor="middle">Lakeflow Connect • Metric Views • Genie Agents • AI/BI Dashboards • RAG</text>

      <!-- Pyramid Tier 1 -->
      <polygon points="110,115 430,115 510,175 30,175" fill="#c8e6c9" stroke="#388e3c" stroke-width="2.2"/>
      <text x="270" y="136" font-family="Architects Daughter" font-size="14" font-weight="bold" fill="#1b5e20" text-anchor="middle">TIER 1: MUST-HAVE CORE FUNDAMENTALS (&lt;4 YOE)</text>
      <text x="270" y="154" font-family="Kalam" font-size="11" fill="#1b5e20" text-anchor="middle">Apache Spark • Delta Lake • Python • SQL • Databricks (Jobs/Clusters)</text>
      <text x="270" y="168" font-family="Kalam" font-size="11" fill="#1b5e20" text-anchor="middle">Unity Catalog • Auto Loader • Data Modeling • Cloud / ADF / CI/CD</text>
    </svg>
  </div>

  <div class="note-box note-box-red">
    <div class="tape"></div>
    <span class="badge badge-imp">SURPRISING REALITY CHECK</span>
    <p style="margin:2px 0 0 0; font-size:14px;">
      If you have <b>&lt; 4 years experience</b>, you do <b>NOT</b> need complex AI agent mastery to get hired today! Solid mastery of <span class="hl">Spark, Delta Lake, SQL, Python, Unity Catalog & Auto Loader</span> is 100% enough to crack interviews.
    </p>
  </div>

  <div class="d-flex">
    <div class="note-box col-half" style="margin:4px 0; background:#fffde7;">
      <h4 style="margin:0 0 4px 0; color:#f57f17;">⏳ Next 3-6 Months (Tier 2)</h4>
      <p style="margin:0; font-size:13px;">These will flip from "good to have" to <b>mandatory</b>: Lakeflow Connect, Declarative DLT, Metric Views, Databricks Genie Agents & AI/BI.</p>
    </div>
    <div class="note-box col-half" style="margin:4px 0; background:#fce4ec;">
      <h4 style="margin:0 0 4px 0; color:#c2185b;">🏛 For Architects (Tier 3)</h4>
      <p style="margin:0; font-size:13px;">Must master right away: MCP servers, Databricks Asset Bundles (DABs), Custom AI Skills, and Enterprise Ontologies to lead teams.</p>
    </div>
  </div>
</div>

<!-- ========================================================================= -->
<!-- PAGE 5: AI READINESS MATURITY MODEL & DIAGNOSTIC                         -->
<!-- ========================================================================= -->
<div class="notebook-page" id="page-5">
  <div class="spiral-track">
    <div class="spiral-spine-shadow"></div>
    <div style="top: 15mm;" class="spiral-hole"></div><div style="top: 14mm;" class="spiral-ring"></div>
    <div style="top: 28mm;" class="spiral-hole"></div><div style="top: 27mm;" class="spiral-ring"></div>
    <div style="top: 41mm;" class="spiral-hole"></div><div style="top: 40mm;" class="spiral-ring"></div>
    <div style="top: 54mm;" class="spiral-hole"></div><div style="top: 53mm;" class="spiral-ring"></div>
    <div style="top: 67mm;" class="spiral-hole"></div><div style="top: 66mm;" class="spiral-ring"></div>
    <div style="top: 80mm;" class="spiral-hole"></div><div style="top: 79mm;" class="spiral-ring"></div>
    <div style="top: 93mm;" class="spiral-hole"></div><div style="top: 92mm;" class="spiral-ring"></div>
    <div style="top: 106mm;" class="spiral-hole"></div><div style="top: 105mm;" class="spiral-ring"></div>
    <div style="top: 119mm;" class="spiral-hole"></div><div style="top: 118mm;" class="spiral-ring"></div>
    <div style="top: 132mm;" class="spiral-hole"></div><div style="top: 131mm;" class="spiral-ring"></div>
    <div style="top: 145mm;" class="spiral-hole"></div><div style="top: 144mm;" class="spiral-ring"></div>
    <div style="top: 158mm;" class="spiral-hole"></div><div style="top: 157mm;" class="spiral-ring"></div>
    <div style="top: 171mm;" class="spiral-hole"></div><div style="top: 170mm;" class="spiral-ring"></div>
    <div style="top: 184mm;" class="spiral-hole"></div><div style="top: 183mm;" class="spiral-ring"></div>
    <div style="top: 197mm;" class="spiral-hole"></div><div style="top: 196mm;" class="spiral-ring"></div>
    <div style="top: 210mm;" class="spiral-hole"></div><div style="top: 209mm;" class="spiral-ring"></div>
    <div style="top: 223mm;" class="spiral-hole"></div><div style="top: 222mm;" class="spiral-ring"></div>
    <div style="top: 236mm;" class="spiral-hole"></div><div style="top: 235mm;" class="spiral-ring"></div>
    <div style="top: 249mm;" class="spiral-hole"></div><div style="top: 248mm;" class="spiral-ring"></div>
    <div style="top: 262mm;" class="spiral-hole"></div><div style="top: 261mm;" class="spiral-ring"></div>
    <div style="top: 275mm;" class="spiral-hole"></div><div style="top: 274mm;" class="spiral-ring"></div>
  </div>

  <div class="page-header">
    <span>TOPIC: HOW AI CHANGED DATA ENGINEERING</span>
    <span>CHAPTER 7: MATURITY MODEL</span>
    <span class="page-number">PAGE 05</span>
  </div>

  <h2>Chapter 7: Where Do You Stand? (AI Readiness)</h2>
  <p>Evaluate your real standing using Narendra Kumar’s 3-level benchmark:</p>

  <div class="note-box" style="background:#e8f5e9; border:2px solid #2e7d32;">
    <div class="tape"></div>
    <h3 style="color:#1b5e20; margin-top:2px;">LEVEL 1: BEGINNER (Tactical User)</h3>
    <ul>
      <li>Uses Genie Code / Copilot to draft standard queries and functions.</li>
      <li>Fixes syntax errors & stack traces using AI prompts.</li>
      <li>Uses AI to add code comments, docstrings, and formatting.</li>
      <li><b>Mindset:</b> AI is a quick syntax assistant and faster Google/StackOverflow.</li>
    </ul>
  </div>

  <div class="note-box" style="background:#fff9c4; border:2px solid #fbc02d;">
    <div class="tape"></div>
    <h3 style="color:#f57f17; margin-top:2px;">LEVEL 2: INTERMEDIATE (Systematic Practitioner)</h3>
    <ul>
      <li>Consistently generates high-quality production code by feeding <span class="hl">proper schema context & business rules</span>.</li>
      <li>Has built 1–2 <span class="hl">Databricks Genie Agents</span> to query lakehouse tables via natural language.</li>
      <li>Critically reviews and tests AI code for subtle hallucinations and edge cases.</li>
      <li>Produces comprehensive pipeline documentation and data dictionaries with AI.</li>
      <li><b>Mindset:</b> Operates as a senior reviewer guiding an AI junior developer.</li>
    </ul>
  </div>

  <div class="note-box note-box-red">
    <div class="tape"></div>
    <h3 style="color:#b71c1c; margin-top:2px;">LEVEL 3: ADVANCED (Ontology & Systems Architect)</h3>
    <ul>
      <li><b>Builds Standard "AI Skills":</b> Real modular prompt/context artifacts for dev, testing, and governance across the company.</li>
      <li><b>Automates Pipeline Documentation:</b> Fully automated living documentation synced with CI/CD.</li>
      <li><b>Architects Enterprise Ontologies:</b> Builds context layers with domain tagging, certified assets, and Metric Views in Databricks.</li>
      <li><b>Mindset:</b> Designs the semantic platform and rules for autonomous AI agents to operate safely.</li>
    </ul>
  </div>

  <div class="note-box" style="background:#ede7f6; border:2px solid #673ab7; margin-top:6px;">
    <span class="badge badge-faq">SELF-CHECK SCORECARD</span>
    Ask yourself: <i>"Can I build a Genie space with Metric Views? Can I package my project's rules as a reusable AI Skill?"</i> That is the line between Level 1 and Level 3!
  </div>
</div>

<!-- ========================================================================= -->
<!-- PAGE 6: THE EXPANDING ROLE (BOUNDARY BLURRING)                           -->
<!-- ========================================================================= -->
<div class="notebook-page" id="page-6">
  <div class="spiral-track">
    <div class="spiral-spine-shadow"></div>
    <div style="top: 15mm;" class="spiral-hole"></div><div style="top: 14mm;" class="spiral-ring"></div>
    <div style="top: 28mm;" class="spiral-hole"></div><div style="top: 27mm;" class="spiral-ring"></div>
    <div style="top: 41mm;" class="spiral-hole"></div><div style="top: 40mm;" class="spiral-ring"></div>
    <div style="top: 54mm;" class="spiral-hole"></div><div style="top: 53mm;" class="spiral-ring"></div>
    <div style="top: 67mm;" class="spiral-hole"></div><div style="top: 66mm;" class="spiral-ring"></div>
    <div style="top: 80mm;" class="spiral-hole"></div><div style="top: 79mm;" class="spiral-ring"></div>
    <div style="top: 93mm;" class="spiral-hole"></div><div style="top: 92mm;" class="spiral-ring"></div>
    <div style="top: 106mm;" class="spiral-hole"></div><div style="top: 105mm;" class="spiral-ring"></div>
    <div style="top: 119mm;" class="spiral-hole"></div><div style="top: 118mm;" class="spiral-ring"></div>
    <div style="top: 132mm;" class="spiral-hole"></div><div style="top: 131mm;" class="spiral-ring"></div>
    <div style="top: 145mm;" class="spiral-hole"></div><div style="top: 144mm;" class="spiral-ring"></div>
    <div style="top: 158mm;" class="spiral-hole"></div><div style="top: 157mm;" class="spiral-ring"></div>
    <div style="top: 171mm;" class="spiral-hole"></div><div style="top: 170mm;" class="spiral-ring"></div>
    <div style="top: 184mm;" class="spiral-hole"></div><div style="top: 183mm;" class="spiral-ring"></div>
    <div style="top: 197mm;" class="spiral-hole"></div><div style="top: 196mm;" class="spiral-ring"></div>
    <div style="top: 210mm;" class="spiral-hole"></div><div style="top: 209mm;" class="spiral-ring"></div>
    <div style="top: 223mm;" class="spiral-hole"></div><div style="top: 222mm;" class="spiral-ring"></div>
    <div style="top: 236mm;" class="spiral-hole"></div><div style="top: 235mm;" class="spiral-ring"></div>
    <div style="top: 249mm;" class="spiral-hole"></div><div style="top: 248mm;" class="spiral-ring"></div>
    <div style="top: 262mm;" class="spiral-hole"></div><div style="top: 261mm;" class="spiral-ring"></div>
    <div style="top: 275mm;" class="spiral-hole"></div><div style="top: 274mm;" class="spiral-ring"></div>
  </div>

  <div class="page-header">
    <span>TOPIC: HOW AI CHANGED DATA ENGINEERING</span>
    <span>CHAPTER 8: ROLE EXPANSION</span>
    <span class="page-number">PAGE 06</span>
  </div>

  <h2>Chapter 8: How the DE Role is Expanding</h2>
  <p>The traditional boundary of Data Engineering (Ingestion, Transformation, Pipelines, DQ & Auditing) is <span class="hl">expanding into 4 adjacent disciplines</span>:</p>

  <div class="diagram-container">
    <svg class="hand-drawn" width="540" height="230" viewBox="0 0 540 230">
      <!-- Center Circle -->
      <circle cx="270" cy="115" r="55" fill="#e3f2fd" stroke="#1565c0" stroke-width="2.5"/>
      <text x="270" y="110" font-family="Architects Daughter" font-size="14" font-weight="bold" fill="#0d47a1" text-anchor="middle">MODERN DE</text>
      <text x="270" y="128" font-family="Kalam" font-size="11" fill="#0d47a1" text-anchor="middle">Multi-Role Core</text>

      <!-- Node 1: BI Analyst -->
      <rect x="20" y="15" width="165" height="70" rx="8" fill="#fff9c4" stroke="#fbc02d" stroke-width="2"/>
      <text x="102" y="38" font-family="Architects Daughter" font-size="13" font-weight="bold" fill="#b71c1c" text-anchor="middle">1. BI ANALYST</text>
      <text x="102" y="55" font-family="Kalam" font-size="11" fill="#0f3460" text-anchor="middle">AIBI Dashboards in Databricks</text>
      <text x="102" y="70" font-family="Kalam" font-size="11" fill="#0f3460" text-anchor="middle">built via Natural Language.</text>
      <line x1="165" y1="75" x2="225" y2="95" stroke="#546e7a" stroke-width="2" stroke-dasharray="3,2"/>

      <!-- Node 2: Data Modeler -->
      <rect x="355" y="15" width="165" height="70" rx="8" fill="#e8f5e9" stroke="#43a047" stroke-width="2"/>
      <text x="437" y="38" font-family="Architects Daughter" font-size="13" font-weight="bold" fill="#2e7d32" text-anchor="middle">2. DATA MODELER</text>
      <text x="437" y="55" font-family="Kalam" font-size="11" fill="#0f3460" text-anchor="middle">AI generates conceptual ER</text>
      <text x="437" y="70" font-family="Kalam" font-size="11" fill="#0f3460" text-anchor="middle">models & table schemas directly.</text>
      <line x1="375" y1="75" x2="315" y2="95" stroke="#546e7a" stroke-width="2" stroke-dasharray="3,2"/>

      <!-- Node 3: App Engineer -->
      <rect x="20" y="145" width="165" height="70" rx="8" fill="#fce4ec" stroke="#d81b60" stroke-width="2"/>
      <text x="102" y="168" font-family="Architects Daughter" font-size="13" font-weight="bold" fill="#880e4f" text-anchor="middle">3. APP ENGINEER</text>
      <text x="102" y="185" font-family="Kalam" font-size="11" fill="#0f3460" text-anchor="middle">Databricks Apps: Full-stack</text>
      <text x="102" y="200" font-family="Kalam" font-size="11" fill="#0f3460" text-anchor="middle">MVP apps via prompt-to-app.</text>
      <line x1="165" y1="155" x2="225" y2="135" stroke="#546e7a" stroke-width="2" stroke-dasharray="3,2"/>

      <!-- Node 4: Data Scientist -->
      <rect x="355" y="145" width="165" height="70" rx="8" fill="#ede7f6" stroke="#7e57c2" stroke-width="2"/>
      <text x="437" y="168" font-family="Architects Daughter" font-size="13" font-weight="bold" fill="#4a148c" text-anchor="middle">4. DATA SCIENTIST</text>
      <text x="437" y="185" font-family="Kalam" font-size="11" fill="#0f3460" text-anchor="middle">RAG, vector embeddings &</text>
      <text x="437" y="200" font-family="Kalam" font-size="11" fill="#0f3460" text-anchor="middle">unstructured data ingestion.</text>
      <line x1="375" y1="155" x2="315" y2="135" stroke="#546e7a" stroke-width="2" stroke-dasharray="3,2"/>
    </svg>
  </div>

  <div class="note-box note-box-blue" style="margin-top:6px;">
    <span class="badge badge-imp">THE NEW NORMAL</span>
    <b>What this means:</b> Within months, companies will expect a single Data Engineering squad to build data pipelines, create AI/BI dashboards, deploy basic MVP Databricks Apps, and manage RAG ingestion. 
    <b>The siloed ETL coder is merging into the Full-Stack Data & AI Systems Engineer!</b>
  </div>
</div>

<!-- ========================================================================= -->
<!-- PAGE 7: CAREER ROADMAP & STRATEGIC PLAYBOOK                              -->
<!-- ========================================================================= -->
<div class="notebook-page" id="page-7">
  <div class="spiral-track">
    <div class="spiral-spine-shadow"></div>
    <div style="top: 15mm;" class="spiral-hole"></div><div style="top: 14mm;" class="spiral-ring"></div>
    <div style="top: 28mm;" class="spiral-hole"></div><div style="top: 27mm;" class="spiral-ring"></div>
    <div style="top: 41mm;" class="spiral-hole"></div><div style="top: 40mm;" class="spiral-ring"></div>
    <div style="top: 54mm;" class="spiral-hole"></div><div style="top: 53mm;" class="spiral-ring"></div>
    <div style="top: 67mm;" class="spiral-hole"></div><div style="top: 66mm;" class="spiral-ring"></div>
    <div style="top: 80mm;" class="spiral-hole"></div><div style="top: 79mm;" class="spiral-ring"></div>
    <div style="top: 93mm;" class="spiral-hole"></div><div style="top: 92mm;" class="spiral-ring"></div>
    <div style="top: 106mm;" class="spiral-hole"></div><div style="top: 105mm;" class="spiral-ring"></div>
    <div style="top: 119mm;" class="spiral-hole"></div><div style="top: 118mm;" class="spiral-ring"></div>
    <div style="top: 132mm;" class="spiral-hole"></div><div style="top: 131mm;" class="spiral-ring"></div>
    <div style="top: 145mm;" class="spiral-hole"></div><div style="top: 144mm;" class="spiral-ring"></div>
    <div style="top: 158mm;" class="spiral-hole"></div><div style="top: 157mm;" class="spiral-ring"></div>
    <div style="top: 171mm;" class="spiral-hole"></div><div style="top: 170mm;" class="spiral-ring"></div>
    <div style="top: 184mm;" class="spiral-hole"></div><div style="top: 183mm;" class="spiral-ring"></div>
    <div style="top: 197mm;" class="spiral-hole"></div><div style="top: 196mm;" class="spiral-ring"></div>
    <div style="top: 210mm;" class="spiral-hole"></div><div style="top: 209mm;" class="spiral-ring"></div>
    <div style="top: 223mm;" class="spiral-hole"></div><div style="top: 222mm;" class="spiral-ring"></div>
    <div style="top: 236mm;" class="spiral-hole"></div><div style="top: 235mm;" class="spiral-ring"></div>
    <div style="top: 249mm;" class="spiral-hole"></div><div style="top: 248mm;" class="spiral-ring"></div>
    <div style="top: 262mm;" class="spiral-hole"></div><div style="top: 261mm;" class="spiral-ring"></div>
    <div style="top: 275mm;" class="spiral-hole"></div><div style="top: 274mm;" class="spiral-ring"></div>
  </div>

  <div class="page-header">
    <span>TOPIC: HOW AI CHANGED DATA ENGINEERING</span>
    <span>CHAPTER 9: CAREER PLAYBOOK</span>
    <span class="page-number">PAGE 07</span>
  </div>

  <h2>Chapter 9: Action Plan by Experience Level</h2>
  <p>Your strategic roadmap depends strictly on where you are in your career journey:</p>

  <div class="note-box" style="background:#e8f5e9; border:2px solid #2e7d32;">
    <div class="tape"></div>
    <h3 style="color:#1b5e20; margin-top:2px;">1. For Aspiring DEs & Career Switchers (&lt; 3 YOE)</h3>
    <ul>
      <li><b>Do NOT chase complex AI agents yet.</b> Master core skills: SQL, Python, Spark internals, Delta Lake, Databricks Jobs & Unity Catalog.</li>
      <li>Get hired quickly on the strength of your fundamentals.</li>
      <li>Once hired inside a project, immediately start upskilling into AI tools to build high productivity and career velocity.</li>
    </ul>
  </div>

  <div class="note-box" style="background:#fff9c4; border:2px solid #fbc02d;">
    <div class="tape"></div>
    <h3 style="color:#f57f17; margin-top:2px;">2. For Mid-Level & Senior Data Engineers (3–7 YOE)</h3>
    <ul>
      <li>Start building your <span class="hl">AI platform skills immediately</span> to stay competitive.</li>
      <li>Master <b>Lakeflow Connect</b>, <b>Declarative Pipelines</b>, and <b>Metric Views</b>.</li>
      <li>Build 1–2 production <b>Databricks Genie Agents</b> and integrate RAG into your pipelines.</li>
      <li>Transition from writing raw syntax to high-context prompt engineering and rigorous code audits.</li>
    </ul>
  </div>

  <div class="note-box note-box-red">
    <div class="tape"></div>
    <h3 style="color:#b71c1c; margin-top:2px;">3. For Data Architects & Tech Leads (8+ YOE)</h3>
    <ul>
      <li><b>You must be up to date right away—zero lag permitted!</b></li>
      <li>Architects are expected to guide teams on AI-ready platforms, ontologies, and asset certification.</li>
      <li>Master <b>Databricks Asset Bundles (DABs)</b>, <b>MCP servers</b>, and <b>Custom AI Skills</b>.</li>
      <li>If architects fall behind, the entire project delivery model suffers.</li>
    </ul>
  </div>

  <div class="quote-statement" style="font-size:18px; margin-top:12px;">
    "Gone are the days when we learned one technology and worked on it until retirement. If you want to stay relevant, continuous upgrading is the only practical way."
  </div>
</div>

<!-- ========================================================================= -->
<!-- PAGE 8: REVISION SHEET (INTERVIEW Q&A & KNOWLEDGE CHECK)                  -->
<!-- ========================================================================= -->
<div class="notebook-page" id="page-8">
  <div class="spiral-track">
    <div class="spiral-spine-shadow"></div>
    <div style="top: 15mm;" class="spiral-hole"></div><div style="top: 14mm;" class="spiral-ring"></div>
    <div style="top: 28mm;" class="spiral-hole"></div><div style="top: 27mm;" class="spiral-ring"></div>
    <div style="top: 41mm;" class="spiral-hole"></div><div style="top: 40mm;" class="spiral-ring"></div>
    <div style="top: 54mm;" class="spiral-hole"></div><div style="top: 53mm;" class="spiral-ring"></div>
    <div style="top: 67mm;" class="spiral-hole"></div><div style="top: 66mm;" class="spiral-ring"></div>
    <div style="top: 80mm;" class="spiral-hole"></div><div style="top: 79mm;" class="spiral-ring"></div>
    <div style="top: 93mm;" class="spiral-hole"></div><div style="top: 92mm;" class="spiral-ring"></div>
    <div style="top: 106mm;" class="spiral-hole"></div><div style="top: 105mm;" class="spiral-ring"></div>
    <div style="top: 119mm;" class="spiral-hole"></div><div style="top: 118mm;" class="spiral-ring"></div>
    <div style="top: 132mm;" class="spiral-hole"></div><div style="top: 131mm;" class="spiral-ring"></div>
    <div style="top: 145mm;" class="spiral-hole"></div><div style="top: 144mm;" class="spiral-ring"></div>
    <div style="top: 158mm;" class="spiral-hole"></div><div style="top: 157mm;" class="spiral-ring"></div>
    <div style="top: 171mm;" class="spiral-hole"></div><div style="top: 170mm;" class="spiral-ring"></div>
    <div style="top: 184mm;" class="spiral-hole"></div><div style="top: 183mm;" class="spiral-ring"></div>
    <div style="top: 197mm;" class="spiral-hole"></div><div style="top: 196mm;" class="spiral-ring"></div>
    <div style="top: 210mm;" class="spiral-hole"></div><div style="top: 209mm;" class="spiral-ring"></div>
    <div style="top: 223mm;" class="spiral-hole"></div><div style="top: 222mm;" class="spiral-ring"></div>
    <div style="top: 236mm;" class="spiral-hole"></div><div style="top: 235mm;" class="spiral-ring"></div>
    <div style="top: 249mm;" class="spiral-hole"></div><div style="top: 248mm;" class="spiral-ring"></div>
    <div style="top: 262mm;" class="spiral-hole"></div><div style="top: 261mm;" class="spiral-ring"></div>
    <div style="top: 275mm;" class="spiral-hole"></div><div style="top: 274mm;" class="spiral-ring"></div>
  </div>

  <div class="page-header">
    <span>TOPIC: HOW AI CHANGED DATA ENGINEERING</span>
    <span>TOPPER'S RAPID REVISION</span>
    <span class="page-number">PAGE 08</span>
  </div>

  <h2>Topper's Rapid Revision & Interview Drill</h2>

  <div class="note-box note-box-red">
    <div class="tape"></div>
    <span class="badge badge-faq">Q1: WHY PK/FK IN UNITY CATALOG IF NOT ENFORCED?</span>
    <p style="margin:4px 0 0 0; font-size:14px;">
      <b>Ans:</b> 1) Helps Spark Cost-Based Optimizer prune joins. 2) <span class="hl">Crucial topological map for AI agents (Genie)</span> so they know how tables connect without guessing or hallucinating invalid joins!
    </p>
  </div>

  <div class="note-box" style="background:#e3f2fd; border:2px solid #1976d2;">
    <div class="tape"></div>
    <span class="badge badge-faq">Q2: WHAT IS A METRIC VIEW & WHY DOES AI NEED IT?</span>
    <p style="margin:4px 0 0 0; font-size:14px;">
      <b>Ans:</b> A single source of truth for calculations (e.g. Churn Rate, MRR). Without it, LLMs write arbitrary SQL logic that yields conflicting business numbers.
    </p>
  </div>

  <div class="note-box" style="background:#fffde7; border:2px solid #fbc02d;">
    <div class="tape"></div>
    <span class="badge badge-faq">Q3: WHY DO INTERVIEWERS STILL ASK SPARK INTERNALS?</span>
    <p style="margin:4px 0 0 0; font-size:14px;">
      <b>Ans:</b> AI writes code, but AI cannot look at the Spark UI to fix a cluster hung on task 199 due to <span class="hl">data skew and memory spill</span>! Only an engineer with core distributed fundamentals can debug and optimize it.
    </p>
  </div>

  <div class="note-box" style="background:#f3e5f5; border:2px solid #7b1fa2;">
    <span class="badge badge-memory">RAPID KNOWLEDGE CHECK</span>
    <ol style="margin:6px 0 0 16px; font-size:13.5px;">
      <li><b>Entry Level Mandate:</b> Spark, Delta Lake, Python, SQL, Unity Catalog, Auto Loader.</li>
      <li><b>3-6 Months Mandate:</b> Lakeflow Connect, Metric Views, Genie Agents, AI/BI.</li>
      <li><b>Architect Mandate:</b> Enterprise Ontology, Asset Certification, DABs, MCP Servers.</li>
    </ol>
  </div>

  <div style="text-align:center; margin-top:14px; font-family:'Architects Daughter'; color:#b71c1c; font-size:18px;">
    ✨ End of Master Notebook — Prepared by Narendra Kumar (Databricks MVP) ✨
  </div>
</div>

</body>
</html>"""

    paths = [
        r"C:\notes_sql\databeli\How_AI_Has_Changed_Data_Engineering_2026_Handwritten_Notebook.html",
        r"C:\notes_sql\databeli\how ai has chnaged the data enginerring in 2026 ,the grounth truth and future\How_AI_Has_Changed_Data_Engineering_2026_Handwritten_Notebook.html"
    ]

    for p in paths:
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "w", encoding="utf-8") as f:
            f.write(html_code)
        print(f"Successfully generated handwritten notebook: {p} ({len(html_code)} bytes)")

if __name__ == "__main__":
    create_notebook_html()
