const API = 'https://api.brandmeister.network/v2';
const TG_CACHE_TTL = 86400000; // 24 hours

let profiles = [];
let savedDevices = [];
let tgCache = {};
let currentGroups = [];
let currentGroupsData = [];
let currentGroupsSlot = null;
let selectedId = null;
let editingId = null;
let tempGroups = [];
let busy = false;
let fetchingNames = false;
let currentLang = 'en';
let currentBadgeKey = 'badge_idle';

// ── i18n ───────────────────────────────────────────────────────────────────
function t(key, vars = {}) {
  let str = (I18N[currentLang] ?? I18N.en)[key] ?? I18N.en[key] ?? key;
  for (const [k, v] of Object.entries(vars)) {
    str = str.replaceAll(`{${k}}`, v);
  }
  return str;
}

function applyLang() {
  document.documentElement.lang = currentLang;
  document.querySelectorAll('[data-i18n]').forEach(el => {
    el.textContent = t(el.dataset.i18n);
  });
  document.querySelectorAll('[data-i18n-placeholder]').forEach(el => {
    el.placeholder = t(el.dataset.i18nPlaceholder);
  });
  document.querySelectorAll('[data-i18n-title]').forEach(el => {
    el.title = t(el.dataset.i18nTitle);
  });
  document.querySelectorAll('#slot option[data-i18n]').forEach(el => {
    el.textContent = t(el.dataset.i18n);
  });
  const logReady = document.getElementById('logReadyMsg');
  if (logReady) logReady.textContent = t('log_ready');
  renderProfiles();
  if (selectedId) {
    const p = profiles.find(x => x.id === selectedId);
    document.getElementById('selectedLabel').textContent = p
      ? t('selected_prefix') + p.name
      : t('no_profile_selected');
  }
  document.getElementById('statusBadge').textContent = t(currentBadgeKey || 'badge_idle');
  renderCurrentCard();
}

function setLang(lang) {
  currentLang = lang;
  localStorage.setItem('bm_lang', lang);
  applyLang();
}

// ── Theme ──────────────────────────────────────────────────────────────────
function applyTheme(theme) {
  document.documentElement.classList.toggle('light', theme === 'light');
  document.getElementById('themeBtn').textContent = theme === 'light' ? '🌙 Dark' : '☀️ Light';
}

function toggleTheme() {
  const next = document.documentElement.classList.contains('light') ? 'dark' : 'light';
  localStorage.setItem('bm_theme', next);
  applyTheme(next);
}

// ── Talk group name cache ──────────────────────────────────────────────────
function loadTgCache() {
  try { tgCache = JSON.parse(localStorage.getItem('bm_tg_names') || '{}'); }
  catch { tgCache = {}; }
}

function saveTgCache() {
  localStorage.setItem('bm_tg_names', JSON.stringify(tgCache));
}

async function getTgName(id) {
  const cached = tgCache[id];
  if (cached !== undefined && (Date.now() - cached.ts < TG_CACHE_TTL)) return cached.name;
  try {
    const r = await fetch(`${API}/talkgroup/${id}`, { signal: AbortSignal.timeout(5000) });
    const name = r.ok ? ((await r.json()).Name || null) : null;
    tgCache[id] = { name, ts: Date.now() };
  } catch {
    tgCache[id] = { name: null, ts: Date.now() };
  }
  saveTgCache();
  return tgCache[id].name;
}

function tgLabel(id) {
  const name = tgCache[id]?.name;
  return name
    ? `${id}<span class="tg-name" title="${esc(name)}"> · ${esc(name)}</span>`
    : `${id}`;
}

async function prefetchAndRender(groups, renderFn) {
  if (fetchingNames) return;
  const missing = groups.filter(id => {
    const c = tgCache[id];
    return c === undefined || (Date.now() - c.ts > TG_CACHE_TTL);
  });
  if (!missing.length) return;
  fetchingNames = true;
  await Promise.allSettled(missing.map(getTgName));
  fetchingNames = false;
  renderFn();
}

