from __future__ import annotations


BASE_CSS = """
:root{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;color:#20231f;background:#f5f6f3}
*{box-sizing:border-box}body{margin:0}a{color:#146b5c}button,input,textarea,select{font:inherit}
button{border:0;border-radius:6px;background:#176d5e;color:#fff;padding:10px 14px;cursor:pointer}
button.secondary{background:#e8ece6;color:#20231f}button.danger{background:#a33a32}button:disabled{opacity:.55}
input,textarea,select{width:100%;border:1px solid #bbc4b5;border-radius:6px;padding:10px;background:#fff}
textarea{min-height:120px;resize:vertical}.shell{min-height:100vh}.nav{height:58px;background:#fff;border-bottom:1px solid #d9ddd4;display:flex;align-items:center;padding:0 22px;gap:18px}
.brand{font-weight:750;color:#20231f;text-decoration:none}.nav a{color:#4d574e;text-decoration:none}.nav .spacer{flex:1}
main{width:min(980px,calc(100vw - 28px));margin:26px auto 60px}.panel{background:#fff;border:1px solid #d9ddd4;border-radius:8px;padding:18px;margin-bottom:16px}
h1{font-size:26px;margin:0 0 6px}h2{font-size:18px;margin:0 0 14px}.muted{color:#687169;font-size:14px}.error{color:#a33a32}.ok{color:#176d5e}
.grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px}.field{display:grid;gap:6px}.actions{display:flex;gap:10px;align-items:center;flex-wrap:wrap;margin-top:14px}
.hidden{display:none!important}.calendar-chip{display:inline-flex;align-items:center;gap:7px}.dot{width:10px;height:10px;border-radius:50%}
.agenda-day{margin:22px 0 10px;font-size:16px}.event-row{display:grid;grid-template-columns:110px 12px 1fr auto;gap:12px;align-items:start;padding:14px 0;border-bottom:1px solid #ecefe9}
.subscription{display:grid;gap:8px;background:#f7f8f5;padding:12px;border-radius:6px}.url{word-break:break-all;font-family:ui-monospace,monospace;font-size:13px}
.auth{width:min(420px,calc(100vw - 28px));margin:10vh auto}.auth .panel{padding:24px}.calendar-card{border-top:1px solid #e4e8e1;padding:16px 0}
dialog{border:1px solid #d9ddd4;border-radius:8px;padding:0;width:min(620px,calc(100vw - 28px));box-shadow:0 18px 60px rgba(0,0,0,.2)}
dialog::backdrop{background:rgba(20,26,22,.38)}dialog .panel{margin:0;border:0}
@media(max-width:700px){.grid{grid-template-columns:1fr}.nav{padding:0 12px;gap:10px}.nav a:not(.brand){font-size:13px}.event-row{grid-template-columns:80px 10px 1fr}.event-row .actions{grid-column:3}}
"""


COMMON_JS = """
async function api(url, options={}) {
  const response = await fetch(url, {credentials:"same-origin", ...options});
  if (response.status === 401) { window.location.href="/login"; throw new Error("Authentication required"); }
  if (response.status === 204) return null;
  const data = await response.json();
  if (!response.ok) throw new Error(formatError(data.detail));
  return data;
}
function formatError(detail){
  if (typeof detail === "string") return detail;
  if (Array.isArray(detail)) return detail.map(item => item.msg || item.message || String(item)).join("; ");
  if (detail && typeof detail === "object") return detail.msg || detail.message || JSON.stringify(detail);
  return "Request failed";
}
async function logout(){await api("/api/auth/logout",{method:"POST"});window.location.href="/login"}
function esc(value){return String(value ?? "").replace(/[&<>"']/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;","\\"":"&quot;","'":"&#039;"}[c]))}
function localInput(value){const d=new Date(value),o=d.getTimezoneOffset()*60000;return new Date(d-o).toISOString().slice(0,16)}
function iso(value){return new Date(value).toISOString()}
async function copyText(value, target){await navigator.clipboard.writeText(value);target.textContent="Copied";setTimeout(()=>target.textContent="Copy",1400)}
const $ = (id) => document.getElementById(id);
"""


