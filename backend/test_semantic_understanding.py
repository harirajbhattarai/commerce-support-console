import pytest
from unittest.mock import patch, MagicMock
import app.services.semantic_understanding as sem_mod
from app.services.semantic_understanding import analyze_semantics, Intent, ProductFamily, RiskLevel, SemanticUnderstanding

@pytest.fixture(autouse=True)
def mock_api_key():
    sem_mod.settings.MINIMAX_API_KEY = "test_key"
    yield

def _mock_minimax_response(json_str: str):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "choices": [{"message": {"content": json_str}}]
    }
    return mock_response

# ==========================================
# MESSY LANGUAGE / SEMANTIC TESTS (15)
# ==========================================
def test_messy_1():
    with patch("app.services.semantic_understanding.requests.post", return_value=_mock_minimax_response('{"intent": "product_recommendation", "product_family": "electric_scooter", "age_context": "9", "risk_level": "low"}')):
        res = analyze_semantics("i have 9 year old kid which scooter should i buy")
        assert res.intent == Intent.product_recommendation

def test_messy_2():
    with patch("app.services.semantic_understanding.requests.post", return_value=_mock_minimax_response('{"intent": "product_recommendation", "product_family": "unknown", "age_context": "9", "risk_level": "low"}')):
        res = analyze_semantics("bought for child 9 what one best")
        assert res.intent == Intent.product_recommendation

def test_messy_3():
    with patch("app.services.semantic_understanding.requests.post", return_value=_mock_minimax_response('{"intent": "product_recommendation", "product_family": "unknown", "risk_level": "low"}')):
        res = analyze_semantics("what size best my son")
        assert res.intent == Intent.product_recommendation

def test_messy_4():
    with patch("app.services.semantic_understanding.requests.post", return_value=_mock_minimax_response('{"intent": "power_issue", "product_family": "electric_scooter", "risk_level": "low"}')):
        res = analyze_semantics("my x2 scooter stop work charger green but no turn")
        assert res.intent == Intent.power_issue

def test_messy_5():
    with patch("app.services.semantic_understanding.requests.post", return_value=_mock_minimax_response('{"intent": "power_issue", "product_family": "hoverboard", "risk_level": "low"}')):
        res = analyze_semantics("charger green but board dead")
        assert res.intent == Intent.power_issue

def test_messy_6():
    with patch("app.services.semantic_understanding.requests.post", return_value=_mock_minimax_response('{"intent": "wheel_motor_issue", "product_family": "hoverboard", "risk_level": "low"}')):
        res = analyze_semantics("board work one side only")
        assert res.intent == Intent.wheel_motor_issue

def test_messy_7():
    with patch("app.services.semantic_understanding.requests.post", return_value=_mock_minimax_response('{"intent": "reset_calibration", "product_family": "unknown", "risk_level": "low"}')):
        res = analyze_semantics("i dont want return just need know how reset this thing")
        assert res.intent == Intent.reset_calibration

def test_messy_8():
    with patch("app.services.semantic_understanding.requests.post", return_value=_mock_minimax_response('{"intent": "reset_calibration", "product_family": "hoverboard", "risk_level": "low"}')):
        res = analyze_semantics("how reset board keeps leaning")
        assert res.intent == Intent.reset_calibration

def test_messy_9():
    with patch("app.services.semantic_understanding.requests.post", return_value=_mock_minimax_response('{"intent": "product_compatibility", "product_family": "hoverkart", "risk_level": "low"}')):
        res = analyze_semantics("how put kart on board")
        assert res.intent == Intent.product_compatibility

def test_messy_10():
    with patch("app.services.semantic_understanding.requests.post", return_value=_mock_minimax_response('{"intent": "product_compatibility", "product_family": "hoverkart", "risk_level": "low"}')):
        res = analyze_semantics("does kart fit 85 board")
        assert res.intent == Intent.product_compatibility

def test_messy_11():
    with patch("app.services.semantic_understanding.requests.post", return_value=_mock_minimax_response('{"intent": "unknown", "product_family": "unknown", "needs_clarification": true, "risk_level": "low"}')):
        res = analyze_semantics("it not work")
        assert res.needs_clarification == True