// ── Init ───────────────────────────────────────────────────────────────────
function init() {
  currentLang = localStorage.getItem('bm_lang') || 'en';
  document.getElementById('langSelect').value = currentLang;
  applyTheme(localStorage.getItem('bm_theme') || 'dark');
  loadTgCache();
  savedDevices = JSON.parse(localStorage.getItem('bm_devices') || '[]');
  const s = loadSettings();
  document.getElementById('callsign').value = (s.callsign || '').toUpperCase();
  document.getElementById('token').value    = s.token || '';
  document.getElementById('slot').value     = s.slot  || '0';
  renderDeviceSelect(s.deviceId || '');
  profiles = JSON.parse(localStorage.getItem('bm_profiles') || '[]');
  applyLang();
}

function loadSettings() {
  try { return JSON.parse(localStorage.getItem('bm_settings') || '{}'); }
  catch { return {}; }
}

function saveSettings() {
  const deviceId = document.getElementById('deviceSelect').value;
  localStorage.setItem('bm_settings', JSON.stringify({
    deviceId,
    callsign: val('callsign').toUpperCase(),
    token: val('token'),
    slot:  val('slot'),
  }));
  toast(t('toast_settings_saved'), 'ok');
}

function getConn() {
  return {
    deviceId: document.getElementById('deviceSelect').value,
    token:    val('token'),
    slot:     parseInt(val('slot')),
  };
}

// ── Device dropdown ────────────────────────────────────────────────────────
function renderDeviceSelect(currentId = '') {
  const sel = document.getElementById('deviceSelect');
  sel.innerHTML = `<option value="">${t('option_select_device')}</option>` +
    savedDevices.map(d =>
      `<option value="${esc(d)}" ${d === currentId ? 'selected' : ''}>${esc(d)}</option>`
    ).join('');
}

function onDeviceSelect() {}

async function fetchMyDevices() {
  const token    = val('token').trim();
  const callsign = val('callsign').trim().toUpperCase();
  if (!token)    { toast(t('err_token'), 'err'); return; }
  if (!callsign) { toast(t('err_callsign'), 'err'); return; }

  const btn = document.getElementById('fetchDevicesBtn');
  btn.disabled = true;
  btn.textContent = '⏳';

  try {
    const r = await fetch(`${API}/device/byCall?callsign=${encodeURIComponent(callsign)}`, {
      headers: { 'Authorization': `Bearer ${token}` },
      signal: AbortSignal.timeout(15000),
    });
    if (!r.ok) throw new Error(`HTTP ${r.status}`);
    const devices = await r.json();

    if (!Array.isArray(devices) || !devices.length) {
      toast(t('toast_devices_none', { cs: callsign }), 'err');
      return;
    }

    let added = 0;
    devices.forEach(d => {
      const id = String(d.id);
      if (!savedDevices.includes(id)) { savedDevices.push(id); added++; }
    });
    localStorage.setItem('bm_devices', JSON.stringify(savedDevices));

    const sel = document.getElementById('deviceSelect');
    sel.innerHTML = `<option value="">${t('option_select_device2')}</option>` +
      devices.map(d =>
        `<option value="${esc(String(d.id))}">${esc(d.callsign)} — ${esc(d.linkname)} (${d.id})</option>`
      ).join('');

    const addedPart = added ? t('toast_new_devices', { n: added }) : '';
    const s = devices.length !== 1
      ? (currentLang === 'pl' ? 'a' : 's')
      : '';
    toast(t('toast_devices_ok', { n: devices.length, s, cs: callsign, added: addedPart }), 'ok');
  } catch (e) {
    toast(t('toast_fail_devices', { msg: e.message }), 'err');
  } finally {
    btn.disabled = false;
    btn.textContent = t('btn_fetch');
  }
}

function toggleToken() {
  const inp = document.getElementById('token');
  inp.type = inp.type === 'password' ? 'text' : 'password';
}

