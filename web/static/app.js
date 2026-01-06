let jobId = null;
let pollTimer = null;

const elFile = document.getElementById('file');
const btnUpload = document.getElementById('btnUpload');
const btnValidate = document.getElementById('btnValidate');
const btnSend = document.getElementById('btnSend');
const btnDownload = document.getElementById('btnDownload');

const elJobId = document.getElementById('jobId');
const elJobStatus = document.getElementById('jobStatus');
const elJobProgress = document.getElementById('jobProgress');
const elMessages = document.getElementById('messages');
const elErrors = document.getElementById('errors');

function msg(text) {
  const div = document.createElement('div');
  div.className = 'msg';
  div.textContent = text;
  elMessages.prepend(div);
}

function clearErrors() {
  elErrors.innerHTML = '';
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
}

function setStatus(job) {
  elJobId.textContent = job.job_id || '-';
  elJobStatus.textContent = job.status || '-';
  const total = job.total ?? 0;
  const done = (job.success ?? 0) + (job.errors_count ?? 0);
  elJobProgress.textContent = total ? `${done}/${total}` : '-';

  if (job.status === 'validated') {
    btnSend.disabled = false;
  }

  if (job.status === 'completed' || job.status === 'failed') {
    if (pollTimer) {
      clearInterval(pollTimer);
      pollTimer = null;
    }

    if (job.log_path) {
      btnDownload.href = `/download-log/${job.job_id}`;
      btnDownload.style.display = 'inline-block';
    }
  }
}

async function fetchJob() {
  if (!jobId) return;
  const r = await fetch(`/job/${jobId}`);
  if (!r.ok) return;
  const job = await r.json();
  setStatus(job);

  if (job.validation_errors && job.validation_errors.length > 0) {
    showErrors(job.validation_errors);
  }

  if (job.import_errors && job.import_errors.length > 0) {
    showErrors(job.import_errors);
  }
}

function startPolling() {
  if (pollTimer) return;
  pollTimer = setInterval(fetchJob, 1200);
}

elFile.addEventListener('change', () => {
  btnUpload.disabled = !(elFile.files && elFile.files.length);
});

btnUpload.addEventListener('click', async () => {
  clearErrors();
  btnValidate.disabled = true;
  btnSend.disabled = true;
  btnDownload.style.display = 'none';

  const f = elFile.files[0];
  const fd = new FormData();
  fd.append('file', f);

  const r = await fetch('/upload', { method: 'POST', body: fd });
  if (!r.ok) {
    msg('Falha no upload');
    return;
  }

  const data = await r.json();
  jobId = data.job_id;
  elJobId.textContent = jobId;
  msg(`Arquivo carregado. job_id=${jobId}`);
  btnValidate.disabled = false;
  startPolling();
  await fetchJob();
});

btnValidate.addEventListener('click', async () => {
  clearErrors();
  btnValidate.disabled = true;
  btnSend.disabled = true;
  const fd = new FormData();
  fd.append('job_id', jobId);

  const r = await fetch('/validate', { method: 'POST', body: fd });
  const data = await r.json();

  if (!r.ok) {
    msg('Erro ao validar');
    btnValidate.disabled = false;
    return;
  }

  if (data.errors && data.errors.length > 0) {
    msg('Validação concluída com avisos (não impede o envio).');
    showErrors(data.errors);
  } else {
    msg('Validação OK. Você já pode enviar.');
  }

  btnSend.disabled = false;
  await fetchJob();
});

btnSend.addEventListener('click', async () => {
  clearErrors();
  btnSend.disabled = true;
  const fd = new FormData();
  fd.append('job_id', jobId);

  const r = await fetch('/import', { method: 'POST', body: fd });
  if (!r.ok) {
    msg('Erro ao iniciar importação');
    btnSend.disabled = false;
    return;
  }

  msg('Importação iniciada. Acompanhe o status.');
  startPolling();
  await fetchJob();
});
