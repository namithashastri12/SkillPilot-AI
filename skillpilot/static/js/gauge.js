/**
 * SkillPilot AI — Attitude Indicator gauge.
 * The signature visual: career readiness read the way a pilot reads an
 * artificial horizon. More visible "sky" + nose-up tilt = more ready.
 *
 * renderGauge(el, score, opts) — score is 0-100.
 */
function renderGauge(el, score, opts) {
  opts = opts || {};
  const size = opts.size || 220;
  const r = size / 2;
  score = Math.max(0, Math.min(100, score || 0));

  // map score -> tilt angle (-24deg .. +24deg) and vertical shift (more sky when higher)
  const angle = ((score - 50) / 50) * 22;
  const shift = ((score - 50) / 50) * (r * 0.55);

  const clipId = 'clip-' + Math.random().toString(36).slice(2, 9);

  const svg = `
  <svg viewBox="0 0 ${size} ${size}" width="${size}" height="${size}" role="img" aria-label="Career readiness gauge: ${score} percent">
    <defs>
      <clipPath id="${clipId}">
        <circle cx="${r}" cy="${r}" r="${r - 10}" />
      </clipPath>
      <linearGradient id="sky-${clipId}" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0%" stop-color="#2c5aa0" />
        <stop offset="100%" stop-color="#173863" />
      </linearGradient>
      <linearGradient id="ground-${clipId}" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0%" stop-color="#6b4a1f" />
        <stop offset="100%" stop-color="#3a2811" />
      </linearGradient>
    </defs>

    <circle cx="${r}" cy="${r}" r="${r - 3}" fill="#0b1220" stroke="#2e4364" stroke-width="1.5" />

    <g clip-path="url(#${clipId})">
      <g transform="translate(${r} ${r + shift}) rotate(${angle}) translate(${-r} ${-r})">
        <rect x="-40" y="-200" width="${size + 80}" height="${size + 200}" fill="url(#sky-${clipId})" />
        <rect x="-40" y="${r}" width="${size + 80}" height="${size + 200}" fill="url(#ground-${clipId})" />
        <rect x="-40" y="${r - 1.5}" width="${size + 80}" height="3" fill="#e9f0fb" />
        ${[-40, -20, 20, 40].map(o => `<line x1="${r + o - 8}" y1="${r}" x2="${r + o - 8}" y2="${r + (o < 0 ? 6 : -6)}" stroke="#cdd9ee" stroke-width="1.5" opacity="0.6"/>`).join('')}
      </g>
    </g>

    <!-- bezel ticks -->
    ${Array.from({ length: 24 }).map((_, i) => {
      const a = (i / 24) * 360;
      const rad = (a * Math.PI) / 180;
      const inner = r - 10;
      const outer = r - (i % 6 === 0 ? 20 : 15);
      const x1 = r + inner * Math.sin(rad), y1 = r - inner * Math.cos(rad);
      const x2 = r + outer * Math.sin(rad), y2 = r - outer * Math.cos(rad);
      return `<line x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}" stroke="#3d5578" stroke-width="${i % 6 === 0 ? 2 : 1}" />`;
    }).join('')}

    <!-- fixed aircraft symbol -->
    <g stroke="#ffb020" stroke-width="3" stroke-linecap="round">
      <line x1="${r - 34}" y1="${r}" x2="${r - 10}" y2="${r}" />
      <line x1="${r + 10}" y1="${r}" x2="${r + 34}" y2="${r}" />
      <circle cx="${r}" cy="${r}" r="3.5" fill="#ffb020" stroke="none" />
    </g>

    <circle cx="${r}" cy="${r}" r="${r - 3}" fill="none" stroke="#2e4364" stroke-width="1.5" />
  </svg>`;

  el.innerHTML = svg;
}

if (typeof module !== 'undefined') { module.exports = { renderGauge }; }
