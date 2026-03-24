// Loader
window.addEventListener('load', () => {
  document.getElementById('loader').style.display = 'none';
});

// i18n Language Toggle
let currentLang = localStorage.getItem('lang') || 'en';
const langToggle = document.getElementById('langToggle');

function applyTranslations(lang) {
  if (!window.translations) return;
  const dict = window.translations[lang];
  document.querySelectorAll('[data-i18n]').forEach(el => {
    const key = el.getAttribute('data-i18n');
    if (dict[key]) {
      if (el.tagName === 'INPUT' && el.type === 'button') {
        el.value = dict[key];
      } else {
        el.innerHTML = dict[key];
      }
    }
  });
  if (langToggle) {
    langToggle.textContent = lang === 'en' ? '🌐 HIN' : '🌐 ENG';
  }
}

applyTranslations(currentLang);

if (langToggle) {
  langToggle.addEventListener('click', () => {
    currentLang = currentLang === 'en' ? 'hi' : 'en';
    localStorage.setItem('lang', currentLang);
    applyTranslations(currentLang);
  });
}

// Role-Based UI
const userRole = localStorage.getItem('userRole');

// Protect dashboard
if (window.location.pathname.includes('dashboard.html') && userRole !== 'asha') {
  window.location.href = 'index.html';
}

function updateNav() {
  const navActions = document.querySelector('.nav-actions');
  if (!navActions) return;

  // Find existing dynamic buttons to remove them if re-running
  const existingLogout = document.getElementById('navLogout');
  const existingLogin = document.getElementById('navLogin');
  if (existingLogout) existingLogout.remove();
  if (existingLogin) existingLogin.remove();

  if (userRole) {
    // Logged in
    const logoutBtn = document.createElement('a');
    logoutBtn.href = '#';
    logoutBtn.id = 'navLogout';
    logoutBtn.className = 'nav-btn';
    logoutBtn.textContent = 'Logout';
    logoutBtn.onclick = async (e) => {
      e.preventDefault();
      await fetch('/api/auth/logout', { method: 'POST' });
      localStorage.removeItem('userRole');
      window.location.href = 'login.html';
    };
    navActions.appendChild(logoutBtn);

    // Hide dashboard link for patients
    const dashLink = document.querySelector('a[href="dashboard.html"]');
    if (dashLink && userRole === 'patient') {
      dashLink.style.display = 'none';
    }
  } else {
    // Not logged in
    // Only show login on pages that aren't login.html
    if (!window.location.pathname.includes('login.html')) {
      const loginBtn = document.createElement('a');
      loginBtn.href = 'login.html';
      loginBtn.id = 'navLogin';
      loginBtn.className = 'nav-btn';
      loginBtn.textContent = 'Login / Signup';
      navActions.appendChild(loginBtn);
    }
  }
}
updateNav();

// Dark mode
const toggle = document.getElementById('themeToggle');
if (localStorage.getItem('theme') === 'dark') {
  document.body.classList.add('dark');
}

toggle?.addEventListener('click', () => {
  document.body.classList.toggle('dark');
  localStorage.setItem(
    'theme',
    document.body.classList.contains('dark') ? 'dark' : 'light'
  );
});

// 3D Tilt
document.querySelectorAll('.tilt').forEach(card => {
  card.addEventListener('mousemove', e => {
    const r = card.getBoundingClientRect();
    const x = e.clientX - r.left;
    const y = e.clientY - r.top;
    card.style.transform =
      `rotateX(${-(y / r.height - 0.5) * 10}deg)
       rotateY(${(x / r.width - 0.5) * 10}deg)`;
  });

  card.addEventListener('mouseleave', () => {
    card.style.transform = 'rotateX(0) rotateY(0)';
  });
});

// Form Submission (Screening Form)
const screeningForm = document.querySelector('.screening-form');
if (screeningForm) {
  screeningForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const resultElement = document.getElementById('predictionResult');
    resultElement.textContent = "⚙️ Processing your data...";

    const payload = {
      age: document.getElementById('ageInput').value,
      gestational_month: document.getElementById('monthInput').value,
      blood_pressure: document.getElementById('bpInput').value,
      hemoglobin: document.getElementById('hbInput').value,
      complications: document.getElementById('compInput').value
    };

    try {
      const response = await fetch('/api/predict', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(payload)
      });
      const data = await response.json();

      if (data.status === 'success') {
        resultElement.innerHTML = `Risk Level: <strong>${data.risk_level}</strong>`;
        // Basic coloring based on risk:
        if (data.risk_level === 'High Risk') resultElement.style.color = '#ff4d4d'; // Red
        else if (data.risk_level === 'Mid Risk') resultElement.style.color = '#ff9900'; // Orange
        else resultElement.style.color = '#32cd32'; // Green
      } else {
        resultElement.textContent = "❌ Error processing data.";
      }
    } catch (err) {
      console.error(err);
      resultElement.textContent = "❌ Network error.";
    }
  });
}

