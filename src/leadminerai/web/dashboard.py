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
  <title>LeadMinerAI - B2B Research Platform</title>
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
      --max: 1180px;
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
    h1 { margin: 18px 0 10px; font-size: clamp(2.2rem, 4.5vw, 4.1rem); line-height: 0.96; letter-spacing: -0.05em; }
    .lead { margin: 0; max-width: 62ch; color: var(--muted); font-size: 1.02rem; line-height: 1.65; }
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

    .tab-content {
      display: none;
    }
    .tab-content.active {
      display: block;
    }

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

    /* Intelligence styling */
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
      font-size: 1.15rem;
      font-weight: 700;
      margin: 0;
      color: #fff;
    }
    .intel-industry {
      font-size: 0.85rem;
      color: var(--accent);
      background: rgba(102, 217, 255, 0.08);
      padding: 4px 10px;
      border-radius: 999px;
      border: 1px solid rgba(102, 217, 255, 0.15);
    }
    .intel-body {
      display: grid;
      grid-template-columns: 1.2fr 1fr;
      gap: 20px;
      padding: 20px;
    }
    @media (max-width: 768px) {
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
    .intel-list {
      display: flex;
      flex-direction: column;
      gap: 10px;
    }
    .intel-item {
      display: flex;
      justify-content: space-between;
      align-items: center;
      background: rgba(255,255,255,0.01);
      padding: 10px 14px;
      border-radius: 10px;
      border: 1px solid rgba(255,255,255,0.03);
    }
    .intel-item-left {
      display: flex;
      flex-direction: column;
      gap: 3px;
    }
    .intel-item-val {
      font-weight: 600;
      font-size: 0.92rem;
      word-break: break-all;
    }
    .intel-item-val a {
      color: var(--text);
      text-decoration: none;
    }
    .intel-item-val a:hover {
      color: var(--accent);
      text-decoration: underline;
    }
    .intel-item-sub {
      font-size: 0.78rem;
      color: var(--muted);
      display: flex;
      align-items: center;
      gap: 6px;
    }
    .intel-item-right {
      display: flex;
      align-items: center;
      gap: 8px;
    }
    .prio-badge {
      font-size: 0.72rem;
      font-weight: 700;
      padding: 2px 6px;
      border-radius: 4px;
      background: rgba(138, 125, 255, 0.15);
      color: #c0b8ff;
      border: 1px solid rgba(138, 125, 255, 0.25);
    }
    .conf-badge {
      font-size: 0.72rem;
      font-weight: 700;
      padding: 2px 6px;
      border-radius: 4px;
    }
    .link-btn {
      color: var(--accent);
      text-decoration: none;
      font-size: 0.78rem;
    }
    .link-btn:hover {
      text-decoration: underline;
    }
    @media (max-width: 980px) { .hero, .grid { grid-template-columns: 1fr; } }
  </style>
</head>
<body>
  <div class="wrap">
    <section class="hero">
      <div class="brand">
        <span class="eyebrow">LeadMinerAI Dashboard</span>
        <h1>Upload companies, resolve websites, export results.</h1>
        <p class="lead">A focused B2B intelligence workspace for finding official company websites, scraping public contact details, and downloading reports. Respects robots.txt, rate limits crawler page requests, and parses structures via GPT.</p>
        <div class="brand-actions">
          <a class="btn" href="/docs" target="_blank" rel="noreferrer">Open API docs</a>
          <button class="btn secondary" id="refreshTop">Refresh data</button>
        </div>
        <div class="chips">
          <span class="chip">CSV / XLSX upload</span>
          <span class="chip">Tavily search</span>
          <span class="chip">Playwright crawler</span>
          <span class="chip">AI Contact Extractor</span>
          <span class="chip">Excel / CSV export</span>
        </div>
      </div>
      <div class="stats">
        <div class="stat"><div class="label">Total companies</div><div class="value" id="statTotal">0</div><div class="sub">Rows currently stored</div></div>
        <div class="stat"><div class="label">Resolved websites</div><div class="value" id="statFound">0</div><div class="sub">Companies marked FOUND</div></div>
        <div class="stat"><div class="label">Intelligence profiles</div><div class="value" id="statContacts">0</div><div class="sub">Profiles resolved</div></div>
      </div>
    </section>

    <div class="tabs-bar">
      <button class="tab-btn active" id="tabCompaniesBtn">Companies & Websites</button>
      <button class="tab-btn" id="tabContactsBtn">Company Intelligence</button>
    </div>

    <!-- Companies Tab -->
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
          <h2>2. Results</h2>
          <p class="desc">Shows each company’s status, website URL, and options to scrape contacts.</p>
          <div id="tableWrap"></div>
          <div class="notice">Tip: click “Trigger search” after uploading to resolve pending companies in the background.</div>
        </div>
      </section>
    </div>

    <!-- Company Intelligence Tab -->
    <div id="tabContacts" class="tab-content">
      <section class="grid" style="grid-template-columns: 1fr;">
        <div class="panel">
          <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 16px;">
            <div>
              <h2>Company Intelligence</h2>
              <p class="desc" style="margin-bottom: 0;">Automatically scraped and analyzed multi-channel communication profiles and decision makers.</p>
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
      statContacts: document.getElementById('statContacts'),
      
      tabCompanies: document.getElementById('tabCompanies'),
      tabContacts: document.getElementById('tabContacts'),
      tabCompaniesBtn: document.getElementById('tabCompaniesBtn'),
      tabContactsBtn: document.getElementById('tabContactsBtn'),
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
      if (target === 'companies') {
        elements.tabCompanies.classList.add('active');
        elements.tabContacts.classList.remove('active');
        elements.tabCompaniesBtn.classList.add('active');
        elements.tabContactsBtn.classList.remove('active');
        refreshCompanies().catch(err => showToast('Error', err.message));
      } else {
        elements.tabCompanies.classList.remove('active');
        elements.tabContacts.classList.add('active');
        elements.tabCompaniesBtn.classList.remove('active');
        elements.tabContactsBtn.classList.add('active');
        refreshContacts().catch(err => showToast('Error', err.message));
      }
    }

    elements.tabCompaniesBtn.addEventListener('click', () => switchTab('companies'));
    elements.tabContactsBtn.addEventListener('click', () => switchTab('contacts'));

    async function refreshCompanies() {
      const response = await fetch('/api/v1/companies?limit=200');
      if (!response.ok) throw new Error('Failed to load companies');
      const data = await response.json();
      const items = data.items || [];
      const found = items.filter(item => item.status === 'FOUND').length;

      elements.statTotal.textContent = data.total ?? items.length;
      elements.statFound.textContent = found;

      // Fetch count of intelligence profiles
      const cResponse = await fetch('/api/v1/intelligence?limit=500');
      if (cResponse.ok) {
        const intelList = await cResponse.json();
        elements.statContacts.textContent = intelList.length;
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
                    ? `<button class="btn secondary" style="padding:6px 12px; font-size:0.8rem; font-weight:700;" onclick="extractSingleContact('${item.id}', '${item.name.replace(/'/g, "\\'")}', this)">Extract Intel</button>` 
                    : '<span style="color:var(--muted)">Requires Website</span>'}
                </td>
                <td>${item.last_error ? item.last_error : '<span style="color:var(--muted)">—</span>'}</td>
              </tr>
            `).join('')}
          </tbody>
        </table>
      `;
    }

    async function refreshContacts() {
      const response = await fetch('/api/v1/intelligence?limit=200');
      if (!response.ok) throw new Error('Failed to load intelligence');
      const intelList = await response.json();
      
      elements.statContacts.textContent = intelList.length;

      if (!intelList.length) {
        elements.contactsTableWrap.innerHTML = `<div class="empty">No intelligence profiles extracted yet. Click "Bulk Extract Intelligence" or trigger single company extraction.</div>`;
        return;
      }

      elements.contactsTableWrap.innerHTML = intelList.map(companyIntel => {
        // Sort contacts & dms by priority
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
              
              const sourceLink = c.source_url 
                ? `<a href="${c.source_url}" target="_blank" rel="noreferrer" class="link-btn">Source Page</a>`
                : '';

              return `
                <div class="intel-item">
                  <div class="intel-item-left">
                    <div class="intel-item-val">${valueDisplay}</div>
                    <div class="intel-item-sub">
                      <span>Label: <strong>${c.contact_label || c.contact_type}</strong></span>
                      ${sourceLink ? `<span>•</span> ${sourceLink}` : ''}
                    </div>
                  </div>
                  <div class="intel-item-right">
                    <span class="prio-badge">P: ${c.priority}</span>
                    <span class="conf-badge" style="background: ${confColor}20; color: ${confColor}; border: 1px solid ${confColor}30;">${c.confidence}%</span>
                  </div>
                </div>
              `;
            }).join('')
          : `<div style="color: var(--muted); font-size: 0.9rem; font-style: italic;">No communication channels found.</div>`;

        const dmsHtml = dms.length > 0
          ? dms.map(d => {
              const confColor = d.confidence > 70 ? 'var(--success)' : d.confidence > 40 ? 'var(--warn)' : 'var(--danger)';
              const linkedinLink = d.linkedin_url 
                ? `<a href="${d.linkedin_url}" target="_blank" rel="noreferrer" class="link-btn" style="color: #66d9ff; display: inline-flex; align-items: center; gap: 4px;">LinkedIn Profile</a>`
                : '<span style="color: var(--muted);">No LinkedIn</span>';
              
              const sourceLink = d.source_url
                ? `<a href="${d.source_url}" target="_blank" rel="noreferrer" class="link-btn">Source</a>`
                : '';

              return `
                <div class="intel-item" style="border-left: 3px solid var(--accent-2);">
                  <div class="intel-item-left">
                    <div class="intel-item-val">${d.name}</div>
                    <div class="intel-item-sub">
                      <strong style="color: #e7edf8;">${d.designation}</strong>
                      <span>•</span>
                      ${linkedinLink}
                      ${sourceLink ? `<span>•</span> ${sourceLink}` : ''}
                    </div>
                  </div>
                  <div class="intel-item-right">
                    <span class="prio-badge" style="background: rgba(138, 125, 255, 0.25); color: #dfdaff;">P: ${d.priority}</span>
                    <span class="conf-badge" style="background: ${confColor}20; color: ${confColor}; border: 1px solid ${confColor}30;">${d.confidence}%</span>
                  </div>
                </div>
              `;
            }).join('')
          : `<div style="color: var(--muted); font-size: 0.9rem; font-style: italic;">No leadership/decision makers identified.</div>`;

        return `
          <div class="intel-company">
            <div class="intel-header">
              <h3 class="intel-title">${companyIntel.company_name}</h3>
              ${companyIntel.industry ? `<span class="intel-industry">${companyIntel.industry}</span>` : ''}
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

    window.extractSingleContact = async (companyId, name, btn) => {
      if (btn) {
        btn.disabled = true;
        btn.textContent = 'Extracting...';
      }
      showToast('Extraction started', `Crawling official website and extracting intelligence for ${name}...`);
      try {
        const response = await fetch(`/api/v1/intelligence/extract/${companyId}`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' }
        });
        const data = await response.json();
        if (!response.ok) throw new Error(data.detail || 'Extraction failed');
        showToast('Extraction complete', `Successfully resolved profile for ${name}.`);
        await refreshCompanies();
      } catch (error) {
        showToast('Extraction failed', error.message);
      } finally {
        if (btn) {
          btn.disabled = false;
          btn.textContent = 'Extract Intel';
        }
      }
    };

    elements.extractAllBtn.addEventListener('click', async () => {
      elements.extractAllBtn.disabled = true;
      elements.extractAllBtn.textContent = 'Queuing...';
      try {
        const response = await fetch('/api/v1/intelligence/extract-all', { method: 'POST' });
        const data = await response.json();
        if (!response.ok) throw new Error(data.detail || 'Bulk extraction failed');
        showToast('Bulk extraction queued', `${data.queued} companies queued in the background.`);
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
        showToast('Search queued', `${data.queued} companies are queued for website search.`);
        await refreshCompanies();
      } catch (error) {
        showToast('Search failed', error.message);
      } finally {
        elements.searchBtn.disabled = false;
        elements.searchBtn.textContent = 'Trigger search';
      }
    });

    elements.refreshTop.addEventListener('click', () => {
      if (activeTab === 'companies') {
        refreshCompanies().catch(error => showToast('Refresh failed', error.message));
      } else {
        refreshContacts().catch(error => showToast('Refresh failed', error.message));
      }
    });
    
    // Initial load
    refreshCompanies().catch(error => showToast('Load failed', error.message));
  </script>
</body>
</html>
        """
    )