def test_messy_12():
    with patch("app.services.semantic_understanding.requests.post", return_value=_mock_minimax_response('{"intent": "product_recommendation", "product_family": "unknown", "needs_clarification": true, "risk_level": "low"}')):
        res = analyze_semantics("which one best")
        assert res.needs_clarification == True

def test_messy_13():
    with patch("app.services.semantic_understanding.requests.post", return_value=_mock_minimax_response('{"intent": "power_issue", "product_family": "hoverboard", "risk_level": "low"}')):
        res = analyze_semantics("my hoverbord wont trun on")
        assert res.intent == Intent.power_issue

def test_messy_14():
    with patch("app.services.semantic_understanding.requests.post", return_value=_mock_minimax_response('{"intent": "power_issue", "product_family": "electric_scooter", "risk_level": "low"}')):
        res = analyze_semantics("scootr chargr gren no power")
        assert res.intent == Intent.power_issue

def test_messy_15():
    with patch("app.services.semantic_understanding.requests.post", return_value=_mock_minimax_response('{"intent": "battery_safety", "product_family": "hoverboard", "risk_level": "high"}')):
        res = analyze_semantics("can sm1 help board smell weird")
        assert res.intent == Intent.battery_safety

# ==========================================
# PRODUCT FAMILY TESTS (3)
# ==========================================
def test_product_family_1():
    with patch("app.services.semantic_understanding.requests.post", return_value=_mock_minimax_response('{"intent": "power_issue", "product_family": "electric_scooter", "risk_level": "low"}')):
        res = analyze_semantics("my x2 scooter is not working")
        assert res.product_family == ProductFamily.electric_scooter

def test_product_family_2():
    with patch("app.services.semantic_understanding.requests.post", return_value=_mock_minimax_response('{"intent": "power_issue", "product_family": "hoverboard", "risk_level": "low"}')):
        res = analyze_semantics("my hoverboard is not working")
        assert res.product_family == ProductFamily.hoverboard

def test_product_family_3():
    with patch("app.services.semantic_understanding.requests.post", return_value=_mock_minimax_response('{"intent": "product_compatibility", "product_family": "hoverkart", "risk_level": "low"}')):
        res = analyze_semantics("my hoverkart does not fit")
        assert res.product_family == ProductFamily.hoverkart

# ==========================================
# MULTI-TURN TESTS (3)
# ==========================================
def test_multi_turn_1():
    context = [
        {"sender": "user", "content": "my board not working"},
        {"sender": "bot", "content": "What is wrong with it?"},
        {"sender": "user", "content": "charger is green"}
    ]
    with patch("app.services.semantic_understanding.requests.post", return_value=_mock_minimax_response('{"intent": "power_issue", "product_family": "hoverboard", "risk_level": "low"}')):
        res = analyze_semantics("still wont turn on", previous_context=context)
        assert res.product_family == ProductFamily.hoverboard
        assert res.intent == Intent.power_issue

def test_multi_turn_2():
    context = [
        {"sender": "user", "content": "need one for my son"}
    ]
    with patch("app.services.semantic_understanding.requests.post", return_value=_mock_minimax_response('{"intent": "product_recommendation", "product_family": "unknown", "age_context": "9", "risk_level": "low"}')):
        res = analyze_semantics("hes 9", previous_context=context)
        assert res.intent == Intent.product_recommendation
        assert res.age_context == "9"
        assert res.product_family == ProductFamily.unknown

def test_multi_turn_3():
    context = [
        {"sender": "user", "content": "my scooter stopped"}
    ]
    with patch("app.services.semantic_understanding.requests.post", return_value=_mock_minimax_response('{"intent": "power_issue", "product_family": "electric_scooter", "risk_level": "low"}')):
        res = analyze_semantics("charger green", previous_context=context)
        assert res.product_family == ProductFamily.electric_scooter
        assert res.intent == Intent.power_issue