// ── Profiles ───────────────────────────────────────────────────────────────
function tgCountLabel(n) {
  if (currentLang === 'pl') {
    if (n === 1) return `1 grupa wywołania`;
    if (n >= 2 && n <= 4) return `${n} grupy wywołania`;
    return `${n} grup wywołania`;
  }
  return `${n} talk group${n !== 1 ? 's' : ''}`;
}

function renderProfiles() {
  const el = document.getElementById('profileList');
  if (!profiles.length) {
    const lines = t('profile_empty').split('\n');
    el.innerHTML = `<div class="empty"><div class="icon">📋</div>${lines[0]}${lines[1] ? `<br>${lines[1]}` : ''}</div>`;
    return;
  }
  el.innerHTML = profiles.map(p => `
    <div class="profile-item ${p.id === selectedId ? 'selected' : ''}" onclick="selectProfile('${p.id}')">
      <div class="profile-name">${esc(p.name)}</div>
      <div class="profile-meta">${tgCountLabel(p.groups.length)}</div>
      <div class="tags">
        ${p.groups.slice(0, 10).map(g => `<span class="tag">${tgLabel(g)}</span>`).join('')}
        ${p.groups.length > 10 ? `<span class="tag">${t('more_groups', { n: p.groups.length - 10 })}</span>` : ''}
      </div>
      <div class="profile-actions">
        <button class="btn btn-secondary btn-sm" onclick="event.stopPropagation();openEdit('${p.id}')">${t('btn_edit')}</button>
        <button class="btn btn-secondary btn-sm" onclick="event.stopPropagation();exportProfile('${p.id}')">${t('btn_export')}</button>
        <button class="btn btn-ghost btn-sm" onclick="event.stopPropagation();deleteProfile('${p.id}')">${t('btn_delete')}</button>
        <button class="btn btn-primary btn-sm ml-auto" onclick="event.stopPropagation();quickApply('${p.id}')">${t('btn_quick_apply')}</button>
      </div>
    </div>
  `).join('');

  const allGroups = [...new Set(profiles.flatMap(p => p.groups))];
  prefetchAndRender(allGroups, renderProfiles);
}

function selectProfile(id) {
  selectedId = id;
  const p = profiles.find(x => x.id === id);
  document.getElementById('selectedLabel').textContent = p
    ? t('selected_prefix') + p.name
    : t('no_profile_selected');
  document.getElementById('applyBtn').disabled = !p;
  renderProfiles();
}

function quickApply(id) {
  selectProfile(id);
  confirmApply();
}

function openCreate() {
  editingId = null; tempGroups = [];
  document.getElementById('modalTitle').textContent = t('modal_new');
  document.getElementById('pName').value = '';
  document.getElementById('importJson').value = '';
  document.getElementById('newTg').value = '';
  renderModalTags();
  document.getElementById('modal').style.display = 'flex';
}

function openEdit(id) {
  const p = profiles.find(x => x.id === id);
  if (!p) return;
  editingId = id; tempGroups = [...p.groups];
  document.getElementById('modalTitle').textContent = t('modal_edit');
  document.getElementById('pName').value = p.name;
  document.getElementById('importJson').value = '';
  document.getElementById('newTg').value = '';
  renderModalTags();
  document.getElementById('modal').style.display = 'flex';
}

function closeModal() { document.getElementById('modal').style.display = 'none'; }

function tgKeydown(e) { if (e.key === 'Enter') addTg(); }

function addTg() {
  const inp = document.getElementById('newTg');
  const n = parseInt(inp.value.trim());
  if (!isNaN(n) && n > 0 && !tempGroups.includes(n)) {
    tempGroups.push(n);
    tempGroups.sort((a,b) => a-b);
    renderModalTags();
  }
  inp.value = ''; inp.focus();
}

function removeTg(n) {
  tempGroups = tempGroups.filter(g => g !== n);
  renderModalTags();
}

