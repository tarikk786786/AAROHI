/* Companion memory strip: soft filter of brain facts for the chat home sidebar. */
(function () {
  "use strict";

  function $(id) { return document.getElementById(id); }
  function esc(s) {
    return String(s == null ? "" : s).replace(/[&<>"']/g, function (c) {
      return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c];
    });
  }

  function ensurePanel() {
    var host = $("chatSide") || $("hudRight") || document.querySelector(".chat-side, .hud-right");
    if (!host || $("companionMemPanel")) return $("companionMemPanel");
    var box = document.createElement("div");
    box.id = "companionMemPanel";
    box.className = "companion-mem-panel";
    box.innerHTML =
      '<div class="companion-mem-head">Remembered</div>' +
      '<div class="companion-mem-filters">' +
      '<button type="button" class="mem-chip" data-f="all" aria-pressed="true">All</button>' +
      '<button type="button" class="mem-chip" data-f="user">About you</button>' +
      '<button type="button" class="mem-chip" data-f="preference">Prefs</button>' +
      '<button type="button" class="mem-chip" data-f="decision">Decisions</button>' +
      "</div>" +
      '<div class="companion-mem-list" id="companionMemList"><span class="dim">Loading…</span></div>';
    host.insertBefore(box, host.firstChild);
    box.querySelectorAll(".mem-chip").forEach(function (btn) {
      btn.addEventListener("click", function () {
        box.querySelectorAll(".mem-chip").forEach(function (b) { b.setAttribute("aria-pressed", "false"); });
        btn.setAttribute("aria-pressed", "true");
        load(btn.getAttribute("data-f") || "all");
      });
    });
    return box;
  }

  async function load(filter) {
    var list = $("companionMemList");
    if (!list) return;
    list.innerHTML = '<span class="dim">Loading…</span>';
    try {
      var r = await fetch("/memory/items");
      if (!r.ok) {
        list.innerHTML = '<span class="dim">Say "remember …" and I will keep it here.</span>';
        return;
      }
      var data = await r.json();
      var facts = (data && (data.items || data.facts || data.memories || data)) || [];
      if (!Array.isArray(facts)) facts = [];
      if (filter && filter !== "all") {
        facts = facts.filter(function (f) {
          return String((f.type || f.kind || f.tag || "")).toLowerCase() === filter;
        });
      }
      if (!facts.length) {
        list.innerHTML = '<span class="dim">No memories in this filter yet.</span>';
        return;
      }
      list.innerHTML = facts.slice(0, 24).map(function (f) {
        var title = f.title || f.slug || f.name || "memory";
        var body = f.summary || f.content || f.text || "";
        body = String(body).replace(/\s+/g, " ").trim().slice(0, 120);
        return '<div class="companion-mem-item"><b>' + esc(title) + "</b>" +
          (body ? '<div class="dim">' + esc(body) + "</div>" : "") + "</div>";
      }).join("");
    } catch (e) {
      list.innerHTML = '<span class="dim">Memory panel unavailable right now.</span>';
    }
  }

  function injectCss() {
    if ($("companionMemCss")) return;
    var s = document.createElement("style");
    s.id = "companionMemCss";
    s.textContent =
      ".companion-mem-panel{padding:10px 12px;border-bottom:1px solid var(--border);font-size:13px}" +
      ".companion-mem-head{font-weight:700;letter-spacing:.06em;color:var(--accent-ink);margin-bottom:6px}" +
      ".companion-mem-filters{display:flex;flex-wrap:wrap;gap:4px;margin-bottom:8px}" +
      ".companion-mem-filters .mem-chip[aria-pressed=true]{background:var(--accent-wash-2);border-color:var(--accent);color:var(--accent-ink)}" +
      ".companion-mem-item{padding:6px 0;border-bottom:1px solid var(--hairline)}" +
      ".companion-mem-item:last-child{border-bottom:0}";
    document.head.appendChild(s);
  }

  function boot() {
    injectCss();
    if (!ensurePanel()) return;
    load("all");
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", function () { setTimeout(boot, 800); });
  } else {
    setTimeout(boot, 800);
  }
})();