# ==========================================
# MINIMAX FAILURE TESTS (7)
# ==========================================
def test_failure_timeout():
    import requests
    with patch("app.services.semantic_understanding.requests.post", side_effect=requests.exceptions.Timeout):
        res = analyze_semantics("hello")
        assert res.intent == Intent.unknown

def test_failure_http():
    mock_response = MagicMock()
    mock_response.status_code = 500
    with patch("app.services.semantic_understanding.requests.post", return_value=mock_response):
        res = analyze_semantics("hello")
        assert res.intent == Intent.unknown

def test_failure_invalid_json():
    with patch("app.services.semantic_understanding.requests.post", return_value=_mock_minimax_response('this is not json')):
        res = analyze_semantics("hello")
        assert res.intent == Intent.unknown

def test_failure_missing_fields():
    with patch("app.services.semantic_understanding.requests.post", return_value=_mock_minimax_response('{"product_family": "hoverboard"}')):
        res = analyze_semantics("hello")
        # should fall back or validation error triggers unknown
        assert res.intent == Intent.unknown

def test_failure_unsupported_intent():
    with patch("app.services.semantic_understanding.requests.post", return_value=_mock_minimax_response('{"intent": "made_up_intent", "product_family": "hoverboard", "risk_level": "low"}')):
        res = analyze_semantics("hello")
        assert res.intent == Intent.unknown

def test_failure_unsupported_product_family():
    with patch("app.services.semantic_understanding.requests.post", return_value=_mock_minimax_response('{"intent": "general_support", "product_family": "unicycle", "risk_level": "low"}')):
        res = analyze_semantics("hello")
        assert res.product_family == ProductFamily.unknown

def test_failure_confidence_bounds():
    # If confidence is > 1.0, validation fails, falls back to unknown
    with patch("app.services.semantic_understanding.requests.post", return_value=_mock_minimax_response('{"intent": "general_support", "product_family": "hoverboard", "risk_level": "low", "confidence": 1.5}')):
        res = analyze_semantics("hello")
        assert res.intent == Intent.unknown


def test_semantic_metadata_mapping():
    from app.services.semantic_understanding import build_semantic_metadata, SemanticUnderstanding, Intent, ProductFamily, RiskLevel

    mock_sem = SemanticUnderstanding(
        intent=Intent.power_issue,
        sub_intent="power_issue",
        product_family=ProductFamily.electric_scooter,
        product_entity="x2 scooter",
        issue_category="charging",
        risk_level=RiskLevel.low,
        customer_goal="power_issue",
        age_context="adult",
        order_specific=False,
        needs_clarification=False,
        clarification_reason="",
        confidence=0.98
    )

    meta = build_semantic_metadata(mock_sem, "MINIMAX_STRUCTURED")

    assert meta["semantic_intent"] == "power_issue"
    assert meta["semantic_sub_intent"] == "power_issue"
    assert meta["semantic_product_entity"] == "x2 scooter"
    assert meta["semantic_product_family"] == "electric_scooter"
    assert meta["semantic_issue_category"] == "charging"
    assert meta["semantic_risk_level"] == "low"
    assert meta["semantic_customer_goal"] == "power_issue"
    assert meta["semantic_age_context"] == "adult"
    assert meta["semantic_order_specific"] is False
    assert meta["semantic_needs_clarification"] is False
    assert meta["semantic_clarification_reason"] == ""
    assert meta["semantic_confidence"] == 0.98
    assert meta["semantic_classifier_mode"] == "MINIMAX_STRUCTURED"

# ==========================================
# RESPONSE PARSER TESTS (8)
# ==========================================
from app.services.semantic_understanding import extract_minimax_semantic_payload

def _build_response(status, data):
    r = MagicMock()
    r.status_code = status
    r.json.return_value = data
    return r

def _create_fallback(reason):
    return SemanticUnderstanding(
        intent=Intent.unknown,
        product_family=ProductFamily.unknown,
        risk_level=RiskLevel.unknown,
        confidence=0.0,
        error_reason=reason
    )

