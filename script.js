/* CloudLabs · shared script · v0.2.0 */
(function(){
  /* Mobile nav overflow fade */
  var navEl  = document.querySelector('nav.tabs');
  var navWrap = navEl && navEl.closest('.nav-wrap');
  if(navEl && navWrap){
    var checkOverflow = function(){
      navWrap.classList.toggle('has-overflow', navEl.scrollWidth > navEl.clientWidth);
    };
    checkOverflow();
    navEl.addEventListener('scroll', checkOverflow);
    window.addEventListener('resize', checkOverflow);
  }
  var html = document.documentElement;

  /* Language toggle */
  var setLang = function(l){
    html.setAttribute('data-lang', l);
    document.querySelectorAll('.lang-toggle button').forEach(function(b){
      b.setAttribute('aria-pressed', b.dataset.setLang === l ? 'true' : 'false');
    });
    try{ localStorage.setItem('cl_lang', l); }catch(e){}
  };
  document.querySelectorAll('.lang-toggle button').forEach(function(b){
    b.addEventListener('click', function(){ setLang(b.dataset.setLang); });
  });
  try{
    var saved = localStorage.getItem('cl_lang');
    if(saved === 'nl' || saved === 'en'){
      setLang(saved);
    } else {
      /* Auto-detect from browser language if no stored preference */
      var browserLang = (navigator.language || navigator.userLanguage || '').toLowerCase();
      if(browserLang === 'nl' || browserLang.indexOf('nl-') === 0){
        setLang('nl');
      }
    }
  }catch(e){}

  /* Findings switcher (only on findings page) */
  var cards = document.querySelectorAll('.finding-card[data-finding]');
  if(cards.length){
    var pills = document.querySelectorAll('.pill-btn[data-finding]');
    var prev  = document.getElementById('finding-prev');
    var next  = document.getElementById('finding-next');
    var order = Array.from(pills).map(function(p){ return p.dataset.finding; });
    var idx   = 0;
    var show  = function(i){
      idx = (i + order.length) % order.length;
      var id = order[idx];
      cards.forEach(function(c){ c.classList.toggle('active', c.dataset.finding === id); });
      pills.forEach(function(p){ p.setAttribute('aria-current', p.dataset.finding === id ? 'true' : 'false'); });
      if(prev) prev.disabled = idx === 0;
      if(next) next.disabled = idx === order.length - 1;
    };
    pills.forEach(function(p, i){ p.addEventListener('click', function(){ show(i); }); });
    if(prev) prev.addEventListener('click', function(){ show(idx - 1); });
    if(next) next.addEventListener('click', function(){ show(idx + 1); });
    show(0);
  }

  /* Book form mailto (only on book page) */
  var send = document.getElementById('send-mail');
  if(send){
    send.addEventListener('click', function(){
      var v = function(id){ return (document.getElementById(id) || {}).value || ''; };
      var lang = html.getAttribute('data-lang');
      var subj = lang === 'nl'
        ? 'CloudLabs intake aanvraag · ' + v('f-svc')
        : 'CloudLabs intake request · ' + v('f-svc');
      var body = lang === 'nl'
        ? 'Naam: ' + v('f-name') + '\nOrganisatie: ' + v('f-org') + '\nE-mail: ' + v('f-email') + '\nDienst: ' + v('f-svc') + '\nRichtblok: ' + v('f-block') + '\n\nToelichting:\n' + v('f-notes') + '\n'
        : 'Name: ' + v('f-name') + '\nOrganisation: ' + v('f-org') + '\nEmail: ' + v('f-email') + '\nService: ' + v('f-svc') + '\nIndicative block: ' + v('f-block') + '\n\nNotes:\n' + v('f-notes') + '\n';
      location.href = 'mailto:hans.vredevoort@cldlbs.com?subject=' + encodeURIComponent(subj) + '&body=' + encodeURIComponent(body);
    });
  }

  /* ── Stagger index assignment ─────────────────────────────── */
  document.querySelectorAll('.anim-stagger').forEach(function(parent){
    Array.from(parent.children).forEach(function(child, i){
      child.style.setProperty('--i', i);
    });
  });

  /* ── Scroll animations ────────────────────────────────────── */
  if('IntersectionObserver' in window){
    var observer = new IntersectionObserver(function(entries){
      entries.forEach(function(entry){
        if(entry.isIntersecting){
          entry.target.classList.add('is-visible');
          observer.unobserve(entry.target);
        }
      });
    }, {threshold: 0.12, rootMargin: '0px 0px -40px 0px'});

    document.querySelectorAll('.anim-fade, .anim-stagger').forEach(function(el){
      observer.observe(el);
    });
  } else {
    /* Fallback: show everything immediately */
    document.querySelectorAll('.anim-fade, .anim-stagger').forEach(function(el){
      el.classList.add('is-visible');
    });
  }

  /* Stat counter animation */
  function animateCounter(el, target, suffix, duration){
    var start = 0;
    var step  = Math.ceil(target / (duration / 16));
    var timer = setInterval(function(){
      start = Math.min(start + step, target);
      el.textContent = start + suffix;
      if(start >= target) clearInterval(timer);
    }, 16);
  }

  var statsObserver = new IntersectionObserver(function(entries){
    entries.forEach(function(entry){
      if(!entry.isIntersecting) return;
      var el = entry.target;
      var raw   = el.dataset.count;
      var suffix = el.dataset.suffix || '';
      animateCounter(el, parseInt(raw, 10), suffix, 900);
      statsObserver.unobserve(el);
    });
  }, {threshold: 0.5});

  document.querySelectorAll('[data-count]').forEach(function(el){
    statsObserver.observe(el);
  });
  /* ── End scroll animations ─────────────────────────────────── */

  /* Cookie consent */
  var KEY     = 'cl_consent';
  var banner  = document.getElementById('consentBanner');
  var reopen  = document.getElementById('consentReopen');
  var accept  = document.getElementById('consentAccept');
  var decline = document.getElementById('consentDecline');

  if(banner){
    function showBanner(){ banner.classList.add('show'); }
    function hideBanner(){ banner.classList.remove('show'); }
    function update(state){
      if(typeof gtag !== 'undefined'){
        gtag('consent', 'update', {
          analytics_storage: state,
          ad_storage: 'denied',
          ad_user_data: 'denied',
          ad_personalization: 'denied'
        });
      }
      try{ localStorage.setItem(KEY, state); }catch(e){}
      hideBanner();
    }
    var savedConsent = null;
    try{ savedConsent = localStorage.getItem(KEY); }catch(e){}
    if(savedConsent === 'granted'){ update('granted'); hideBanner(); }
    else if(savedConsent === 'denied'){ hideBanner(); }
    else{ showBanner(); }
    if(accept)  accept.addEventListener('click',  function(){ update('granted'); });
    if(decline) decline.addEventListener('click', function(){ update('denied');  });
    if(reopen)  reopen.addEventListener('click',  function(){ showBanner(); });
  }
})();
