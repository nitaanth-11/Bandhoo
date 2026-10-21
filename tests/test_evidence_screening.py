"""
Unit tests for Evidence Screening, Document Validation, Image Quality and Manipulation (P2.2 & P2.3).

Key Invariants:
1. Valid magic bytes are verified; unsupported formats rejected cleanly.
2. Unreadable or blurry images trigger a request for a clearer upload, NEVER a fraud allegation.
3. Manipulation and AI-generation detection is strictly probabilistic screening, not proof.
4. Suspicious evidence is flagged for human examination, never automatically deemed fraudulent.
"""

import pytest
from complaint_engine.evidence_screening import (
    validate_and_screen_evidence_file,
    inspect_magic_bytes,
)


def test_magic_byte_validation_for_supported_types():
    # JPEG
    jpeg_bytes = b"\xff\xd8\xff\xe0\x00\x10JFIF" + b"\x00" * 200
    res = validate_and_screen_evidence_file(jpeg_bytes, "incident_photo.jpg")
    assert res.is_supported is True
    assert res.detected_mime_type == "image/jpeg"
    assert res.format_valid is True

    # PNG
    png_bytes = b"\x89PNG\r\n\x1a\n" + b"\x00" * 200
    res = validate_and_screen_evidence_file(png_bytes, "screenshot.png")
    assert res.is_supported is True
    assert res.detected_mime_type == "image/png"

    # PDF
    pdf_bytes = b"%PDF-1.7\n%\xe2\xe3\xcf\xd3\n" + b"\x00" * 200
    res = validate_and_screen_evidence_file(pdf_bytes, "medical_report.pdf")
    assert res.is_supported is True
    assert res.detected_mime_type == "application/pdf"


def test_unsupported_format_rejected():
    fake_exe = b"MZ\x90\x00\x03\x00\x00\x00" + b"\x00" * 100
    res = validate_and_screen_evidence_file(fake_exe, "malicious.exe")
    assert res.is_supported is False
    assert "Unsupported file format" in res.validation_error


def test_blurry_unreadable_image_requests_clearer_copy_never_claims_fraud():
    # Create flat, zero-variance low-sharpness byte payload mimicking extreme blur
    blurry_jpeg = b"\xff\xd8\xff\xe0\x00\x10JFIF" + bytes([128] * 1000)
    res = validate_and_screen_evidence_file(blurry_jpeg, "blurred_camera.jpg")
    
    assert res.is_supported is True
    assert res.quality.is_readable is False
    assert res.quality.action_prompt_for_user is not None
    assert "upload a clearer" in res.quality.action_prompt_for_user.lower()
    # Invariant: Must NOT accuse the complainant of fraud
    assert res.manipulation.screening_status != "fraudulent"
    assert not any("fraud" in n.lower() for n in res.quality.quality_notes)


def test_synthetic_ai_detection_is_probabilistic_screening_with_disclaimer():
    # Simulate an image embedding Midjourney / generative metadata
    synthetic_jpeg = (
        b"\xff\xd8\xff\xe0\x00\x10JFIF"
        b"\x00\x00\x00Metadata: prompt=cyberpunk street generator=Midjourney v6"
        + b"\xaa\xbb\xcc" * 200
    )
    res = validate_and_screen_evidence_file(synthetic_jpeg, "cctv_frame.jpg")
    
    assert res.manipulation.screening_status == "flagged_for_human_review"
    assert res.manipulation.synthetic_probability_score >= 0.5
    # Invariant: Must explicitly include screening disclaimer stating it is not proof
    assert "Probabilistic screening indicator only; not forensic proof" in res.manipulation.screening_disclaimer
    assert "flagged for human examiner review" in res.manipulation.screening_disclaimer


def test_normal_sharp_photo_passes_screening_cleanly():
    # Varied bytes simulating real photo high-contrast transitions
    photo_data = b"\xff\xd8\xff\xe0\x00\x10JFIF" + bytes([(i * 53) % 256 for i in range(2000)])
    res = validate_and_screen_evidence_file(photo_data, "photo_scene.jpg")
    
    assert res.is_supported is True
    assert res.quality.is_readable is True
    assert res.manipulation.screening_status == "clean_screening"