def test_parser_a_valid_envelope():
    # Test A: Valid OpenAI-compatible envelope
    data = {
        "choices": [{
            "message": {
                "content": '{"intent":"power_issue", "product_family":"hoverboard"}'
            }
        }]
    }
    r = _build_response(200, data)
    res = extract_minimax_semantic_payload(r, _create_fallback)
    assert res.intent == Intent.power_issue

def test_parser_b_code_fence():
    # Test B: Valid semantic JSON inside ```json code fence
    data = {
        "choices": [{
            "message": {
                "content": "```json\n{\"intent\":\"power_issue\"}\n```"
            }
        }]
    }
    r = _build_response(200, data)
    res = extract_minimax_semantic_payload(r, _create_fallback)
    assert res.intent == Intent.power_issue

def test_parser_c_empty_choices():
    # Test C: Empty choices
    data = {"choices": []}
    r = _build_response(200, data)
    res = extract_minimax_semantic_payload(r, _create_fallback)
    assert res.error_reason == "MINIMAX_EMPTY_CONTENT"

def test_parser_d_content_null():
    # Test D: message.content = null
    data = {
        "choices": [{
            "message": {
                "content": None
            }
        }]
    }
    r = _build_response(200, data)
    res = extract_minimax_semantic_payload(r, _create_fallback)
    assert res.error_reason == "MINIMAX_EMPTY_CONTENT"

def test_parser_e_content_empty():
    # Test E: message.content = ""
    data = {
        "choices": [{
            "message": {
                "content": ""
            }
        }]
    }
    r = _build_response(200, data)
    res = extract_minimax_semantic_payload(r, _create_fallback)
    assert res.error_reason == "MINIMAX_EMPTY_CONTENT"

def test_parser_f_non_json():
    # Test F: non-JSON final content
    data = {
        "choices": [{
            "message": {
                "content": "Here is the result: not a json object"
            }
        }]
    }
    r = _build_response(200, data)
    res = extract_minimax_semantic_payload(r, _create_fallback)
    assert res.error_reason == "MINIMAX_INVALID_JSON"

def test_parser_g_schema_failure():
    # Test G: JSON object fails Pydantic semantic schema (e.g. invalid type)
    # The current pydantic model might ignore invalid keys or fallback, but if we give invalid confidence string it raises validation error
    data = {
        "choices": [{
            "message": {
                "content": '{"intent":"power_issue", "confidence": "not-a-number"}'
            }
        }]
    }
    r = _build_response(200, data)
    res = extract_minimax_semantic_payload(r, _create_fallback)
    assert res.error_reason == "MINIMAX_SCHEMA_VALIDATION_FAILURE"

def test_parser_h_reasoning_split():
    # Test H: MiniMax thinking is separated using reasoning_split
    # Final message.content contains valid semantic JSON, and reasoning_details exists but is ignored
    data = {
        "choices": [{
            "message": {
                "content": '{"intent":"power_issue"}',
                "reasoning_details": "I am thinking about the user issue..."
            }
        }]
    }
    r = _build_response(200, data)
    res = extract_minimax_semantic_payload(r, _create_fallback)
    assert res.intent == Intent.power_issue

def test_extract_customer_answer_payload():
    from app.services.support_brain import extract_customer_answer_payload

    # Clean text
    data1 = {"choices": [{"message": {"content": "Hello there"}}]}
    assert extract_customer_answer_payload(data1) == "Hello there"

    # Text with <think> tag
    data2 = {"choices": [{"message": {"content": "<think>Thinking deeply...</think>Hello there"}}]}
    assert extract_customer_answer_payload(data2) == "Hello there"

    # Text with Markdown formatting
    data3 = {"choices": [{"message": {"content": "**Bold** and *italic* and ### Header"}}]}
    assert extract_customer_answer_payload(data3) == "Bold and italic and Header"

    # Empty content
    import pytest
    data4 = {"choices": [{"message": {"content": "<think>Just thinking</think>"}}]}
    with pytest.raises(ValueError):
        extract_customer_answer_payload(data4)
