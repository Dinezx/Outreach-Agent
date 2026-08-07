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
    .btn.danger { background: rgba(255, 123, 137, 0.2); border: 1px solid rgba(255, 123, 137, 0.4); color: var(--danger); }
    .btn.success { background: rgba(124, 242, 177, 0.2); border: 1px solid rgba(124, 242, 177, 0.4); color: var(--success); }
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
      flex-wrap: wrap;
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
    .tab-btn:hover { color: var(--text); background: rgba(255,255,255,0.03); }
    .tab-btn.active { color: var(--accent); background: rgba(102, 217, 255, 0.08); }

    .tab-content { display: none; }
    .tab-content.active { display: block; }

    .grid { display: grid; grid-template-columns: 1.08fr 1.4fr; gap: 20px; align-items: start; }
    .panel { padding: 22px; }
    .panel h2 { margin: 0 0 8px; font-size: 1.1rem; }
    .panel p.desc { margin: 0 0 18px; color: var(--muted); line-height: 1.55; }

    .upload-box { border: 1px dashed rgba(102, 217, 255, 0.28); border-radius: 18px; padding: 18px; background: rgba(255,255,255,0.03); }
    .upload-row { display: flex; gap: 12px; align-items: center; flex-wrap: wrap; }
    .file-label { display: inline-flex; align-items: center; gap: 10px; padding: 12px 16px; border-radius: 14px; background: rgba(255,255,255,0.05); color: var(--text); border: 1px solid var(--line); font-weight: 700; }
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
    
    /* Outreach Status Badges */
    .status-badge {
      display: inline-flex; align-items: center; padding: 4px 10px; border-radius: 999px; font-weight: 700; font-size: 0.78rem;
    }
    .status-PENDING_APPROVAL { background: rgba(255, 211, 111, 0.15); color: var(--warn); border: 1px solid rgba(255, 211, 111, 0.3); }
    .status-APPROVED { background: rgba(124, 242, 177, 0.15); color: var(--success); border: 1px solid rgba(124, 242, 177, 0.3); }
    .status-REJECTED { background: rgba(255, 123, 137, 0.15); color: var(--danger); border: 1px solid rgba(255, 123, 137, 0.3); }
    .status-SENT { background: rgba(102, 217, 255, 0.15); color: var(--accent); border: 1px solid rgba(102, 217, 255, 0.3); }
    .status-SCHEDULED { background: rgba(138, 125, 255, 0.15); color: var(--accent-2); border: 1px solid rgba(138, 125, 255, 0.3); }

    .empty { padding: 26px; border-radius: 18px; background: rgba(255,255,255,0.03); color: var(--muted); text-align: center; border: 1px dashed rgba(255,255,255,0.08); }
    .notice { margin-top: 14px; font-size: 0.92rem; color: var(--muted); }
    .toast {
      position: fixed; right: 18px; bottom: 18px; min-width: 280px; max-width: 420px; padding: 14px 16px; border-radius: 14px;
      background: rgba(9, 17, 31, 0.95); border: 1px solid rgba(102, 217, 255, 0.24); box-shadow: var(--shadow); transform: translateY(16px); opacity: 0; pointer-events: none; transition: .22s ease; z-index: 100;
    }
    .toast.show { opacity: 1; transform: translateY(0); }
    .toast strong { display: block; margin-bottom: 4px; }

    /* Modal / Drawer for Preview & Edit */
    .modal-overlay {
      position: fixed; inset: 0; background: rgba(0, 0, 0, 0.75); backdrop-filter: blur(8px);
      display: none; justify-content: center; align-items: center; z-index: 90; padding: 20px;
    }
    .modal-overlay.active { display: flex; }
    .modal-card {
      background: #0d1728; border: 1px solid var(--line); border-radius: var(--radius); width: 100%; max-width: 850px;
      max-height: 90vh; overflow-y: auto; padding: 28px; box-shadow: var(--shadow); position: relative;
    }
    .modal-close {
      position: absolute; top: 20px; right: 20px; background: transparent; border: none; color: var(--muted); font-size: 1.5rem; cursor: pointer;
    }
    .modal-close:hover { color: #fff; }
    .form-group { margin-bottom: 16px; }
    .form-label { display: block; font-weight: 700; font-size: 0.88rem; color: #aebadd; margin-bottom: 6px; }
    .form-input, .form-textarea {
      width: 100%; padding: 12px 14px; border-radius: 12px; background: rgba(0, 0, 0, 0.4); border: 1px solid var(--line); color: var(--text); font-family: var(--font); font-size: 0.95rem;
    }
    .form-textarea { min-height: 140px; resize: vertical; line-height: 1.5; }
    .form-input:focus, .form-textarea:focus { outline: none; border-color: var(--accent); }

    .meta-box {
      background: rgba(255,255,255,0.03); border: 1px solid var(--line); padding: 14px 18px; border-radius: 14px; margin-bottom: 20px;
      display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 12px;
    }
    .meta-item .key { font-size: 0.78rem; text-transform: uppercase; color: var(--muted); font-weight: 700; }
    .meta-item .val { font-size: 0.95rem; font-weight: 700; color: #fff; margin-top: 2px; }

    .sub-tabs { display: flex; gap: 8px; margin-bottom: 16px; border-bottom: 1px solid var(--line); padding-bottom: 8px; }
    .sub-tab-btn { background: transparent; border: none; color: var(--muted); padding: 6px 14px; border-radius: 6px; cursor: pointer; font-weight: 700; font-size: 0.9rem; }
    .sub-tab-btn.active { color: var(--accent); background: rgba(102, 217, 255, 0.1); }

    .counter { font-size: 0.8rem; color: var(--muted); text-align: right; margin-top: 4px; }
    .counter.warn { color: var(--warn); }
    .counter.danger { color: var(--danger); }
  </style>
</head>
<body>
  <div class="wrap">
    <section class="hero">
      <div class="brand">
        <span class="eyebrow">LeadMinerAI Dashboard & Platform</span>
        <h1>Industrial B2B Business & Contact Intelligence.</h1>
        <p class="lead">Automated public web crawling, contact extraction, industrial classification, department prediction, operational pain forecasting, and human-approved research outreach campaigns.</p>
        <div class="brand-actions">
          <a class="btn" href="/docs" target="_blank" rel="noreferrer">Open API docs</a>
          <button class="btn secondary" id="refreshTop">Refresh data</button>
        </div>
      </div>
      <div class="stats">
        <div class="stat"><div class="label">Total companies</div><div class="value" id="statTotal">0</div><div class="sub">Companies in database</div></div>
        <div class="stat"><div class="label">Business Profiles</div><div class="value" id="statBusiness">0</div><div class="sub">Analyzed profiles</div></div>
        <div class="stat"><div class="label">Outreach Campaigns</div><div class="value" id="statOutreach">0</div><div class="sub">Pending & approved</div></div>
      </div>
    </section>

    <div class="tabs-bar">
      <button class="tab-btn active" id="tabCompaniesBtn">Companies & Websites</button>
      <button class="tab-btn" id="tabBusinessBtn">Business Intelligence</button>
      <button class="tab-btn" id="tabContactsBtn">Contact Intelligence</button>
      <button class="tab-btn" id="tabOutreachBtn" style="color: var(--accent);">Outreach Center</button>
      <button class="tab-btn" id="tabGmailBtn" style="color: var(--success);">Gmail Monitor</button>
    </div>

    <!-- Tab 1: Companies -->
    <div id="tabCompanies" class="tab-content active">
      <section class="grid">
        <div class="panel">
          <h2>1. Upload companies</h2>
          <p class="desc">Upload a CSV or Excel (.xlsx) file with a <strong>company_name</strong> column.</p>
          <div class="upload-box">
            <div class="upload-row">
              <label class="file-label" for="csvFile">Choose File</label>
              <input id="csvFile" type="file" accept=".csv,.xlsx" />
              <span class="file-name" id="fileName">No file chosen</span>
            </div>
            <div class="toolbar">
              <button class="btn" id="uploadBtn">Upload file</button>
              <button class="btn secondary" id="searchBtn">Trigger search</button>
              <a class="btn secondary" href="/api/v1/companies/export">Export Excel</a>
            </div>
          </div>
          <div class="notice" id="uploadResult"></div>
        </div>

        <div class="panel">
          <h2>2. Company List & Actions</h2>
          <div id="tableWrap"></div>
        </div>
      </section>
    </div>

    <!-- Tab 2: Business Intelligence -->
    <div id="tabBusiness" class="tab-content">
      <section class="grid" style="grid-template-columns: 1fr;">
        <div class="panel">
          <h2>Business Intelligence Profiles</h2>
          <div id="businessListWrap" style="margin-top: 15px;"></div>
        </div>
      </section>
    </div>

    <!-- Tab 3: Contact Intelligence -->
    <div id="tabContacts" class="tab-content">
      <section class="grid" style="grid-template-columns: 1fr;">
        <div class="panel">
          <h2>Contact Intelligence</h2>
          <div id="contactsTableWrap" style="margin-top: 25px;"></div>
        </div>
      </section>
    </div>

    <!-- Tab 4: Outreach Center -->
    <div id="tabOutreach" class="tab-content">
      <section class="grid" style="grid-template-columns: 1fr;">
        <div class="panel">
          <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 16px; margin-bottom: 20px;">
            <div>
              <h2>Outreach Intelligence Center</h2>
              <p class="desc" style="margin-bottom: 0;">Multi-channel research outreach invitations with human approval workflow (Strictly non-sales research).</p>
            </div>
            <div class="toolbar" style="margin-top: 0;">
              <button class="btn" id="generateAllOutreachBtn">Bulk Generate Outreach</button>
              <a class="btn secondary" href="/api/outreach/export/csv">Export CSV</a>
              <a class="btn secondary" href="/api/outreach/export/excel">Export Excel</a>
              <a class="btn secondary" href="/api/outreach/export/pdf" target="_blank">Export PDF Briefs</a>
            </div>
          </div>

          <div id="outreachTableWrap"></div>
        </div>
      </section>
    </div>

    <!-- Tab 5: Gmail Outreach Monitor -->
    <div id="tabGmail" class="tab-content">
      <section class="grid" style="grid-template-columns: 1fr;">
        <div class="panel">
          <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 16px; margin-bottom: 20px;">
            <div>
              <h2>Gmail Outreach Monitor & Integration</h2>
              <p class="desc" style="margin-bottom: 0;">Official Gmail REST API Integration (OAuth 2.0). Automatic thread tracking & reply monitoring.</p>
            </div>
            <div class="toolbar" style="margin-top: 0;">
              <button class="btn success" id="connectGmailBtn">Connect Gmail (OAuth 2.0)</button>
              <button class="btn secondary" id="pollRepliesBtn">Poll New Replies</button>
              <button class="btn" id="bulkSendGmailBtn">Bulk Send via Gmail API</button>
            </div>
          </div>

          <!-- Account Connection Banner -->
          <div style="background: rgba(124, 242, 177, 0.08); border: 1px solid rgba(124, 242, 177, 0.25); padding: 14px 18px; border-radius: 14px; margin-bottom: 20px; display: flex; justify-content: space-between; align-items: center;" id="gmailAccountBanner">
            <div>
              <span style="color: var(--muted); font-size: 0.85rem;">Authenticated Gmail Account:</span>
              <strong style="color: var(--success); font-size: 1.05rem; display: block; margin-top: 2px;" id="gmailAccountEmail">dineshkumarsaj@gmail.com (Connected)</strong>
            </div>
            <span class="badge" style="background: rgba(124, 242, 177, 0.15); color: var(--success); font-size: 0.82rem; padding: 6px 12px; border-radius: 999px;">OAuth 2.0 Active</span>
          </div>

          <div id="gmailTableWrap"></div>
        </div>
      </section>
    </div>

  </div>

  <!-- Preview & Edit Modal -->
  <div class="modal-overlay" id="previewModal">
    <div class="modal-card">
      <button class="modal-close" id="modalCloseBtn">&times;</button>
      <h2 style="margin: 0 0 6px 0; color: #fff;" id="modalCompanyTitle">Company Outreach Preview</h2>
      <div style="color: var(--muted); font-size: 0.9rem; margin-bottom: 16px;" id="modalSubTitle">Targeting Operations Manager</div>

      <div class="meta-box">
        <div class="meta-item"><div class="key">Target Role</div><div class="val" id="metaRole">-</div></div>
        <div class="meta-item"><div class="key">Best Channel</div><div class="val" id="metaChannel">-</div></div>
        <div class="meta-item"><div class="key">Channel Conf.</div><div class="val" id="metaConf">-</div></div>
        <div class="meta-item"><div class="key">Status</div><div class="val" id="metaStatus">-</div></div>
      </div>

      <div style="background: rgba(102, 217, 255, 0.06); border: 1px solid rgba(102, 217, 255, 0.15); padding: 12px; border-radius: 12px; font-size: 0.88rem; color: #bde7ff; margin-bottom: 18px;" id="modalReason">
        Reasoning: Primary operations contact identified.
      </div>

      <div class="sub-tabs">
        <button class="sub-tab-btn active" id="subTabEmailBtn">1. Research Email</button>
        <button class="sub-tab-btn" id="subTabLinkedinBtn">2. LinkedIn Message</button>
        <button class="sub-tab-btn" id="subTabPhoneBtn">3. Phone Script</button>
        <button class="sub-tab-btn" id="subTabHistoryBtn">4. Approval History</button>
      </div>

      <!-- Sub Tab 1: Email -->
      <div id="subTabEmail" class="sub-tab-content">
        <div class="form-group">
          <label class="form-label">Subject Line</label>
          <input type="text" class="form-input" id="editSubject" />
        </div>
        <div class="form-group">
          <label class="form-label">Research Invitation Email Body (Non-Sales Pitch)</label>
          <textarea class="form-textarea" id="editEmailBody" style="min-height: 200px;"></textarea>
          <div class="counter" id="emailWordCount">Words: 0 / 180 (Max 180)</div>
        </div>
      </div>

      <!-- Sub Tab 2: LinkedIn -->
      <div id="subTabLinkedin" class="sub-tab-content" style="display: none;">
        <div class="form-group">
          <label class="form-label">LinkedIn Research Invitation (Max 300 Chars)</label>
          <textarea class="form-textarea" id="editLinkedinMsg" style="min-height: 120px;"></textarea>
          <div class="counter" id="linkedinCharCount">Chars: 0 / 300 (Max 300)</div>
        </div>
      </div>

      <!-- Sub Tab 3: Phone Script -->
      <div id="subTabPhone" class="sub-tab-content" style="display: none;">
        <div class="form-group">
          <label class="form-label">Independent Researcher Call Script</label>
          <textarea class="form-textarea" id="editPhoneScript" style="min-height: 160px;"></textarea>
        </div>
      </div>

      <!-- Sub Tab 4: History -->
      <div id="subTabHistory" class="sub-tab-content" style="display: none;">
        <div id="historyLogWrap" style="font-size: 0.9rem;"></div>
      </div>

      <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px; margin-top: 24px; border-top: 1px solid var(--line); padding-top: 18px;">
        <button class="btn secondary" id="modalSaveBtn">Save Changes</button>
        <div style="display: flex; gap: 10px; flex-wrap: wrap;">
          <button class="btn danger" id="modalRejectBtn">Reject</button>
          <button class="btn success" id="modalApproveBtn">Approve Campaign</button>
          <button class="btn" id="modalSendBtn">Send Outreach Now</button>
        </div>
      </div>
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
      tableWrap: document.getElementById('tableWrap'),
      toast: document.getElementById('toast'),
      statTotal: document.getElementById('statTotal'),
      statBusiness: document.getElementById('statBusiness'),
      statOutreach: document.getElementById('statOutreach'),
      
      tabCompanies: document.getElementById('tabCompanies'),
      tabBusiness: document.getElementById('tabBusiness'),
      tabContacts: document.getElementById('tabContacts'),
      tabOutreach: document.getElementById('tabOutreach'),
      tabCompaniesBtn: document.getElementById('tabCompaniesBtn'),
      tabBusinessBtn: document.getElementById('tabBusinessBtn'),
      tabContactsBtn: document.getElementById('tabContactsBtn'),
      tabOutreachBtn: document.getElementById('tabOutreachBtn'),
      tabGmailBtn: document.getElementById('tabGmailBtn'),
      
      tabCompanies: document.getElementById('tabCompanies'),
      tabBusiness: document.getElementById('tabBusiness'),
      tabContacts: document.getElementById('tabContacts'),
      tabOutreach: document.getElementById('tabOutreach'),
      tabGmail: document.getElementById('tabGmail'),
      
      businessListWrap: document.getElementById('businessListWrap'),
      contactsTableWrap: document.getElementById('contactsTableWrap'),
      outreachTableWrap: document.getElementById('outreachTableWrap'),
      gmailTableWrap: document.getElementById('gmailTableWrap'),
      generateAllOutreachBtn: document.getElementById('generateAllOutreachBtn'),
      
      connectGmailBtn: document.getElementById('connectGmailBtn'),
      pollRepliesBtn: document.getElementById('pollRepliesBtn'),
      bulkSendGmailBtn: document.getElementById('bulkSendGmailBtn'),
      gmailAccountEmail: document.getElementById('gmailAccountEmail'),
      
      // Modal elements
      modal: document.getElementById('previewModal'),
      modalCloseBtn: document.getElementById('modalCloseBtn'),
      modalCompanyTitle: document.getElementById('modalCompanyTitle'),
      modalSubTitle: document.getElementById('modalSubTitle'),
      metaRole: document.getElementById('metaRole'),
      metaChannel: document.getElementById('metaChannel'),
      metaConf: document.getElementById('metaConf'),
      metaStatus: document.getElementById('metaStatus'),
      modalReason: document.getElementById('modalReason'),
      
      editSubject: document.getElementById('editSubject'),
      editEmailBody: document.getElementById('editEmailBody'),
      editLinkedinMsg: document.getElementById('editLinkedinMsg'),
      editPhoneScript: document.getElementById('editPhoneScript'),
      emailWordCount: document.getElementById('emailWordCount'),
      linkedinCharCount: document.getElementById('linkedinCharCount'),
      historyLogWrap: document.getElementById('historyLogWrap'),
      
      modalSaveBtn: document.getElementById('modalSaveBtn'),
      modalApproveBtn: document.getElementById('modalApproveBtn'),
      modalRejectBtn: document.getElementById('modalRejectBtn'),
      modalSendBtn: document.getElementById('modalSendBtn'),
      
      subTabEmailBtn: document.getElementById('subTabEmailBtn'),
      subTabLinkedinBtn: document.getElementById('subTabLinkedinBtn'),
      subTabPhoneBtn: document.getElementById('subTabPhoneBtn'),
      subTabHistoryBtn: document.getElementById('subTabHistoryBtn'),
      subTabEmail: document.getElementById('subTabEmail'),
      subTabLinkedin: document.getElementById('subTabLinkedin'),
      subTabPhone: document.getElementById('subTabPhone'),
      subTabHistory: document.getElementById('subTabHistory'),
    };

    let activeTab = 'companies';
    let currentCampaign = null;

    function showToast(title, message) {
      elements.toast.innerHTML = `<strong>${title}</strong><div>${message}</div>`;
      elements.toast.classList.add('show');
      clearTimeout(window.__toastTimer);
      window.__toastTimer = setTimeout(() => elements.toast.classList.remove('show'), 3500);
    }

    function switchTab(target) {
      activeTab = target;
      [elements.tabCompanies, elements.tabBusiness, elements.tabContacts, elements.tabOutreach, elements.tabGmail].forEach(el => el && el.classList.remove('active'));
      [elements.tabCompaniesBtn, elements.tabBusinessBtn, elements.tabContactsBtn, elements.tabOutreachBtn, elements.tabGmailBtn].forEach(el => el && el.classList.remove('active'));

      if (target === 'companies') {
        elements.tabCompanies.classList.add('active');
        elements.tabCompaniesBtn.classList.add('active');
        refreshCompanies();
      } else if (target === 'business') {
        elements.tabBusiness.classList.add('active');
        elements.tabBusinessBtn.classList.add('active');
        refreshBusinessIntelligence();
      } else if (target === 'contacts') {
        elements.tabContacts.classList.add('active');
        elements.tabContactsBtn.classList.add('active');
        refreshContacts();
      } else if (target === 'outreach') {
        elements.tabOutreach.classList.add('active');
        elements.tabOutreachBtn.classList.add('active');
        refreshOutreach();
      } else if (target === 'gmail') {
        elements.tabGmail.classList.add('active');
        elements.tabGmailBtn.classList.add('active');
        refreshGmail();
      }
    }

    elements.tabCompaniesBtn.addEventListener('click', () => switchTab('companies'));
    elements.tabBusinessBtn.addEventListener('click', () => switchTab('business'));
    elements.tabContactsBtn.addEventListener('click', () => switchTab('contacts'));
    elements.tabOutreachBtn.addEventListener('click', () => switchTab('outreach'));
    elements.tabGmailBtn.addEventListener('click', () => switchTab('gmail'));


    async function refreshCompanies() {
      const response = await fetch('/api/v1/companies?limit=200');
      if (!response.ok) return;
      const data = await response.json();
      const items = data.items || [];
      elements.statTotal.textContent = data.total ?? items.length;

      if (!items.length) {
        elements.tableWrap.innerHTML = `<div class="empty">No companies yet. Upload a CSV/XLSX to begin.</div>`;
        return;
      }

      elements.tableWrap.innerHTML = `
        <table>
          <thead>
            <tr><th>Company</th><th>Status</th><th>Website</th><th>Actions</th></tr>
          </thead>
          <tbody>
            ${items.map(item => `
              <tr>
                <td><strong>${item.name}</strong></td>
                <td><span class="status ${item.status}">${item.status}</span></td>
                <td>${item.website_url ? `<a href="${item.website_url}" target="_blank" rel="noreferrer">${item.website_url}</a>` : '—'}</td>
                <td>
                  <button class="btn secondary" style="padding:4px 8px; font-size:0.78rem;" onclick="generateSingleOutreach('${item.id}', '${item.name.replace(/'/g, "\\'")}', this)">Generate Outreach</button>
                </td>
              </tr>
            `).join('')}
          </tbody>
        </table>
      `;
    }

    async function refreshOutreach() {
      const response = await fetch('/api/outreach?limit=200');
      if (!response.ok) return;
      const data = await response.json();
      const items = data.items || [];
      elements.statOutreach.textContent = data.total ?? items.length;

      if (!items.length) {
        elements.outreachTableWrap.innerHTML = `<div class="empty">No outreach campaigns generated yet. Click "Bulk Generate Outreach" or generate per company.</div>`;
        return;
      }

      elements.outreachTableWrap.innerHTML = `
        <table>
          <thead>
            <tr>
              <th>Company</th>
              <th>Target Contact & Role</th>
              <th>Channel</th>
              <th>Subject</th>
              <th>Status</th>
              <th>Confidence</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            ${items.map(c => `
              <tr>
                <td><strong>${c.company_name || 'Company'}</strong></td>
                <td>
                  <strong style="color:#fff;">${c.decision_maker_name || c.target_role || 'Operations Lead'}</strong>
                  <div style="font-size:0.8rem; color:var(--muted);">${c.decision_maker_designation || c.target_role || ''}</div>
                </td>
                <td><span class="chip" style="font-size:0.8rem;">${c.channel}</span></td>
                <td style="max-width:220px; overflow:hidden; text-overflow:ellipsis; white-space:nowrap;">${c.subject || '—'}</td>
                <td><span class="status-badge status-${c.status}">${c.status}</span></td>
                <td><strong style="color:var(--accent);">${c.overall_confidence}%</strong></td>
                <td>
                  <div style="display:flex; gap:6px; flex-wrap:wrap;">
                    <button class="btn secondary" style="padding:4px 8px; font-size:0.76rem;" onclick="openPreviewModal('${c.id}')">Preview / Edit</button>
                    ${c.status !== 'APPROVED' && c.status !== 'SENT' ? `<button class="btn success" style="padding:4px 8px; font-size:0.76rem;" onclick="quickApprove('${c.id}', this)">Approve</button>` : ''}
                    ${c.status === 'APPROVED' ? `<button class="btn" style="padding:4px 8px; font-size:0.76rem;" onclick="quickSend('${c.id}', this)">Send</button>` : ''}
                  </div>
                </td>
              </tr>
            `).join('')}
          </tbody>
        </table>
      `;
    }

    async function openPreviewModal(campaignId) {
      const response = await fetch(`/api/outreach/${campaignId}`);
      if (!response.ok) return showToast('Error', 'Failed to fetch campaign details');
      currentCampaign = await response.json();

      elements.modalCompanyTitle.textContent = currentCampaign.company_name || 'Company Outreach';
      elements.modalSubTitle.textContent = `Targeting: ${currentCampaign.decision_maker_name || currentCampaign.target_role || 'Operations Lead'}`;
      elements.metaRole.textContent = currentCampaign.target_role || 'Operations Lead';
      elements.metaChannel.textContent = `${currentCampaign.channel} (${currentCampaign.channel_confidence}%)`;
      elements.metaConf.textContent = `${currentCampaign.overall_confidence}%`;
      elements.metaStatus.textContent = currentCampaign.status;
      elements.modalReason.textContent = `Recommendation Reasoning: ${currentCampaign.recommendation_reason || 'Primary operations leadership selected.'}`;

      elements.editSubject.value = currentCampaign.subject || '';
      elements.editEmailBody.value = currentCampaign.email_body || '';
      elements.editLinkedinMsg.value = currentCampaign.linkedin_message || '';
      elements.editPhoneScript.value = currentCampaign.phone_script || '';

      updateCounters();

      // Render History Log
      const hist = currentCampaign.history || [];
      elements.historyLogWrap.innerHTML = hist.map(h => `
        <div style="border-left: 2px solid var(--accent); padding-left: 10px; margin-bottom: 10px;">
          <div style="font-weight: 700; color: #fff;">${h.action} <span style="font-size:0.78rem; color:var(--muted); font-weight:normal;">• ${new Date(h.timestamp).toLocaleString()}</span></div>
          <div style="color: var(--muted);">${h.notes || ''}</div>
        </div>
      `).join('') || '<div style="color:var(--muted)">No history entries</div>';

      elements.modal.classList.add('active');
    }

    function updateCounters() {
      const emailWords = (elements.editEmailBody.value.trim().match(/\\s+/) ? elements.editEmailBody.value.trim().split(/\\s+/).length : (elements.editEmailBody.value ? 1 : 0));
      elements.emailWordCount.textContent = `Words: ${emailWords} / 180 (Max 180)`;
      elements.emailWordCount.className = emailWords > 180 ? 'counter danger' : emailWords > 160 ? 'counter warn' : 'counter';

      const linkedinChars = elements.editLinkedinMsg.value.length;
      elements.linkedinCharCount.textContent = `Chars: ${linkedinChars} / 300 (Max 300)`;
      elements.linkedinCharCount.className = linkedinChars > 300 ? 'counter danger' : linkedinChars > 270 ? 'counter warn' : 'counter';
    }

    elements.editEmailBody.addEventListener('input', updateCounters);
    elements.editLinkedinMsg.addEventListener('input', updateCounters);

    elements.modalCloseBtn.addEventListener('click', () => elements.modal.classList.remove('active'));

    // Modal Sub Tabs
    function switchSubTab(target) {
      [elements.subTabEmail, elements.subTabLinkedin, elements.subTabPhone, elements.subTabHistory].forEach(el => el.style.display = 'none');
      [elements.subTabEmailBtn, elements.subTabLinkedinBtn, elements.subTabPhoneBtn, elements.subTabHistoryBtn].forEach(el => el.classList.remove('active'));

      if (target === 'email') { elements.subTabEmail.style.display = 'block'; elements.subTabEmailBtn.classList.add('active'); }
      else if (target === 'linkedin') { elements.subTabLinkedin.style.display = 'block'; elements.subTabLinkedinBtn.classList.add('active'); }
      else if (target === 'phone') { elements.subTabPhone.style.display = 'block'; elements.subTabPhoneBtn.classList.add('active'); }
      else { elements.subTabHistory.style.display = 'block'; elements.subTabHistoryBtn.classList.add('active'); }
    }

    elements.subTabEmailBtn.addEventListener('click', () => switchSubTab('email'));
    elements.subTabLinkedinBtn.addEventListener('click', () => switchSubTab('linkedin'));
    elements.subTabPhoneBtn.addEventListener('click', () => switchSubTab('phone'));
    elements.subTabHistoryBtn.addEventListener('click', () => switchSubTab('history'));

    // Modal Actions
    elements.modalSaveBtn.addEventListener('click', async () => {
      if (!currentCampaign) return;
      try {
        const resp = await fetch(`/api/outreach/${currentCampaign.id}/edit`, {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            subject: elements.editSubject.value,
            email_body: elements.editEmailBody.value,
            linkedin_message: elements.editLinkedinMsg.value,
            phone_script: elements.editPhoneScript.value
          })
        });
        if (!resp.ok) throw new Error('Save failed');
        showToast('Saved', 'Outreach message updated successfully.');
        elements.modal.classList.remove('active');
        await refreshOutreach();
      } catch (err) { showToast('Error', err.message); }
    });

    elements.modalApproveBtn.addEventListener('click', async () => {
      if (!currentCampaign) return;
      try {
        const resp = await fetch(`/api/outreach/${currentCampaign.id}/approve`, { method: 'PUT', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({notes: 'Approved via Preview Modal'}) });
        if (!resp.ok) throw new Error('Approve failed');
        showToast('Approved', 'Campaign approved for outreach.');
        elements.modal.classList.remove('active');
        await refreshOutreach();
      } catch (err) { showToast('Error', err.message); }
    });

    elements.modalRejectBtn.addEventListener('click', async () => {
      if (!currentCampaign) return;
      const reason = prompt('Enter rejection reason:') || 'Rejected by human reviewer';
      try {
        const resp = await fetch(`/api/outreach/${currentCampaign.id}/reject`, { method: 'PUT', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({reason}) });
        if (!resp.ok) throw new Error('Reject failed');
        showToast('Rejected', 'Campaign marked as REJECTED.');
        elements.modal.classList.remove('active');
        await refreshOutreach();
      } catch (err) { showToast('Error', err.message); }
    });

    elements.modalSendBtn.addEventListener('click', async () => {
      if (!currentCampaign) return;
      try {
        const resp = await fetch(`/api/outreach/${currentCampaign.id}/send`, { method: 'POST' });
        if (!resp.ok) throw new Error('Send failed');
        showToast('Sent', 'Outreach invitation sent successfully.');
        elements.modal.classList.remove('active');
        await refreshOutreach();
      } catch (err) { showToast('Error', err.message); }
    });

    window.quickApprove = async (id, btn) => {
      if (btn) btn.disabled = true;
      try {
        const resp = await fetch(`/api/outreach/${id}/approve`, { method: 'PUT', headers: {'Content-Type':'application/json'}, body: JSON.stringify({}) });
        if (!resp.ok) throw new Error('Approve failed');
        showToast('Approved', 'Campaign approved.');
        await refreshOutreach();
      } catch (err) { showToast('Error', err.message); }
    };

    window.quickSend = async (id, btn) => {
      if (btn) btn.disabled = true;
      try {
        const resp = await fetch(`/api/outreach/${id}/send`, { method: 'POST' });
        if (!resp.ok) throw new Error('Send failed');
        showToast('Sent', 'Outreach invitation dispatched.');
        await refreshOutreach();
      } catch (err) { showToast('Error', err.message); }
    };

    window.generateSingleOutreach = async (companyId, name, btn) => {
      if (btn) { btn.disabled = true; btn.textContent = 'Generating...'; }
      showToast('Outreach Generation', `Generating research outreach for ${name}...`);
      try {
        const resp = await fetch(`/api/outreach/generate/${companyId}`, { method: 'POST' });
        if (!resp.ok) throw new Error('Outreach generation failed');
        showToast('Generated', `Successfully created outreach campaign for ${name}.`);
        switchTab('outreach');
      } catch (err) { showToast('Error', err.message); }
      finally { if (btn) { btn.disabled = false; btn.textContent = 'Generate Outreach'; } }
    };

    elements.generateAllOutreachBtn.addEventListener('click', async () => {
      elements.generateAllOutreachBtn.disabled = true;
      elements.generateAllOutreachBtn.textContent = 'Queuing...';
      try {
        const resp = await fetch('/api/outreach/generate-all', { method: 'POST' });
        if (!resp.ok) throw new Error('Bulk outreach generation failed');
        showToast('Queued', 'Bulk outreach generation queued in background.');
        await refreshOutreach();
      } catch (err) { showToast('Error', err.message); }
      finally {
        elements.generateAllOutreachBtn.disabled = false;
        elements.generateAllOutreachBtn.textContent = 'Bulk Generate Outreach';
      }
    });

    elements.refreshTop.addEventListener('click', () => {
      if (activeTab === 'companies') refreshCompanies();
      else if (activeTab === 'outreach') refreshOutreach();
      else if (activeTab === 'gmail') refreshGmail();
    });

    async function refreshGmail() {
      try {
        const accResp = await fetch('/api/gmail/me');
        if (accResp.ok) {
          const acc = await accResp.json();
          elements.gmailAccountEmail.textContent = `${acc.email} (Connected via OAuth 2.0)`;
        }
      } catch (err) {}

      const response = await fetch('/api/gmail/messages');
      if (!response.ok) return;
      const data = await response.json();
      const items = data.items || [];

      if (!items.length) {
        elements.gmailTableWrap.innerHTML = '<div style="color:var(--muted); text-align:center; padding:30px;">No Gmail outreach messages logged yet. Use <strong>Outreach Center</strong> to generate and approve emails.</div>';
        return;
      }

      elements.gmailTableWrap.innerHTML = `
        <table>
          <thead>
            <tr>
              <th>Company</th>
              <th>Recipient Email</th>
              <th>Status</th>
              <th>Sent At</th>
              <th>Replied At</th>
              <th>Thread ID</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            ${items.map(m => `
              <tr>
                <td><strong>${m.company_name || 'Company'}</strong></td>
                <td>${m.recipient_email || '-'}</td>
                <td><span class="badge ${m.status === 'REPLIED' ? 'success' : m.status === 'SENT' ? 'warn' : 'danger'}">${m.status}</span></td>
                <td>${m.sent_at ? new Date(m.sent_at).toLocaleTimeString() : '-'}</td>
                <td>${m.replied_at ? new Date(m.replied_at).toLocaleTimeString() : '-'}</td>
                <td><code style="color:var(--accent);">${(m.thread_id || '-').substring(0, 12)}</code></td>
                <td>
                  <div style="display:flex; gap:6px; flex-wrap:wrap;">
                    ${m.reply_body ? `<button class="btn secondary" style="padding:4px 8px; font-size:0.76rem;" onclick="alert('Reply from ${m.reply_from}:\\\\n\\\\n${m.reply_body}')">View Reply</button>` : ''}
                    <button class="btn secondary" style="padding:4px 8px; font-size:0.76rem;" onclick="scheduleFollowUp('${m.id}')">Follow-Up (3d)</button>
                  </div>
                </td>
              </tr>
            `).join('')}
          </tbody>
        </table>
      `;
    }

    elements.connectGmailBtn.addEventListener('click', async () => {
      try {
        const resp = await fetch('/api/gmail/auth-url');
        const data = await resp.json();
        if (data.auth_url) {
          window.open(data.auth_url, '_blank');
          showToast('OAuth 2.0', 'Redirecting to Google OAuth login screen...');
        }
      } catch (err) { showToast('Error', err.message); }
    });

    elements.pollRepliesBtn.addEventListener('click', async () => {
      elements.pollRepliesBtn.disabled = true;
      elements.pollRepliesBtn.textContent = 'Polling...';
      try {
        const resp = await fetch('/api/gmail/poll-replies', { method: 'POST' });
        if (!resp.ok) throw new Error('Polling failed');
        const resData = await resp.json();
        showToast('Reply Tracker', resData.message);
        await refreshGmail();
      } catch (err) { showToast('Error', err.message); }
      finally {
        elements.pollRepliesBtn.disabled = false;
        elements.pollRepliesBtn.textContent = 'Poll New Replies';
      }
    });

    elements.bulkSendGmailBtn.addEventListener('click', async () => {
      elements.bulkSendGmailBtn.disabled = true;
      elements.bulkSendGmailBtn.textContent = 'Sending...';
      try {
        const listResp = await fetch('/api/outreach?status=APPROVED');
        if (!listResp.ok) throw new Error('Failed to fetch approved campaigns');
        const listData = await listResp.json();
        const campaignIds = (listData.items || []).map(c => c.id);

        if (!campaignIds.length) {
          showToast('Notice', 'No APPROVED campaigns ready for Gmail dispatch.');
          return;
        }

        const resp = await fetch('/api/gmail/send-bulk', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ campaign_ids: campaignIds })
        });
        if (!resp.ok) throw new Error('Bulk send failed');
        const resData = await resp.json();
        showToast('Gmail Dispatch', resData.message);
        await refreshGmail();
      } catch (err) { showToast('Error', err.message); }
      finally {
        elements.bulkSendGmailBtn.disabled = false;
        elements.bulkSendGmailBtn.textContent = 'Bulk Send via Gmail API';
      }
    });

    window.scheduleFollowUp = async (msgId) => {
      try {
        const resp = await fetch(`/api/gmail/messages/${msgId}/follow-up`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ follow_up_days: 3 })
        });
        if (!resp.ok) throw new Error('Schedule follow up failed');
        showToast('Follow-Up Scheduled', 'Scheduled 3-day follow-up message.');
        await refreshGmail();
      } catch (err) { showToast('Error', err.message); }
    };

    // Initial load
    refreshCompanies();
  </script>
</body>
</html>
        """
    )

