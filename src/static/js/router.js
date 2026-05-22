class Router {
  constructor() {
    this.routes = {};
    this.currentParams = {};
    this.currentRoute = null;
    window.addEventListener('hashchange', () => this.resolve());
  }

  on(pattern, handler) {
    this.routes[pattern] = handler;
  }

  navigate(hash) {
    window.location.hash = hash;
  }

  resolve() {
    const hash = window.location.hash.slice(1) || '/';
    for (const [pattern, handler] of Object.entries(this.routes)) {
      const regex = new RegExp('^' + pattern.replace(/:(\w+)/g, '(?<$1>[^/]+)') + '$');
      const match = hash.match(regex);
      if (match) {
        this.currentParams = match.groups || {};
        this.currentRoute = pattern;
        handler(this.currentParams);
        this.updateNav(hash);
        return;
      }
    }
    this.routes['/']({});
    this.updateNav('/');
  }

  updateNav(hash) {
    document.querySelectorAll('[data-nav]').forEach(el => {
      const href = el.getAttribute('href') || '';
      const target = href.replace('#', '');
      el.classList.toggle('active', hash.startsWith(target) && (target !== '/' || hash === '/'));
    });
  }

  start() {
    this.resolve();
  }
}

window.router = new Router();
