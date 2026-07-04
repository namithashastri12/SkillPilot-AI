/* SkillPilot AI — dashboard controller */

const state = {
  student: null,
  lastGapResult: null,
};

// ---------------------------------------------------------------- utils --
function $(sel) { return document.querySelector(sel); }
function $all(sel) { return Array.from(document.querySelectorAll(sel)); }

function toast(msg) {
  const t = $('#toast');
  t.textContent = msg;
  t.classList.add('show');
  setTimeout(() => t.classList.remove('show'), 3200);
}

async function api(path, opts) {
  opts = opts || {};
  opts.headers = Object.assign({ 'Content-Type': 'application/json' }, opts.headers || {});
  const res = await fetch(path, opts);
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(data.error || 'Something went wrong');
  return data;
}

function setLoading(id, on) {
  $(id).classList.toggle('active', !!on);
}

// ------------------------------------------------------------- nav view --
function showView(id) {
  $all('.view').forEach(v => v.classList.remove('active'));
  $(`#${id}`).classList.add('active');
  $all('.side-link').forEach(l => l.classList.toggle('active', l.dataset.view === id));
}

$all('.side-link').forEach(link => {
  link.addEventListener('click', () => showView(link.dataset.view));
});

// ------------------------------------------------------------ role field --
$('#in-role').addEventListener('change', (e) => {
  $('#custom-role-field').style.display = e.target.value === '__custom' ? 'block' : 'none';
});

function currentTargetRole() {
  const sel = $('#in-role').value;
  if (sel === '__custom') return $('#in-role-custom').value.trim();
  return sel;
}

// -------------------------------------------------------------- onboard --
$('#btn-onboard').addEventListener('click', async () => {
  const name = $('#in-name').value.trim();
  const email = $('#in-email').value.trim();
  const target_role = currentTargetRole();

  if (!name || !email) { toast('Name and email are required.'); return; }

  setLoading('#loader-onboard', true);
  try {
    const res = await api('/api/onboard', {
      method: 'POST',
      body: JSON.stringify({ name, email, target_role }),
    });
    state.student = res.student;
    $('#badge-status').textContent = `flying as ${res.student.name.split(' ')[0]}`;
    $('#badge-status').classList.add('live');
    updateSystemBadge(res.system);
    toast('Flight profile saved. Head to Resume analysis next.');
    loadDashboard();
  } catch (e) {
    toast(e.message);
  } finally {
    setLoading('#loader-onboard', false);
  }
});

function updateSystemBadge(sys) {
  const el = $('#system-status');
  if (!sys) return;
  if (sys.live_mode) {
    el.textContent = `● gemini live · ${sys.model}`;
  } else {
    el.textContent = `● offline mode · rule-based agents`;
  }
}

// -------------------------------------------------------------- resume ---
$('#file-drop-label').addEventListener('click', () => $('#in-resume').click());
$('#in-resume').addEventListener('change', async (e) => {
  const file = e.target.files[0];
  if (!file) return;
  if (!state.student) { toast('Save your flight profile first.'); showView('view-profile'); return; }

  $('#file-drop-label').textContent = file.name;
  setLoading('#loader-resume', true);

  const fd = new FormData();
  fd.append('resume', file);
  try {
    const res = await fetch('/api/upload_resume', { method: 'POST', body: fd });
    const data = await res.json();
    if (!res.ok) throw new Error(data.error);

    renderResume(data.analysis);
    toast('Resume analyzed. Skills captured for your gap analysis.');
  } catch (err) {
    toast(err.message);
  } finally {
    setLoading('#loader-resume', false);
  }
});

function renderResume(analysis) {
  $('#panel-resume-results').style.display = 'block';
  const skillsEl = $('#resume-skills');
  skillsEl.innerHTML = analysis.skills.map(s => `<span class="chip">${escapeHtml(s)}</span>`).join('') || '<span class="chip">No specific skills detected</span>';

  const sugEl = $('#resume-suggestions');
  sugEl.innerHTML = analysis.suggestions.map(s => `<li>${escapeHtml(s)}</li>`).join('');
}

