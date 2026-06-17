from __future__ import annotations

import json


APP_NAME = "Calendar Maker"
APP_SHORT_NAME = "Calendar"
THEME_COLOR = "#f6f7f3"


TRANSLATIONS = {
    "en": {
        "app.name": APP_NAME,
        "app.shortName": APP_SHORT_NAME,
        "nav.create": "Create",
        "nav.agenda": "Agenda",
        "nav.calendars": "Calendars",
        "nav.logout": "Log out",
        "language.label": "Language",
        "language.en": "EN",
        "language.zh": "中文",
        "common.email": "Email",
        "common.password": "Password",
        "common.status.copied": "Copied",
        "common.status.copy": "Copy",
        "common.error.requestFailed": "Request failed",
        "common.error.authRequired": "Authentication required",
        "login.title": "Log in",
        "login.subtitle": "Open your calendars and agenda.",
        "login.submit": "Log in",
        "login.createAccount": "Create account",
        "register.title": "Create account",
        "register.subtitle": "Registration requires a single-use invite code.",
        "register.invite": "Invite code",
        "register.submit": "Create account",
        "register.login": "Log in",
        "maker.title": "Create an event",
        "maker.subtitle": "Describe it naturally, review every field, then confirm.",
        "maker.source": "Event description",
        "maker.placeholder": "Lunch with Mei next Tuesday at 12:30 near the office, about 90 minutes",
        "maker.preferred": "Preferred calendar",
        "maker.aiChoose": "Let AI choose",
        "maker.compile": "Compile event",
        "maker.compiling": "Compiling...",
        "maker.review": "Review the result",
        "maker.reviewTitle": "Review event",
        "maker.aiSuggestion": "AI suggestion",
        "maker.createSuggested": "Create calendar",
        "maker.proposedPrefix": "No existing calendar fits well. Suggested:",
        "maker.confirm": "Confirm event",
        "maker.added": "Added to calendar",
        "maker.ready": "Ready for another event",
        "maker.stepDescribe": "Describe",
        "maker.stepReview": "Review",
        "maker.stepConfirm": "Confirm",
        "field.title": "Title",
        "field.calendar": "Calendar",
        "field.start": "Start",
        "field.end": "End",
        "field.location": "Location",
        "field.timezone": "Timezone",
        "field.notes": "Notes",
        "agenda.title": "All-calendar agenda",
        "agenda.subtitle": "Upcoming events across your calendars.",
        "agenda.filter": "Calendar",
        "agenda.allCalendars": "All calendars",
        "agenda.includePast": "Include past events",
        "agenda.empty": "No events in this range.",
        "agenda.edit": "Edit",
        "agenda.delete": "Delete",
        "agenda.editTitle": "Edit event",
        "agenda.save": "Save",
        "agenda.cancel": "Cancel",
        "calendars.title": "Calendars",
        "calendars.subtitle": "Organize events and manage subscription links.",
        "calendars.detailSubtitle": "Edit calendar details and manage its subscription link.",
        "calendars.back": "Back to calendars",
        "calendars.open": "Open calendar settings",
        "calendars.settings": "Settings",
        "calendars.createTitle": "Create calendar",
        "calendars.name": "Name",
        "calendars.color": "Color",
        "calendars.description": "Description",
        "calendars.create": "Create",
        "calendars.combined": "Combined subscription",
        "calendars.yours": "Your calendars",
        "calendars.subscribeApple": "Subscribe to Apple Calendar",
        "calendars.downloadIcs": "Download ICS",
        "calendars.regenerate": "Regenerate link",
        "calendars.save": "Save",
        "calendars.saved": "Saved",
        "calendars.notFound": "Calendar not found.",
        "calendars.updated": "Calendar updated",
    },
    "zh": {
        "app.name": "日历助手",
        "app.shortName": "日历",
        "nav.create": "创建",
        "nav.agenda": "日程",
        "nav.calendars": "日历",
        "nav.logout": "退出",
        "language.label": "语言",
        "language.en": "EN",
        "language.zh": "中文",
        "common.email": "邮箱",
        "common.password": "密码",
        "common.status.copied": "已复制",
        "common.status.copy": "复制",
        "common.error.requestFailed": "请求失败",
        "common.error.authRequired": "需要登录",
        "login.title": "登录",
        "login.subtitle": "打开你的日历和日程。",
        "login.submit": "登录",
        "login.createAccount": "创建账号",
        "register.title": "创建账号",
        "register.subtitle": "注册需要一个一次性邀请码。",
        "register.invite": "邀请码",
        "register.submit": "创建账号",
        "register.login": "登录",
        "maker.title": "创建事件",
        "maker.subtitle": "自然描述事件，检查字段，然后确认加入日历。",
        "maker.source": "事件描述",
        "maker.placeholder": "下周二 12:30 和 Mei 在办公室附近吃午饭，大约 90 分钟",
        "maker.preferred": "优先日历",
        "maker.aiChoose": "让 AI 选择",
        "maker.compile": "生成事件",
        "maker.compiling": "生成中...",
        "maker.review": "请检查结果",
        "maker.reviewTitle": "检查事件",
        "maker.aiSuggestion": "AI 建议",
        "maker.createSuggested": "创建日历",
        "maker.proposedPrefix": "现有日历不太匹配。建议：",
        "maker.confirm": "确认事件",
        "maker.added": "已加入日历",
        "maker.ready": "可以继续创建下一个事件",
        "maker.stepDescribe": "描述",
        "maker.stepReview": "检查",
        "maker.stepConfirm": "确认",
        "field.title": "标题",
        "field.calendar": "日历",
        "field.start": "开始",
        "field.end": "结束",
        "field.location": "地点",
        "field.timezone": "时区",
        "field.notes": "备注",
        "agenda.title": "全部日程",
        "agenda.subtitle": "查看所有日历中的近期事件。",
        "agenda.filter": "日历",
        "agenda.allCalendars": "全部日历",
        "agenda.includePast": "包含过去事件",
        "agenda.empty": "这个时间范围内没有事件。",
        "agenda.edit": "编辑",
        "agenda.delete": "删除",
        "agenda.editTitle": "编辑事件",
        "agenda.save": "保存",
        "agenda.cancel": "取消",
        "calendars.title": "日历",
        "calendars.subtitle": "管理事件分类和订阅链接。",
        "calendars.detailSubtitle": "修改日历信息并管理它的订阅链接。",
        "calendars.back": "返回日历",
        "calendars.open": "打开日历设置",
        "calendars.settings": "设置",
        "calendars.createTitle": "创建日历",
        "calendars.name": "名称",
        "calendars.color": "颜色",
        "calendars.description": "描述",
        "calendars.create": "创建",
        "calendars.combined": "合并订阅",
        "calendars.yours": "你的日历",
        "calendars.subscribeApple": "订阅到 Apple 日历",
        "calendars.downloadIcs": "下载 ICS",
        "calendars.regenerate": "重新生成链接",
        "calendars.save": "保存",
        "calendars.saved": "已保存",
        "calendars.notFound": "没有找到这个日历。",
        "calendars.updated": "日历已更新",
    },
}