function renderModalTags() {
  document.getElementById('modalTags').innerHTML =
    tempGroups.map(g => `<span class="tag">${tgLabel(g)}<span class="tag-x" onclick="removeTg(${g})">×</span></span>`).join('');
  prefetchAndRender(tempGroups, renderModalTags);
}

function importJson() {
  const raw = val('importJson').trim();
  try {
    const parsed = JSON.parse(raw);
    const arr = Array.isArray(parsed) ? parsed : (parsed.static_groups || []);
    let added = 0;
    arr.forEach(g => {
      const n = parseInt(g);
      if (!isNaN(n) && n > 0 && !tempGroups.includes(n)) { tempGroups.push(n); added++; }
    });
    tempGroups.sort((a,b) => a-b);
    renderModalTags();
    document.getElementById('importJson').value = '';
    toast(t('toast_import_tg', { n: added }), 'ok');
  } catch { toast(t('toast_invalid_json'), 'err'); }
}

function saveProfile() {
  const name = val('pName').trim();
  if (!name) { toast(t('err_no_name'), 'err'); return; }
  if (!tempGroups.length) { toast(t('err_no_tgs'), 'err'); return; }

  if (editingId) {
    const i = profiles.findIndex(p => p.id === editingId);
    profiles[i] = { ...profiles[i], name, groups: tempGroups };
  } else {
    profiles.push({ id: Date.now().toString(), name, groups: tempGroups });
  }
  persist(); renderProfiles(); closeModal();
  toast(t('toast_profile_saved'), 'ok');
}

function deleteProfile(id) {
  if (!confirm(t('confirm_delete_profile'))) return;
  profiles = profiles.filter(p => p.id !== id);
  if (selectedId === id) {
    selectedId = null;
    document.getElementById('selectedLabel').textContent = t('no_profile_selected');
    document.getElementById('applyBtn').disabled = true;
  }
  persist(); renderProfiles();
  toast(t('toast_profile_deleted'), 'ok');
}

function exportProfile(id) {
  const p = profiles.find(x => x.id === id);
  if (!p) return;
  const blob = new Blob([JSON.stringify({ static_groups: p.groups }, null, 2)], { type: 'application/json' });
  const a = Object.assign(document.createElement('a'), { href: URL.createObjectURL(blob), download: `${p.name.replace(/\s+/g,'_')}.json` });
  a.click(); URL.revokeObjectURL(a.href);
}

function persist() { localStorage.setItem('bm_profiles', JSON.stringify(profiles)); }

function exportAllProfiles() {
  if (!profiles.length) { toast(t('toast_no_profiles'), 'err'); return; }
  const blob = new Blob([JSON.stringify({ profiles }, null, 2)], { type: 'application/json' });
  const a = Object.assign(document.createElement('a'), {
    href: URL.createObjectURL(blob),
    download: 'bm-profiles.json',
  });
  a.click(); URL.revokeObjectURL(a.href);
  toast(t('toast_exported', { n: profiles.length }), 'ok');
}

function importAllProfiles() {
  const input = document.createElement('input');
  input.type = 'file'; input.accept = '.json,application/json';
  input.onchange = async () => {
    const file = input.files[0];
    if (!file) return;
    try {
      const data = JSON.parse(await file.text());
      const incoming = data.profiles || (Array.isArray(data) ? data : null);
      if (!Array.isArray(incoming)) { toast(t('toast_invalid_format'), 'err'); return; }
      if (!confirm(t('confirm_replace', { n: profiles.length, m: incoming.length }))) return;
      profiles = incoming;
      persist(); renderProfiles();
      toast(t('toast_imported', { n: incoming.length }), 'ok');
    } catch { toast(t('toast_invalid_file'), 'err'); }
  };
  input.click();
}

