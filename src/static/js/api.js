class API {
  constructor() {
    this.base = '/api';
  }

  async request(method, path, body) {
    const opts = {
      method,
      headers: { 'Content-Type': 'application/json' },
    };
    if (body) opts.body = JSON.stringify(body);
    const res = await fetch(this.base + path, opts);
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: res.statusText }));
      throw new Error(err.detail || `HTTP ${res.status}`);
    }
    return res.json();
  }

  getDigests(limit, offset, platform, search, sort) {
    const params = new URLSearchParams();
    if (limit) params.set('limit', limit);
    if (offset) params.set('offset', offset);
    if (platform && platform !== 'all') params.set('platform', platform);
    if (search) params.set('search', search);
    if (sort) params.set('sort', sort);
    return this.request('GET', `/digests?${params}`);
  }

  getDigest(id) {
    return this.request('GET', `/digests/${id}`);
  }

  deleteDigest(id) {
    return this.request('DELETE', `/digests/${id}`);
  }

  processVideos(urls) {
    return this.request('POST', '/process', { urls });
  }

  discover(keywords, limit) {
    return this.request('POST', '/discover', { keywords, limit });
  }

  getStats() {
    return this.request('GET', '/stats');
  }

  getTrending() {
    return this.request('GET', '/trending');
  }

  search(query, limit) {
    const params = new URLSearchParams({ q: query, limit: limit || 20 });
    return this.request('GET', `/search?${params}`);
  }

  getTechDigests(limit, minScore) {
    const params = new URLSearchParams();
    if (limit) params.set('limit', limit);
    if (minScore) params.set('min_score', minScore);
    return this.request('GET', `/tech-digests?${params}`);
  }
}

window.api = new API();