BASE_CSS = """
:root{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif;color:#1f2621;background:#f6f7f3;color-scheme:light;--bg:#f6f7f3;--surface:#fff;--surface-soft:#f0f3ed;--line:#d9ded5;--line-strong:#b8c1b2;--text:#1f2621;--muted:#657066;--primary:#176d5e;--primary-strong:#105548;--danger:#a33a32;--ok:#176d5e;--focus:#72b7a8}
*{box-sizing:border-box}html{-webkit-text-size-adjust:100%}body{margin:0;background:var(--bg)}a{color:var(--primary);text-underline-offset:3px}button,input,textarea,select{font:inherit}
button{min-height:44px;border:0;border-radius:8px;background:var(--primary);color:#fff;padding:10px 16px;cursor:pointer;font-weight:700;line-height:1.2}
button:hover{background:var(--primary-strong)}button.secondary{background:#e7ece4;color:var(--text)}button.secondary:hover{background:#dce4d8}button.danger{background:var(--danger)}button:disabled{opacity:.55;cursor:not-allowed}
input,textarea,select{width:100%;min-height:44px;border:1px solid var(--line-strong);border-radius:8px;padding:10px 12px;background:#fff;color:var(--text)}
input:focus,textarea:focus,select:focus,button:focus-visible,a:focus-visible{outline:3px solid color-mix(in srgb,var(--focus) 45%,transparent);outline-offset:2px}
textarea{min-height:132px;resize:vertical}.shell{min-height:100vh}.nav{position:sticky;top:0;z-index:10;background:rgba(255,255,255,.94);backdrop-filter:saturate(140%) blur(12px);border-bottom:1px solid var(--line);display:flex;align-items:center;padding:10px 22px;gap:16px}
.brand{display:inline-flex;align-items:center;gap:9px;font-weight:800;color:var(--text);text-decoration:none;white-space:nowrap}.brand-mark{width:28px;height:28px;border-radius:8px;background:var(--primary);display:grid;place-items:center;color:#fff;font-size:15px}.brand-text{line-height:1}
.nav-links{display:flex;align-items:center;gap:4px}.nav-link{color:#4d574e;text-decoration:none;border-radius:8px;padding:9px 10px;white-space:nowrap}.nav-link:hover{background:var(--surface-soft);color:var(--text)}.nav .spacer{flex:1}
.nav-tools{display:flex;align-items:center;gap:8px}.language-select{width:auto;min-height:40px;padding:8px 30px 8px 10px;border-color:var(--line);background-color:#fff}.logout-button{min-height:40px;padding:8px 12px}
main{width:min(1000px,calc(100vw - 32px));margin:28px auto 64px}.page-head{margin:0 0 16px}.page-head h1{font-size:clamp(25px,3vw,34px);margin:0 0 6px;letter-spacing:0}.page-head p{margin:0}
.panel{background:var(--surface);border:1px solid var(--line);border-radius:8px;padding:20px;margin-bottom:16px}.panel h2{font-size:18px;margin:0 0 14px}.muted{color:var(--muted);font-size:14px}.error{color:var(--danger);font-weight:650}.ok{color:var(--ok);font-weight:650}
.grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:14px}.field{display:grid;gap:7px;margin-bottom:12px}.field label{font-weight:650;color:#30382f}.actions{display:flex;gap:10px;align-items:center;flex-wrap:wrap;margin-top:14px}.actions.compact{margin-top:0}
.hidden{display:none!important}.steps{display:grid;grid-template-columns:repeat(3,1fr);gap:8px;margin-bottom:14px}.step{min-height:36px;border-radius:8px;background:var(--surface-soft);display:flex;align-items:center;justify-content:center;gap:7px;color:var(--muted);font-weight:700;font-size:13px}.step::before{content:attr(data-step);width:20px;height:20px;border-radius:50%;display:grid;place-items:center;background:#dfe7dd;color:var(--text);font-size:12px}.step.active{background:#e3f0ec;color:var(--primary)}.step.active::before{background:var(--primary);color:#fff}
.subscription{display:grid;gap:9px;background:#f7f9f5;border:1px solid #e3e8df;padding:14px;border-radius:8px}.subscription-actions{display:flex;gap:8px;flex-wrap:wrap}.subscription-actions a,.calendar-action{display:inline-flex;align-items:center;justify-content:center;min-height:40px;border-radius:8px;padding:9px 12px;background:rgba(255,255,255,.94);color:#173f36;text-decoration:none;font-weight:800}.url-label{font-size:12px;color:var(--muted);font-weight:700}.url{word-break:break-all;font-family:ui-monospace,SFMono-Regular,Menlo,monospace;font-size:13px;background:#fff;border:1px solid #e0e5dc;border-radius:6px;padding:10px}
.auth{width:min(440px,calc(100vw - 32px));margin:10vh auto}.auth .panel{padding:26px}.calendar-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:14px;align-items:stretch}.calendar-card,.calendar-create-card{min-height:178px;border-radius:8px;padding:16px;box-shadow:0 10px 28px rgba(31,38,33,.08)}.calendar-card{border:0;color:#fff;text-align:left;display:flex;flex-direction:column;justify-content:space-between;cursor:pointer}.calendar-card:hover{filter:saturate(108%) brightness(.98)}.calendar-card h2,.calendar-create-card h2{margin:0 0 8px;font-size:20px}.calendar-card h2{color:#fff}.calendar-card .muted{color:rgba(255,255,255,.78)}.calendar-create-card{background:#fff;border:1px solid var(--line);display:grid;gap:10px}.calendar-create-card .field{margin-bottom:0}.calendar-create-card label{font-size:13px}.calendar-card-actions{display:flex;gap:8px;flex-wrap:wrap;margin-top:14px}.calendar-card-actions a{flex:1}.edit-panel{max-width:760px}.detail-actions{justify-content:space-between}
.color-option{display:flex;align-items:center;gap:8px}.swatch{width:12px;height:12px;border-radius:50%;display:inline-block;border:1px solid rgba(0,0,0,.12)}
.agenda-toolbar{align-items:end}.checkbox-label{display:flex;align-items:center;gap:9px;min-height:44px;font-weight:650}.checkbox-label input{width:auto;min-height:0}
.agenda-list{padding-top:6px}.agenda-day{margin:22px 0 10px;font-size:16px;color:#30382f}.event-row{display:grid;grid-template-columns:96px 12px 1fr auto;gap:12px;align-items:start;padding:15px 0;border-bottom:1px solid #ecefe9}.event-time{font-weight:750;color:#30382f}.event-title{font-weight:800}.event-meta{margin-top:3px}.event-description{margin-top:6px;color:#3e473f}.event-row .actions{margin-top:0;justify-content:flex-end}
dialog{border:1px solid var(--line);border-radius:8px;padding:0;width:min(640px,calc(100vw - 28px));box-shadow:0 18px 60px rgba(0,0,0,.2)}dialog::backdrop{background:rgba(20,26,22,.38)}dialog .panel{margin:0;border:0}
@media(max-width:760px){.nav{padding:8px 10px;gap:8px;align-items:center}.brand{gap:7px}.brand-mark{width:30px;height:30px}.brand-text{display:none}.nav-links{flex:1;justify-content:center;gap:0}.nav-link{font-size:13px;padding:9px 7px}.nav-tools{gap:6px}.language-select{max-width:76px;min-height:38px;padding:7px 24px 7px 8px;font-size:13px}.logout-button{min-height:38px;padding:7px 9px;font-size:13px}main{width:min(100% - 24px,640px);margin:22px auto 48px}.panel{padding:16px}.grid{grid-template-columns:1fr;gap:0}.steps{gap:6px}.step{font-size:12px}.event-row{grid-template-columns:1fr;gap:8px;background:#fff;border:1px solid var(--line);border-radius:8px;padding:14px;margin-bottom:10px}.event-row .dot{display:none}.event-row .actions{justify-content:flex-start}.agenda-day{margin:18px 0 8px}.subscription-actions button,.subscription-actions a{flex:1}.auth{margin:8vh auto}}
@media(max-width:390px){.nav-link{padding-inline:5px}.logout-button{font-size:0;width:38px;padding:0}.logout-button::before{content:"↪";font-size:17px}.language-select{max-width:66px}.page-head h1{font-size:25px}}
"""


