"""Universal Brain: auth/quota helpers + free anonymous wake (no network)."""
import aux_engine
import universal_brain


def test_is_auth_failure_llm7_401():
    msg = ("OpenAI Compatible 401: Your API key is invalid, expired, or revoked. "
           "Generate a new key at https://dash.llm7.io/#/api-keys (authentication_error)")
    assert aux_engine.is_auth_failure(msg)
    assert aux_engine.is_route_failure(msg)


def test_is_quota_daily_retry_after():
    msg = ("OpenAI Compatible 429: Daily token quota exceeded. "
           "Retry after 88367 seconds. (insufficient_quota)")
    assert aux_engine.is_quota_exhaustion(msg)
    assert aux_engine.is_route_failure(msg)
    assert aux_engine.cooldown_for(msg) >= 3600


def test_free_anon_chain_has_llm7_and_ovh():
    chain = universal_brain.free_anon_chain()
    bases = {c["base_url"] for c in chain}
    assert "https://api.llm7.io/v1" in bases
    assert "https://oai.endpoints.kepler.ai.cloud.ovh.net/v1" in bases


def test_cooldown_constants_exist():
    assert aux_engine.COOLDOWN_DAILY_MAX_S >= aux_engine.COOLDOWN_MAX_S
    assert "insufficient_quota" in aux_engine._QUOTA_WORDS
