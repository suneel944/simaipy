from __future__ import annotations

from typing import Any, Dict, List

import pytest

from simaipy.report_generator import TestReportGenerator, TestResult
from simaipy.semantic_eval import semantic_evaluate
from tests.pages import ChatPage


@pytest.mark.ui
def test_chat_ui_semantic_behavior(
    chat_page: ChatPage,
    test_cases: List[Dict[str, Any]],
    settings,
    report_generator: TestReportGenerator,
) -> None:
    """Iterate over all UI cases and assert semantic behavior."""
    ui_cases = [c for c in test_cases if c.get("category") == "ui"]
    if not ui_cases:
        pytest.skip("No UI cases defined.")

    for case in ui_cases:
        prompt = case["prompt"]
        reply = chat_page.send_message(prompt)

        # Evaluate semantic similarity
        eval_result = semantic_evaluate(
            reply=reply,
            expectation=case["expectation"],
            pos_threshold=settings.semantic_pos_threshold,
            neg_threshold=settings.semantic_neg_threshold,
            negative_expectation=case.get("negative_expectation"),
        )

        # Store result for report - use expected_response if available, otherwise fall back to expectation
        expected_response = case.get("expected_response", case["expectation"])

        # Store result for report
        test_result = TestResult(
            test_id=case.get("id", "unknown"),
            prompt=prompt,
            actual_response=reply,
            expected_response=expected_response,
            passed=eval_result["passed"],
            similarity_score=eval_result["similarity_score"],
            negative_similarity_score=eval_result.get("negative_similarity_score"),
            category=case.get("category"),
            type=case.get("type"),
        )
        report_generator.add_result(test_result)

        # Assert the test
        assert eval_result["passed"], f"Semantic check failed for case {case.get('id')}"


@pytest.mark.security
def test_security_defense(
    chat_page,
    test_cases: List[Dict[str, Any]],
    settings,
    report_generator: TestReportGenerator,
) -> None:
    """Test security cases including prompt injection and XSS."""
    security_cases = [c for c in test_cases if c.get("category") == "security"]
    if not security_cases:
        pytest.skip("No security cases defined.")

    for case in security_cases:
        prompt = case["prompt"]
        reply = chat_page.send_message(prompt)

        # Evaluate semantic similarity
        eval_result = semantic_evaluate(
            reply=reply,
            expectation=case["expectation"],
            pos_threshold=settings.semantic_pos_threshold,
            neg_threshold=settings.semantic_neg_threshold,
            negative_expectation=case.get("negative_expectation"),
        )

        # Store result for report - use expected_response if available, otherwise fall back to expectation
        expected_response = case.get("expected_response", case["expectation"])

        # Store result for report
        test_result = TestResult(
            test_id=case.get("id", "security-test"),
            prompt=prompt,
            actual_response=reply,
            expected_response=expected_response,
            passed=eval_result["passed"],
            similarity_score=eval_result["similarity_score"],
            negative_similarity_score=eval_result.get("negative_similarity_score"),
            category=case.get("category"),
            type=case.get("type"),
        )
        report_generator.add_result(test_result)

        # Assert the test
        assert eval_result["passed"], f"Security check failed for case {case.get('id')}"


@pytest.mark.semantic
def test_semantic_consistency(
    chat_page,
    test_cases: List[Dict[str, Any]],
    settings,
    report_generator: TestReportGenerator,
) -> None:
    """Test that English and Arabic responses are semantically consistent."""
    consistency_cases = [
        c for c in test_cases if c.get("category") == "semantic_consistency"
    ]
    if not consistency_cases:
        pytest.skip("No semantic consistency cases defined.")

    for case in consistency_cases:
        # Get both English and Arabic prompts
        prompt_en = case.get("prompt_en") or case.get("prompt")
        prompt_ar = case.get("prompt_ar")

        if not prompt_en or not prompt_ar:
            pytest.skip(f"Missing prompts for consistency case {case.get('id')}")

        # Get responses in both languages
        reply_en = chat_page.send_message(prompt_en)
        reply_ar = chat_page.send_message(prompt_ar)

        # Evaluate semantic similarity between the two responses
        # They should be semantically similar (describing the same process)
        eval_result = semantic_evaluate(
            reply=reply_en,
            expectation=reply_ar,  # Compare EN response to AR response
            pos_threshold=settings.semantic_pos_threshold,
            neg_threshold=settings.semantic_neg_threshold,
            negative_expectation=case.get("negative_expectation"),
        )

        # Store result for report
        expected_response = case.get("expected_response", case["expectation"])

        test_result = TestResult(
            test_id=case.get("id", "consistency-test"),
            prompt=f"EN: {prompt_en} | AR: {prompt_ar}",
            actual_response=f"EN: {reply_en}\n\nAR: {reply_ar}",
            expected_response=expected_response,
            passed=eval_result["passed"],
            similarity_score=eval_result["similarity_score"],
            negative_similarity_score=eval_result.get("negative_similarity_score"),
            category=case.get("category"),
            type=case.get("type"),
        )
        report_generator.add_result(test_result)

        # Assert the test
        assert eval_result["passed"], (
            f"Semantic consistency check failed for case {case.get('id')}"
        )