// --------------------------------------------------------- full pipeline -
$('#btn-generate').addEventListener('click', async () => {
  if (!state.student) { toast('Save your flight profile first.'); showView('view-profile'); return; }
  const target_role = currentTargetRole();
  if (!target_role) { toast('Set a target role in Flight profile first.'); showView('view-profile'); return; }

  const weeks_available = parseInt($('#in-weeks').value || '12', 10);
  const extra = $('#in-extra-skills').value.split(',').map(s => s.trim()).filter(Boolean);

  setLoading('#loader-plan', true);
  try {
    const res = await api('/api/generate_plan', {
      method: 'POST',
      body: JSON.stringify({ target_role, weeks_available, skills: extra }),
    });
    state.lastGapResult = res;
    renderGapResults(res);
    renderRoadmap(res.roadmap);
    renderRecommendations(res.recommendations);
    toast('Flight plan generated — check Roadmap and Courses tabs.');
    loadProgress();
  } catch (e) {
    toast(e.message);
  } finally {
    setLoading('#loader-plan', false);
  }
});

function renderGapResults(res) {
  $('#gap-results').style.display = 'block';
  const gap = res.gap;
  $('#stat-readiness').textContent = gap.readiness_score + '%';
  $('#stat-have').textContent = gap.have_skills.length;
  $('#stat-missing').textContent = gap.missing_skills.length;
  $('#stat-weeks').textContent = (res.roadmap.phases || []).reduce((acc, p) => {
    const parts = (p.weeks || '1-1').split('-').map(Number);
    return Math.max(acc, parts[1] || parts[0] || 0);
  }, 0);

  renderGauge($('#gap-gauge'), gap.readiness_score);
  $('#gap-insight-text').textContent = res.insight.insight;

  $('#chips-have').innerHTML = gap.have_skills.map(s => `<span class="chip have">✓ ${escapeHtml(s)}</span>`).join('') || '<span class="chip">No matches yet</span>';
  $('#chips-missing').innerHTML = gap.missing_skills.map(s => `<span class="chip missing">${escapeHtml(s)}</span>`).join('') || '<span class="chip">No gaps — great work</span>';
}

function renderRoadmap(roadmap) {
  const list = $('#roadmap-list');
  const phases = roadmap.phases || [];
  $('#roadmap-empty').style.display = phases.length ? 'none' : 'block';
  list.innerHTML = phases.map(p => `
    <div class="plan-row">
      <div class="wk">WK ${escapeHtml(p.weeks)}</div>
      <div>
        <h4>${escapeHtml(p.phase)}</h4>
        <p>${escapeHtml(p.milestone || '')}</p>
        <div class="pill-row">${(p.focus_skills || []).map(s => `<span class="pill">${escapeHtml(s)}</span>`).join('')}</div>
      </div>
    </div>
  `).join('');
}

function renderRecommendations(recs) {
  const hasCourses = recs.courses && recs.courses.length;
  const hasProjects = recs.projects && recs.projects.length;
  $('#courses-empty').style.display = (hasCourses || hasProjects) ? 'none' : 'block';

  $('#panel-courses').style.display = hasCourses ? 'block' : 'none';
  $('#course-list').innerHTML = (recs.courses || []).map(c => `
    <div class="course-row">
      <div>
        <div class="title">${escapeHtml(c.title)}</div>
        <div class="meta">${escapeHtml(c.skill)} · ${escapeHtml(c.provider)}</div>
      </div>
      <span class="pill">${escapeHtml(c.level || '')}</span>
    </div>
  `).join('');

  $('#panel-projects').style.display = hasProjects ? 'block' : 'none';
  $('#project-list').innerHTML = (recs.projects || []).map(p => `<li>${escapeHtml(p)}</li>`).join('');
}

