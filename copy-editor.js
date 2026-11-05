(function () {
  var isLocal =
    location.hostname === 'localhost' ||
    location.hostname === '127.0.0.1' ||
    location.protocol === 'file:' ||
    location.search.indexOf('edit=1') !== -1;

  var inStudioIframe = window.parent && window.parent !== window && location.search.indexOf('studio=1') !== -1;

  // Helper to get/set text on a [data-copy] element, handling .mask-rv word splits cleanly
  function getInnerTarget(el) {
    if (el.classList.contains('mask-rv')) {
      var inner = el.querySelector('.mask > span');
      if (inner) return inner;
    }
    return el;
  }

  function unwrapWords(target) {
    var words = target.querySelectorAll('.w');
    if (words.length > 0) {
      var txt = Array.prototype.map.call(words, function (w) { return w.textContent; }).join(' ');
      target.textContent = txt;
    }
  }

  function rewrapWords(target) {
    var maskParent = target.closest('.mask');
    if (!maskParent) return;
    var text = target.textContent || '';
    var words = text.split(' ');
    target.textContent = '';
    words.forEach(function (word, k) {
      var w = document.createElement('span');
      w.className = 'w';
      w.style.setProperty('--w', k);
      w.textContent = word;
      target.appendChild(w);
      if (k < words.length - 1) target.appendChild(document.createTextNode(' '));
    });
  }

  function getElementCopyText(el) {
    var target = getInnerTarget(el);
    var words = target.querySelectorAll('.w');
    if (words.length > 0) {
      return Array.prototype.map.call(words, function (w) { return w.textContent; }).join(' ');
    }
    return target.textContent;
  }

  function setElementCopyText(el, val, isEditingNow) {
    var target = getInnerTarget(el);
    var hasWords = target.querySelectorAll('.w').length > 0 || (target.closest('.mask') && !isEditingNow);
    target.textContent = val;
    if (hasWords && !isEditingNow) {
      rewrapWords(target);
    }
  }

  // Listen for live updates from Copy Studio iframe parent
  window.addEventListener('message', function (ev) {
    if (!ev.data || typeof ev.data !== 'object') return;
    if (ev.data.type === 'copy:update') {
      var key = ev.data.key;
      var val = ev.data.value;
      document.querySelectorAll('[data-copy="' + key + '"]').forEach(function (el) {
        if (document.activeElement !== getInnerTarget(el)) {
          setElementCopyText(el, val, editMode);
        }
      });
      if (ev.data.scrollIntoView) {
        var first = document.querySelector('[data-copy="' + key + '"]');
        if (first) first.scrollIntoView({ behavior: 'smooth', block: 'center' });
      }
    } else if (ev.data.type === 'copy:highlight') {
      document.querySelectorAll('.copy-studio-focus').forEach(function (el) {
        el.classList.remove('copy-studio-focus');
      });
      if (ev.data.key) {
        var el = document.querySelector('[data-copy="' + ev.data.key + '"]');
        if (el) {
          el.classList.add('copy-studio-focus');
          el.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }
      }
    } else if (ev.data.type === 'copy:toggle-inline') {
      setEditMode(!!ev.data.enabled);
    }
  });

  if (!isLocal) return;

  var editMode = false;
  var dirtyCopy = {};
  var dirtyCount = 0;

  // Inject styles for inline editing & floating toolbar
  var style = document.createElement('style');
  style.textContent = [
    '.copy-bar { position: fixed; left: 1rem; bottom: 1rem; z-index: 9999; display: flex; flex-wrap: wrap; align-items: center; gap: .45rem; font-family: var(--sans, Georgia, serif); font-size: .86rem; background: rgba(38, 24, 15, .94); border: 1px solid color-mix(in srgb, var(--a1, #9fb697) 40%, transparent); padding: .4rem .55rem; border-radius: 4px; box-shadow: 0 14px 34px rgba(0,0,0,.55); backdrop-filter: blur(8px); }',
    'body:has(.mockbar) .copy-bar { bottom: 3.4rem; }',
    '.copy-bar button, .copy-bar a { font: inherit; color: var(--ink, #f5ede1); background: rgba(67, 47, 39, .9); border: 1px solid rgba(245, 237, 225, .2); padding: .35rem .7rem; border-radius: 3px; cursor: pointer; text-decoration: none; display: inline-flex; align-items: center; gap: .35rem; transition: border-color .15s, background .15s; }',
    '.copy-bar button:hover, .copy-bar a:hover { border-color: var(--a1, #9fb697); }',
    '.copy-bar button.active { background: var(--a1, #9fb697); color: var(--on, #26180f); border-color: var(--a1, #9fb697); font-weight: 600; }',
    '.copy-bar button.save-btn { background: var(--a2, #e1b38c); color: var(--on, #26180f); border-color: var(--a2, #e1b38c); font-weight: 600; }',
    '.copy-bar button.save-btn[disabled] { opacity: .45; cursor: default; background: transparent; color: var(--ink2, #cfbda9); border-color: rgba(245, 237, 225, .15); font-weight: 400; }',
    '.copy-bar .copy-status { color: var(--ink2, #cfbda9); font-size: .82rem; padding-inline: .3rem; }',
    'html[data-copy-edit="on"] [data-copy] { outline: 1px dashed rgba(225, 179, 140, .45); outline-offset: 3px; border-radius: 2px; cursor: text !important; transition: outline-color .15s, background-color .15s; }',
    'html[data-copy-edit="on"] [data-copy]:hover { outline-color: var(--a2, #e1b38c); background-color: rgba(225, 179, 140, .08); }',
    'html[data-copy-edit="on"] [data-copy]:focus, html[data-copy-edit="on"] [data-copy]:focus-within { outline: 2px solid var(--a1, #9fb697) !important; outline-offset: 4px; background-color: rgba(159, 182, 151, .12); }',
    '.copy-studio-focus { outline: 2px solid var(--a2, #e1b38c) !important; outline-offset: 5px !important; background-color: rgba(225, 179, 140, .14) !important; border-radius: 2px; }'
  ].join('\n');
  document.head.appendChild(style);

  var bar = document.createElement('div');
  bar.className = 'copy-bar';
  if (inStudioIframe) {
    bar.style.display = 'none';
  }
  bar.innerHTML = [
    '<button type="button" id="ce-toggle" title="Shortcut: Ctrl+E">✎ Edit text on page</button>',
    '<button type="button" id="ce-save" class="save-btn" disabled title="Shortcut: Ctrl+S">Save changes</button>',
    '<button type="button" id="ce-commit" title="Save & create a Git version checkpoint">Save + Git checkpoint</button>',
    '<a href="/copy-studio.html" id="ce-studio">All-page copy sheet ↗</a>',
    '<span class="copy-status" id="ce-status"></span>'
  ].join('');
  document.body.appendChild(bar);

  var btnToggle = document.getElementById('ce-toggle');
  var btnSave = document.getElementById('ce-save');
  var btnCommit = document.getElementById('ce-commit');
  var statusEl = document.getElementById('ce-status');

  function setStatus(msg, isErr) {
    if (!statusEl) return;
    statusEl.textContent = msg;
    statusEl.style.color = isErr ? '#f2a38a' : 'var(--ink2, #cfbda9)';
  }

  function updateSaveBtn() {
    dirtyCount = Object.keys(dirtyCopy).length;
    if (btnSave) {
      btnSave.disabled = dirtyCount === 0;
      btnSave.textContent = dirtyCount > 0 ? 'Save changes (' + dirtyCount + ')' : 'Saved';
    }
  }

  function setEditMode(on) {
    editMode = on;
    document.documentElement.setAttribute('data-copy-edit', on ? 'on' : 'off');
    if (btnToggle) {
      btnToggle.classList.toggle('active', on);
      btnToggle.textContent = on ? '✓ Editing text (click any text)' : '✎ Edit text on page';
    }
    document.querySelectorAll('[data-copy]').forEach(function (el) {
      var target = getInnerTarget(el);
      if (on) {
        unwrapWords(target);
        target.setAttribute('contenteditable', 'true');
        target.setAttribute('spellcheck', 'true');
      } else {
        target.removeAttribute('contenteditable');
        rewrapWords(target);
      }
    });
    if (on) {
      setStatus('Click any text on the page to edit. Press Ctrl+S to save.');
    } else if (dirtyCount === 0) {
      setStatus('');
    }
  }

  // Prevent link navigation or form submission when clicking an editable element in editMode
  document.addEventListener('click', function (e) {
    if (!editMode) return;
    var copyEl = e.target.closest('[data-copy]');
    if (copyEl) {
      var linkOrBtn = e.target.closest('a, button[type="submit"], .chip, .door');
      if (linkOrBtn && !linkOrBtn.closest('.copy-bar')) {
        e.preventDefault();
        e.stopPropagation();
        getInnerTarget(copyEl).focus();
      }
    }
  }, true);

  // Prevent Enter from inserting <div>/<br> inside single-line headings/buttons
  document.addEventListener('keydown', function (e) {
    if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'e') {
      e.preventDefault();
      setEditMode(!editMode);
      return;
    }
    if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 's') {
      if (editMode || dirtyCount > 0) {
        e.preventDefault();
        saveChanges(false);
      }
      return;
    }
    if (!editMode) return;
    var copyEl = e.target.closest && e.target.closest('[data-copy]');
    if (copyEl && e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      e.target.blur();
    }
  });

  // Track input on any [data-copy]
  document.addEventListener('input', function (e) {
    if (!editMode) return;
    var copyEl = e.target.closest && e.target.closest('[data-copy]');
    if (!copyEl) return;
    var key = copyEl.getAttribute('data-copy');
    var target = getInnerTarget(copyEl);
    var val = (target.textContent || '').replace(/\r?\n/g, ' ');
    dirtyCopy[key] = val;
    if (key === 'global.email') {
      dirtyCopy['__email__'] = val.trim();
    }
    // Sync any other elements on the same page sharing this key
    document.querySelectorAll('[data-copy="' + key + '"]').forEach(function (other) {
      if (other !== copyEl) {
        setElementCopyText(other, val, editMode);
      }
    });
    updateSaveBtn();
    setStatus('Unsaved edits (' + Object.keys(dirtyCopy).length + ')');
    // Notify parent studio if inside iframe
    if (window.parent && window.parent !== window) {
      window.parent.postMessage({ type: 'studio:from-iframe', key: key, value: val }, '*');
    }
  });

  function apiFetch(path, opts) {
    var base = location.port === '8000' ? 'http://localhost:8080' : '';
    return fetch(base + path, opts).then(function (r) {
      if (!r.ok && !base) {
        return fetch('http://localhost:8080' + path, opts);
      }
      return r;
    });
  }

  function saveChanges(withCommit) {
    var payload = { copy: Object.assign({}, dirtyCopy) };
    if (dirtyCopy['__email__']) {
      payload.settings = { email: dirtyCopy['__email__'] };
      delete payload.copy['__email__'];
    }
    setStatus('Saving to files...');
    return apiFetch('/api/save-copy', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    })
      .then(function (r) {
        if (!r.ok) throw new Error('HTTP ' + r.status);
        return r.json();
      })
      .then(function (res) {
        dirtyCopy = {};
        updateSaveBtn();
        setStatus('✓ Saved to HTML files (' + (res.updated_files || 0) + ' updated)');
        if (withCommit) {
          var msg = window.prompt('Short description for this version checkpoint:', 'Update website copy');
          if (!msg) return;
          setStatus('Creating Git checkpoint...');
          return apiFetch('/api/git-checkpoint', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: msg, push: true })
          })
            .then(function (r) { return r.json(); })
            .then(function (gres) {
              if (gres.ok) {
                setStatus('✓ Saved & committed (' + gres.commit + ')' + (gres.pushed ? ' + pushed to GitHub' : ''));
              } else {
                setStatus('Saved files (Git note: ' + (gres.error || 'no changes') + ')');
              }
            });
        }
      })
      .catch(function (err) {
        setStatus('Could not reach local save server. Make sure server.py is running on port 8080.', true);
      });
  }

  btnToggle.addEventListener('click', function () {
    setEditMode(!editMode);
  });
  btnSave.addEventListener('click', function () {
    saveChanges(false);
  });
  btnCommit.addEventListener('click', function () {
    saveChanges(true);
  });

  if (location.search.indexOf('edit=1') !== -1) {
    setEditMode(true);
  }
})();