COMMON_JS = f"""
const I18N = {json.dumps(TRANSLATIONS, ensure_ascii=False)};
const LANGUAGE_KEY = "calendarMakerLanguage";
let currentLanguage = initialLanguage();
function initialLanguage(){{
  const saved = localStorage.getItem(LANGUAGE_KEY);
  if (saved === "zh" || saved === "en") return saved;
  return (navigator.language || "").toLowerCase().startsWith("zh") ? "zh" : "en";
}}
function t(key){{return (I18N[currentLanguage] && I18N[currentLanguage][key]) || I18N.en[key] || key}}
function applyLanguage(){{
  document.documentElement.lang = currentLanguage === "zh" ? "zh-CN" : "en";
  document.querySelectorAll("[data-i18n]").forEach(el => el.textContent = t(el.dataset.i18n));
  document.querySelectorAll("[data-i18n-placeholder]").forEach(el => el.placeholder = t(el.dataset.i18nPlaceholder));
  document.querySelectorAll("[data-i18n-label]").forEach(el => el.setAttribute("aria-label", t(el.dataset.i18nLabel)));
  document.title = document.body.dataset.pageTitle ? `${{t(document.body.dataset.pageTitle)}} · ${{t("app.name")}}` : t("app.name");
  document.querySelectorAll(".language-select").forEach(el => el.value = currentLanguage);
}}
function setLanguage(value){{currentLanguage=value;localStorage.setItem(LANGUAGE_KEY,value);applyLanguage();if(window.renderLocalized)window.renderLocalized()}}
async function api(url, options={{}}) {{
  const response = await fetch(url, {{credentials:"same-origin", ...options}});
  if (response.status === 401) {{ window.location.href="/login"; throw new Error(t("common.error.authRequired")); }}
  if (response.status === 204) return null;
  const data = await response.json();
  if (!response.ok) throw new Error(formatError(data.detail));
  return data;
}}
function formatError(detail){{
  if (typeof detail === "string") return detail;
  if (Array.isArray(detail)) return detail.map(item => item.msg || item.message || String(item)).join("; ");
  if (detail && typeof detail === "object") return detail.msg || detail.message || JSON.stringify(detail);
  return t("common.error.requestFailed");
}}
async function logout(){{await api("/api/auth/logout",{{method:"POST"}});window.location.href="/login"}}
function esc(value){{return String(value ?? "").replace(/[&<>"']/g,c=>({{"&":"&amp;","<":"&lt;",">":"&gt;","\\\"":"&quot;","'":"&#039;"}}[c]))}}
function localInput(value){{const d=new Date(value),o=d.getTimezoneOffset()*60000;return new Date(d-o).toISOString().slice(0,16)}}
function iso(value){{return new Date(value).toISOString()}}
async function copyText(value, target){{await navigator.clipboard.writeText(value);target.textContent=t("common.status.copied");setTimeout(()=>target.textContent=t("common.status.copy"),1400)}}
const $ = (id) => document.getElementById(id);
document.addEventListener("DOMContentLoaded",()=>{{document.querySelectorAll(".language-select").forEach(el=>el.onchange=()=>setLanguage(el.value));applyLanguage();if(window.renderLocalized)window.renderLocalized()}});
"""


