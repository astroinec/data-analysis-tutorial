/* 零基础数据分析 - 页面交互
   无第三方依赖，双击 HTML 即可使用。
   页面结构与类名约定见 tools/templates/COMPONENTS.md */
(function () {
  "use strict";

  var DONE_KEY = "da-done";
  var CHECK_KEY = "da-checklist";

  function load(key, fallback) {
    try { var v = JSON.parse(localStorage.getItem(key)); return v == null ? fallback : v; } catch (e) { return fallback; }
  }
  function save(key, val) { try { localStorage.setItem(key, JSON.stringify(val)); } catch (e) {} }
  function $(sel, root) { return (root || document).querySelector(sel); }
  function $all(sel, root) { return Array.prototype.slice.call((root || document).querySelectorAll(sel)); }
  function esc(s) { return String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;"); }

  var DA = window.DA = window.DA || {};
  DA.widgets = DA.widgets || {};
  DA.esc = esc;
  DA.$ = $;
  DA.$all = $all;

  /* ---------- 主题切换 ---------- */
  var themeBtn = $(".theme-btn");
  if (themeBtn) themeBtn.addEventListener("click", function () {
    var cur = document.documentElement.dataset.theme === "dark" ? "light" : "dark";
    document.documentElement.dataset.theme = cur;
    try { localStorage.setItem("da-theme", cur); } catch (e) {}
  });

  /* ---------- 手机端目录 ---------- */
  var menuBtn = $(".menu-btn");
  if (menuBtn) menuBtn.addEventListener("click", function () { document.body.classList.toggle("nav-open"); });
  var mask = $(".sidebar-mask");
  if (mask) mask.addEventListener("click", function () { document.body.classList.remove("nav-open"); });

  /* ---------- 代码高亮 ---------- */
  var PY_KW = "False None True and as assert async await break class continue def del elif else except finally for from global if import in is lambda nonlocal not or pass raise return try while with yield".split(" ");
  var PY_BI = "print len range type int float str bool list dict set tuple sum min max abs round sorted enumerate zip map filter open input isinstance help dir any all".split(" ");
  var PY_RE = /(#[^\n]*)|([rRbBuUfF]{0,2}"""[\s\S]*?"""|[rRbBuUfF]{0,2}'''[\s\S]*?'''|[rRbBuUfF]{0,2}"(?:\\.|[^"\\\n])*"|[rRbBuUfF]{0,2}'(?:\\.|[^'\\\n])*')|(^[ \t]*@[\w.]+)|(\.\.\.|___+)|(\b\d+(?:\.\d+)?(?:[eE][+-]?\d+)?\b)|([A-Za-z_\u4e00-\u9fa5][\w\u4e00-\u9fa5]*)/gm;

  function highlightPython(src) {
    var out = "", last = 0, m;
    PY_RE.lastIndex = 0;
    while ((m = PY_RE.exec(src))) {
      out += esc(src.slice(last, m.index));
      var cls = null;
      if (m[1]) cls = "tok-com";
      else if (m[2]) cls = "tok-str";
      else if (m[3]) cls = "tok-dec";
      else if (m[4]) cls = "tok-blank";
      else if (m[5]) cls = "tok-num";
      else if (m[6]) {
        if (PY_KW.indexOf(m[6]) >= 0) cls = "tok-kw";
        else if (PY_BI.indexOf(m[6]) >= 0) cls = "tok-bi";
        else if (/^\s*\(/.test(src.slice(PY_RE.lastIndex))) cls = "tok-fn";
      }
      out += cls ? '<span class="' + cls + '">' + esc(m[0]) + "</span>" : esc(m[0]);
      last = PY_RE.lastIndex;
    }
    return out + esc(src.slice(last));
  }

  var SQL_KW = /\b(SELECT|FROM|WHERE|GROUP BY|ORDER BY|HAVING|LIMIT|JOIN|LEFT JOIN|INNER JOIN|ON|AS|AND|OR|NOT|IN|IS|NULL|COUNT|SUM|AVG|MIN|MAX|DISTINCT|CASE|WHEN|THEN|ELSE|END|DESC|ASC|BETWEEN|LIKE)\b/gi;
  function highlightSql(src) {
    return esc(src).replace(/('(?:[^']|'')*')/g, '<span class="tok-str">$1</span>')
      .replace(SQL_KW, '<span class="tok-kw">$1</span>')
      .replace(/(--[^\n]*)/g, '<span class="tok-com">$1</span>');
  }

  var PROMPT_RE = /^((?:\([\w.\-]+\)\s*)?(?:[A-Za-z]:\\[^>\n]*>|PS [^>\n]*>|\$ |>>> ))(.*)$/;
  var ERR_RE = /(Error|错误|不是内部或外部命令|无法将|not recognized|not found|Traceback|拒绝访问)/i;
  function highlightTerminal(src) {
    return src.split("\n").map(function (line) {
      var m = line.match(PROMPT_RE);
      if (m) return '<span class="term-prompt">' + esc(m[1]) + '</span><span class="term-cmd">' + esc(m[2]) + "</span>";
      if (ERR_RE.test(line)) return '<span class="term-err">' + esc(line) + "</span>";
      return '<span class="term-out">' + esc(line) + "</span>";
    }).join("\n");
  }

  var LANG_TITLE = {
    python: "Python", py: "Python", output: "运行结果", text: "文本",
    terminal: "Anaconda Prompt", cmd: "命令提示符 (cmd)", powershell: "Windows PowerShell",
    bat: "批处理文件 .bat", json: "JSON", sql: "SQL", csv: "CSV 文件内容", error: "报错信息"
  };

  function copyText(text, btn) {
    function ok() {
      btn.textContent = "已复制"; btn.classList.add("copied");
      setTimeout(function () { btn.textContent = "复制"; btn.classList.remove("copied"); }, 1500);
    }
    if (navigator.clipboard && window.isSecureContext) {
      navigator.clipboard.writeText(text).then(ok, fallback);
    } else fallback();
    function fallback() {
      var ta = document.createElement("textarea");
      ta.value = text; ta.style.position = "fixed"; ta.style.opacity = "0";
      document.body.appendChild(ta); ta.select();
      try { document.execCommand("copy"); ok(); } catch (e) { btn.textContent = "请手动复制"; }
      document.body.removeChild(ta);
    }
  }

  DA.enhanceCode = function (root) {
    $all("pre > code", root).forEach(function (code) {
      var pre = code.parentNode;
      if (pre.parentNode && pre.parentNode.classList && pre.parentNode.classList.contains("code-wrap")) return;
      var m = (code.className || "").match(/language-([\w-]+)/);
      var lang = m ? m[1].toLowerCase() : "text";
      var title = pre.getAttribute("data-title") || LANG_TITLE[lang] || lang;
      var raw = code.textContent.replace(/\n$/, "");
      var wrap = document.createElement("div");
      wrap.className = "code-wrap";
      if (lang === "output") wrap.classList.add("is-output");
      if (lang === "error") wrap.classList.add("is-output", "is-error");
      var isTerm = lang === "terminal" || lang === "cmd" || lang === "powershell";
      if (isTerm) wrap.classList.add("is-terminal");

      if (lang === "python" || lang === "py") code.innerHTML = highlightPython(raw);
      else if (lang === "sql") code.innerHTML = highlightSql(raw);
      else if (isTerm) code.innerHTML = highlightTerminal(raw);

      var head = document.createElement("div");
      head.className = "code-head";
      head.innerHTML = '<span class="lang">' + esc(title) + "</span>";
      if (lang !== "output" && lang !== "error") {
        var btn = document.createElement("button");
        btn.type = "button"; btn.className = "copy-btn"; btn.textContent = "复制";
        btn.addEventListener("click", function () {
          var text = raw;
          if (isTerm) {
            // 终端块只复制命令行，不复制提示符和输出
            text = raw.split("\n").map(function (l) { var mm = l.match(PROMPT_RE); return mm ? mm[2] : null; })
              .filter(function (l) { return l !== null; }).join("\n") || raw;
          }
          copyText(text, btn);
        });
        head.appendChild(btn);
      }
      pre.parentNode.insertBefore(wrap, pre);
      wrap.appendChild(head);
      wrap.appendChild(pre);
    });
  };
  DA.enhanceCode(document);

  /* ---------- 标签页 ---------- */
  $all(".tabs").forEach(function (tabs) {
    var panels = $all(":scope > .tab-panel", tabs);
    var bar = document.createElement("div");
    bar.className = "tab-bar"; bar.setAttribute("role", "tablist");
    var tabPrefix = "da-tab-" + $all(".tabs").indexOf(tabs) + "-";
    panels.forEach(function (p, i) {
      var b = document.createElement("button");
      b.type = "button"; b.textContent = p.getAttribute("data-label") || ("标签 " + (i + 1));
      b.id = tabPrefix + i;
      p.id = p.id || tabPrefix + "panel-" + i;
      p.setAttribute("role", "tabpanel");
      p.setAttribute("aria-labelledby", b.id);
      b.setAttribute("role", "tab");
      b.setAttribute("aria-controls", p.id);
      b.addEventListener("click", function () {
        panels.forEach(function (q, j) { q.hidden = j !== i; });
        $all("button", bar).forEach(function (x, j) {
          x.classList.toggle("active", j === i);
          x.setAttribute("aria-selected", String(j === i));
          x.tabIndex = j === i ? 0 : -1;
        });
      });
      b.addEventListener("keydown", function (event) {
        var next = i;
        if (event.key === "ArrowRight") next = (i + 1) % panels.length;
        else if (event.key === "ArrowLeft") next = (i + panels.length - 1) % panels.length;
        else if (event.key === "Home") next = 0;
        else if (event.key === "End") next = panels.length - 1;
        else return;
        event.preventDefault();
        var target = $all("button", bar)[next];
        target.click(); target.focus();
      });
      bar.appendChild(b);
    });
    tabs.insertBefore(bar, tabs.firstChild);
    if (panels.length) $all("button", bar)[0].click();
  });

  /* ---------- 小测验 ---------- */
  $all(".quiz").forEach(function (quiz) {
    $all(".quiz-options button", quiz).forEach(function (btn) {
      btn.addEventListener("click", function () {
        var right = btn.getAttribute("data-correct") === "1";
        btn.classList.add(right ? "right" : "wrong");
        if (right) {
          quiz.classList.add("answered");
          $all(".quiz-options button", quiz).forEach(function (b) { b.disabled = true; });
        } else if (quiz.getAttribute("data-reveal") !== "0") {
          quiz.classList.add("answered");
        }
      });
    });
  });

  /* ---------- 打勾清单（本机浏览器自动保存） ---------- */
  var checks = load(CHECK_KEY, {});
  $all(".checklist input[type=checkbox]").forEach(function (cb) {
    var id = cb.getAttribute("data-id");
    if (id && checks[id]) cb.checked = true;
    cb.addEventListener("change", function () {
      checks = load(CHECK_KEY, {});
      if (cb.checked) checks[id] = 1; else delete checks[id];
      save(CHECK_KEY, checks);
      updateChecklistCount(cb.closest(".checklist"));
    });
  });
  function updateChecklistCount(cl) {
    if (!cl) return;
    var all = $all("input[type=checkbox]", cl), n = all.filter(function (x) { return x.checked; }).length;
    var c = $(".cl-count", cl);
    if (!c) { c = document.createElement("div"); c.className = "cl-count"; cl.appendChild(c); }
    c.textContent = "已完成 " + n + " / " + all.length + (n === all.length ? "，全部通过！" : "");
    cl.classList.toggle("all-done", n === all.length);
  }
  $all(".checklist").forEach(updateChecklistCount);

  /* ---------- 学习进度 ---------- */
  var outline = window.DA_OUTLINE || { stages: [] };
  var readyIds = [];
  outline.stages.forEach(function (s) { s.lessons.forEach(function (l) { if (l.status === "ready") readyIds.push(l.id); }); });

  function refreshProgress() {
    var done = load(DONE_KEY, {});
    var n = readyIds.filter(function (id) { return done[id]; }).length;
    var pct = readyIds.length ? Math.round((n / readyIds.length) * 100) : 0;
    var bar = $(".op-bar i"); if (bar) bar.style.width = pct + "%";
    var txt = $(".op-text"); if (txt) txt.textContent = pct + "%";
    $all("[data-lid]").forEach(function (el) { el.classList.toggle("done", !!done[el.getAttribute("data-lid")]); });
    $all(".stage-card[data-sid]").forEach(function (card) {
      var ids = $all("[data-lid]", card).map(function (e) { return e.getAttribute("data-lid"); })
        .filter(function (id) { return readyIds.indexOf(id) >= 0; });
      var k = ids.filter(function (id) { return done[id]; }).length;
      var b = $(".stage-bar i", card); if (b) b.style.width = (ids.length ? (k / ids.length) * 100 : 0) + "%";
    });
    var lid = document.body.getAttribute("data-lesson");
    var db = $(".done-btn");
    if (db && lid) {
      db.classList.toggle("is-done", !!done[lid]);
      db.textContent = done[lid] ? "已学完 ✓（点击取消）" : "标记本课已学完";
    }
    var resume = $(".resume-link");
    if (resume) {
      var next = null;
      outline.stages.some(function (s) {
        return s.lessons.some(function (l) { if (l.status === "ready" && !done[l.id]) { next = l; return true; } return false; });
      });
      if (next) { resume.href = "lessons/" + next.id + "-" + next.slug + ".html"; resume.textContent = n ? "继续学习：" + next.id + " " + next.title : "从第一课开始"; }
      else {
        var project = null;
        outline.stages.forEach(function (s) { s.lessons.forEach(function (l) { if (l.id === "P-1") project = l; }); });
        if (project) resume.href = "lessons/" + project.id + "-" + project.slug + ".html";
        resume.textContent = "第一批已学完：复盘项目";
      }
    }
  }
  var doneBtn = $(".done-btn");
  if (doneBtn) doneBtn.addEventListener("click", function () {
    var lid = document.body.getAttribute("data-lesson");
    var done = load(DONE_KEY, {});
    if (done[lid]) delete done[lid]; else done[lid] = Date.now();
    save(DONE_KEY, done);
    refreshProgress();
  });
  refreshProgress();
  window.addEventListener("storage", function (event) { if (event.key === DONE_KEY) refreshProgress(); });

  var searchInput = $("#course-search");
  if (searchInput) searchInput.addEventListener("input", function () {
    var query = searchInput.value.trim().toLowerCase();
    var count = 0;
    $all(".stage-card").forEach(function (card) {
      var visible = 0;
      var stageMatches = $("h3", card).textContent.toLowerCase().indexOf(query) >= 0;
      $all("li", card).forEach(function (item) {
        var match = !query || stageMatches || item.textContent.toLowerCase().indexOf(query) >= 0;
        item.hidden = !match;
        if (match) { visible += 1; count += 1; }
      });
      card.hidden = !visible;
    });
    var summary = $(".search-summary");
    if (summary) summary.textContent = query ? "找到 " + count + " 节匹配课程（灰色为后续内容）" : "";
  });

  /* ---------- 本页目录高亮 & 阅读进度 ---------- */
  var rp = $(".read-progress");
  var tocLinks = $all(".toc a[href^='#']");
  var heads = tocLinks.map(function (a) { return document.getElementById(decodeURIComponent(a.getAttribute("href").slice(1))); });
  function onScroll() {
    var h = document.documentElement, max = h.scrollHeight - h.clientHeight;
    if (rp) rp.style.width = (max > 0 ? (h.scrollTop / max) * 100 : 0) + "%";
    var cur = -1;
    heads.forEach(function (el, i) { if (el && el.getBoundingClientRect().top < 120) cur = i; });
    tocLinks.forEach(function (a, i) { a.classList.toggle("active", i === cur); });
  }
  window.addEventListener("scroll", onScroll, { passive: true });
  onScroll();

  var activeNav = $(".sidebar a.active");
  if (activeNav && activeNav.scrollIntoView) activeNav.scrollIntoView({ block: "center" });

  /* ---------- 图片点击放大 ---------- */
  document.addEventListener("click", function (e) {
    var img = e.target.closest && e.target.closest(".lesson-body figure img");
    if (!img) return;
    var box = document.createElement("div");
    box.className = "lightbox";
    box.setAttribute("role", "dialog");
    box.setAttribute("aria-modal", "true");
    box.setAttribute("aria-label", "放大图片，按 Escape 关闭");
    box.tabIndex = -1;
    var enlarged = document.createElement("img");
    enlarged.src = img.src; enlarged.alt = img.alt;
    box.appendChild(enlarged);
    var previousFocus = document.activeElement;
    function close() {
      box.remove(); document.removeEventListener("keydown", onKey);
      if (previousFocus && previousFocus.focus) previousFocus.focus();
    }
    function onKey(event) { if (event.key === "Escape") close(); }
    box.addEventListener("click", close);
    document.addEventListener("keydown", onKey);
    document.body.appendChild(box); box.focus();
  });

  /* ---------- 交互组件 ----------
     <div class="widget" data-widget="名字"><script type="application/json">配置</script></div>
     组件脚本在 assets/js/widgets/名字.js 里，通过 DA.widgets["名字"] = function (el, config) {...} 注册 */
  function mountWidgets() {
    $all(".widget[data-widget]").forEach(function (el) {
      if (el.getAttribute("data-mounted")) return;
      var name = el.getAttribute("data-widget");
      var fn = DA.widgets[name];
      if (!fn) return;
      var cfgEl = $("script[type='application/json']", el);
      var cfg = {};
      if (cfgEl) { try { cfg = JSON.parse(cfgEl.textContent); } catch (err) { el.innerHTML = '<p class="widget-error">组件配置有误：' + esc(err.message) + "</p>"; return; } }
      el.setAttribute("data-mounted", "1");
      try { fn(el, cfg); } catch (err) { el.innerHTML += '<p class="widget-error">组件加载失败：' + esc(err.message) + "</p>"; if (window.console) console.error(err); }
    });
  }
  DA.mountWidgets = mountWidgets;
  window.addEventListener("DOMContentLoaded", mountWidgets);
  if (document.readyState !== "loading") setTimeout(mountWidgets, 0);
})();
