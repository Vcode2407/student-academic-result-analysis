const subjects = ["Python", "Algorithms", "Network Security", "Database"];
let records = [];
let selected = null;

function escapeHtml(value) {
  return String(value).replace(/[&<>"']/g, char => ({"&":"&amp;","<":"&lt;",">":"&gt;","\"":"&quot;","'":"&#39;"})[char]);
}

async function getJson(url, options) {
  const response = await fetch(url, options);
  const data = await response.json();
  if (!response.ok) throw new Error(data.error || "Something went wrong.");
  return data;
}

function renderRecords() {
  const body = document.querySelector("#records-body");
  if (!records.length) {
    body.innerHTML = '<tr><td colspan="5">No students yet. Enter marks to add one.</td></tr>';
    return;
  }
  body.innerHTML = records.map(({registration, result}) => `
    <tr data-id="${escapeHtml(registration)}" class="${selected === registration ? "selected" : ""}" tabindex="0">
      <td>${escapeHtml(registration)}</td><td>${result.total.toFixed(0)} / 400</td>
      <td>${result.percentage.toFixed(1)}%</td><td>${escapeHtml(result.grade)}</td>
      <td><span class="status ${result.status === "Fail" ? "fail" : ""}">${escapeHtml(result.status)}</span></td>
    </tr>`).join("");
  body.querySelectorAll("tr[data-id]").forEach(row => {
    row.addEventListener("click", () => showResult(row.dataset.id));
    row.addEventListener("keydown", event => {
      if (event.key === "Enter" || event.key === " ") { event.preventDefault(); showResult(row.dataset.id); }
    });
  });
}

function showResult(registration) {
  const record = records.find(item => item.registration === registration);
  if (!record) return;
  selected = registration;
  renderRecords();
  const {marks, result} = record;
  document.querySelector("#detail-content").className = "";
  document.querySelector("#detail-content").innerHTML = `
    <div class="result-grid">
      <div class="result-tile"><span>REGISTRATION</span><strong>${escapeHtml(registration)}</strong></div>
      <div class="result-tile"><span>TOTAL MARKS</span><strong>${result.total.toFixed(0)} / 400</strong></div>
      <div class="result-tile"><span>PERCENTAGE</span><strong>${result.percentage.toFixed(1)}%</strong></div>
      <div class="result-tile"><span>GRADE / STATUS</span><strong>${escapeHtml(result.grade)} · ${escapeHtml(result.status)}</strong></div>
    </div>
    <p class="chart-title">Subject performance</p>
    ${subjects.map(subject => `<div class="bar-row"><span>${subject}</span><div class="bar-track"><div class="bar-fill" style="width:${marks[subject]}%"></div></div><b>${Number(marks[subject]).toFixed(0)}</b></div>`).join("")}`;
}

function renderSummary(summary) {
  const area = document.querySelector("#analysis-content");
  if (!summary) {
    area.className = "empty-state";
    area.textContent = "Add a student to see the class analysis.";
    return;
  }
  area.className = "";
  area.innerHTML = `
    <p class="analysis-note">Average mark in each subject, based on ${summary.students} saved student${summary.students === 1 ? "" : "s"}.</p>
    ${subjects.map(subject => `<div class="bar-row"><span>${subject}</span><div class="bar-track"><div class="bar-fill" style="width:${summary.subject_averages[subject]}%"></div></div><b>${summary.subject_averages[subject].toFixed(1)}</b></div>`).join("")}
    <p class="analysis-highest">Highest total: <strong>${summary.highest_total.toFixed(0)} / 400</strong> · ${summary.highest_students.map(escapeHtml).join(", ")}</p>`;
}

function renderComparison() {
  const area = document.querySelector("#comparison-content");
  if (records.length < 2) {
    area.className = "empty-state";
    area.textContent = "Add at least two students to compare their results.";
    return;
  }
  area.className = "";
  const ranked = [...records].sort((a, b) => b.result.percentage - a.result.percentage);
  const failures = ranked.flatMap(({registration, marks, result}) => {
    if (result.status !== "Fail") return [];
    const low = subjects.filter(subject => marks[subject] < 40);
    return [`${registration} fails because ${low.map(subject => `${subject} (${marks[subject]})`).join(", ")} ${low.length === 1 ? "is" : "are"} below 40.`];
  });
  const demoNote = ranked.some(({registration}) => registration.startsWith("DEMO_"))
    ? "DEMO records use sample marks." : "";
  area.innerHTML = `
    <p class="analysis-note">Ranked by percentage. Pass or fail still depends on every subject mark.</p>
    ${ranked.map(({registration, result}) => `
      <div class="compare-row">
        <strong>${escapeHtml(registration)}</strong>
        <div class="bar-track"><div class="bar-fill ${result.status === "Fail" ? "fail-bar" : ""}" style="width:${result.percentage}%"></div></div>
        <b>${result.percentage.toFixed(1)}%</b>
        <span class="status ${result.status === "Fail" ? "fail" : ""}">${escapeHtml(result.grade)} · ${escapeHtml(result.status)}</span>
      </div>`).join("")}
    <p class="comparison-note">Highest result: <strong>${escapeHtml(ranked[0].registration)}</strong> with ${ranked[0].result.percentage.toFixed(1)}%.
    ${failures.map(escapeHtml).join(" ")} ${demoNote}</p>`;
}

async function refresh() {
  records = await getJson("/api/records");
  const summary = await getJson("/api/summary");
  document.querySelector("#stat-students").textContent = summary ? summary.students : 0;
  document.querySelector("#stat-average").textContent = summary ? `${summary.class_average.toFixed(1)}%` : "—";
  document.querySelector("#stat-pass").textContent = summary ? `${summary.pass_percentage.toFixed(1)}%` : "—";
  renderSummary(summary);
  renderComparison();
  renderRecords();
  if (selected) showResult(selected);
}

document.querySelector("#student-form").addEventListener("submit", async event => {
  event.preventDefault();
  const form = event.currentTarget;
  const message = document.querySelector("#form-message");
  message.className = "form-message";
  const marks = Object.fromEntries(subjects.map(subject => [subject, form.elements.namedItem(subject).value]));
  try {
    const saved = await getJson("/api/records", {
      method: "POST", headers: {"Content-Type": "application/json"},
      body: JSON.stringify({registration: form.registration.value, marks})
    });
    message.textContent = "Student saved successfully.";
    message.classList.add("success");
    form.reset();
    await refresh();
    showResult(saved.registration);
  } catch (error) {
    message.textContent = error.message;
  }
});

refresh().catch(error => {
  document.querySelector("#records-body").innerHTML = `<tr><td colspan="5">${escapeHtml(error.message)}</td></tr>`;
});