def language_select() -> str:
    return """
    <select class="language-select" data-i18n-label="language.label" aria-label="Language">
      <option value="en" data-i18n="language.en">EN</option>
      <option value="zh" data-i18n="language.zh">中文</option>
    </select>
    """


def layout(title_key: str, body: str, script: str, nav: bool = True) -> str:
    navigation = f"""
    <nav class="nav">
      <a class="brand" href="/" aria-label="Calendar Maker"><span class="brand-mark">✓</span><span class="brand-text" data-i18n="app.name">Calendar Maker</span></a>
      <div class="nav-links">
        <a class="nav-link" href="/" data-i18n="nav.create">Create</a>
        <a class="nav-link" href="/agenda" data-i18n="nav.agenda">Agenda</a>
        <a class="nav-link" href="/calendars" data-i18n="nav.calendars">Calendars</a>
      </div>
      <span class="spacer"></span>
      <div class="nav-tools">{language_select()}<button class="secondary logout-button" onclick="logout()" data-i18n="nav.logout">Log out</button></div>
    </nav>
    """ if nav else f"""<div class="nav auth-nav"><a class="brand" href="/"><span class="brand-mark">✓</span><span class="brand-text" data-i18n="app.name">Calendar Maker</span></a><span class="spacer"></span>{language_select()}</div>"""
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
    <meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
    <meta name="theme-color" content="{THEME_COLOR}">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-title" content="{APP_SHORT_NAME}">
    <link rel="manifest" href="/manifest.webmanifest">
    <link rel="icon" href="/static/icons/app-icon.svg" type="image/svg+xml">
    <link rel="apple-touch-icon" href="/static/icons/app-icon.svg">
    <title>{APP_NAME}</title><style>{BASE_CSS}</style></head>
    <body data-page-title="{title_key}"><div class="shell">{navigation}{body}</div>
    <script>{COMMON_JS}{script}</script></body></html>"""


def page_head(title_key: str, subtitle_key: str) -> str:
    return f"""<header class="page-head"><h1 data-i18n="{title_key}"></h1><p class="muted" data-i18n="{subtitle_key}"></p></header>"""


def login_page() -> str:
    return layout("login.title", f"""
    <main class="auth"><section class="panel">{page_head("login.title", "login.subtitle")}
    <div class="field"><label data-i18n="common.email">Email</label><input id="email" type="email" autocomplete="email"></div>
    <div class="field"><label data-i18n="common.password">Password</label><input id="password" type="password" autocomplete="current-password"></div>
    <div class="actions"><button id="submit" data-i18n="login.submit">Log in</button><a href="/register" data-i18n="login.createAccount">Create account</a><span id="status"></span></div>
    </section></main>""", """
    const emailInput=$("email"),passwordInput=$("password"),submitButton=$("submit"),statusText=$("status");
    submitButton.onclick=async()=>{try{await api("/api/auth/login",{method:"POST",headers:{"Content-Type":"application/json"},
    body:JSON.stringify({email:emailInput.value,password:passwordInput.value})});location.href="/"}catch(e){statusText.textContent=e.message;statusText.className="error"}};
    """, nav=False)


def register_page() -> str:
    return layout("register.title", f"""
    <main class="auth"><section class="panel">{page_head("register.title", "register.subtitle")}
    <div class="field"><label data-i18n="common.email">Email</label><input id="email" type="email" autocomplete="email"></div>
    <div class="field"><label data-i18n="common.password">Password</label><input id="password" type="password" autocomplete="new-password"></div>
    <div class="field"><label data-i18n="register.invite">Invite code</label><input id="invite" autocomplete="off"></div>
    <div class="actions"><button id="submit" data-i18n="register.submit">Create account</button><a href="/login" data-i18n="register.login">Log in</a><span id="status"></span></div>
    </section></main>""", """
    const emailInput=$("email"),passwordInput=$("password"),inviteInput=$("invite"),submitButton=$("submit"),statusText=$("status");
    submitButton.onclick=async()=>{try{await api("/api/auth/register",{method:"POST",headers:{"Content-Type":"application/json"},
    body:JSON.stringify({email:emailInput.value,password:passwordInput.value,invite_code:inviteInput.value})});location.href="/"}catch(e){statusText.textContent=e.message;statusText.className="error"}};
    """, nav=False)


def maker_page() -> str:
    return layout("maker.title", f"""
    <main>{page_head("maker.title", "maker.subtitle")}
    <section class="panel">
    <div class="steps"><div class="step active" data-step="1" data-i18n="maker.stepDescribe">Describe</div><div class="step" data-step="2" data-i18n="maker.stepReview">Review</div><div class="step" data-step="3" data-i18n="maker.stepConfirm">Confirm</div></div>
    <div class="field"><label data-i18n="maker.source">Event description</label>
    <textarea id="source" data-i18n-placeholder="maker.placeholder" placeholder="Lunch with Mei next Tuesday at 12:30 near the office, about 90 minutes"></textarea></div>
    <div class="grid"><div class="field"><label data-i18n="maker.preferred">Preferred calendar</label><select id="preferred"></select></div></div>
    <div class="actions"><button id="parse" data-i18n="maker.compile">Compile event</button><span id="parseStatus" class="muted"></span></div></section>
    <section id="draft" class="panel hidden"><h2 data-i18n="maker.reviewTitle">Review event</h2><p id="recommendation" class="muted"></p>
    <div id="proposal" class="subscription hidden"></div>
    <div class="grid"><div class="field"><label data-i18n="field.title">Title</label><input id="title"></div>
    <div class="field"><label data-i18n="field.calendar">Calendar</label><select id="calendar"></select></div>
    <div class="field"><label data-i18n="field.start">Start</label><input id="start" type="datetime-local"></div>
    <div class="field"><label data-i18n="field.end">End</label><input id="end" type="datetime-local"></div>
    <div class="field"><label data-i18n="field.location">Location</label><input id="location"></div>
    <div class="field"><label data-i18n="field.timezone">Timezone</label><input id="timezone"></div></div>
    <div class="field"><label data-i18n="field.notes">Notes</label><textarea id="description"></textarea></div>
    <div class="actions"><button id="confirm" data-i18n="maker.confirm">Confirm event</button><span id="confirmStatus"></span></div></section></main>
    """, """
    let calendars=[],eventId=null,proposed=null,lastRecommendation=null;
    const sourceInput=$("source"),preferredSelect=$("preferred"),parseButton=$("parse"),parseStatusText=$("parseStatus");
    const draftPanel=$("draft"),recommendationText=$("recommendation"),proposalBox=$("proposal"),titleInput=$("title");
    const calendarSelect=$("calendar"),startInput=$("start"),endInput=$("end"),locationInput=$("location");
    const timezoneInput=$("timezone"),descriptionInput=$("description"),confirmButton=$("confirm"),confirmStatusText=$("confirmStatus");
    function options(selected){return calendars.map(c=>`<option value="${c.id}" ${c.id===selected?"selected":""}>${esc(c.name)}</option>`).join("")}
    function renderSelects(selected){preferredSelect.innerHTML=`<option value="">${t("maker.aiChoose")}</option>`+options();calendarSelect.innerHTML=options(selected)}
    function renderRecommendation(){recommendationText.textContent=lastRecommendation?`${t("maker.aiSuggestion")}: ${lastRecommendation.reason} (${Math.round(lastRecommendation.confidence*100)}%)`:""}
    function renderProposal(){if(proposed){proposalBox.classList.remove("hidden");proposalBox.innerHTML=`<div>${t("maker.proposedPrefix")} <strong>${esc(proposed.name)}</strong></div><button class="secondary" id="createSuggested">${t("maker.createSuggested")}</button>`;$("createSuggested").onclick=createProposed}else proposalBox.classList.add("hidden")}
    window.renderLocalized=()=>{renderSelects(Number(calendarSelect.value)||undefined);renderRecommendation();renderProposal();if(parseStatusText.dataset.state)parseStatusText.textContent=t(parseStatusText.dataset.state);if(confirmStatusText.dataset.state)confirmStatusText.textContent=t(confirmStatusText.dataset.state)};
    async function load(){const data=await api("/api/calendars");calendars=data.calendars;renderSelects()}
    parseButton.onclick=async()=>{parseButton.disabled=true;parseStatusText.dataset.state="maker.compiling";parseStatusText.textContent=t("maker.compiling");parseStatusText.className="muted";
      try{const data=await api("/api/parse",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({
      text:sourceInput.value,preferred_calendar_id:preferredSelect.value?Number(preferredSelect.value):null})});eventId=data.event.id;proposed=data.proposed_calendar;
      titleInput.value=data.event.title;startInput.value=localInput(data.event.start);endInput.value=localInput(data.event.end);locationInput.value=data.event.location||"";
      timezoneInput.value=data.event.timezone;descriptionInput.value=data.event.description||"";renderSelects(data.event.calendar_id);
      lastRecommendation=data.recommendation_reason?{reason:data.recommendation_reason,confidence:data.recommendation_confidence}:null;renderRecommendation();renderProposal();
      draftPanel.classList.remove("hidden");parseStatusText.dataset.state="maker.review";parseStatusText.textContent=t("maker.review");}catch(e){parseStatusText.textContent=e.message;parseStatusText.className="error";delete parseStatusText.dataset.state}finally{parseButton.disabled=false}};
    async function createProposed(){const data=await api("/api/calendars",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(proposed)});
      calendars.push(data.calendar);proposed=null;renderSelects(data.calendar.id);renderProposal()}
    confirmButton.onclick=async()=>{confirmButton.disabled=true;try{await api(`/api/events/${eventId}/confirm`,{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({
      calendar_id:Number(calendarSelect.value),title:titleInput.value,start:iso(startInput.value),end:iso(endInput.value),timezone:timezoneInput.value,
      location:locationInput.value||null,description:descriptionInput.value||null})});draftPanel.querySelectorAll("input,textarea,select,button").forEach(x=>x.disabled=true);
      confirmStatusText.dataset.state="maker.added";confirmStatusText.textContent=t("maker.added");confirmStatusText.className="ok";sourceInput.value="";parseStatusText.dataset.state="maker.ready";parseStatusText.textContent=t("maker.ready")}catch(e){confirmButton.disabled=false;confirmStatusText.textContent=e.message;confirmStatusText.className="error";delete confirmStatusText.dataset.state}};
    load();
    """)


def agenda_page() -> str:
    return layout("agenda.title", f"""
    <main>{page_head("agenda.title", "agenda.subtitle")}
    <section class="panel"><div class="grid agenda-toolbar"><div class="field"><label data-i18n="agenda.filter">Calendar</label><select id="filter"></select></div>
    <label class="checkbox-label"><input id="past" type="checkbox"><span data-i18n="agenda.includePast">Include past events</span></label></div></section>
    <section class="panel agenda-list" id="agenda"></section>
    <dialog id="editor"><section class="panel"><h2 data-i18n="agenda.editTitle">Edit event</h2><div class="grid">
    <div class="field"><label data-i18n="field.title">Title</label><input id="editTitle"></div><div class="field"><label data-i18n="field.calendar">Calendar</label><select id="editCalendar"></select></div>
    <div class="field"><label data-i18n="field.start">Start</label><input id="editStart" type="datetime-local"></div><div class="field"><label data-i18n="field.end">End</label><input id="editEnd" type="datetime-local"></div>
    <div class="field"><label data-i18n="field.location">Location</label><input id="editLocation"></div><div class="field"><label data-i18n="field.timezone">Timezone</label><input id="editTimezone"></div></div>
    <div class="field"><label data-i18n="field.notes">Notes</label><textarea id="editDescription"></textarea></div>
    <div class="actions"><button id="saveEdit" data-i18n="agenda.save">Save</button><button class="secondary" id="cancelEdit" data-i18n="agenda.cancel">Cancel</button><span id="editStatus"></span></div>
    </section></dialog></main>
    """, """
    let calendars=[],editing=null,lastEvents=[];
    function eventBody(e,c){return `<div class="event-row" data-id="${e.id}"><div class="event-time">${new Date(e.start).toLocaleTimeString([],{hour:"2-digit",minute:"2-digit"})}</div>
    <span class="dot swatch" style="background:${c.color}"></span><div><div class="event-title">${esc(e.title)}</div><div class="muted event-meta">${esc(c.name)}${e.location?" · "+esc(e.location):""}</div>
    <div class="event-description">${esc(e.description||"")}</div></div><div class="actions compact"><button class="secondary edit">${t("agenda.edit")}</button><button class="danger delete">${t("agenda.delete")}</button></div></div>`}
    function renderFilter(){const selected=filter.value;filter.innerHTML=`<option value="">${t("agenda.allCalendars")}</option>`+calendars.map(x=>`<option value="${x.id}">${esc(x.name)}</option>`).join("");filter.value=selected}
    function renderAgenda(events=lastEvents){let html="",day="";for(const e of events){const c=calendars.find(c=>c.id===e.calendar_id);const d=new Date(e.start).toLocaleDateString([],{weekday:"long",month:"long",day:"numeric"});if(d!==day){day=d;html+=`<h2 class="agenda-day">${d}</h2>`}html+=eventBody(e,c)}agenda.innerHTML=html||`<p class="muted">${t("agenda.empty")}</p>`;agenda.querySelectorAll(".delete").forEach(b=>b.onclick=async()=>{await api(`/api/events/${b.closest(".event-row").dataset.id}`,{method:"DELETE"});loadAgenda()});agenda.querySelectorAll(".edit").forEach(b=>b.onclick=()=>openEditor(b.closest(".event-row").dataset.id,lastEvents))}
    window.renderLocalized=()=>{renderFilter();renderAgenda();};
    async function load(){const c=await api("/api/calendars");calendars=c.calendars;renderFilter();await loadAgenda()}
    async function loadAgenda(){const q=new URLSearchParams({include_past:String(past.checked)});if(filter.value)q.set("calendar_id",filter.value);
      const data=await api("/api/agenda?"+q);lastEvents=data.events;renderAgenda(data.events)}
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
    return layout("calendars.title", f"""
    <main>{page_head("calendars.title", "calendars.subtitle")}
    <section class="calendar-grid" id="calendarFlow"></section></main>
    """, """
    let calendars=[];let subscriptions={};const colors=["#2563eb","#0f766e","#7c3aed","#be123c","#b45309","#4d7c0f","#0369a1","#6b7280"];
    function colorOptions(selected){return colors.map(c=>`<option value="${c}" ${c===selected?"selected":""}>● ${c}</option>`).join("")}
    function downloadUrl(urls){const url=new URL(urls.https_url);return url.pathname+url.search}
    function createCard(){return `<article class="calendar-create-card"><h2>${t("calendars.createTitle")}</h2><div class="field"><label>${t("calendars.name")}</label><input id="newName"></div><div class="field"><label>${t("calendars.color")}</label><select id="newColor">${colorOptions(colors[0])}</select></div><div class="field"><label>${t("calendars.description")}</label><input id="newDescription"></div><button id="create">${t("calendars.create")}</button></article>`}
    function actionLinks(c, urls){return `<div class="calendar-card-actions"><a class="calendar-action" href="${urls.webcal_url}" onclick="event.stopPropagation()">${t("calendars.subscribeApple")}</a><a class="calendar-action" href="${downloadUrl(urls)}" onclick="event.stopPropagation()">${t("calendars.downloadIcs")}</a><a class="calendar-action" href="/calendars/${c.id}/edit" onclick="event.stopPropagation()">${t("calendars.settings")}</a></div>`}
    function openCard(event, id){if(event.target.closest("a"))return;location.href=`/calendars/${id}/edit`}
    function wireCreate(){const createButton=$("create");if(!createButton)return;createButton.onclick=async()=>{await api("/api/calendars",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({name:$("newName").value,color:$("newColor").value,description:$("newDescription").value})});await load()}}
    function renderCards(){calendarFlow.innerHTML=createCard()+calendars.map(c=>{const urls=subscriptions[c.id];return `<article class="calendar-card" role="link" tabindex="0" onclick="openCard(event, ${c.id})" onkeydown="if(event.key==='Enter'||event.key===' '){event.preventDefault();openCard(event, ${c.id})}" style="background:${c.color}" aria-label="${t("calendars.open")}: ${esc(c.name)}"><div><h2>${esc(c.name)}</h2>${c.description?`<div class="muted">${esc(c.description)}</div>`:""}</div>${urls?actionLinks(c, urls):""}</article>`}).join("");wireCreate()}
    window.renderLocalized=()=>renderCards();
    async function load(){const data=await api("/api/calendars/manage");calendars=data.calendars;subscriptions={};for(const c of calendars){subscriptions[c.id]=await api(`/api/calendars/${c.id}/subscription`)}renderCards()}
    load();
    """)


