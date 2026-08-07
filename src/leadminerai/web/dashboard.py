from __future__ import annotations

from fastapi.responses import HTMLResponse


def get_dashboard_html() -> HTMLResponse:
    return HTMLResponse(
        """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>LeadMinerAI - B2B Business & Contact Intelligence</title>
  <style>
    :root {
      color-scheme: dark;
      --bg: #07111f;
      --panel: rgba(12, 19, 34, 0.78);
      --panel-strong: #101a2d;
      --line: rgba(118, 146, 255, 0.16);
      --text: #e7edf8;
      --muted: #8ea0c1;
      --accent: #66d9ff;
      --accent-2: #8a7dff;
      --success: #7cf2b1;
      --warn: #ffd36f;
      --danger: #ff7b89;
      --shadow: 0 24px 80px rgba(0, 0, 0, 0.45);
      --radius: 22px;
      --radius-sm: 14px;
      --max: 1240px;
      --font: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }

    * { box-sizing: border-box; }
    html, body { margin: 0; min-height: 100%; background:
      radial-gradient(circle at 15% 20%, rgba(102, 217, 255, 0.14), transparent 22%),
      radial-gradient(circle at 80% 0%, rgba(138, 125, 255, 0.18), transparent 30%),
      linear-gradient(180deg, #06101d 0%, #091629 48%, #050b14 100%);
      color: var(--text); font-family: var(--font); }

    body::before {
      content: "";
      position: fixed;
      inset: 0;
      pointer-events: none;
      background-image: linear-gradient(rgba(255,255,255,0.03) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.03) 1px, transparent 1px);
      background-size: 38px 38px;
      mask-image: linear-gradient(180deg, rgba(0,0,0,0.9), transparent 90%);
      opacity: 0.28;
    }

    .wrap { max-width: var(--max); margin: 0 auto; padding: 28px 20px 40px; position: relative; }
    .hero {
      display: grid;
      grid-template-columns: 1.5fr 1fr;
      gap: 20px;
      align-items: stretch;
      margin-bottom: 20px;
    }
    .brand, .panel, .stat {
      backdrop-filter: blur(18px);
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: var(--radius);
      box-shadow: var(--shadow);
    }
    .brand { padding: 28px; }
    .eyebrow {
      display: inline-flex; align-items: center; gap: 8px; padding: 7px 12px; border-radius: 999px;
      background: rgba(102, 217, 255, 0.08); color: var(--accent); font-size: 12px; letter-spacing: 0.12em;
      text-transform: uppercase; font-weight: 700;
    }
    h1 { margin: 18px 0 10px; font-size: clamp(2.2rem, 4.5vw, 3.8rem); line-height: 0.96; letter-spacing: -0.05em; }
    .lead { margin: 0; max-width: 65ch; color: var(--muted); font-size: 1.02rem; line-height: 1.65; }
    .brand-actions { display: flex; flex-wrap: wrap; gap: 12px; margin-top: 22px; }
    .btn, button, .file-label {
      appearance: none; border: 0; cursor: pointer; text-decoration: none; transition: transform .18s ease, box-shadow .18s ease, border-color .18s ease, background .18s ease;
    }
    .btn {
      display: inline-flex; align-items: center; justify-content: center; gap: 10px; padding: 13px 18px; border-radius: 14px;
      font-weight: 700; color: white; background: linear-gradient(135deg, rgba(102,217,255,0.95), rgba(138,125,255,0.95)); box-shadow: 0 12px 32px rgba(102, 217, 255, 0.18);
    }
    .btn.secondary { background: rgba(255,255,255,0.04); border: 1px solid var(--line); color: var(--text); box-shadow: none; }
    .btn:hover, button:hover, .file-label:hover { transform: translateY(-1px); }
    .stats { display: grid; gap: 16px; }
    .stat { padding: 20px; background: rgba(12, 19, 34, 0.84); }
    .stat .label { color: var(--muted); font-size: 0.88rem; }
    .stat .value { margin-top: 8px; font-size: 2rem; font-weight: 800; letter-spacing: -0.04em; }
    .stat .sub { margin-top: 4px; color: var(--muted); font-size: 0.92rem; }

    /* Tabs */
    .tabs-bar {
      display: flex;
      gap: 12px;
      margin-bottom: 22px;
      border-bottom: 1px solid var(--line);
      padding-bottom: 10px;
    }
    .tab-btn {
      background: transparent;
      border: none;
      color: var(--muted);
      font-size: 1.05rem;
      font-weight: 700;
      padding: 10px 16px;
      cursor: pointer;
      border-radius: 8px;
      transition: color .2s, background .2s;
    }
    .tab-btn:hover {
      color: var(--text);
      background: rgba(255,255,255,0.03);
    }
    .tab-btn.active {
      color: var(--accent);
      background: rgba(102, 217, 255, 0.08);
    }

    .tab-content { display: none; }
    .tab-content.active { display: block; }

    .grid { display: grid; grid-template-columns: 1.08fr 1.4fr; gap: 20px; align-items: start; }
    .panel { padding: 22px; }
    .panel h2 { margin: 0 0 8px; font-size: 1.1rem; }
    .panel p.desc { margin: 0 0 18px; color: var(--muted); line-height: 1.55; }

    .upload-box {
      border: 1px dashed rgba(102, 217, 255, 0.28); border-radius: 18px; padding: 18px; background: rgba(255,255,255,0.03);
    }
    .upload-row { display: flex; gap: 12px; align-items: center; flex-wrap: wrap; }
    .file-label {
      display: inline-flex; align-items: center; gap: 10px; padding: 12px 16px; border-radius: 14px; background: rgba(255,255,255,0.05); color: var(--text); border: 1px solid var(--line); font-weight: 700;
    }
    input[type="file"] { display: none; }
    .file-name { color: var(--muted); font-size: 0.95rem; }
    .toolbar { display: flex; flex-wrap: wrap; gap: 10px; margin-top: 14px; }
    .toolbar .btn, .toolbar .secondary { padding: 11px 15px; }
    .hint { margin-top: 12px; font-size: 0.92rem; color: var(--muted); }

    .chips { display: flex; flex-wrap: wrap; gap: 8px; margin: 10px 0 0; }
    .chip { padding: 7px 10px; border-radius: 999px; background: rgba(255,255,255,0.05); color: var(--muted); font-size: 0.86rem; border: 1px solid rgba(255,255,255,0.07); }

    table { width: 100%; border-collapse: collapse; margin-top: 16px; overflow: hidden; border-radius: 16px; }
    th, td { text-align: left; padding: 14px 12px; border-bottom: 1px solid rgba(255,255,255,0.06); vertical-align: top; }
    th { color: #aebadd; font-size: 0.76rem; text-transform: uppercase; letter-spacing: 0.12em; background: rgba(255,255,255,0.03); }
    td { color: #dfe6f4; font-size: 0.95rem; }
    tbody tr:hover { background: rgba(255,255,255,0.02); }

    .status {
      display: inline-flex; align-items: center; gap: 8px; padding: 6px 10px; border-radius: 999px; font-weight: 700; font-size: 0.82rem;
      background: rgba(255,255,255,0.05);
    }
    .dot { width: 8px; height: 8px; border-radius: 50%; background: currentColor; box-shadow: 0 0 0 4px color-mix(in srgb, currentColor 18%, transparent); }
    .PENDING { color: var(--warn); }
    .FOUND { color: var(--success); }
    .NOT_FOUND { color: #ffb48f; }
    .FAILED { color: var(--danger); }

    .empty { padding: 26px; border-radius: 18px; background: rgba(255,255,255,0.03); color: var(--muted); text-align: center; border: 1px dashed rgba(255,255,255,0.08); }
    .notice { margin-top: 14px; font-size: 0.92rem; color: var(--muted); }
    .toast {
      position: fixed; right: 18px; bottom: 18px; min-width: 280px; max-width: 420px; padding: 14px 16px; border-radius: 14px;
      background: rgba(9, 17, 31, 0.95); border: 1px solid rgba(102, 217, 255, 0.24); box-shadow: var(--shadow); transform: translateY(16px); opacity: 0; pointer-events: none; transition: .22s ease;
    }
    .toast.show { opacity: 1; transform: translateY(0); }
    .toast strong { display: block; margin-bottom: 4px; }

    /* Business & Contact Intelligence Styling */
    .intel-company {
      margin-bottom: 24px;
      border: 1px solid var(--line);
      border-radius: var(--radius-sm);
      background: var(--panel-strong);
      overflow: hidden;
    }
    .intel-header {
      background: rgba(255,255,255,0.02);
      padding: 16px 20px;
      border-bottom: 1px solid var(--line);
      display: flex;
      justify-content: space-between;
      align-items: center;
      flex-wrap: wrap;
      gap: 12px;
    }
    .intel-title {
      font-size: 1.2rem;
      font-weight: 700;
      margin: 0;
      color: #fff;
    }
    .intel-sub-title {
      font-size: 0.85rem;
      color: var(--muted);
      margin-top: 4px;
    }
    .intel-badge-group {
      display: flex;
      gap: 8px;
      align-items: center;
      flex-wrap: wrap;
    }
    .intel-industry {
      font-size: 0.85rem;
      color: var(--accent);
      background: rgba(102, 217, 255, 0.08);
      padding: 4px 10px;
      border-radius: 999px;
      border: 1px solid rgba(102, 217, 255, 0.15);
      font-weight: 600;
    }
    .intel-mfg-type {
      font-size: 0.85rem;
      color: #dfdaff;
      background: rgba(138, 125, 255, 0.12);
      padding: 4px 10px;
      border-radius: 999px;
      border: 1px solid rgba(138, 125, 255, 0.25);
      font-weight: 600;
    }
    .intel-body {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 20px;
      padding: 20px;
    }
    @media (max-width: 900px) {
      .intel-body { grid-template-columns: 1fr; }
    }
    .intel-section-title {
      font-size: 0.9rem;
      text-transform: uppercase;
      letter-spacing: 0.08em;
      color: #aebadd;
      margin: 0 0 12px 0;
      border-bottom: 1px solid rgba(255,255,255,0.05);
      padding-bottom: 6px;
      font-weight: 700;
    }
    .pain-card {
      background: rgba(255, 123, 137, 0.04);
      border: 1px solid rgba(255, 123, 137, 0.18);
      padding: 12px 14px;
      border-radius: 12px;
      margin-bottom: 10px;
    }
    .pain-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 6px;
    }
    .pain-name {
      font-weight: 700;
      font-size: 0.92rem;
      color: #ffe0e3;
    }
    .severity-bar-bg {
      height: 6px;
      width: 100%;
      background: rgba(255,255,255,0.08);
      border-radius: 3px;
      overflow: hidden;
      margin-top: 6px;
    }
    .severity-bar-fill {
      height: 100%;
      background: linear-gradient(90deg, #ffd36f, #ff7b89);
      border-radius: 3px;
    }
    .filter-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
      gap: 12px;
      background: rgba(255,255,255,0.02);
      padding: 16px;
      border-radius: 16px;
      border: 1px solid var(--line);
      margin-bottom: 20px;
    }
    .filter-input {
      width: 100%;
      padding: 10px 14px;
      border-radius: 10px;
      background: rgba(0,0,0,0.3);
      border: 1px solid var(--line);
      color: var(--text);
      font-size: 0.9rem;
    }
    .filter-input:focus {
      outline: none;
      border-color: var(--accent);
    }
    @media (max-width: 980px) { .hero, .grid { grid-template-columns: 1fr; } }
  </style>
</head>
<body>
  <div class="wrap">
    <section class="hero">
      <div class="brand">
        <span class="eyebrow">LeadMinerAI Dashboard & Platform</span>
        <h1>Industrial B2B Business & Contact Intelligence.</h1>
        <p class="lead">Automated public web crawling, contact extraction, industrial classification, department prediction, and operational pain point AI forecasting for personalized B2B outreach.</p>
        <div class="brand-actions">
          <a class="btn" href="/docs" target="_blank" rel="noreferrer">Open API docs</a>
          <button class="btn secondary" id="refreshTop">Refresh data</button>
        </div>
        <div class="chips">
          <span class="chip">CSV / XLSX upload</span>
          <span class="chip">Tavily web search</span>
          <span class="chip">Playwright crawler</span>
          <span class="chip">Business Intelligence Agent</span>
          <span class="chip">Operational Pain Predictor</span>
          <span class="chip">Multi-format exports</span>
        </div>
      </div>
      <div class="stats">
        <div class="stat"><div class="label">Total companies</div><div class="value" id="statTotal">0</div><div class="sub">Rows currently stored</div></div>
        <div class="stat"><div class="label">Resolved websites</div><div class="value" id="statFound">0</div><div class="sub">Companies marked FOUND</div></div>
        <div class="stat"><div class="label">Business Profiles</div><div class="value" id="statBusiness">0</div><div class="sub">Profiles analyzed</div></div>
      </div>
    </section>

    <div class="tabs-bar">
      <button class="tab-btn active" id="tabCompaniesBtn">Companies & Websites</button>
      <button class="tab-btn" id="tabBusinessBtn">Business Intelligence</button>
      <button class="tab-btn" id="tabContactsBtn">Contact Intelligence</button>
    </div>

    <!-- Tab 1: Companies & Websites -->
    <div id="tabCompanies" class="tab-content active">
      <section class="grid">
        <div class="panel">
          <h2>1. Upload companies</h2>
          <p class="desc">Upload a CSV or Excel (.xlsx) file with a <strong>company_name</strong> or <strong>name</strong> column.</p>
          <div class="upload-box">
            <div class="upload-row">
              <label class="file-label" for="csvFile">Choose File</label>
              <input id="csvFile" type="file" accept=".csv,.xlsx,text/csv,application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" />
              <span class="file-name" id="fileName">No file chosen</span>
            </div>
            <div class="toolbar">
              <button class="btn" id="uploadBtn">Upload file</button>
              <button class="btn secondary" id="searchBtn">Trigger search</button>
              <a class="btn secondary" href="/api/v1/companies/export">Export Excel</a>
            </div>
            <div class="hint">Need a sample? Create a CSV or XLSX file with one column named <code>company_name</code> and place each company on its own row.</div>
          </div>
          <div class="notice" id="uploadResult"></div>
        </div>

        <div class="panel">
          <h2>2. Company List & Actions</h2>
          <p class="desc">Execute website search, contact extraction, or deep business profile analysis.</p>
          <div id="tableWrap"></div>
          <div class="notice">Tip: click “Trigger search” after uploading to resolve pending companies in the background.</div>
        </div>
      </section>
    </div>

    <!-- Tab 2: Business Intelligence -->
    <div id="tabBusiness" class="tab-content">
      <section class="grid" style="grid-template-columns: 1fr;">
        <div class="panel">
          <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 16px; margin-bottom: 16px;">
            <div>
              <h2>Business Intelligence Profiles</h2>
              <p class="desc" style="margin-bottom: 0;">AI Industrial Consultant analysis: Industry, Manufacturing Type, Certifications, Departments, and Operational Pain Predictions.</p>
            </div>
            <div class="toolbar" style="margin-top: 0;">
              <button class="btn" id="analyzeAllBusinessBtn">Bulk Analyze Business</button>
              <a class="btn secondary" id="exportBusinessCsv" href="/api/v1/business-intelligence/export/csv">Export CSV</a>
              <a class="btn secondary" id="exportBusinessExcel" href="/api/v1/business-intelligence/export/excel">Export Excel</a>
              <a class="btn secondary" id="exportBusinessJson" href="/api/v1/business-intelligence/export/json">Export JSON</a>
            </div>
          </div>

          <!-- Search & Filter Controls -->
          <div class="filter-grid">
            <input type="text" class="filter-input" id="filterIndustry" placeholder="Filter by Industry (e.g. Pumps, Auto)" />
            <input type="text" class="filter-input" id="filterCity" placeholder="Filter by City / Location" />
            <input type="text" class="filter-input" id="filterMfgType" placeholder="Filter by Mfg Type (OEM, Job Work)" />
            <input type="text" class="filter-input" id="filterPain" placeholder="Filter by Predicted Pain Point" />
          </div>

          <div id="businessListWrap" style="margin-top: 15px;"></div>
        </div>
      </section>
    </div>

    <!-- Tab 3: Contact Intelligence -->
    <div id="tabContacts" class="tab-content">
      <section class="grid" style="grid-template-columns: 1fr;">
        <div class="panel">
          <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 16px;">
            <div>
              <h2>Contact Intelligence</h2>
              <p class="desc" style="margin-bottom: 0;">Multi-channel communication channels and decision makers.</p>
            </div>
            <div class="toolbar" style="margin-top: 0;">
              <button class="btn" id="extractAllBtn">Bulk Extract Intelligence</button>
              <a class="btn secondary" href="/api/v1/intelligence/export/csv">Export CSV</a>
              <a class="btn secondary" href="/api/v1/intelligence/export/excel">Export Excel</a>
              <a class="btn secondary" href="/api/v1/intelligence/export/json">Export JSON</a>
            </div>
          </div>
          <div id="contactsTableWrap" style="margin-top: 25px;"></div>
        </div>
      </section>
    </div>
  </div>

  <div class="toast" id="toast"></div>

  <script>
    const elements = {
      file: document.getElementById('csvFile'),
      fileName: document.getElementById('fileName'),
      uploadBtn: document.getElementById('uploadBtn'),
      searchBtn: document.getElementById('searchBtn'),
      refreshTop: document.getElementById('refreshTop'),
      uploadResult: document.getElementById('uploadResult'),
      tableWrap: document.getElementById('tableWrap'),
      toast: document.getElementById('toast'),
      statTotal: document.getElementById('statTotal'),
      statFound: document.getElementById('statFound'),
      statBusiness: document.getElementById('statBusiness'),
      
      tabCompanies: document.getElementById('tabCompanies'),
      tabBusiness: document.getElementById('tabBusiness'),
      tabContacts: document.getElementById('tabContacts'),
      tabCompaniesBtn: document.getElementById('tabCompaniesBtn'),
      tabBusinessBtn: document.getElementById('tabBusinessBtn'),
      tabContactsBtn: document.getElementById('tabContactsBtn'),
      
      businessListWrap: document.getElementById('businessListWrap'),
      analyzeAllBusinessBtn: document.getElementById('analyzeAllBusinessBtn'),
      filterIndustry: document.getElementById('filterIndustry'),
      filterCity: document.getElementById('filterCity'),
      filterMfgType: document.getElementById('filterMfgType'),
      filterPain: document.getElementById('filterPain'),
      exportBusinessCsv: document.getElementById('exportBusinessCsv'),
      exportBusinessExcel: document.getElementById('exportBusinessExcel'),
      exportBusinessJson: document.getElementById('exportBusinessJson'),

      contactsTableWrap: document.getElementById('contactsTableWrap'),
      extractAllBtn: document.getElementById('extractAllBtn'),
    };

    let activeTab = 'companies';

    function showToast(title, message) {
      elements.toast.innerHTML = `<strong>${title}</strong><div>${message}</div>`;
      elements.toast.classList.add('show');
      clearTimeout(window.__toastTimer);
      window.__toastTimer = setTimeout(() => elements.toast.classList.remove('show'), 3500);
    }

    function statusBadge(status) {
      return `<span class="status ${status}"><span class="dot"></span>${status}</span>`;
    }

    function switchTab(target) {
      activeTab = target;
      elements.tabCompanies.classList.remove('active');
      elements.tabBusiness.classList.remove('active');
      elements.tabContacts.classList.remove('active');
      elements.tabCompaniesBtn.classList.remove('active');
      elements.tabBusinessBtn.classList.remove('active');
      elements.tabContactsBtn.classList.remove('active');

      if (target === 'companies') {
        elements.tabCompanies.classList.add('active');
        elements.tabCompaniesBtn.classList.add('active');
        refreshCompanies().catch(err => showToast('Error', err.message));
      } else if (target === 'business') {
        elements.tabBusiness.classList.add('active');
        elements.tabBusinessBtn.classList.add('active');
        refreshBusinessIntelligence().catch(err => showToast('Error', err.message));
      } else {
        elements.tabContacts.classList.add('active');
        elements.tabContactsBtn.classList.add('active');
        refreshContacts().catch(err => showToast('Error', err.message));
      }
    }

    elements.tabCompaniesBtn.addEventListener('click', () => switchTab('companies'));
    elements.tabBusinessBtn.addEventListener('click', () => switchTab('business'));
    elements.tabContactsBtn.addEventListener('click', () => switchTab('contacts'));

    async function refreshCompanies() {
      const response = await fetch('/api/v1/companies?limit=200');
      if (!response.ok) throw new Error('Failed to load companies');
      const data = await response.json();
      const items = data.items || [];
      const found = items.filter(item => item.status === 'FOUND').length;

      elements.statTotal.textContent = data.total ?? items.length;
      elements.statFound.textContent = found;

      const biResponse = await fetch('/api/v1/business-intelligence?limit=500');
      if (biResponse.ok) {
        const biData = await biResponse.json();
        elements.statBusiness.textContent = biData.total || biData.items?.length || 0;
      }

      if (!items.length) {
        elements.tableWrap.innerHTML = `<div class="empty">No companies yet. Upload a CSV/XLSX to begin.</div>`;
        return;
      }

      elements.tableWrap.innerHTML = `
        <table>
          <thead>
            <tr>
              <th>Company</th>
              <th>Status</th>
              <th>Website</th>
              <th>Actions</th>
              <th>Error</th>
            </tr>
          </thead>
          <tbody>
            ${items.map(item => `
              <tr>
                <td><strong>${item.name}</strong></td>
                <td>${statusBadge(item.status)}</td>
                <td>${item.website_url ? `<a href="${item.website_url}" target="_blank" rel="noreferrer">${item.website_url}</a>` : '<span style="color:var(--muted)">—</span>'}</td>
                <td>
                  ${item.status === 'FOUND' 
                    ? `<div style="display:flex; gap:6px; flex-wrap:wrap;">
                        <button class="btn secondary" style="padding:5px 10px; font-size:0.78rem; font-weight:700;" onclick="analyzeSingleBusiness('${item.id}', '${item.name.replace(/'/g, "\\'")}', this)">Analyze Business</button>
                        <button class="btn secondary" style="padding:5px 10px; font-size:0.78rem; font-weight:700;" onclick="extractSingleContact('${item.id}', '${item.name.replace(/'/g, "\\'")}', this)">Extract Contacts</button>
                       </div>` 
                    : '<span style="color:var(--muted)">Requires Website</span>'}
                </td>
                <td>${item.last_error ? item.last_error : '<span style="color:var(--muted)">—</span>'}</td>
              </tr>
            `).join('')}
          </tbody>
        </table>
      `;
    }

    async function refreshBusinessIntelligence() {
      const ind = elements.filterIndustry.value.trim();
      const city = elements.filterCity.value.trim();
      const mfg = elements.filterMfgType.value.trim();
      const pain = elements.filterPain.value.trim();

      let queryParams = new URLSearchParams();
      if (ind) queryParams.set('industry', ind);
      if (city) queryParams.set('city', city);
      if (mfg) queryParams.set('manufacturing_type', mfg);
      if (pain) queryParams.set('predicted_pain', pain);

      const qs = queryParams.toString() ? '?' + queryParams.toString() : '';

      elements.exportBusinessCsv.href = `/api/v1/business-intelligence/export/csv${qs}`;
      elements.exportBusinessExcel.href = `/api/v1/business-intelligence/export/excel${qs}`;
      elements.exportBusinessJson.href = `/api/v1/business-intelligence/export/json${qs}`;

      const response = await fetch(`/api/v1/business-intelligence${qs}`);
      if (!response.ok) throw new Error('Failed to load business intelligence');
      const data = await response.json();
      const items = data.items || [];

      elements.statBusiness.textContent = data.total ?? items.length;

      if (!items.length) {
        elements.businessListWrap.innerHTML = `<div class="empty">No business intelligence profiles found matching criteria. Click "Bulk Analyze Business" to process companies.</div>`;
        return;
      }

      elements.businessListWrap.innerHTML = items.map(bi => {
        const confColor = bi.confidence > 70 ? 'var(--success)' : bi.confidence > 40 ? 'var(--warn)' : 'var(--danger)';

        const certsHtml = (bi.certifications || []).map(c => `<span class="chip" style="background: rgba(124, 242, 177, 0.1); color: var(--success); border-color: rgba(124, 242, 177, 0.2);">${c}</span>`).join('');
        const locsHtml = (bi.locations || []).map(l => `<span class="chip">${l}</span>`).join('');
        const prodsHtml = (bi.products || []).map(p => `<span class="chip" style="background: rgba(102, 217, 255, 0.08); color: var(--accent);">${p}</span>`).join('');
        
        const deptsHtml = (bi.departments || []).map(d => {
          const name = typeof d === 'object' ? d.name : d;
          const conf = typeof d === 'object' ? d.confidence : 80;
          return `<div class="intel-item" style="padding: 6px 10px;">
            <span>${name}</span>
            <span class="conf-badge" style="background: rgba(138, 125, 255, 0.15); color: #dfdaff;">${conf}%</span>
          </div>`;
        }).join('');

        const painsHtml = (bi.predicted_pain_points || []).map(p => {
          const name = typeof p === 'object' ? p.name : p;
          const sev = typeof p === 'object' ? (p.severity || 80) : 80;
          const freq = typeof p === 'object' ? (p.frequency || 'Daily') : 'Daily';
          const conf = typeof p === 'object' ? (p.confidence || 80) : 80;

          return `
            <div class="pain-card">
              <div class="pain-header">
                <span class="pain-name">${name}</span>
                <span class="chip" style="font-size: 0.75rem; padding: 2px 8px; background: rgba(255, 123, 137, 0.15); color: #ffb4b9; border: 1px solid rgba(255, 123, 137, 0.25);">${freq}</span>
              </div>
              <div style="display: flex; justify-content: space-between; font-size: 0.78rem; color: var(--muted); margin-top: 4px;">
                <span>Severity: <strong>${sev}/100</strong></span>
                <span>Confidence: <strong>${conf}%</strong></span>
              </div>
              <div class="severity-bar-bg">
                <div class="severity-bar-fill" style="width: ${sev}%;"></div>
              </div>
            </div>
          `;
        }).join('');

        return `
          <div class="intel-company">
            <div class="intel-header">
              <div>
                <h3 class="intel-title">${bi.company_name || 'Company'}</h3>
                <div class="intel-sub-title">${bi.description || 'No description available'}</div>
              </div>
              <div class="intel-badge-group">
                ${bi.industry ? `<span class="intel-industry">${bi.industry}</span>` : ''}
                ${bi.manufacturing_type ? `<span class="intel-mfg-type">${bi.manufacturing_type}</span>` : ''}
                <span class="conf-badge" style="padding: 6px 12px; font-size: 0.85rem; background: ${confColor}20; color: ${confColor}; border: 1px solid ${confColor}30;">Overall: ${bi.confidence}%</span>
              </div>
            </div>

            <div class="intel-body">
              <div>
                <h4 class="intel-section-title">Products & Services</h4>
                <div class="chips" style="margin-bottom: 16px;">${prodsHtml || '<span style="color:var(--muted)">None listed</span>'}</div>

                <h4 class="intel-section-title">Certifications & Locations</h4>
                <div class="chips" style="margin-bottom: 16px;">
                  ${certsHtml} ${locsHtml}
                </div>

                <h4 class="intel-section-title">Predicted Departments</h4>
                <div class="intel-list" style="gap: 6px;">${deptsHtml}</div>
              </div>

              <div>
                <h4 class="intel-section-title">Predicted Operational Pain Points</h4>
                <div>${painsHtml || '<div style="color:var(--muted)">No pain predictions</div>'}</div>
              </div>
            </div>
          </div>
        `;
      }).join('');
    }

    async function refreshContacts() {
      const response = await fetch('/api/v1/intelligence?limit=200');
      if (!response.ok) throw new Error('Failed to load intelligence');
      const intelList = await response.json();

      if (!intelList.length) {
        elements.contactsTableWrap.innerHTML = `<div class="empty">No contact profiles extracted yet. Click "Bulk Extract Intelligence".</div>`;
        return;
      }

      elements.contactsTableWrap.innerHTML = intelList.map(companyIntel => {
        const contacts = (companyIntel.contacts || []).sort((a, b) => b.priority - a.priority);
        const dms = (companyIntel.decision_makers || []).sort((a, b) => b.priority - a.priority);

        const contactsHtml = contacts.length > 0 
          ? contacts.map(c => {
              const confColor = c.confidence > 70 ? 'var(--success)' : c.confidence > 40 ? 'var(--warn)' : 'var(--danger)';
              let valueDisplay = c.contact_value;
              if (c.contact_type === 'email') {
                valueDisplay = `<a href="mailto:${c.contact_value}">${c.contact_value}</a>`;
              } else if (c.contact_type === 'phone') {
                valueDisplay = `<a href="tel:${c.contact_value}">${c.contact_value}</a>`;
              } else if (c.contact_type === 'social' || c.contact_type === 'map') {
                valueDisplay = `<a href="${c.contact_value}" target="_blank" rel="noreferrer">${c.contact_value}</a>`;
              }

              return `
                <div class="intel-item">
                  <div class="intel-item-left">
                    <div class="intel-item-val">${valueDisplay}</div>
                    <div class="intel-item-sub">
                      <span>Label: <strong>${c.contact_label || c.contact_type}</strong></span>
                    </div>
                  </div>
                  <div class="intel-item-right">
                    <span class="prio-badge">P: ${c.priority}</span>
                    <span class="conf-badge" style="background: ${confColor}20; color: ${confColor}; border: 1px solid ${confColor}30;">${c.confidence}%</span>
                  </div>
                </div>
              `;
            }).join('')
          : `<div style="color: var(--muted); font-size: 0.9rem; font-style: italic;">No communication channels.</div>`;

        const dmsHtml = dms.length > 0
          ? dms.map(d => {
              const confColor = d.confidence > 70 ? 'var(--success)' : d.confidence > 40 ? 'var(--warn)' : 'var(--danger)';
              const linkedinLink = d.linkedin_url 
                ? `<a href="${d.linkedin_url}" target="_blank" rel="noreferrer" class="link-btn">LinkedIn Profile</a>`
                : '<span style="color: var(--muted);">No LinkedIn</span>';

              return `
                <div class="intel-item" style="border-left: 3px solid var(--accent-2);">
                  <div class="intel-item-left">
                    <div class="intel-item-val">${d.name}</div>
                    <div class="intel-item-sub">
                      <strong style="color: #e7edf8;">${d.designation}</strong>
                      <span>•</span> ${linkedinLink}
                    </div>
                  </div>
                  <div class="intel-item-right">
                    <span class="prio-badge" style="background: rgba(138, 125, 255, 0.25); color: #dfdaff;">P: ${d.priority}</span>
                    <span class="conf-badge" style="background: ${confColor}20; color: ${confColor}; border: 1px solid ${confColor}30;">${d.confidence}%</span>
                  </div>
                </div>
              `;
            }).join('')
          : `<div style="color: var(--muted); font-size: 0.9rem; font-style: italic;">No decision makers found.</div>`;

        return `
          <div class="intel-company">
            <div class="intel-header">
              <h3 class="intel-title">${companyIntel.company_name}</h3>
            </div>
            <div class="intel-body">
              <div>
                <h4 class="intel-section-title">Communication Channels</h4>
                <div class="intel-list">${contactsHtml}</div>
              </div>
              <div>
                <h4 class="intel-section-title">Decision Makers & Team</h4>
                <div class="intel-list">${dmsHtml}</div>
              </div>
            </div>
          </div>
        `;
      }).join('');
    }

    // Filter Listeners
    [elements.filterIndustry, elements.filterCity, elements.filterMfgType, elements.filterPain].forEach(el => {
      el.addEventListener('input', () => {
        clearTimeout(window.__filterTimer);
        window.__filterTimer = setTimeout(() => {
          if (activeTab === 'business') refreshBusinessIntelligence();
        }, 300);
      });
    });

    window.analyzeSingleBusiness = async (companyId, name, btn) => {
      if (btn) {
        btn.disabled = true;
        btn.textContent = 'Analyzing...';
      }
      showToast('Business Analysis started', `Crawling public site and analyzing business profile for ${name}...`);
      try {
        const response = await fetch(`/api/intelligence/analyze/${companyId}`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' }
        });
        const data = await response.json();
        if (!response.ok) throw new Error(data.detail || 'Analysis failed');
        showToast('Analysis complete', `Successfully built business profile for ${name}.`);
        await refreshCompanies();
      } catch (error) {
        showToast('Analysis failed', error.message);
      } finally {
        if (btn) {
          btn.disabled = false;
          btn.textContent = 'Analyze Business';
        }
      }
    };

    window.extractSingleContact = async (companyId, name, btn) => {
      if (btn) {
        btn.disabled = true;
        btn.textContent = 'Extracting...';
      }
      showToast('Extraction started', `Crawling official website and extracting contacts for ${name}...`);
      try {
        const response = await fetch(`/api/v1/intelligence/extract/${companyId}`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' }
        });
        const data = await response.json();
        if (!response.ok) throw new Error(data.detail || 'Extraction failed');
        showToast('Extraction complete', `Successfully resolved contacts for ${name}.`);
        await refreshCompanies();
      } catch (error) {
        showToast('Extraction failed', error.message);
      } finally {
        if (btn) {
          btn.disabled = false;
          btn.textContent = 'Extract Contacts';
        }
      }
    };

    elements.analyzeAllBusinessBtn.addEventListener('click', async () => {
      elements.analyzeAllBusinessBtn.disabled = true;
      elements.analyzeAllBusinessBtn.textContent = 'Queuing...';
      try {
        const response = await fetch('/api/intelligence/analyze-all', { method: 'POST' });
        const data = await response.json();
        if (!response.ok) throw new Error(data.detail || 'Bulk business analysis failed');
        showToast('Bulk business analysis queued', `${data.queued} companies queued in background.`);
        await refreshBusinessIntelligence();
      } catch (error) {
        showToast('Analysis failed', error.message);
      } finally {
        elements.analyzeAllBusinessBtn.disabled = false;
        elements.analyzeAllBusinessBtn.textContent = 'Bulk Analyze Business';
      }
    });

    elements.extractAllBtn.addEventListener('click', async () => {
      elements.extractAllBtn.disabled = true;
      elements.extractAllBtn.textContent = 'Queuing...';
      try {
        const response = await fetch('/api/v1/intelligence/extract-all', { method: 'POST' });
        const data = await response.json();
        if (!response.ok) throw new Error(data.detail || 'Bulk extraction failed');
        showToast('Bulk extraction queued', `${data.queued} companies queued in background.`);
        await refreshContacts();
      } catch (error) {
        showToast('Extraction failed', error.message);
      } finally {
        elements.extractAllBtn.disabled = false;
        elements.extractAllBtn.textContent = 'Bulk Extract Intelligence';
      }
    });

    elements.file.addEventListener('change', () => {
      elements.fileName.textContent = elements.file.files?.[0]?.name || 'No file chosen';
    });

    elements.uploadBtn.addEventListener('click', async () => {
      const file = elements.file.files?.[0];
      if (!file) {
        showToast('Missing file', 'Choose a CSV/XLSX before uploading.');
        return;
      }

      const form = new FormData();
      form.append('file', file);

      elements.uploadBtn.disabled = true;
      elements.uploadBtn.textContent = 'Uploading...';
      try {
        const response = await fetch('/api/v1/companies/upload', { method: 'POST', body: form });
        const data = await response.json();
        if (!response.ok) throw new Error(data.detail || 'Upload failed');
        elements.uploadResult.textContent = `Uploaded ${data.created} new companies, skipped ${data.skipped} duplicates, received ${data.total_received} rows.`;
        showToast('Upload complete', elements.uploadResult.textContent);
        await refreshCompanies();
      } catch (error) {
        showToast('Upload failed', error.message);
      } finally {
        elements.uploadBtn.disabled = false;
        elements.uploadBtn.textContent = 'Upload file';
      }
    });

    elements.searchBtn.addEventListener('click', async () => {
      elements.searchBtn.disabled = true;
      elements.searchBtn.textContent = 'Queuing...';
      try {
        const response = await fetch('/api/v1/companies/search/trigger', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({}) });
        const data = await response.json();
        if (!response.ok) throw new Error(data.detail || 'Search trigger failed');
        showToast('Search queued', `${data.queued} companies queued for website search.`);
        await refreshCompanies();
      } catch (error) {
        showToast('Search failed', error.message);
      } finally {
        elements.searchBtn.disabled = false;
        elements.searchBtn.textContent = 'Trigger search';
      }
    });

    elements.refreshTop.addEventListener('click', () => {
      if (activeTab === 'companies') refreshCompanies().catch(e => showToast('Error', e.message));
      else if (activeTab === 'business') refreshBusinessIntelligence().catch(e => showToast('Error', e.message));
      else refreshContacts().catch(e => showToast('Error', e.message));
    });

    // Initial load
    refreshCompanies().catch(error => showToast('Load failed', error.message));
  </script>
</body>
</html>
        """
    )
