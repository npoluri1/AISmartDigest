const Views = {
  showLoading() {
    document.getElementById('app').innerHTML = `
      <div class="loading-screen"><div class="loader"></div></div>`;
  },

  showToast(msg) {
    let el = document.querySelector('.toast');
    if (!el) {
      el = document.createElement('div');
      el.className = 'toast';
      document.body.appendChild(el);
    }
    el.textContent = msg;
    el.classList.add('show');
    clearTimeout(el._timeout);
    el._timeout = setTimeout(() => el.classList.remove('show'), 2500);
  },

  platformIcon(platform) {
    const icons = {
      youtube: '<svg viewBox="0 0 24 24" width="14" height="14" fill="currentColor"><polygon points="9.75,15.54 9.75,8.46 15.75,12 9.75,15.54"/><path d="M12,2C6.48,2,2,6.48,2,12s4.48,10,10,10s10-4.48,10-10S17.52,2,12,2z M17,12l-7,4.54V7.46L17,12z"/></svg>',
      tiktok: '<svg viewBox="0 0 24 24" width="14" height="14" fill="currentColor"><path d="M19.59 6.69a4.83 4.83 0 0 1-3.77-4.25V2h-3.45v13.67a2.89 2.89 0 0 1-2.88 2.69 2.89 2.89 0 0 1-2.88-2.89 2.89 2.89 0 0 1 2.88-2.89c.28 0 .56.04.84.1V9.46a6.35 6.35 0 0 0-.84-.06A6.34 6.34 0 0 0 3 15.73a6.34 6.34 0 0 0 6.33 6.33 6.34 6.34 0 0 0 6.34-6.33v-8a8.31 8.31 0 0 0 4.87 1.48v-3.5a4.85 4.85 0 0 1-.95-.02z"/></svg>',
      instagram: '<svg viewBox="0 0 24 24" width="14" height="14" fill="currentColor"><path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zM12 0C8.741 0 8.333.014 7.053.072 2.695.272.273 2.69.073 7.052.014 8.333 0 8.741 0 12c0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98C8.333 23.986 8.741 24 12 24c3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98C15.668.014 15.259 0 12 0zm0 5.838a6.162 6.162 0 1 0 0 12.324 6.162 6.162 0 0 0 0-12.324zM12 16a4 4 0 1 1 0-8 4 4 0 0 1 0 8zm6.406-11.845a1.44 1.44 0 1 0 0 2.881 1.44 1.44 0 0 0 0-2.881z"/></svg>',
      facebook: '<svg viewBox="0 0 24 24" width="14" height="14" fill="currentColor"><path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/></svg>',
    };
    return icons[platform] || '';
  },

  renderDigestCard(e) {
    const score = e.relevance_score || 0;
    const scoreClass = score >= 8 ? 'badge-score-high' : 'badge-score';
    const tools = (e.ai_tools || []).slice(0, 5);
    const thumb = e.thumbnail_url || '';
    const vid = e.url ? (e.url.match(/(?:v=|youtu\.be\/|shorts\/)([\w-]{11})/) || [])[1] || '' : '';
    const thumbHtml = thumb ? `url(${this.escape(thumb)})` : (vid ? `url(https://img.youtube.com/vi/${vid}/mqdefault.jpg)` : '');
    return `
      <div class="digest-card fade-in" onclick="router.navigate('digests/${e.id}')">
        ${thumbHtml ? `<div class="digest-card-thumb" style="background-image:${thumbHtml}"><div class="digest-card-thumb-overlay"><svg viewBox="0 0 24 24" width="40" height="40" fill="white" opacity="0.9"><polygon points="8,5 19,12 8,19"/></svg></div></div>` : ''}
        <div class="digest-card-body">
          <div class="digest-card-top">
            <div class="digest-card-title">${this.escape(e.title || 'Untitled')}</div>
            <div class="digest-card-badges">
              <span class="badge badge-platform">${this.platformIcon(e.platform)} ${e.platform}</span>
              <span class="badge ${scoreClass}">${score}</span>
            </div>
          </div>
          <div class="digest-card-summary">${this.escape((e.summary || '').slice(0, 150))}</div>
          ${tools.length ? `<div class="digest-card-tools">${tools.map(t => `<span class="tool-tag">${this.escape(t)}</span>`).join('')}</div>` : ''}
          <div class="digest-card-meta">
            <span><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>${e.processed_at ? new Date(e.processed_at).toLocaleDateString() : ''}</span>
            <span style="font-size:11px;color:var(--text-tertiary)">${e.platform === 'youtube' ? 'YouTube' : e.platform}</span>
          </div>
        </div>
      </div>`;
  },

  escape(s) {
    if (!s) return '';
    const div = document.createElement('div');
    div.textContent = s;
    return div.innerHTML;
  },

  // ─── Dashboard ───
  async dashboard() {
    this.showLoading();
    try {
      const [trending, tech, status] = await Promise.all([
        api.getTrending(),
        api.getTechDigests(50, 6),
        api.request("GET", "/discover/status"),
      ]);

      const tools = trending.top_tools || [];
      const techEntries = tech.entries || [];
      const uniqueTools = tech.unique_tools || [];
      const total = trending.total_processed || 0;
      const schedulerActive = status.scheduler_active || false;

      document.getElementById("app").innerHTML = `
        <div class="fade-in">
          <div class="hero">
            <h1>AI Intelligence</h1>
            <p>Daily AI development intelligence from YouTube, TikTok, Instagram & Facebook</p>
            <div class="hero-stats">
              <div class="stat-card"><span class="stat-number">${total}</span><span class="stat-label">Videos Analyzed</span></div>
              <div class="stat-card"><span class="stat-number">${uniqueTools.length}</span><span class="stat-label">AI Tools Tracked</span></div>
              <div class="stat-card"><span class="stat-number">${techEntries.length}</span><span class="stat-label">Technical Digests</span></div>
            </div>
          </div>

          <div style="display:flex;gap:12px;align-items:center;justify-content:center;margin-bottom:32px;flex-wrap:wrap">
            <span style="display:flex;align-items:center;gap:6px;padding:6px 16px;background:rgba(52,199,89,0.1);border-radius:20px;font-size:13px;font-weight:500;color:var(--success)">
              <span style="width:8px;height:8px;border-radius:50%;background:var(--success);animation:pulse 2s infinite"></span>
              Auto-discovery ${schedulerActive ? "Active (every 6h)" : "Standby"}
            </span>
            <button class="btn btn-secondary" style="padding:6px 16px;font-size:13px" onclick="Views.runDiscovery()">
              <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2"><polyline points="23 4 23 10 17 10"/><path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"/></svg>
              Refresh Now
            </button>
          </div>

          <div class="quick-actions">
            <a href="#/process" class="action-card" data-nav>
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="23 7 16 12 23 17 23 7"/><rect x="1" y="5" width="15" height="14" rx="2" ry="2"/></svg>
              <div><div class="action-card-text">Process Videos</div><div class="action-card-sub">Extract insights from URLs</div></div>
            </a>
            <a href="#/discover" class="action-card" data-nav>
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
              <div><div class="action-card-text">Discover Content</div><div class="action-card-sub">Find new AI videos</div></div>
            </a>
            <a href="#/digests" class="action-card" data-nav>
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/></svg>
              <div><div class="action-card-text">Browse Digests</div><div class="action-card-sub">View all processed content</div></div>
            </a>
            <a href="#/stats" class="action-card" data-nav>
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/></svg>
              <div><div class="action-card-text">View Stats</div><div class="action-card-sub">Trending tools & analytics</div></div>
            </a>
          </div>

          ${tools.length ? `
          <div class="section">
            <div class="section-header">
              <h2 class="section-title">Latest AI Tools Discovered</h2>
              <a href="#/stats" class="section-link" data-nav>View all →</a>
            </div>
            <div class="digest-grid stagger">
              ${tools.slice(0, 6).map((t, i) => `
                <div class="stats-card fade-in">
                  <div style="display:flex;align-items:center;gap:14px">
                    <span style="font-size:28px">${["1","2","3","4","5","6"][i]}</span>
                    <div>
                      <div style="font-size:16px;font-weight:600">${this.escape(t[0])}</div>
                      <div style="font-size:13px;color:var(--text-secondary)">${t[1]} videos</div>
                    </div>
                  </div>
                </div>`).join('')}
            </div>
          </div>` : ""}

          ${techEntries.length ? `
          <div class="section">
            <div class="section-header">
              <h2 class="section-title">Technical Digests (Score ≥ 6)</h2>
              <a href="#/digests" class="section-link" data-nav>View all →</a>
            </div>
            <div class="digest-grid stagger">
              ${techEntries.slice(0, 8).map(e => this.renderDigestCard(e)).join("")}
            </div>
          </div>` : `
          <div class="section">
            <div class="section-header">
              <h2 class="section-title">No Technical Content Yet</h2>
            </div>
            <div class="empty-state">
              <p>The auto-discovery is searching for AI content. Check back soon or manually add URLs.</p>
            </div>
          </div>`}
        </div>`;
    } catch (err) {
      document.getElementById("app").innerHTML = `
        <div class="empty-state">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
          <h3>Could not load dashboard</h3>
          <p>${this.escape(err.message)}</p>
        </div>`;
    }
  },

  async runDiscovery() {
    try {
      const btn = document.querySelector("button");
      if (btn) btn.disabled = true;
      this.showToast("Starting discovery...");
      await api.request("POST", "/discover/run?keywords=AI development&keywords=AI tools&keywords=AI coding&keywords=machine learning&limit=3");
      this.showToast("Discovery complete! Refreshing...");
      setTimeout(() => this.dashboard(), 1500);
    } catch (err) {
      this.showToast("Error: " + err.message);
    }
  },

  // ─── Digests List ───
  async digests(params) {
    this.showLoading();
    try {
      const limit = 100;
      const offset = 0;
      const data = await api.getDigests(limit, offset, 'all', '', 'date');
      const entries = data.entries || [];

      let platformFilter = params.platform || 'all';

      let filtered = entries;
      if (platformFilter !== 'all') {
        filtered = entries.filter(e => e.platform.toLowerCase() === platformFilter.toLowerCase());
      }

      const platforms = ['all', ...new Set(entries.map(e => e.platform))];

      document.getElementById('app').innerHTML = `
        <div class="fade-in">
          <div style="display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:16px;margin-bottom:24px">
            <h1 style="font-size:32px;font-weight:700;letter-spacing:-0.5px">Digests</h1>
            <a href="#/process" class="btn btn-primary" data-nav style="padding:10px 20px;font-size:14px">
              <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
              New Process
            </a>
          </div>

          <div class="filter-bar">
            <input type="text" id="searchInput" class="filter-input" placeholder="Search digests..." style="padding:10px 16px;">
            <div class="filter-tabs">
              ${platforms.map(p => `
                <button class="filter-tab ${p === platformFilter ? 'active' : ''}" onclick="router.navigate('digests/platform/${p}')">${p === 'all' ? 'All' : p.charAt(0).toUpperCase() + p.slice(1)}</button>
              `).join('')}
            </div>
          </div>

          <div id="digestList" class="digest-grid stagger">
            ${filtered.length ? filtered.map(e => this.renderDigestCard(e)).join('') : '<div class="empty-state"><h3>No digests found</h3><p>Try a different filter or process some videos first</p></div>'}
          </div>
        </div>`;

      document.getElementById('searchInput').addEventListener('input', (e) => {
        const q = e.target.value.toLowerCase();
        document.querySelectorAll('.digest-card').forEach(card => {
          const text = card.textContent.toLowerCase();
          card.style.display = text.includes(q) ? '' : 'none';
        });
      });

    } catch (err) {
      document.getElementById('app').innerHTML = `
        <div class="empty-state"><h3>Error loading digests</h3><p>${this.escape(err.message)}</p></div>`;
    }
  },

  // ─── Digest Detail ───
  async digestDetail(params) {
    this.showLoading();
    try {
      const e = await api.getDigest(parseInt(params.id));
      const tools = e.ai_tools || [];
      const models = e.ai_models || [];
      const insights = e.key_insights || [];
      const news = e.latest_news || [];
      const categories = e.categories || [];

      document.getElementById('app').innerHTML = `
        <div class="fade-in">
          <button class="back-btn" onclick="history.back()">
            <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2"><line x1="19" y1="12" x2="5" y2="12"/><polyline points="12 19 5 12 12 5"/></svg>
            Back
          </button>

          <div class="detail-header">
            <div>
              <h1 class="detail-title">${this.escape(e.title || 'Untitled')}</h1>
              <div class="detail-meta">
                <span class="badge badge-platform">${this.platformIcon(e.platform)} ${e.platform}</span>
                <span class="badge ${(e.relevance_score || 0) >= 8 ? 'badge-score-high' : 'badge-score'}">${e.relevance_score || 0}/10 Relevance</span>
                ${categories.map(c => `<span class="badge badge-platform">${this.escape(c)}</span>`).join('')}
              </div>
              <div style="font-size:13px;color:var(--text-tertiary)">
                ${e.processed_at ? new Date(e.processed_at).toLocaleString() : ''}
                ${e.url ? `&middot; <a href="${this.escape(e.url)}" target="_blank">${this.escape(e.url)}</a>` : ''}
              </div>
            </div>
          </div>

          <div class="detail-section">
            <h3 class="detail-section-title">
              <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="var(--accent)" stroke-width="2"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/></svg>
              Summary
            </h3>
            <p class="detail-summary">${this.escape(e.summary || 'No summary available')}</p>
          </div>

          ${tools.length ? `
          <div class="detail-section">
            <h3 class="detail-section-title">
              <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="var(--accent)" stroke-width="2"><path d="M14.7 6.3a1 1 0 0 0 0 1.4l1.6 1.6a1 1 0 0 0 1.4 0l3.77-3.77a6 6 0 0 1-7.94 7.94l-6.91 6.91a2.12 2.12 0 0 1-3-3l6.91-6.91a6 6 0 0 1 7.94-7.94l-3.76 3.76z"/></svg>
              AI Tools (${tools.length})
            </h3>
            <div class="tool-list">${tools.map(t => `<span class="tool-chip">${this.escape(t)}</span>`).join('')}</div>
          </div>` : ''}

          ${models.length ? `
          <div class="detail-section">
            <h3 class="detail-section-title">
              <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="var(--accent)" stroke-width="2"><path d="M12 2a10 10 0 1 0 10 10h-10V2z"/><path d="M12 12L2 12a10 10 0 0 0 10 10V12z"/><path d="M12 12V2a10 10 0 0 0 0 20V12z"/></svg>
              AI Models (${models.length})
            </h3>
            <div class="tool-list">${models.map(m => `<span class="tool-chip">${this.escape(m)}</span>`).join('')}</div>
          </div>` : ''}

          ${insights.length ? `
          <div class="detail-section">
            <h3 class="detail-section-title">
              <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="var(--accent)" stroke-width="2"><path d="M12 20h9"/><path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z"/></svg>
              Key Insights (${insights.length})
            </h3>
            <ul class="insight-list">${insights.map(i => `<li class="insight-item">${this.escape(i)}</li>`).join('')}</ul>
          </div>` : ''}

          ${news.length ? `
          <div class="detail-section">
            <h3 class="detail-section-title">
              <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="var(--accent)" stroke-width="2"><circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/></svg>
              Latest News (${news.length})
            </h3>
            <ul class="insight-list">${news.map(n => `<li class="insight-item" style="border-left-color:var(--warning)">${this.escape(n)}</li>`).join('')}</ul>
          </div>` : ''}

          ${e.error ? `
          <div class="detail-section" style="border-left:3px solid var(--error)">
            <h3 class="detail-section-title" style="color:var(--error)">Error</h3>
            <p class="detail-summary">${this.escape(e.error)}</p>
          </div>` : ''}

          ${e.raw_text ? `
          <div class="detail-section">
            <h3 class="detail-section-title">
              <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="var(--accent)" stroke-width="2"><path d="M4 20h16"/><path d="M4 4h16"/><path d="M4 12h16"/></svg>
              Raw Transcript
            </h3>
            <div class="transcript-box">${this.escape(e.raw_text)}</div>
          </div>` : ''}
        </div>`;
    } catch (err) {
      document.getElementById('app').innerHTML = `
        <div class="empty-state"><h3>Digest not found</h3><p>${this.escape(err.message)}</p></div>`;
    }
  },

  // ─── Discover ───
  async discover() {
    this.showLoading();
    document.getElementById('app').innerHTML = `
      <div class="fade-in">
        <h1 style="font-size:32px;font-weight:700;letter-spacing:-0.5px;margin-bottom:8px">Discover Content</h1>
        <p style="color:var(--text-secondary);margin-bottom:32px;font-size:16px">Automatically find and process AI-related videos across platforms</p>

        <div class="detail-section">
          <div class="input-group">
            <label class="input-label">Keywords</label>
            <div style="display:flex;gap:8px;flex-wrap:wrap">
              <input type="text" id="kwInput" value="AI development, AI tools, VibeCoding, AI agents" style="flex:1;min-width:200px" placeholder="Enter keywords, comma-separated">
            </div>
          </div>
          <div class="input-group">
            <label class="input-label">Results per keyword</label>
            <input type="number" id="limitInput" value="3" min="1" max="10" style="max-width:120px">
          </div>
          <button id="discoverBtn" class="btn btn-primary">
            <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
            Discover & Process
          </button>
        </div>

        <div id="discoverResults"></div>
      </div>`;

    document.getElementById('discoverBtn').addEventListener('click', async () => {
      const keywords = document.getElementById('kwInput').value.split(',').map(s => s.trim()).filter(Boolean);
      const limit = parseInt(document.getElementById('limitInput').value) || 3;
      const btn = document.getElementById('discoverBtn');
      const resultsDiv = document.getElementById('discoverResults');

      btn.disabled = true;
      btn.innerHTML = '<div class="loader" style="width:18px;height:18px;border-width:2px"></div> Discovering...';

      resultsDiv.innerHTML = '<div class="progress-bar"><div class="progress-fill" style="width:30%"></div></div><p style="color:var(--text-secondary);font-size:14px">Searching platforms and processing videos...</p>';

      try {
        const data = await api.discover(keywords, limit);
        const results = data.results || [];

        let html = `<div style="margin-top:24px">
          <h3 style="font-size:18px;font-weight:600;margin-bottom:16px">Results (${results.length})</h3>`;

        results.forEach(r => {
          const cls = r.status === 'success' ? 'success' : r.status === 'already_exists' ? 'exists' : 'error';
          const label = r.status === 'success' ? 'Processed' : r.status === 'already_exists' ? 'Already Exists' : 'Error';
          const title = r.digest ? (r.digest.title || 'Untitled') : '';
          html += `
            <div class="result-item ${cls}">
              <div style="flex:1;min-width:0">
                <div class="result-url">${Views.escape(title || r.url)}</div>
                <div style="font-size:12px;color:var(--text-tertiary);margin-top:4px">${Views.escape(r.url)}</div>
              </div>
              <span class="result-status ${cls}">${label}</span>
            </div>`;
        });

        html += '</div>';
        resultsDiv.innerHTML = html;
        this.showToast(`Processed ${results.length} videos`);
      } catch (err) {
        resultsDiv.innerHTML = `<div class="result-item error"><span class="result-status error">Error</span><span>${this.escape(err.message)}</span></div>`;
      }

      btn.disabled = false;
      btn.innerHTML = '<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg> Discover & Process';
    });
  },

  // ─── Process ───
  async process() {
    this.showLoading();
    document.getElementById('app').innerHTML = `
      <div class="fade-in">
        <h1 style="font-size:32px;font-weight:700;letter-spacing:-0.5px;margin-bottom:8px">Process Videos</h1>
        <p style="color:var(--text-secondary);margin-bottom:32px;font-size:16px">Enter video URLs to extract AI insights and summaries</p>

        <div class="detail-section">
          <div class="input-group">
            <label class="input-label">Video URLs (one per line)</label>
            <textarea id="urlsInput" placeholder="https://www.youtube.com/watch?v=...&#10;https://www.tiktok.com/...&#10;https://www.instagram.com/reel/..."></textarea>
          </div>
          <button id="processBtn" class="btn btn-primary">
            <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2"><polygon points="23 7 16 12 23 17 23 7"/><rect x="1" y="5" width="15" height="14" rx="2" ry="2"/></svg>
            Process Videos
          </button>
        </div>

        <div id="processResults"></div>
      </div>`;

    document.getElementById('processBtn').addEventListener('click', async () => {
      const raw = document.getElementById('urlsInput').value;
      const urls = raw.split('\n').map(s => s.trim()).filter(Boolean);
      if (!urls.length) {
        this.showToast('Please enter at least one URL');
        return;
      }

      const btn = document.getElementById('processBtn');
      const resultsDiv = document.getElementById('processResults');

      btn.disabled = true;
      btn.innerHTML = '<div class="loader" style="width:18px;height:18px;border-width:2px"></div> Processing...';
      resultsDiv.innerHTML = '<div class="progress-bar"><div class="progress-fill" style="width:20%"></div></div><p style="color:var(--text-secondary);font-size:14px">Processing videos...</p>';

      try {
        const data = await api.processVideos(urls);
        const results = data.results || [];

        let html = `<div style="margin-top:24px">
          <h3 style="font-size:18px;font-weight:600;margin-bottom:16px">Results (${results.length})</h3>`;

        results.forEach(r => {
          const cls = r.status === 'success' ? 'success' : r.status === 'already_exists' ? 'exists' : 'error';
          const label = r.status === 'success' ? 'Processed' : r.status === 'already_exists' ? 'Already Exists' : 'Error';
          const title = r.digest ? (r.digest.title || 'Untitled') : '';
          html += `
            <div class="result-item ${cls}">
              <div style="flex:1;min-width:0">
                <div class="result-url">${Views.escape(title || r.url)}</div>
                <div style="font-size:12px;color:var(--text-tertiary);margin-top:4px">${Views.escape(r.url)}</div>
              </div>
              <span class="result-status ${cls}">${label}</span>
            </div>`;
        });

        html += '</div>';
        resultsDiv.innerHTML = html;
        this.showToast(`Processed ${results.length} videos`);
      } catch (err) {
        resultsDiv.innerHTML = `<div class="result-item error"><span class="result-status error">Error</span><span>${this.escape(err.message)}</span></div>`;
      }

      btn.disabled = false;
      btn.innerHTML = '<svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" stroke-width="2"><polygon points="23 7 16 12 23 17 23 7"/><rect x="1" y="5" width="15" height="14" rx="2" ry="2"/></svg> Process Videos';
    });
  },

  // ─── Stats ───
  async stats() {
    this.showLoading();
    try {
      const [stats, trending] = await Promise.all([
        api.getStats(),
        api.getTrending(),
      ]);

      const tools = trending.top_tools || stats.top_tools || [];
      const models = trending.top_models || stats.top_models || [];
      const categories = trending.top_categories || stats.top_categories || [];
      const total = trending.total_processed || stats.total_processed || 0;
      const errors = trending.error_count || stats.total_errors || 0;

      document.getElementById('app').innerHTML = `
        <div class="fade-in">
          <h1 style="font-size:32px;font-weight:700;letter-spacing:-0.5px;margin-bottom:32px">Analytics</h1>

          <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:16px;margin-bottom:32px">
            <div class="stat-card"><span class="stat-number">${total}</span><span class="stat-label">Total Videos</span></div>
            <div class="stat-card"><span class="stat-number">${tools.length}</span><span class="stat-label">AI Tools</span></div>
            <div class="stat-card"><span class="stat-number">${models.length}</span><span class="stat-label">AI Models</span></div>
            <div class="stat-card"><span class="stat-number">${errors}</span><span class="stat-label">Errors</span></div>
          </div>

          <div class="stats-grid">
            ${tools.length ? `
            <div class="stats-card">
              <h3 class="stats-card-title">Top AI Tools</h3>
              ${tools.slice(0, 10).map((t, i) => `
                <div class="stats-rank">
                  <span class="rank-num ${i < 3 ? `rank-${i+1}` : ''}">${i + 1}</span>
                  <span class="rank-name">${this.escape(t[0])}</span>
                  <span class="rank-count">${t[1]}</span>
                </div>`).join('')}
            </div>` : ''}

            ${models.length ? `
            <div class="stats-card">
              <h3 class="stats-card-title">Top AI Models</h3>
              ${models.slice(0, 10).map((m, i) => `
                <div class="stats-rank">
                  <span class="rank-num ${i < 3 ? `rank-${i+1}` : ''}">${i + 1}</span>
                  <span class="rank-name">${this.escape(m[0])}</span>
                  <span class="rank-count">${m[1]}</span>
                </div>`).join('')}
            </div>` : ''}

            ${categories.length ? `
            <div class="stats-card">
              <h3 class="stats-card-title">Content Categories</h3>
              ${categories.slice(0, 10).map((c, i) => `
                <div class="stats-rank">
                  <span class="rank-num ${i < 3 ? `rank-${i+1}` : ''}">${i + 1}</span>
                  <span class="rank-name">${this.escape(c[0])}</span>
                  <span class="rank-count">${c[1]}</span>
                </div>`).join('')}
            </div>` : ''}
          </div>
        </div>`;
    } catch (err) {
      document.getElementById('app').innerHTML = `
        <div class="empty-state"><h3>Error loading stats</h3><p>${this.escape(err.message)}</p></div>`;
    }
  },
};

window.Views = Views;
