/* Free browser attention gate. This does not identify speakers or remove audio noise.

   0.65.22 (chủ dự án chốt 01/10): bỏ công tắc "Tập trung" và bỏ luật phải gọi tên. Rào chỉ còn
   bật ở đường Live (app.js đặt enabled theo đường gọi): im IDLE_MS thì ngắt nhà cung cấp cho đỡ
   tốn hạn mức, rồi CÂU NÓI THẬT đầu tiên (wakes) là nối lại. Đường Cơ bản không có gì để ngắt nên
   nghe suốt cuộc gọi. Không dùng Groq: chữ "Javis" trình duyệt hay chép thành "David", bắt buộc gọi
   tên là đúng khâu từng làm cuộc gọi không nối lại được. */
(function (root) {
  "use strict";
  // AAROHI: wake on Aarohi / Arohi first, keep Javis/Jarvis as legacy aliases.
  // Web Speech often mangles Hindi names - nearWake catches common mishears without opening the gate alone.
  // AAROHI: always-ready wake - full name PLUS common mic stubs (Ar/Ro/Rahi).
  const wake = /^(?:(?:hey|hi|hello|oye|sun|suno|meri?|yaar|babe|baby|ê|này|alo|chào)\s+)?(?:aarohi|arohi|aaruhi|aarohie|arrohi|ar|aro|ro|roh|rahi|javis|jarvis)(?=$|[\s,.!?:;])/iu;
  // Near-misses only unlock re-listen, not the gate alone.
  const IDLE_MS = 120000;     // AAROHI: stay awake longer so she feels always ready
  const WAKE_MIN_WORDS = 1;   // any real word reopens Live after idle
  const nearWake = /^(?:(?:hey|hi|hello|oye|sun|suno|meri?|babe|ê|này|alo|chào)\s+)?(?:david|davis|javix|jarvix|đa\s*vít|gia\s*vít|ja\s*vít|ja\s*vịt|giá\s*vít|chavis|arrow\s*he|a\s*rohi|rahi|arohie|aaravi|arohee|ahrohi|ar|aro|ro)(?=$|[\s,.!?:;])/iu;
  class Attention {
    constructor({ now = Date.now, idleMs = IDLE_MS, candidateMs = 120000 } = {}) {
      this.now = now; this.idleMs = idleMs; this.candidateMs = candidateMs;
      this.enabled = true; this.stop();
    }
    start() { this.running = true; this.until = this.now() + this.idleMs; this.candidateUntil = 0; }
    stop() { this.running = false; this.until = 0; this.candidateUntil = 0; }
    waiting() { return this.running && this.enabled && this.now() >= Math.max(this.until, this.candidateUntil); }
    keepActive() { if (this.running && !this.waiting()) this.until = this.now() + this.idleMs; }
    preview(text) {
      if (!String(text || '').trim()) { this.candidateUntil = 0; return false; }
      if (!this.running) return false;
      if (!this.waiting()) {
        // Latch the start, not every interim: a stuck recognizer cannot hold this forever.
        if (!this.candidateUntil) this.candidateUntil = this.now() + this.candidateMs;
        return true;
      }
      // A provisional wake must be present again in the FINAL before it opens the gate.
      return wake.test(String(text).trim());
    }
    wakeCandidate(text) {
      return this.running && nearWake.test(String(text || '').trim());
    }
    // Câu nói THẬT để nối lại phiên Live đã ngắt vì im lâu: có tên gọi, hoặc đủ WAKE_MIN_WORDS chữ.
    wakes(text) {
      const t = String(text || '').trim();
      return wake.test(t) || (t.match(/\p{L}+/gu) || []).length >= WAKE_MIN_WORDS;
    }
    accept(text) {
      const ok = this.running && !!String(text || '').trim() &&
        (!this.waiting() || wake.test(String(text).trim()));
      this.candidateUntil = 0;
      if (ok) this.until = this.now() + this.idleMs;
      return ok;
    }
  }
  // Dự phòng khi máy không có bộ nhận giọng của trình duyệt (hay bị chặn): đo âm lượng mic, tiếng
  // to hơn nền đủ lâu là có người nói. Nền chỉ học từ mẫu YÊN, có trần: gieo nền bằng mẫu đầu (lúc
  // đang nói) làm bộ đo tê liệt, đúng bẫy đã gặp ở bộ rình ngắt lời.
  class SpeechLevel {
    constructor({ now = Date.now, minRms = 0.02, ratio = 3, holdMs = 350, floorCap = 0.03 } = {}) {
      this.now = now; this.minRms = minRms; this.ratio = ratio; this.holdMs = holdMs; this.floorCap = floorCap;
      this.floor = 0.004; this.since = 0;
    }
    feed(rms) {
      const t = this.now();
      if (rms <= Math.max(this.minRms, this.floor * this.ratio)) {
        this.floor = Math.min(this.floorCap, this.floor * 0.95 + rms * 0.05);
        this.since = 0;
        return false;
      }
      if (!this.since) this.since = t;
      return t - this.since >= this.holdMs;
    }
  }
  const api = { Attention, SpeechLevel, IDLE_MS };
  if (typeof module === 'object' && module.exports) module.exports = api;
  else root.JavisVoiceAttention = api;
})(typeof window !== 'undefined' ? window : globalThis);
