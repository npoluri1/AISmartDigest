(function () {
  const theme = localStorage.getItem('theme') || 'dark';
  document.documentElement.setAttribute('data-theme', theme);

  document.getElementById('themeToggle').addEventListener('click', () => {
    const current = document.documentElement.getAttribute('data-theme');
    const next = current === 'dark' ? 'light' : 'dark';
    document.documentElement.setAttribute('data-theme', next);
    localStorage.setItem('theme', next);
  });

  document.getElementById('mobileMenuBtn').addEventListener('click', () => {
    document.getElementById('mobileMenu').classList.toggle('open');
  });

  document.querySelectorAll('[data-nav]').forEach(el => {
    el.addEventListener('click', () => {
      document.getElementById('mobileMenu').classList.remove('open');
    });
  });

  router.on('/', () => Views.dashboard());
  router.on('/digests', () => Views.digests({}));
  router.on('/digests/platform/(.+)', (params) => Views.digests({ platform: params[1] }));
  router.on('/digests/:id', (params) => Views.digestDetail(params));
  router.on('/discover', () => Views.discover());
  router.on('/process', () => Views.process());
  router.on('/stats', () => Views.stats());

  router.start();
})();
