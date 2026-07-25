const dropzone = document.getElementById('dropzone');
const fileInput = document.getElementById('file-input');
const dzContent = document.getElementById('dz-content');
const dzFile = document.getElementById('dz-file');
const fileNameEl = document.getElementById('file-name');
const runBtn = document.getElementById('run-btn');
const statusBox = document.getElementById('status');
const errorBox = document.getElementById('error-box');
const results = document.getElementById('results');
const frText = document.getElementById('fr-text');
const deText = document.getElementById('de-text');
const frCount = document.getElementById('fr-count');
const deCount = document.getElementById('de-count');
const downloadBtn = document.getElementById('download-btn');

let selectedFile = null;

dropzone.addEventListener('click', () => fileInput.click());

['dragover', 'dragenter'].forEach(evt =>
  dropzone.addEventListener(evt, e => {
    e.preventDefault();
    dropzone.classList.add('drag-over');
  })
);
['dragleave', 'drop'].forEach(evt =>
  dropzone.addEventListener(evt, e => {
    e.preventDefault();
    dropzone.classList.remove('drag-over');
  })
);
dropzone.addEventListener('drop', e => {
  const file = e.dataTransfer.files[0];
  if (file) setFile(file);
});
fileInput.addEventListener('change', () => {
  if (fileInput.files[0]) setFile(fileInput.files[0]);
});

function setFile(file) {
  selectedFile = file;
  fileNameEl.textContent = file.name;
  dzContent.hidden = true;
  dzFile.hidden = false;
  runBtn.disabled = false;
  hideError();
}

function hideError() {
  errorBox.hidden = true;
  errorBox.textContent = '';
}

function showError(msg) {
  errorBox.hidden = false;
  errorBox.textContent = msg;
}

function setStep(step) {
  const order = ['audio', 'transcribe', 'translate'];
  const idx = order.indexOf(step);
  document.querySelectorAll('.status-line').forEach(line => {
    const lineIdx = order.indexOf(line.dataset.step);
    line.classList.remove('active', 'done');
    if (lineIdx < idx) line.classList.add('done');
    if (lineIdx === idx) line.classList.add('active');
  });
}

runBtn.addEventListener('click', async () => {
  if (!selectedFile) return;
  hideError();
  results.hidden = true;
  runBtn.disabled = true;
  statusBox.hidden = false;
  setStep('audio');

  const formData = new FormData();
  formData.append('video', selectedFile);

  // Progression simulée pour les deux premières étapes (le backend est synchrone)
  const t1 = setTimeout(() => setStep('transcribe'), 1200);

  try {
    const res = await fetch('/api/process', { method: 'POST', body: formData });
    clearTimeout(t1);
    setStep('translate');
    const data = await res.json();

    if (!res.ok) {
      throw new Error(data.error || 'Une erreur inconnue est survenue.');
    }

    frText.textContent = data.french;
    deText.textContent = data.german;
    frCount.textContent = `${data.french_word_count} mots`;
    deCount.textContent = `${data.german_word_count} mots`;

    results.hidden = false;
    statusBox.hidden = true;
  } catch (err) {
    statusBox.hidden = true;
    showError(err.message);
  } finally {
    runBtn.disabled = false;
  }
});

document.querySelectorAll('[data-copy]').forEach(btn => {
  btn.addEventListener('click', () => {
    const el = document.getElementById(btn.dataset.copy);
    navigator.clipboard.writeText(el.textContent);
    const original = btn.textContent;
    btn.textContent = 'Copié !';
    setTimeout(() => (btn.textContent = original), 1200);
  });
});

downloadBtn.addEventListener('click', () => {
  const blob = new Blob([deText.textContent], { type: 'text/plain;charset=utf-8' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = 'script-allemand.txt';
  a.click();
  URL.revokeObjectURL(url);
});