def calendar_detail_page(calendar_id: int) -> str:
    return layout("calendars.title", f"""
    <main><header class="page-head"><a href="/calendars" data-i18n="calendars.back">Back to calendars</a><h1 id="pageTitle" data-i18n="calendars.title">Calendars</h1><p class="muted" data-i18n="calendars.detailSubtitle">Edit calendar details and manage its subscription link.</p></header>
    <section class="panel edit-panel" id="editorPanel">
    <div class="grid"><div class="field"><label data-i18n="calendars.name">Name</label><input id="name"></div>
    <div class="field"><label data-i18n="calendars.color">Color</label><select id="color"></select></div></div>
    <div class="field"><label data-i18n="calendars.description">Description</label><input id="description"></div>
    <div class="subscription" id="subscription"></div>
    <div class="actions detail-actions"><span><button id="save" data-i18n="calendars.save">Save</button> <button class="secondary" id="regen" data-i18n="calendars.regenerate">Regenerate link</button></span><span id="status"></span></div>
    </section></main>
    """, f"""
    const calendarId={calendar_id};let calendar=null;let urls=null;const colors=["#2563eb","#0f766e","#7c3aed","#be123c","#b45309","#4d7c0f","#0369a1","#6b7280"];
    const nameInput=$("name"),colorSelect=$("color"),descriptionInput=$("description"),statusText=$("status");
    function colorOptions(selected){{return colors.map(c=>`<option value="${{c}}" ${{c===selected?"selected":""}}>● ${{c}}</option>`).join("")}}
    function downloadUrl(urls){{const url=new URL(urls.https_url);return url.pathname+url.search}}
    function renderSubscription(){{subscription.innerHTML=`<div class="subscription-actions"><a href="${{urls.webcal_url}}">${{t("calendars.subscribeApple")}}</a><a href="${{downloadUrl(urls)}}">${{t("calendars.downloadIcs")}}</a></div>`}}
    function render(){{if(!calendar)return;pageTitle.textContent=calendar.name;colorSelect.innerHTML=colorOptions(calendar.color);renderSubscription();}}
    window.renderLocalized=()=>{{render();if(statusText.dataset.state)statusText.textContent=t(statusText.dataset.state)}};
    async function load(){{const data=await api("/api/calendars/manage");calendar=data.calendars.find(c=>c.id===calendarId);if(!calendar){{editorPanel.innerHTML=`<p class="error">${{t("calendars.notFound")}}</p>`;return}}urls=await api(`/api/calendars/${{calendarId}}/subscription`);nameInput.value=calendar.name;descriptionInput.value=calendar.description;colorSelect.innerHTML=colorOptions(calendar.color);render()}}
    save.onclick=async()=>{{try{{const data=await api(`/api/calendars/${{calendarId}}`,{{method:"PATCH",headers:{{"Content-Type":"application/json"}},body:JSON.stringify({{name:nameInput.value,color:colorSelect.value,description:descriptionInput.value}})}});calendar=data.calendar;statusText.dataset.state="calendars.updated";statusText.textContent=t("calendars.updated");statusText.className="ok";render()}}catch(e){{statusText.textContent=e.message;statusText.className="error";delete statusText.dataset.state}}}};
    regen.onclick=async()=>{{try{{await api(`/api/calendars/${{calendarId}}/regenerate-token`,{{method:"POST"}});urls=await api(`/api/calendars/${{calendarId}}/subscription`);statusText.dataset.state="calendars.saved";statusText.textContent=t("calendars.saved");statusText.className="ok";renderSubscription()}}catch(e){{statusText.textContent=e.message;statusText.className="error";delete statusText.dataset.state}}}};
    load();
    """)
