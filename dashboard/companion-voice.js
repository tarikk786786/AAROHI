/* AAROHI Companion voice helpers (clean-room Mark behaviors).
   - Push-to-talk: hold Space (not in input) or hold #voiceBtn / #dictBtn
   - Self-echo guard: drop STT that matches the last TTS transcript
   - Instant Hinglish ack: speak a short line when a long tool turn starts
*/
(function () {
  "use strict";

  var PTT_KEY = " ";
  var _pttHeld = false;
  var _lastTtsNorm = "";
  var _ackSpokenFor = "";

  function norm(s) {
    return String(s || "")
      .toLowerCase()
      .replace(/[^\p{L}\p{N}\s]/gu, " ")
      .replace(/\s+/g, " ")
      .trim();
  }

  function similar(a, b) {
    a = norm(a); b = norm(b);
    if (!a || !b) return false;
    if (a === b) return true;
    if (a.length >= 8 && b.indexOf(a) >= 0) return true;
    if (b.length >= 8 && a.indexOf(b) >= 0) return true;
    // short ack echoes like "haan jaan" / "theek hai"
    if (a.length <= 40 && b.length <= 80) {
      var aw = a.split(" "), bw = new Set(b.split(" "));
      var hit = 0;
      for (var i = 0; i < aw.length; i++) if (aw[i].length > 2 && bw.has(aw[i])) hit++;
      if (aw.length && hit / aw.length >= 0.75) return true;
    }
    return false;
  }

  function voice() { return window.voice || null; }

  function rememberTts(text) {
    var n = norm(text);
    if (n) _lastTtsNorm = n.slice(0, 400);
  }

  function isEcho(transcript) {
    if (!_lastTtsNorm) return false;
    return similar(transcript, _lastTtsNorm);
  }

  /** Wrap recognition final path: ignore self-echo of last spoken TTS. */
  function installEchoGuard() {
    var v = voice();
    if (!v || v._aarohiEchoGuard) return;
    v._aarohiEchoGuard = true;
    var origSpeak = v.speak && v.speak.bind(v);
    if (origSpeak) {
      v.speak = function (text) {
        rememberTts(text);
        return origSpeak(text);
      };
    }
    // Patch stopListening path used when a final utterance is committed
    var origStop = v.stopListening && v.stopListening.bind(v);
    if (origStop) {
      v.stopListening = function () {
        try {
          var t = (v.accumulatedTranscript || "") + " " + (v._duoiTam || "");
          if (isEcho(t)) {
            v.accumulatedTranscript = "";
            v._duoiTam = "";
            v.userStopped = true;
            try { if (v.recognition) v.recognition.abort(); } catch (e) {}
            return;
          }
        } catch (e) {}
        return origStop();
      };
    }
  }

  function inEditable(el) {
    if (!el) return false;
    var tag = (el.tagName || "").toLowerCase();
    if (tag === "input" || tag === "textarea" || tag === "select") return true;
    if (el.isContentEditable) return true;
    return !!(el.closest && el.closest("[contenteditable=true], .cm-editor, .ProseMirror"));
  }

  function startPtt() {
    if (_pttHeld) return;
    _pttHeld = true;
    document.body.classList.add("ptt-held");
    var btn = document.getElementById("voiceBtn");
    if (btn) btn.classList.add("ptt-held");
    try {
      if (typeof window.batRanhTay === "function" && !window.handsFreeActive?.()) {
        // Prefer dictation listen if available; else start call listen
      }
      var v = voice();
      if (v && !v.isListening && typeof v.startListening === "function") {
        v.startListening();
      }
    } catch (e) {}
  }

  function endPtt() {
    if (!_pttHeld) return;
    _pttHeld = false;
    document.body.classList.remove("ptt-held");
    var btn = document.getElementById("voiceBtn");
    if (btn) btn.classList.remove("ptt-held");
    try {
      var v = voice();
      if (v && v.isListening && typeof v.stopListening === "function") v.stopListening();
    } catch (e) {}
  }

  function installPtt() {
    document.addEventListener("keydown", function (ev) {
      if (ev.code !== "Space" && ev.key !== PTT_KEY) return;
      if (ev.repeat) return;
      if (inEditable(ev.target)) return;
      // Don't steal Space when not on companion call home / when typing elsewhere
      if (document.body.classList.contains("in-console")) return;
      ev.preventDefault();
      startPtt();
    }, true);
    document.addEventListener("keyup", function (ev) {
      if (ev.code !== "Space" && ev.key !== PTT_KEY) return;
      if (!_pttHeld) return;
      ev.preventDefault();
      endPtt();
    }, true);
    window.addEventListener("blur", endPtt);

    ["voiceBtn", "dictBtn"].forEach(function (id) {
      var el = document.getElementById(id);
      if (!el || el._aarohiPtt) return;
      el._aarohiPtt = true;
      el.addEventListener("mousedown", function (ev) {
        if (ev.button !== 0) return;
        // Hold = PTT; short click still handled by existing click handlers
        el._pttTimer = setTimeout(function () { startPtt(); }, 220);
      });
      el.addEventListener("mouseup", function () {
        clearTimeout(el._pttTimer);
        if (_pttHeld) endPtt();
      });
      el.addEventListener("mouseleave", function () {
        clearTimeout(el._pttTimer);
        if (_pttHeld) endPtt();
      });
      el.addEventListener("touchstart", function () {
        el._pttTimer = setTimeout(function () { startPtt(); }, 220);
      }, { passive: true });
      el.addEventListener("touchend", function () {
        clearTimeout(el._pttTimer);
        if (_pttHeld) endPtt();
      });
    });
  }

  var ACKS = [
    "Haan jaan, ek second...",
    "Theek hai, dekh rahi hoon...",
    "Okay sweetheart, wait na...",
    "Haan, kar rahi hoon...",
    "Got it babe, one sec..."
  ];

  function maybeAck(statusText) {
    var v = voice();
    if (!v || typeof v.speak !== "function") return;
    var s = String(statusText || "");
    // Long / tool turns: thinking, checking, working
    if (!/thinking|suy nghĩ|checking|kiểm tra|working|đang|tool|looking/i.test(s)) return;
    if (_ackSpokenFor === s) return;
    _ackSpokenFor = s;
    // Don't stack ack on top of existing speech
    if (v.isSpeaking && v.isSpeaking()) return;
    var line = ACKS[Math.floor(Math.random() * ACKS.length)];
    try { v.speak(line); } catch (e) {}
  }

  function installAckHook() {
    // Observe orb/status text changes from app.js
    var orb = document.getElementById("orbState");
    if (orb && !orb._aarohiAck) {
      orb._aarohiAck = true;
      var mo = new MutationObserver(function () { maybeAck(orb.textContent || ""); });
      mo.observe(orb, { childList: true, characterData: true, subtree: true });
    }
    // Also listen for WS status via a small hook if app exposes it
    var prev = window.onAarohiStatus;
    window.onAarohiStatus = function (msg) {
      try { maybeAck(msg); } catch (e) {}
      if (typeof prev === "function") prev(msg);
    };
  }

  function boot() {
    installEchoGuard();
    installPtt();
    installAckHook();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", function () { setTimeout(boot, 400); });
  } else {
    setTimeout(boot, 400);
  }

  window.AarohiCompanionVoice = {
    isEcho: isEcho,
    rememberTts: rememberTts,
    maybeAck: maybeAck,
    startPtt: startPtt,
    endPtt: endPtt
  };
})();