// Load Dashboard Alerts
const dashboardGrid = document.getElementById('dashboardGrid');
if (dashboardGrid) {
  async function loadAlerts() {
    try {
      const response = await fetch('/api/alerts');
      const data = await response.json();

      dashboardGrid.innerHTML = '';
      if (!data.alerts || data.alerts.length === 0) {
        dashboardGrid.innerHTML = '<p>No alerts found.</p>';
        return;
      }

      data.alerts.forEach((alert) => {
        const card = document.createElement('div');
        let riskClass = 'low';
        let riskTextRaw = alert.risk_level || 'Low Risk';
        if (riskTextRaw === 'High Risk') riskClass = 'high';
        else if (riskTextRaw === 'Mid Risk') riskClass = 'medium';

        // Translate risk text manually if dictionary exists
        let riskText = riskTextRaw;
        if (window.translations && currentLang === 'hi') {
          if (riskTextRaw === 'High Risk') riskText = 'उच्च जोखिम';
          else if (riskTextRaw === 'Mid Risk') riskText = 'मध्यम जोखिम';
          else if (riskTextRaw === 'Low Risk') riskText = 'कम जोखिम';
        }

        const dict = window.translations ? window.translations[currentLang] : {};
        const ptLabel = currentLang === 'hi' ? 'रोगी' : 'Patient';
        const ageLabel = currentLang === 'hi' ? 'उम्र' : 'Age';
        const bpLabel = currentLang === 'hi' ? 'रक्तचाप' : 'BP';

        card.className = `patient glass tilt ${riskClass}`;
        card.innerHTML = `
          <h4>${ptLabel} ${alert.id}</h4>
          <p><strong>${ageLabel}:</strong> ${alert.age} | <strong>${bpLabel}:</strong> ${alert.blood_pressure}</p>
          <p class="risk-badge">${riskText}</p>
          <small>${new Date(alert.timestamp).toLocaleString()}</small>
        `;
        dashboardGrid.appendChild(card);
      });

      // Re-initialize tilt effect for new cards
      document.querySelectorAll('.tilt').forEach(card => {
        card.addEventListener('mousemove', e => {
          const r = card.getBoundingClientRect();
          const x = e.clientX - r.left;
          const y = e.clientY - r.top;
          card.style.transform = `rotateX(${-(y / r.height - 0.5) * 10}deg) rotateY(${(x / r.width - 0.5) * 10}deg)`;
        });
        card.addEventListener('mouseleave', () => {
          card.style.transform = 'rotateX(0) rotateY(0)';
        });
      });

    } catch (err) {
      console.error(err);
      dashboardGrid.innerHTML = '<p>❌ Failed to load alerts.</p>';
    }
  }
  loadAlerts();
}

// Daily Tracker Submission
const trackerForm = document.querySelector('.tracker-form');
if (trackerForm) {
  trackerForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const resultElement = document.getElementById('trackerResult');
    resultElement.textContent = "⚙️ Saving entry...";

    const payload = {
      mood: document.getElementById('moodInput').value,
      water_intake: parseInt(document.getElementById('waterInput').value, 10),
      sleep_hours: parseFloat(document.getElementById('sleepInput').value),
      symptoms: document.getElementById('symptomsInput').value
    };

    try {
      const response = await fetch('/api/tracker', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      const data = await response.json();
      if (data.status === 'success') {
        resultElement.innerHTML = `✅ Tracker data saved!`;
        resultElement.style.color = '#32cd32';
        trackerForm.reset();
        if (typeof loadTrackerEntries === 'function') loadTrackerEntries();
      } else {
        resultElement.textContent = "❌ Error saving entry.";
      }
    } catch (err) {
      console.error(err);
      resultElement.textContent = "❌ Network error.";
    }
  });
}

