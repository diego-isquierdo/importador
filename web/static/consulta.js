let pollTimer = null;
let currentJobId = null;
let currentMode = 'single';

const tabSingle = document.getElementById('tabSingle');
const tabBatch = document.getElementById('tabBatch');
const panelSingle = document.getElementById('panelSingle');
const panelBatch = document.getElementById('panelBatch');

const elMessages = document.getElementById('messages');
const elErrors = document.getElementById('errors');
const elResults = document.getElementById('results');

const elMessagesCard = document.getElementById('messagesCard');
const elErrorsCard = document.getElementById('errorsCard');
let hideValidationTimer = null;

const singleWorkflow = document.getElementById('singleWorkflow');
const btnSingleSearch = document.getElementById('btnSingleSearch');

const singleJobId = document.getElementById('singleJobId');
const singleJobStatus = document.getElementById('singleJobStatus');
const singleJobProgress = document.getElementById('singleJobProgress');

const batchFile = document.getElementById('batchFile');
const btnBatchUpload = document.getElementById('btnBatchUpload');
const btnBatchValidate = document.getElementById('btnBatchValidate');
const btnBatchRun = document.getElementById('btnBatchRun');

const batchJobId = document.getElementById('batchJobId');
const batchJobStatus = document.getElementById('batchJobStatus');
const batchJobProgress = document.getElementById('batchJobProgress');

function msg(text) {
  const div = document.createElement('div');
  div.className = 'msg';
  div.textContent = text;
  elMessages.prepend(div);
  showValidationCards();
  scheduleHideValidationCards();
}

function clearErrors() {
  elErrors.innerHTML = '';
}

function clearMessages() {
  elMessages.innerHTML = '';
}

function showValidationCards() {
  if (elMessagesCard) elMessagesCard.style.display = '';
  if (elErrorsCard) elErrorsCard.style.display = '';
}

function hideValidationCards() {
  if (elMessagesCard) elMessagesCard.style.display = 'none';
  if (elErrorsCard) elErrorsCard.style.display = 'none';
}

function cancelHideValidationCards() {
  if (hideValidationTimer) {
    clearTimeout(hideValidationTimer);
    hideValidationTimer = null;
  }
}

function scheduleHideValidationCards() {
  cancelHideValidationCards();
  if (currentMode !== 'single') return;
  hideValidationTimer = setTimeout(() => {
    hideValidationCards();
  }, 10000);
}

function clearResults() {
  elResults.innerHTML = '';
}

function showErrors(errors) {
  elErrors.innerHTML = '';
  if (!errors || errors.length === 0) return;
  for (const e of errors) {
    const div = document.createElement('div');
    div.className = 'err';
    div.textContent = `Linha ${e.line} - ${e.column}: ${e.message}`;
    elErrors.appendChild(div);
  }
  showValidationCards();
  scheduleHideValidationCards();
}

function setMode(mode) {
  currentMode = mode;
  clearErrors();
  clearResults();
  clearMessages();
  showValidationCards();
  cancelHideValidationCards();
  if (mode === 'single') {
    panelSingle.style.display = 'block';
    panelBatch.style.display = 'none';
    tabSingle.className = 'btn btn--primary';
    tabBatch.className = 'btn';
  } else {
    panelSingle.style.display = 'none';
    panelBatch.style.display = 'block';
    tabSingle.className = 'btn';
    tabBatch.className = 'btn btn--primary';
  }
}

tabSingle.addEventListener('click', () => setMode('single'));
tabBatch.addEventListener('click', () => setMode('batch'));

function startPolling() {
  if (pollTimer) return;
  pollTimer = setInterval(fetchJob, 1200);
}

function stopPolling() {
  if (!pollTimer) return;
  clearInterval(pollTimer);
  pollTimer = null;
}

function normalizeTicket(t) {
  return {
    platform: t.platform,
    id: t.id,
    subject: t.subject,
    status: t.status,
    serviceFirstLevel: t.serviceFirstLevel,
    serviceSecondLevel: t.serviceSecondLevel,
    lastActionDate: t.lastActionDate,
  };
}

function isClosedStatus(status) {
  const s = (status || '').toString().trim().toLowerCase();
  return s === 'fechado' || s === 'resolvido';
}

async function fetchTicketDetail(platform, id) {
  const url = `/consulta/ticket-detail?platform=${encodeURIComponent(platform)}&id=${encodeURIComponent(id)}`;
  const r = await fetch(url);
  const data = await r.json();
  if (!r.ok) {
    throw new Error(data.detail || 'Erro ao buscar detalhe');
  }
  if (data.descriptions && Array.isArray(data.descriptions)) {
    return data.descriptions;
  }
  if (typeof data.description === 'string') {
    return data.description ? [data.description] : [];
  }
  return [];
}

function renderResults(results) {
  elResults.innerHTML = '';
  if (!results || results.length === 0) return;

  for (const raw of results) {
    const t = normalizeTicket(raw);

    const row = document.createElement('div');
    row.className = 'msg';
    row.style.cursor = 'pointer';

    const header = document.createElement('div');
    const statusClass = isClosedStatus(t.status) ? 'statusText--ok' : 'statusText--bad';
    const statusText = (t.status || '').toString();
    header.innerHTML = `<strong>${t.lastActionDate || ''}</strong> | ${t.serviceSecondLevel || ''} | ${t.serviceFirstLevel || ''} | <span class="statusText ${statusClass}">${statusText}</span> | ${t.subject || ''} | #${t.id}`;

    const detail = document.createElement('div');
    detail.style.display = 'none';
    detail.style.marginTop = '8px';
    detail.style.whiteSpace = 'pre-wrap';

    row.appendChild(header);
    row.appendChild(detail);

    row.addEventListener('click', async () => {
      if (detail.style.display === 'block') {
        detail.style.display = 'none';
        return;
      }

      if (detail.textContent && detail.textContent.trim()) {
        detail.style.display = 'block';
        return;
      }

      detail.textContent = 'Carregando...';
      detail.style.display = 'block';

      try {
        const descs = await fetchTicketDetail(t.platform, t.id);
        if (!descs || descs.length === 0) {
          detail.textContent = '(sem descrição)';
        } else {
          detail.textContent = descs.join('\n\n---\n\n');
        }
      } catch (e) {
        detail.textContent = e.message || 'Erro ao carregar detalhe';
      }
    });

    elResults.appendChild(row);
  }
}

