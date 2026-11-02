"""Hinglish / Hindi lexicon - English base plus Roman Hinglish and common Devanagari.

Fast-path gates need BOTH English (code/docs) and Hinglish (how the owner texts).
Missing DENY for Hinglish live-data asks would invent numbers; missing ALLOW only
costs tokens (falls through to full path). Prefer missing ALLOW over missing DENY.
"""
import re

# Reuse English coverage, then widen with Hinglish surface forms.
from lexicon.en import (  # noqa: F401
    DENY as _EN_DENY,
    ALLOW as _EN_ALLOW,
    STATE_REF as _EN_STATE_REF,
    WRITE_INTENT as _EN_WRITE_INTENT,
    ACTION_VERBS,
    FALSE_ACTION,
    QUANTITATIVE,
    CAPABILITY_DENIAL as _EN_CAPABILITY_DENIAL,
    PROMISE as _EN_PROMISE,
    MEMORY_CLAIM as _EN_MEMORY_CLAIM,
    REMEMBER as _EN_REMEMBER,
    DENSE as _EN_DENSE,
    STUCK as _EN_STUCK,
)

DENY = _EN_DENY + (
    ("live_data_hi", re.compile(
        r"(?i)\b(aaj|kal|abhi|is hafte|is mahine|pichhle|kitna|kitne|kitni|"
        r"doanh.?thu|revenue|sales|order|orders|paise|kamaya|kamaaye|"
        r"mera calendar|meri email|inbox|weather|mausam)\b"
        r"|आज|कल|अभी|कितना|कितने|कितनी|मौसम|कमाई"
    )),
    ("side_effect_hi", re.compile(
        r"(?i)\b(bhej|bhejo|bhejna|delete kar|hata|hatao|cancel kar|"
        r"bana|banao|banani|schedule|yaad dilana|reminder|yaad rakh|"
        r"save kar|likh|likho|post kar|publish)\b"
        r"|भेज|हटा|बना|याद|सेव|लिख"
    )),
    ("agentic_hi", re.compile(
        r"(?i)\b(check kar|dekh|dekho|dekhna|dhund|dhundo|search|find|"
        r"nikal|nikalo|open kar|khol|kholo)\b"
        r"|देख|ढूंढ|खोल|निकाल"
    )),
    ("conversation_state_hi", re.compile(
        r"(?i)\b(pehle|pahle|last time|yaad hai|yaad|continue|aage|"
        r"wahi|waisa hi|jaise bola)\b"
        r"|पहले|याद|आगे|वही"
    )),
)

ALLOW = _EN_ALLOW + (
    ("conversation_hi", re.compile(
        r"(?i)^(namaste|namaskar|hola|hey|hi|hello|haan|han|theek|accha|"
        r"shukriya|thanks|thank you|good morning|good evening|"
        r"kaise ho|kya haal|miss you)\b"
        r"|^नमस्ते|^नमस्कार|^हाँ|^ठीक|^अच्छा|^शुक्रिया"
    )),
    ("explanation_hi", re.compile(
        r"(?i)\b(kya hota hai|kya hai|matlab kya|samjha|samjhao|"
        r"kyun|kyunki|kaise kaam|difference)\b"
        r"|क्या है|मतलब|समझा|क्यों|कैसे"
    )),
)

STATE_REF = re.compile(
    _EN_STATE_REF.pattern + r"|\b(pehle|pahle|yaad hai|wahi|continue|aage)\b|पहले|याद",
    re.I,
)

WRITE_INTENT = re.compile(
    _EN_WRITE_INTENT.pattern
    + r"|\b(bhej|bhejo|hata|hatao|bana|banao|yaad|save kar|likh|likho|post kar)\b"
    + r"|भेज|हटा|बना|याद|लिख",
    re.I,
)

CAPABILITY_DENIAL = _EN_CAPABILITY_DENIAL + (
    "mere paas tools nahi", "tools nahi hain", "access nahi hai",
    "mein tools use nahi kar sakti", "tool available nahi",
)

PROMISE = _EN_PROMISE + (
    ("get_back_hi", re.compile(
        r"(?i)\b(baad mein|thodi der mein|abhi check|dekh ke|"
        r"bataungi|bataata|batata|update karungi|update karunga)\b"
        r"[^.!?]{0,40}?\b(bata|batati|batungi|batunga|update)\b"
        r"|बाद में बता|थोड़ी देर"
    )),
    ("give_moment_hi", re.compile(
        r"(?i)\b(ek minute|ek sec|thodi der|ruk ja|wait kar)\b"
        r"|एक मिनट|थोड़ी देर|रुक जा"
    )),
)

MEMORY_CLAIM = _EN_MEMORY_CLAIM + (
    ("will_remember_hi", re.compile(
        r"(?i)\b(yaad rakh|yaad rakhungi|yaad rakhungi|note kar liya|"
        r"save kar liya|memory mein)\b"
        r"|याद रख|नोट कर|सेव कर"
    )),
)

REMEMBER = re.compile(
    _EN_REMEMBER.pattern
    + r"|\b(yaad rakh|yaad rakhna|mat bhulna|note kar|save this|"
    r"yaad rahe|remember this)\b"
    + r"|याद रख|मत भूल|नोट कर",
    re.I,
)

DENSE = re.compile(
    _EN_DENSE.pattern
    + r"|\b(kya hai|kaise kaam|framework|principle|steps|"
    r"concept|approach)\b"
    + r"|क्या है|कैसे काम",
    re.I,
)

STUCK = _EN_STUCK + (
    "mujhe nahi pata", "pata nahi", "information nahi hai",
    "sure nahi hoon", "transfer kar deti", "human se baat",
)