// ------------------------------------------------------------- progress --
async function loadProgress() {
  try {
    const dash = await api('/api/dashboard');
    renderProgress(dash.progress || []);
  } catch (e) { /* silent — likely no session yet */ }
}

function renderProgress(progress) {
  $('#progress-empty').style.display = progress.length ? 'none' : 'block';
  $('#panel-progress').style.display = progress.length ? 'block' : 'none';

  $('#milestone-list').innerHTML = progress.map(m => `
    <div class="milestone-row">
      <input type="checkbox" data-week="${m.week_number}" data-milestone="${escapeAttr(m.milestone)}" ${m.status === 'done' ? 'checked' : ''} />
      <div class="wk-tag">WK ${m.week_number}</div>
      <div class="txt ${m.status === 'done' ? 'done' : ''}">${escapeHtml(m.milestone)}</div>
    </div>
  `).join('');

  $all('#milestone-list input[type="checkbox"]').forEach(cb => {
    cb.addEventListener('change', async () => {
      const status = cb.checked ? 'done' : 'pending';
      try {
        await api('/api/progress/update', {
          method: 'POST',
          body: JSON.stringify({
            week_number: parseInt(cb.dataset.week, 10),
            milestone: cb.dataset.milestone,
            status,
          }),
        });
        cb.closest('.milestone-row').querySelector('.txt').classList.toggle('done', cb.checked);
        toast(status === 'done' ? 'Milestone logged. Memory Agent updated.' : 'Milestone reopened.');
      } catch (e) {
        toast(e.message);
        cb.checked = !cb.checked;
      }
    });
  });
}

// ----------------------------------------------------------- full reload -
async function loadDashboard() {
  try {
    const dash = await api('/api/dashboard');
    if (dash.resume) renderResume({ skills: dash.resume.extracted_skills, suggestions: dash.resume.suggestions });
    if (dash.skill_gap && dash.roadmap && dash.recommendations) {
      const gap = dash.skill_gap;
      const fakeRes = {
        gap,
        roadmap: dash.roadmap.roadmap,
        recommendations: dash.recommendations,
        insight: {
          insight: gap.readiness_score >= 80
            ? "You're close to hire-ready — focus on interview polish and networking."
            : gap.readiness_score >= 50
              ? 'Solid foundation. Stay consistent on your roadmap and you\'ll close the gap fast.'
              : 'Early stage — that\'s fine. Prioritize the Foundations phase before jumping to projects.',
        },
      };
      renderGapResults(fakeRes);
      renderRoadmap(dash.roadmap.roadmap);
      renderRecommendations(dash.recommendations);
    }
    renderProgress(dash.progress || []);
  } catch (e) { /* no session yet — fine */ }
}

// ------------------------------------------------------------------ init -
function escapeHtml(str) {
  return String(str ?? '').replace(/[&<>"']/g, s => ({
    '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;',
  }[s]));
}
function escapeAttr(str) { return escapeHtml(str).replace(/"/g, '&quot;'); }

(async function init() {
  try {
    const me = await api('/api/me');
    if (me.student) {
      state.student = me.student;
      $('#in-name').value = me.student.name;
      $('#in-email').value = me.student.email;
      if (me.student.target_role) {
        const opt = Array.from($('#in-role').options).find(o => o.value === me.student.target_role);
        if (opt) { $('#in-role').value = me.student.target_role; }
        else { $('#in-role').value = '__custom'; $('#custom-role-field').style.display = 'block'; $('#in-role-custom').value = me.student.target_role; }
      }
      $('#badge-status').textContent = `flying as ${me.student.name.split(' ')[0]}`;
      $('#badge-status').classList.add('live');
      loadDashboard();
    }
  } catch (e) { /* not onboarded yet */ }

  try {
    const sys = await api('/api/system_status');
    updateSystemBadge(sys);
  } catch (e) { /* ignore */ }
})();