function loadTgFromFile() {
  const input = document.createElement('input');
  input.type = 'file'; input.accept = '.json,application/json';
  input.onchange = async () => {
    const file = input.files[0];
    if (!file) return;
    try {
      const parsed = JSON.parse(await file.text());
      const arr = Array.isArray(parsed) ? parsed : (parsed.static_groups || []);
      let added = 0;
      arr.forEach(g => {
        const n = parseInt(g);
        if (!isNaN(n) && n > 0 && !tempGroups.includes(n)) { tempGroups.push(n); added++; }
      });
      tempGroups.sort((a,b) => a-b);
      renderModalTags();
      toast(t('toast_load_tg', { n: added }), 'ok');
    } catch { toast(t('toast_invalid_file'), 'err'); }
  };
  input.click();
}

// ── Current groups card ────────────────────────────────────────────────────
function renderCurrentCard() {
  if (currentGroupsSlot === null) return;
  const slot = currentGroupsSlot;
  const groups = currentGroupsData;
  document.getElementById('currentCardTitle').textContent = t('current_card_title', { slot });
  const content = document.getElementById('currentContent');
  if (!groups.length) {
    content.innerHTML = `<div class="empty">${t('no_groups_on_slot', { slot })}</div>`;
  } else {
    content.innerHTML = `
      <div class="help" style="margin-bottom:0.5rem">${t('groups_count_on_slot', { n: groups.length, slot })}</div>
      <div class="group-chips">
        ${groups.map(g => {
          const name = tgCache[g.talkgroup]?.name;
          return `<span class="chip">${g.talkgroup}${name ? ` <span class="tg-name" style="max-width:none"> · ${esc(name)}</span>` : ''}</span>`;
        }).join('')}
      </div>`;
  }
}