function setStatus(job) {
  const total = job.total ?? 0;
  const done = job.processed ?? 0;

  if (currentMode === 'single') {
    singleJobId.textContent = job.job_id || '-';
    singleJobStatus.textContent = job.status || '-';
    singleJobProgress.textContent = total ? `${done}/${total}` : '-';
  } else {
    batchJobId.textContent = job.job_id || '-';
    batchJobStatus.textContent = job.status || '-';
    batchJobProgress.textContent = total ? `${done}/${total}` : '-';
  }

  if (job.validation_errors && job.validation_errors.length > 0) {
    showErrors(job.validation_errors);
  }
  if (job.line_errors && job.line_errors.length > 0) {
    showErrors(job.line_errors);
  }

  if (job.results) {
    renderResults(job.results);
  }

  if (job.status === 'completed' || job.status === 'failed') {
    stopPolling();
    if (job.status === 'completed' && (!job.results || job.results.length === 0)) {
      msg('Nenhum ticket encontrado...');
    }
    if (job.status === 'failed') {
      msg(job.detail || 'Falha no processamento');
    }
  }
}

async function fetchJob() {
  if (!currentJobId) return;
  const url = `/consulta/job/${currentJobId}`;
  const r = await fetch(url);
  if (!r.ok) return;
  const job = await r.json();
  setStatus(job);
}

btnSingleSearch.addEventListener('click', async () => {
  clearErrors();
  clearMessages();
  showValidationCards();
  cancelHideValidationCards();
  clearResults();
  const workflow = (singleWorkflow.value || '').trim();
  const baseEl = document.querySelector('input[name="singleBase"]:checked');
  const base = baseEl ? (baseEl.value || '').trim() : '';
  if (!workflow) {
    showErrors([{ line: 0, column: 'workflow', message: 'workflow é obrigatório' }]);
    return;
  }
  if (!base) {
    showErrors([{ line: 0, column: 'base', message: 'base é obrigatória' }]);
    return;
  }

  const fd = new FormData();
  fd.append('workflow', workflow);
  fd.append('base', base);

  const r = await fetch('/consulta/search', { method: 'POST', body: fd });
  const data = await r.json();
  if (!r.ok) {
    msg(data.detail || 'Erro ao consultar');
    return;
  }

  currentMode = 'single';
  currentJobId = data.job_id;
  singleJobId.textContent = currentJobId;
  msg('Consulta iniciada. Acompanhe o status.');
  startPolling();
  await fetchJob();
});

batchFile.addEventListener('change', () => {
  btnBatchUpload.disabled = !(batchFile.files && batchFile.files.length);
});

btnBatchUpload.addEventListener('click', async () => {
  clearErrors();
  clearMessages();
  showValidationCards();
  cancelHideValidationCards();
  clearResults();
  btnBatchValidate.disabled = true;
  btnBatchRun.disabled = true;

  const f = batchFile.files[0];
  const fd = new FormData();
  fd.append('file', f);

  const r = await fetch('/consulta/upload', { method: 'POST', body: fd });
  const data = await r.json();
  if (!r.ok) {
    msg(data.detail || 'Falha no upload');
    return;
  }

  currentMode = 'batch';
  currentJobId = data.job_id;
  batchJobId.textContent = currentJobId;
  msg(`Arquivo carregado. job_id=${currentJobId}`);
  btnBatchValidate.disabled = false;
  startPolling();
  await fetchJob();
});

btnBatchValidate.addEventListener('click', async () => {
  clearErrors();
  clearMessages();
  showValidationCards();
  cancelHideValidationCards();
  btnBatchValidate.disabled = true;
  btnBatchRun.disabled = true;

  const fd = new FormData();
  fd.append('job_id', currentJobId);

  const r = await fetch('/consulta/validate', { method: 'POST', body: fd });
  const data = await r.json();
  if (!r.ok) {
    msg(data.detail || 'Erro ao validar');
    btnBatchValidate.disabled = false;
    return;
  }

  if (data.errors && data.errors.length > 0) {
    msg('Validação concluída com avisos (linhas inválidas não serão consultadas).');
    showErrors(data.errors);
  } else {
    msg('Validação OK. Você já pode consultar.');
  }

  btnBatchRun.disabled = false;
  await fetchJob();
});

btnBatchRun.addEventListener('click', async () => {
  clearErrors();
  clearMessages();
  hideValidationCards();
  cancelHideValidationCards();
  btnBatchRun.disabled = true;

  const fd = new FormData();
  fd.append('job_id', currentJobId);

  const r = await fetch('/consulta/run', { method: 'POST', body: fd });
  const data = await r.json();
  if (!r.ok) {
    msg(data.detail || 'Erro ao iniciar consulta');
    btnBatchRun.disabled = false;
    return;
  }

  msg('Consulta em lote iniciada. Acompanhe o status.');
  startPolling();
  await fetchJob();
});

setMode('single');
