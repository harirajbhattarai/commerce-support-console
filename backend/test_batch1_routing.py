import pytest
from app.services.intent_router import normalize_message, hard_safety_gate, hard_human_handoff_gate

def test_normalization():
    # Apostrophe and punctuation
    res = normalize_message("I'm burning! Can't you see?")
    assert "im burn cant you see" == res["normalized_message"]
    
    # Word families
    res2 = normalize_message("My board is swelling and overheating.")
    assert "my board is swell and overheat" == res2["normalized_message"]
    
    res3 = normalize_message("I want to speak with a human support team representative.")
    assert "i want to speak with a agent agent agent" == res3["normalized_message"]

def test_hard_safety_gate():
    # Direct danger words without device
    assert hard_safety_gate(normalize_message("there is fire"))["matched"] == True
    assert hard_safety_gate(normalize_message("it is smoking"))["matched"] == True 
    assert hard_safety_gate(normalize_message("there is smoke"))["matched"] == True
    assert hard_safety_gate(normalize_message("sparks flying"))["matched"] == True
    assert hard_safety_gate(normalize_message("my hoverboard is burn"))["matched"] == True
    assert hard_safety_gate(normalize_message("it is burned"))["matched"] == True
    
    # Contextual - smell
    assert hard_safety_gate(normalize_message("it smells funny"))["matched"] == True # "it" is in device_context
    assert hard_safety_gate(normalize_message("smells funny"))["matched"] == False
    assert hard_safety_gate(normalize_message("my hoverboard smells"))["matched"] == True
    
    # Contextual - swell
    assert hard_safety_gate(normalize_message("my foot is swelling"))["matched"] == False
    assert hard_safety_gate(normalize_message("the battery is swollen"))["matched"] == True
    
    # Contextual - hot
    assert hard_safety_gate(normalize_message("it is a hot day"))["matched"] == False
    assert hard_safety_gate(normalize_message("battery is getting very hot"))["matched"] == True

def test_hard_human_handoff_gate():
    # Must match human requests
    assert hard_human_handoff_gate(normalize_message("i need agent"))["matched"] == True
    assert hard_human_handoff_gate(normalize_message("i want talk to person"))["matched"] == True
    assert hard_human_handoff_gate(normalize_message("i want to talk to a person"))["matched"] == True
    assert hard_human_handoff_gate(normalize_message("speak to advisor"))["matched"] == True
    assert hard_human_handoff_gate(normalize_message("human please"))["matched"] == True
    
    # Must NOT match general conversation
    assert hard_human_handoff_gate(normalize_message("how do i ride this"))["matched"] == False

def test_negative_controls():
    assert hard_human_handoff_gate(normalize_message("Personal Light Electric Vehicle rules"))["matched"] == False
    assert hard_human_handoff_gate(normalize_message("person buying for a child"))["matched"] == False
    assert hard_safety_gate(normalize_message("fire red colour"))["matched"] == False