// ── API ────────────────────────────────────────────────────────────────────
async function req(method, path, body, token) {
  const headers = { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' };
  const r = await fetch(`${API}${path}`, { method, headers, body: body ? JSON.stringify(body) : undefined });
  if (!r.ok) {
    const txt = await r.text().catch(() => '');
    throw new Error(`HTTP ${r.status}${txt ? ': ' + txt : ''}`);
  }
  return r;
}

async function fetchCurrentGroups() {
  const { deviceId, token, slot } = getConn();
  if (!deviceId || !token) { toast(t('err_no_device_token'), 'err'); return; }
  log(t('log_fetching_groups', { slot }), 'info');
  try {
    const r = await req('GET', `/device/${deviceId}/talkgroup`, null, token);
    const all = await r.json();
    const groups = all.filter(g => parseInt(g.slot) === slot);
    const card = document.getElementById('currentCard');
    currentGroups = groups.map(g => parseInt(g.talkgroup));
    currentGroupsData = groups;
    currentGroupsSlot = slot;
    card.style.display = 'block';
    renderCurrentCard();
    prefetchAndRender(groups.map(g => g.talkgroup), renderCurrentCard);
    log(t('log_found_groups', { n: groups.length, slot }), 'success');
  } catch (e) {
    log(t('log_err_generic', { msg: e.message }), 'error');
    toast(t('toast_fail_fetch'), 'err');
  }
}

function saveCurrentAsProfile() {
  if (!currentGroups.length) { toast(t('toast_no_groups'), 'err'); return; }
  editingId = null;
  tempGroups = [...currentGroups];
  document.getElementById('modalTitle').textContent = t('modal_new_from_current');
  document.getElementById('pName').value = '';
  document.getElementById('importJson').value = '';
  document.getElementById('newTg').value = '';
  renderModalTags();
  document.getElementById('modal').style.display = 'flex';
}

async function clearSlot() {
  if (busy) return;
  const { deviceId, token, slot } = getConn();
  if (!deviceId || !token) { toast(t('err_no_device_token'), 'err'); return; }

  const r0 = await req('GET', `/device/${deviceId}/talkgroup`, null, token).catch(() => null);
  if (!r0) { toast(t('toast_fail_fetch'), 'err'); return; }
  const toDelete = (await r0.json()).filter(g => parseInt(g.slot) === slot);

  if (!toDelete.length) { toast(t('err_no_static_groups', { slot }), 'err'); return; }
  if (!confirm(t('confirm_clear_slot', { n: toDelete.length, slot, deviceId }))) return;

  busy = true;
  document.getElementById('clearSlotBtn').disabled = true;
  logSep();
  log(t('log_clearing', { n: toDelete.length, slot }), 'info');
  try {
    await Promise.all(toDelete.map(async g => {
      await req('DELETE', `/device/${deviceId}/talkgroup/${g.slot}/${g.talkgroup}`, null, token);
      const name = tgCache[g.talkgroup]?.name;
      log(t('log_deleted_group', { id: g.talkgroup, name: name ? ` (${name})` : '', slot: g.slot }), 'info');
    }));
    log(t('log_cleared_ok', { n: toDelete.length, slot }), 'success');
    toast(t('toast_clear_ok', { slot }), 'ok');
    fetchCurrentGroups();
  } catch (e) {
    log(t('log_err_generic', { msg: e.message }), 'error');
    toast(t('toast_fail_clear'), 'err');
  } finally {
    busy = false;
    document.getElementById('clearSlotBtn').disabled = false;
  }
}

function confirmApply() {
  if (busy) return;
  const { deviceId, token, slot } = getConn();
  if (!deviceId || !token) { toast(t('err_no_device_token'), 'err'); return; }
  const profile = profiles.find(p => p.id === selectedId);
  if (!profile) { toast(t('err_no_profile'), 'err'); return; }

  const slotLabel = slot === 0 ? t('slot_0') : `Slot ${slot}`;
  document.getElementById('confirmMsg').innerHTML =
    `Profile <strong>${profile.name}</strong> — ${tgCountLabel(profile.groups.length)} on <strong>${slotLabel}</strong>.`;

  const modal = document.getElementById('confirmModal');
  modal.style.display = 'flex';
  const okBtn = document.getElementById('confirmOkBtn');
  okBtn.onclick = () => { closeConfirm(); applyProfile(); };
}

function closeConfirm() {
  document.getElementById('confirmModal').style.display = 'none';
}

async function applyProfile() {
  if (busy) return;
  const { deviceId, token, slot } = getConn();
  if (!deviceId || !token) { toast(t('err_no_device_token'), 'err'); return; }
  const profile = profiles.find(p => p.id === selectedId);
  if (!profile) { toast(t('err_no_profile'), 'err'); return; }

  busy = true;
  document.getElementById('applyBtn').disabled = true;
  setBadge('run', 'badge_run');
  resetSteps();

  logSep();
  log(t('log_applying', { name: profile.name }), 'info');
  log(t('log_applying_groups', { n: profile.groups.length, groups: profile.groups.join(', ') }), 'info');

  try {
    // 1 – Delete existing static groups on the selected slot only
    setStep('delete', 'run');
    log(t('log_fetching_existing'), 'info');
    const r = await req('GET', `/device/${deviceId}/talkgroup`, null, token);
    const existing = await r.json();
    const toDelete = existing.filter(g => parseInt(g.slot) === slot);
    const skipped  = existing.length - toDelete.length;
    const skippedPart = skipped ? t('log_skipped', { n: skipped }) : '';
    log(t('log_deleting_groups', { n: toDelete.length, slot, skipped: skippedPart }), 'info');
    await Promise.all(toDelete.map(async g => {
      await req('DELETE', `/device/${deviceId}/talkgroup/${g.slot}/${g.talkgroup}`, null, token);
      const name = tgCache[g.talkgroup]?.name;
      log(t('log_deleted_group', { id: g.talkgroup, name: name ? ` (${name})` : '', slot: g.slot }), 'info');
    }));
    setStep('delete', 'done');
    log(t('log_deleted_ok', { n: toDelete.length, slot }), 'success');

    // 2 – Drop dynamic groups
    setStep('dynamic', 'run');
    await req('GET', `/device/${deviceId}/action/dropDynamicGroups/${slot}`, null, token);
    setStep('dynamic', 'done');
    log(t('log_dropped_dynamic'), 'success');

    // 3 – Drop current call
    setStep('call', 'run');
    await req('GET', `/device/${deviceId}/action/dropCallRoute/${slot}`, null, token);
    setStep('call', 'done');
    log(t('log_dropped_call'), 'success');

    // 4 – Reset connection
    setStep('reset', 'run');
    await req('GET', `/device/${deviceId}/action/removeContext`, null, token);
    setStep('reset', 'done');
    log(t('log_reset_conn'), 'success');

    // 5 – Add new static groups
    setStep('add', 'run');
    log(t('log_adding_groups', { n: profile.groups.length }), 'info');
    await Promise.all(profile.groups.map(async g => {
      await req('POST', `/device/${deviceId}/talkgroup`, { group: g, slot }, token);
      const name = tgCache[g]?.name;
      log(t('log_added_group', { id: g, name: name ? ` (${name})` : '', slot }), 'info');
    }));
    setStep('add', 'done');
    log(t('log_added_ok', { n: profile.groups.length }), 'success');

    setBadge('ok', 'badge_ok');
    log(t('log_success'), 'success');
    toast(t('toast_profile_applied'), 'ok');

  } catch (e) {
    log(t('log_error', { msg: e.message }), 'error');
    setBadge('err', 'badge_err');
    toast(t('toast_fail_apply'), 'err');
    document.querySelector('.step.s-run')?.classList.replace('s-run', 's-err');
  } finally {
    busy = false;
    document.getElementById('applyBtn').disabled = false;
  }
}

// ── Step / badge helpers ───────────────────────────────────────────────────
const STEPS = ['delete', 'dynamic', 'call', 'reset', 'add'];

function resetSteps() {
  STEPS.forEach((s, i) => {
    const el = document.getElementById(`s-${s}`);
    el.className = 'step';
    el.querySelector('.step-dot').textContent = i + 1;
  });
}

function setStep(name, state) {
  const el = document.getElementById(`s-${name}`);
  el.className = `step s-${state}`;
  const dot = el.querySelector('.step-dot');
  if (state === 'done') dot.textContent = '✓';
  else if (state === 'err') dot.textContent = '✗';
  else dot.textContent = '…';
}

function setBadge(type, key) {
  currentBadgeKey = key;
  const b = document.getElementById('statusBadge');
  b.className = `badge badge-${type}`;
  b.textContent = t(key);
}

// ── Log helpers ────────────────────────────────────────────────────────────
function log(msg, type = 'info') {
  const logEl = document.getElementById('log');
  const readyMsg = document.getElementById('logReadyMsg');
  if (readyMsg) readyMsg.closest('.log-row')?.remove();

  const ts = new Date().toTimeString().slice(0,8);
  const cls = type === 'success' ? 'c-success' : type === 'error' ? 'c-error' : 'c-info';
  const row = document.createElement('div');
  row.className = 'log-row';
  row.innerHTML = `<span class="log-ts">${ts}</span><span class="${cls}">${esc(msg)}</span>`;
  logEl.appendChild(row);
  logEl.scrollTop = logEl.scrollHeight;
}

function logSep() {
  const c = document.getElementById('log');
  const d = document.createElement('div');
  d.className = 'log-sep';
  c.appendChild(d);
}

function clearLog() {
  const logEl = document.getElementById('log');
  logEl.innerHTML = `<div class="log-row"><span class="log-ts">--:--:--</span><span class="c-muted" id="logReadyMsg">${t('log_ready')}</span></div>`;
}

// ── Toast ──────────────────────────────────────────────────────────────────
function toast(msg, type = 'ok') {
  const c = document.getElementById('toasts');
  const el = document.createElement('div');
  el.className = `toast toast-${type}`;
  el.textContent = msg;
  c.appendChild(el);
  setTimeout(() => el.remove(), 3000);
}

// ── Utilities ──────────────────────────────────────────────────────────────
function val(id) { return document.getElementById(id).value; }
function esc(s) { return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;'); }

init();
