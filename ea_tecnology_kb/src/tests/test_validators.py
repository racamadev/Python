"""Unit tests for src.utils.validators."""

from __future__ import annotations

from datetime import datetime

import pytest
from bson import ObjectId

from src.exceptions import ValidationError
from src.utils.validators import (
    is_valid_url,
    sanitize_string,
    validate_choice,
    validate_object_id,
    validate_optional_date,
    validate_optional_string,
    validate_required_date,
    validate_required_string,
    validate_url,
)


class TestSanitizeString:
    def test_strips_whitespace(self):
        assert sanitize_string("  hello  ") == "hello"

    def test_none_returns_empty_string(self):
        assert sanitize_string(None) == ""

    def test_removes_control_characters(self):
        assert sanitize_string("hello\x00world") == "helloworld"

    def test_escapes_html(self):
        assert sanitize_string("<script>") == "&lt;script&gt;"


class TestValidateRequiredString:
    def test_valid_value_passes(self):
        assert validate_required_string("MongoDB", "tech_product") == "MongoDB"

    def test_empty_value_raises(self):
        with pytest.raises(ValidationError):
            validate_required_string("", "tech_product")

    def test_whitespace_only_raises(self):
        with pytest.raises(ValidationError):
            validate_required_string("   ", "tech_product")

    def test_none_raises(self):
        with pytest.raises(ValidationError):
            validate_required_string(None, "tech_product")


class TestValidateChoice:
    def test_valid_choice_passes(self):
        assert validate_choice("Yes", "tech_std", ["Yes", "No"]) == "Yes"

    def test_invalid_choice_raises(self):
        with pytest.raises(ValidationError):
            validate_choice("Maybe", "tech_std", ["Yes", "No"])

    def test_empty_raises(self):
        with pytest.raises(ValidationError):
            validate_choice("", "tech_std", ["Yes", "No"])


class TestValidateOptionalString:
    def test_none_returns_empty(self):
        assert validate_optional_string(None) == ""

    def test_value_is_sanitized(self):
        assert validate_optional_string("  Cloud  ") == "Cloud"


class TestValidateUrl:
    def test_valid_https_url(self):
        assert validate_url("https://example.com") == "https://example.com"

    def test_missing_scheme_raises(self):
        with pytest.raises(ValidationError):
            validate_url("example.com")

    def test_ftp_scheme_raises(self):
        with pytest.raises(ValidationError):
            validate_url("ftp://example.com")

    def test_empty_raises(self):
        with pytest.raises(ValidationError):
            validate_url("")


class TestIsValidUrl:
    def test_valid_url_returns_true(self):
        assert is_valid_url("https://example.com") is True

    def test_invalid_url_returns_false(self):
        assert is_valid_url("not-a-url") is False

    def test_none_returns_false(self):
        assert is_valid_url(None) is False


class TestValidateObjectId:
    def test_valid_object_id(self):
        oid = ObjectId()
        assert validate_object_id(str(oid), "id") == oid

    def test_invalid_object_id_raises(self):
        with pytest.raises(ValidationError):
            validate_object_id("not-an-id", "id")

    def test_missing_raises(self):
        with pytest.raises(ValidationError):
            validate_object_id("", "id")


class TestValidateDates:
    def test_optional_date_none_passes(self):
        assert validate_optional_date(None, "tech_date") is None

    def test_optional_date_invalid_type_raises(self):
        with pytest.raises(ValidationError):
            validate_optional_date("2024-01-01", "tech_date")

    def test_required_date_valid_passes(self):
        value = datetime(2024, 1, 1)
        assert validate_required_date(value, "tech_date") == value

    def test_required_date_none_raises(self):
        with pytest.raises(ValidationError):
            validate_required_date(None, "tech_date")