def layout(title: str, body: str, script: str, nav: bool = True) -> str:
    navigation = """
    <nav class="nav"><a class="brand" href="/">Calendar Maker</a><a href="/">Create</a>
    <a href="/agenda">Agenda</a><a href="/calendars">Calendars</a><span class="spacer"></span>
    <button class="secondary" onclick="logout()">Log out</button></nav>
    """ if nav else ""
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
    <meta name="viewport" content="width=device-width,initial-scale=1"><title>{title}</title>
    <style>{BASE_CSS}</style></head><body><div class="shell">{navigation}{body}</div>
    <script>{COMMON_JS}{script}</script></body></html>"""


def login_page() -> str:
    return layout("Log in", """
    <main class="auth"><section class="panel"><h1>Log in</h1><p class="muted">Open your calendars and agenda.</p>
    <div class="field"><label>Email</label><input id="email" type="email" autocomplete="email"></div>
    <div class="field"><label>Password</label><input id="password" type="password" autocomplete="current-password"></div>
    <div class="actions"><button id="submit">Log in</button><a href="/register">Create account</a><span id="status"></span></div>
    </section></main>""", """
    const emailInput=$("email"),passwordInput=$("password"),submitButton=$("submit"),statusText=$("status");
    submitButton.onclick=async()=>{try{await api("/api/auth/login",{method:"POST",headers:{"Content-Type":"application/json"},
    body:JSON.stringify({email:emailInput.value,password:passwordInput.value})});location.href="/"}catch(e){statusText.textContent=e.message;statusText.className="error"}};
    """, nav=False)


def register_page() -> str:
    return layout("Create account", """
    <main class="auth"><section class="panel"><h1>Create account</h1><p class="muted">Registration requires a single-use invite code.</p>
    <div class="field"><label>Email</label><input id="email" type="email" autocomplete="email"></div>
    <div class="field"><label>Password</label><input id="password" type="password" autocomplete="new-password"></div>
    <div class="field"><label>Invite code</label><input id="invite" autocomplete="off"></div>
    <div class="actions"><button id="submit">Create account</button><a href="/login">Log in</a><span id="status"></span></div>
    </section></main>""", """
    const emailInput=$("email"),passwordInput=$("password"),inviteInput=$("invite"),submitButton=$("submit"),statusText=$("status");
    submitButton.onclick=async()=>{try{await api("/api/auth/register",{method:"POST",headers:{"Content-Type":"application/json"},
    body:JSON.stringify({email:emailInput.value,password:passwordInput.value,invite_code:inviteInput.value})});location.href="/"}catch(e){statusText.textContent=e.message;statusText.className="error"}};
    """, nav=False)


def maker_page() -> str:
    return layout("Create event", """
    <main><h1>Create an event</h1><p class="muted">Describe it naturally, review every field, then confirm.</p>
    <section class="panel"><div class="field"><label>Event description</label>
    <textarea id="source" placeholder="Lunch with Mei next Tuesday at 12:30 near the office, about 90 minutes"></textarea></div>
    <div class="grid"><div class="field"><label>Preferred calendar</label><select id="preferred"></select></div></div>
    <div class="actions"><button id="parse">Compile event</button><span id="parseStatus" class="muted"></span></div></section>
    <section id="draft" class="panel hidden"><h2>Review event</h2><p id="recommendation" class="muted"></p>
    <div id="proposal" class="subscription hidden"></div>
    <div class="grid"><div class="field"><label>Title</label><input id="title"></div>
    <div class="field"><label>Calendar</label><select id="calendar"></select></div>
    <div class="field"><label>Start</label><input id="start" type="datetime-local"></div>
    <div class="field"><label>End</label><input id="end" type="datetime-local"></div>
    <div class="field"><label>Location</label><input id="location"></div>
    <div class="field"><label>Timezone</label><input id="timezone"></div></div>
    <div class="field"><label>Notes</label><textarea id="description"></textarea></div>
    <div class="actions"><button id="confirm">Confirm event</button><span id="confirmStatus"></span></div></section></main>
    """, """
    let calendars=[],eventId=null,proposed=null;
    const sourceInput=$("source"),preferredSelect=$("preferred"),parseButton=$("parse"),parseStatusText=$("parseStatus");
    const draftPanel=$("draft"),recommendationText=$("recommendation"),proposalBox=$("proposal"),titleInput=$("title");
    const calendarSelect=$("calendar"),startInput=$("start"),endInput=$("end"),locationInput=$("location");
    const timezoneInput=$("timezone"),descriptionInput=$("description"),confirmButton=$("confirm"),confirmStatusText=$("confirmStatus");
    function options(selected){return calendars.map(c=>`<option value="${c.id}" ${c.id===selected?"selected":""}>${esc(c.name)}</option>`).join("")}
    async function load(){const data=await api("/api/calendars");calendars=data.calendars;preferredSelect.innerHTML='<option value="">Let AI choose</option>'+options();calendarSelect.innerHTML=options()}
    parseButton.onclick=async()=>{parseButton.disabled=true;parseStatusText.textContent="Compiling...";
      try{const data=await api("/api/parse",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({
      text:sourceInput.value,preferred_calendar_id:preferredSelect.value?Number(preferredSelect.value):null})});eventId=data.event.id;proposed=data.proposed_calendar;
      titleInput.value=data.event.title;startInput.value=localInput(data.event.start);endInput.value=localInput(data.event.end);locationInput.value=data.event.location||"";
      timezoneInput.value=data.event.timezone;descriptionInput.value=data.event.description||"";calendarSelect.innerHTML=options(data.event.calendar_id);
      recommendationText.textContent=data.recommendation_reason?`AI suggestion: ${data.recommendation_reason} (${Math.round(data.recommendation_confidence*100)}%)`:"";
      if(proposed){proposalBox.classList.remove("hidden");proposalBox.innerHTML=`No existing calendar fits well. Suggested: <strong>${esc(proposed.name)}</strong>
      <button class="secondary" id="createSuggested">Create calendar</button>`;$("createSuggested").onclick=createProposed}else proposalBox.classList.add("hidden");
      draftPanel.classList.remove("hidden");parseStatusText.textContent="Review the result";}catch(e){parseStatusText.textContent=e.message;parseStatusText.className="error"}finally{parseButton.disabled=false}};
    async function createProposed(){const data=await api("/api/calendars",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(proposed)});
      calendars.push(data.calendar);calendarSelect.innerHTML=options(data.calendar.id);preferredSelect.innerHTML='<option value="">Let AI choose</option>'+options();proposalBox.classList.add("hidden")}
    confirmButton.onclick=async()=>{confirmButton.disabled=true;try{await api(`/api/events/${eventId}/confirm`,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({
      calendar_id:Number(calendarSelect.value),title:titleInput.value,start:iso(startInput.value),end:iso(endInput.value),timezone:timezoneInput.value,
      location:locationInput.value||null,description:descriptionInput.value||null})});draftPanel.querySelectorAll("input,textarea,select,button").forEach(x=>x.disabled=true);
      confirmStatusText.textContent="Added to calendar";confirmStatusText.className="ok";sourceInput.value="";parseStatusText.textContent="Ready for another event"}catch(e){confirmButton.disabled=false;confirmStatusText.textContent=e.message;confirmStatusText.className="error"}};
    load();
    """)


def agenda_page() -> str:
    return layout("Agenda", """
    <main><h1>All-calendar agenda</h1><p class="muted">Upcoming events across your calendars.</p>
    <section class="panel"><div class="grid"><div class="field"><label>Calendar</label><select id="filter"></select></div>
    <div class="field"><label><input id="past" type="checkbox" style="width:auto"> Include past events</label></div></div></section>
    <section class="panel" id="agenda"></section>
    <dialog id="editor"><section class="panel"><h2>Edit event</h2><div class="grid">
    <div class="field"><label>Title</label><input id="editTitle"></div><div class="field"><label>Calendar</label><select id="editCalendar"></select></div>
    <div class="field"><label>Start</label><input id="editStart" type="datetime-local"></div><div class="field"><label>End</label><input id="editEnd" type="datetime-local"></div>
    <div class="field"><label>Location</label><input id="editLocation"></div><div class="field"><label>Timezone</label><input id="editTimezone"></div></div>
    <div class="field"><label>Notes</label><textarea id="editDescription"></textarea></div>
    <div class="actions"><button id="saveEdit">Save</button><button class="secondary" id="cancelEdit">Cancel</button><span id="editStatus"></span></div>
    </section></dialog></main>
    """, """
    let calendars=[],editing=null;
    function eventBody(e,c){return `<div class="event-row" data-id="${e.id}"><div>${new Date(e.start).toLocaleTimeString([],{hour:"2-digit",minute:"2-digit"})}</div>
    <span class="dot" style="background:${c.color}"></span><div><strong>${esc(e.title)}</strong><div class="muted">${esc(c.name)}${e.location?" · "+esc(e.location):""}</div>
    <div>${esc(e.description||"")}</div></div><div class="actions"><button class="secondary edit">Edit</button><button class="danger delete">Delete</button></div></div>`}
    async function load(){const c=await api("/api/calendars");calendars=c.calendars;filter.innerHTML='<option value="">All calendars</option>'+calendars.map(x=>`<option value="${x.id}">${esc(x.name)}</option>`).join("");
    await loadAgenda()}
    async function loadAgenda(){const q=new URLSearchParams({include_past:String(past.checked)});if(filter.value)q.set("calendar_id",filter.value);
      const data=await api("/api/agenda?"+q);let html="",day="";
      for(const e of data.events){const d=new Date(e.start).toLocaleDateString([],{weekday:"long",month:"long",day:"numeric"});if(d!==day){day=d;html+=`<h2 class="agenda-day">${d}</h2>`}
      html+=eventBody(e,calendars.find(c=>c.id===e.calendar_id))}agenda.innerHTML=html||'<p class="muted">No events in this range.</p>';
      agenda.querySelectorAll(".delete").forEach(b=>b.onclick=async()=>{await api(`/api/events/${b.closest(".event-row").dataset.id}`,{method:"DELETE"});loadAgenda()});
      agenda.querySelectorAll(".edit").forEach(b=>b.onclick=()=>openEditor(b.closest(".event-row").dataset.id,data.events))}
    function openEditor(id,events){editing=events.find(x=>x.id===Number(id));editTitle.value=editing.title;editStart.value=localInput(editing.start);editEnd.value=localInput(editing.end);
      editLocation.value=editing.location||"";editTimezone.value=editing.timezone;editDescription.value=editing.description||"";
      editCalendar.innerHTML=calendars.map(c=>`<option value="${c.id}" ${c.id===editing.calendar_id?"selected":""}>${esc(c.name)}</option>`).join("");editor.showModal()}
    saveEdit.onclick=async()=>{try{await api(`/api/events/${editing.id}`,{method:"PATCH",headers:{"Content-Type":"application/json"},body:JSON.stringify({
      calendar_id:Number(editCalendar.value),title:editTitle.value,start:iso(editStart.value),end:iso(editEnd.value),timezone:editTimezone.value,
      location:editLocation.value||null,description:editDescription.value||null})});editor.close();loadAgenda()}catch(e){editStatus.textContent=e.message;editStatus.className="error"}};
    cancelEdit.onclick=()=>editor.close();
    filter.onchange=loadAgenda;past.onchange=loadAgenda;load();
    """)


def calendars_page() -> str:
    return layout("Calendars", """
    <main><h1>Calendars</h1><p class="muted">Organize events and manage subscription links.</p>
    <section class="panel"><h2>Create calendar</h2><div class="grid"><div class="field"><label>Name</label><input id="newName"></div>
    <div class="field"><label>Color</label><select id="newColor"></select></div></div>
    <div class="field"><label>Description</label><input id="newDescription"></div><div class="actions"><button id="create">Create</button></div></section>
    <section class="panel"><h2>Combined subscription</h2><div id="allSubscription"></div></section>
    <section class="panel"><h2>Your calendars</h2><div id="list"></div></section></main>
    """, """
    let calendars=[];const colors=["#2563eb","#0f766e","#7c3aed","#be123c","#b45309","#4d7c0f","#0369a1","#6b7280"];
    function colorOptions(selected){return colors.map(c=>`<option value="${c}" ${c===selected?"selected":""}>${c}</option>`).join("")}
    function wireCopies(){document.querySelectorAll(".copy").forEach(b=>b.onclick=()=>copyText(b.dataset.url,b))}
    function downloadUrl(urls){const url=new URL(urls.https_url);return url.pathname+url.search}
    function subBlock(urls){return `<div class="subscription"><a href="${urls.webcal_url}">Subscribe to Apple Calendar</a>
    <a href="${downloadUrl(urls)}">Download ICS</a><span class="url">${esc(urls.https_url)}</span>
    <button class="secondary copy" data-url="${esc(urls.https_url)}">Copy</button></div>`}
    async function load(){const data=await api("/api/calendars/manage");calendars=data.calendars;const all=await api("/api/feeds/all/subscription");
      allSubscription.innerHTML=subBlock(all)+'<div class="actions"><button class="secondary" id="regenAll">Regenerate link</button></div>';regenAll.onclick=async()=>{await api("/api/feeds/all/regenerate-token",{method:"POST"});load()};
      list.innerHTML="";for(const c of calendars){const urls=await api(`/api/calendars/${c.id}/subscription`);const el=document.createElement("div");el.className="calendar-card";
      el.innerHTML=`<div class="grid"><div class="field"><label>Name</label><input class="name" value="${esc(c.name)}"></div>
      <div class="field"><label>Color</label><select class="color">${colorOptions(c.color)}</select></div></div>
      <div class="field"><label>Description</label><input class="description" value="${esc(c.description)}"></div>${subBlock(urls)}
      <div class="actions"><button class="save">Save</button><button class="secondary regen">Regenerate link</button><span class="status"></span></div>`;
      el.querySelector(".save").onclick=async()=>{await api(`/api/calendars/${c.id}`,{method:"PATCH",headers:{"Content-Type":"application/json"},body:JSON.stringify({
      name:el.querySelector(".name").value,color:el.querySelector(".color").value,description:el.querySelector(".description").value})});el.querySelector(".status").textContent="Saved"};
      el.querySelector(".regen").onclick=async()=>{await api(`/api/calendars/${c.id}/regenerate-token`,{method:"POST"});load()};list.appendChild(el)}
      wireCopies()}
    create.onclick=async()=>{await api("/api/calendars",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({
      name:newName.value,color:newColor.value,description:newDescription.value})});newName.value="";newDescription.value="";load()};newColor.innerHTML=colorOptions(colors[0]);load();
    """)