// Load Tracker Timeline Entries
const trackerTimeline = document.getElementById('trackerTimeline');
if (trackerTimeline) {
  window.loadTrackerEntries = async function () {
    try {
      const response = await fetch('/api/tracker');
      const data = await response.json();

      trackerTimeline.innerHTML = '';
      if (!data.logs || data.logs.length === 0) {
        trackerTimeline.innerHTML = '<p>No tracker logs found.</p>';
        return;
      }

      data.logs.forEach((log) => {
        const card = document.createElement('div');
        let cardColorClass = 'low';
        if (log.mood === 'Bad') cardColorClass = 'high';
        else if (log.mood === 'Okay') cardColorClass = 'medium';

        let moodText = log.mood;
        if (window.translations && currentLang === 'hi') {
          if (log.mood === 'Great') moodText = 'बहुत अच्छा';
          else if (log.mood === 'Good') moodText = 'अच्छा';
          else if (log.mood === 'Okay') moodText = 'ठीक है';
          else if (log.mood === 'Bad') moodText = 'खराब';
        }

        const moodLabel = currentLang === 'hi' ? 'मनोदशा' : 'Mood';
        const sleepLabel = currentLang === 'hi' ? 'नींद' : 'Sleep';
        const waterLabel = currentLang === 'hi' ? 'पानी' : 'Water';
        const symptomsLabel = currentLang === 'hi' ? 'लक्षण' : 'Symptoms';
        const hLabel = currentLang === 'hi' ? 'घंटे' : 'h';
        const glassLabel = currentLang === 'hi' ? 'गिलास' : 'glasses';

        card.className = `patient glass tilt ${cardColorClass}`;
        card.innerHTML = `
          <h4>${new Date(log.timestamp).toLocaleDateString()}</h4>
          <p><strong>${moodLabel}:</strong> ${moodText}</p>
          <p><strong>${sleepLabel}:</strong> ${log.sleep_hours}${hLabel} | <strong>${waterLabel}:</strong> ${log.water_intake} ${glassLabel}</p>
          ${log.symptoms ? `<p><strong>${symptomsLabel}:</strong> ${log.symptoms}</p>` : ''}
        `;
        trackerTimeline.appendChild(card);
      });
    } catch (err) {
      console.error(err);
      trackerTimeline.innerHTML = '<p>❌ Failed to load tracker timeline.</p>';
    }
  }
  loadTrackerEntries();
}

// Auth Handlers (login.html)
const loginForm = document.getElementById('loginForm');
const signupForm = document.getElementById('signupForm');
const btnSwitchToSignup = document.getElementById('switchToSignup');
const btnSwitchToLogin = document.getElementById('switchToLogin');

if (btnSwitchToSignup) {
  btnSwitchToSignup.addEventListener('click', () => {
    document.getElementById('loginFormContainer').style.display = 'none';
    document.getElementById('signupFormContainer').style.display = 'block';
  });
}

if (btnSwitchToLogin) {
  btnSwitchToLogin.addEventListener('click', () => {
    document.getElementById('signupFormContainer').style.display = 'none';
    document.getElementById('loginFormContainer').style.display = 'block';
  });
}

if (loginForm) {
  loginForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const out = document.getElementById('loginOutput');
    out.textContent = "Logging in...";
    out.style.color = "var(--text)";

    try {
      const res = await fetch('/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          username: document.getElementById('loginUser').value,
          password: document.getElementById('loginPass').value
        })
      });
      const data = await res.json();
      if (data.status === 'success') {
        localStorage.setItem('userRole', data.role);
        out.style.color = '#32cd32';
        out.textContent = "Success! Redirecting...";
        setTimeout(() => {
          if (data.role === 'asha') window.location.href = 'dashboard.html';
          else window.location.href = 'index.html';
        }, 1000);
      } else {
        out.style.color = '#ff4d4d';
        out.textContent = data.message;
      }
    } catch (err) {
      out.style.color = '#ff4d4d';
      out.textContent = "Error logging in.";
    }
  });
}

if (signupForm) {
  signupForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const out = document.getElementById('signupOutput');
    out.textContent = "Creating account...";
    out.style.color = "var(--text)";

    try {
      const res = await fetch('/api/auth/signup', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          username: document.getElementById('signupUser').value,
          password: document.getElementById('signupPass').value,
          role: document.getElementById('signupRole').value
        })
      });
      const data = await res.json();
      if (data.status === 'success') {
        localStorage.setItem('userRole', data.role);
        out.style.color = '#32cd32';
        out.textContent = "Account created! Redirecting...";
        setTimeout(() => {
          if (data.role === 'asha') window.location.href = 'dashboard.html';
          else window.location.href = 'index.html';
        }, 1000);
      } else {
        out.style.color = '#ff4d4d';
        out.textContent = data.message;
      }
    } catch (err) {
      out.style.color = '#ff4d4d';
      out.textContent = "Error creating account.";
    }
  });
}
