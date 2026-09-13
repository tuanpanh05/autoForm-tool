# TESTING STRATEGY

> **Document Version**: 1.0  
> **Date**: 2026-09-13  
> **Status**: Draft

---

## 1. Testing Pyramid

```
        ┌─────────────┐
        │   E2E Tests  │     ~10 tests
        │  (Real forms)│     Slow, expensive
        ├─────────────┤
        │ Integration  │     ~30 tests
        │   Tests      │     Medium speed
        ├─────────────┤
        │  Unit Tests  │     ~100+ tests
        │              │     Fast, cheap
        └─────────────┘
```

---

## 2. Unit Tests

### 2.1. What to Unit Test

| Module | Test Focus | Priority |
|---|---|---|
| **Rule Matcher** | Keyword matching, regex patterns | 🔴 Critical |
| **Fuzzy Matcher** | Similarity scores, threshold behavior | 🔴 Critical |
| **Confidence Scorer** | Score calculation, classification | 🔴 Critical |
| **Label Extractor** | Extract labels from HTML snippets | 🔴 Critical |
| **Field Detector** | Detect field types from HTML | 🟡 High |
| **Validators** | Email, phone, date format validation | 🟡 High |
| **Profile Manager** | CRUD operations, custom fields | 🟡 High |
| **Data Models** | Serialization, deserialization | 🟢 Medium |
| **Config Manager** | Config loading, defaults | 🟢 Medium |
| **Log Redaction** | PII redaction patterns | 🟡 High |

### 2.2. Example Unit Tests

#### Rule Matcher Tests

```python
class TestRuleMatcher:
    def test_exact_match_full_name(self):
        matcher = RuleMatcher()
        results = matcher.match("Full Name", profile_fields)
        assert results[0].profile_path == "personal.full_name"
        assert results[0].confidence >= 0.95
    
    def test_contains_match_email(self):
        matcher = RuleMatcher()
        results = matcher.match("Your Email Address", profile_fields)
        assert results[0].profile_path == "contact.email"
        assert results[0].confidence >= 0.85
    
    def test_no_match_random_text(self):
        matcher = RuleMatcher()
        results = matcher.match("Favorite dinosaur", profile_fields)
        assert len(results) == 0
    
    def test_case_insensitive(self):
        matcher = RuleMatcher()
        results = matcher.match("EMAIL", profile_fields)
        assert results[0].profile_path == "contact.email"
    
    def test_vietnamese_label(self):
        matcher = RuleMatcher()
        results = matcher.match("Họ và tên", profile_fields)
        assert results[0].profile_path == "personal.full_name"
```

#### Confidence Scorer Tests

```python
class TestConfidenceScorer:
    def test_high_confidence_classification(self):
        scorer = ConfidenceScorer()
        level = scorer.classify(0.95)
        assert level == ConfidenceLevel.HIGH
    
    def test_medium_confidence_classification(self):
        scorer = ConfidenceScorer()
        level = scorer.classify(0.72)
        assert level == ConfidenceLevel.MEDIUM
    
    def test_low_confidence_classification(self):
        scorer = ConfidenceScorer()
        level = scorer.classify(0.45)
        assert level == ConfidenceLevel.LOW
    
    def test_no_match_classification(self):
        scorer = ConfidenceScorer()
        level = scorer.classify(0.15)
        assert level == ConfidenceLevel.NO_MATCH
    
    def test_type_compatibility_bonus(self):
        scorer = ConfidenceScorer()
        # email field mapped to email profile field → bonus
        score = scorer.calculate(
            method_score=0.90,
            field_type=FieldType.EMAIL,
            profile_path="contact.email"
        )
        assert score > 0.90  # Should get bonus
```

#### Log Redaction Tests

```python
class TestLogRedaction:
    def test_email_redacted(self):
        result = redact_processor(None, None, {"msg": "test@email.com"})
        assert "[EMAIL_REDACTED]" in result["msg"]
    
    def test_api_key_redacted(self):
        result = redact_processor(None, None, {"msg": "sk-abc123xyz"})
        assert "[API_KEY_REDACTED]" in result["msg"]
    
    def test_sensitive_key_redacted(self):
        result = redact_processor(None, None, {"password": "secret123"})
        assert result["password"] == "[REDACTED]"
    
    def test_non_sensitive_preserved(self):
        result = redact_processor(None, None, {"field_id": "field_01"})
        assert result["field_id"] == "field_01"
```

### 2.3. Test Data / Fixtures

```python
# tests/conftest.py

@pytest.fixture
def sample_profile():
    return UserProfile(
        personal={"full_name": "Nguyen Van A", "date_of_birth": "2004-05-20", "gender": "Male"},
        contact={"email": "test@example.com", "phone": "0123456789"},
        education={"university": "FPT University", "major": "Software Engineering"},
        work={"years_of_experience": 1},
        skills={"programming_languages": ["Python", "Java"]},
        preferences={},
        custom={"github": "https://github.com/example"}
    )

@pytest.fixture
def sample_form_fields():
    return [
        FormField(field_id="f1", label="Full Name", field_type=FieldType.TEXT, ...),
        FormField(field_id="f2", label="Email", field_type=FieldType.EMAIL, ...),
        FormField(field_id="f3", label="Gender", field_type=FieldType.RADIO, 
                  options=[FieldOption("male", "Male", ...), FieldOption("female", "Female", ...)]),
    ]
```

---

## 3. Integration Tests

### 3.1. What to Integration Test

| Test Scenario | Components Involved |
|---|---|
| Form analysis on local HTML | BrowserAdapter + FormAnalyzer + GenericHTMLAdapter |
| Full mapping pipeline | MappingEngine + RuleMatcher + FuzzyMatcher + ConfidenceScorer |
| Fill flow on local HTML | AutofillEngine + BrowserAdapter + FormAdapter |
| Profile CRUD | ProfileManager + ProfileStorage (JSON) |

### 3.2. Local HTML Test Forms

Create test HTML forms that simulate real-world forms:

```
test_forms/
├── basic_contact.html        # Name, email, phone — simplest case
├── radio_checkbox.html       # Gender radio, skills checkboxes
├── dropdown_select.html      # Country select, dropdown menus
├── required_validation.html  # Required fields, input validation
├── multi_section.html        # Form with labeled sections
├── no_labels.html            # Fields without explicit labels (edge case)
├── aria_labels.html          # Accessibility-annotated form
├── complex_mixed.html        # All field types combined
└── google_forms_mock.html    # Simulated Google Forms DOM structure
```

### 3.3. Example Integration Test

```python
@pytest.mark.asyncio
class TestFormAnalysisIntegration:
    async def test_analyze_basic_contact_form(self):
        browser = PlaywrightAdapter()
        await browser.launch(headless=True)
        
        test_form_path = Path("test_forms/basic_contact.html").absolute()
        await browser.open(f"file://{test_form_path}")
        
        adapter = GenericHTMLFormAdapter()
        fields = await adapter.detect_fields(browser)
        
        assert len(fields) >= 3  # name, email, phone
        
        names = [f.label.lower() for f in fields]
        assert any("name" in n for n in names)
        assert any("email" in n for n in names)
        
        await browser.close()

@pytest.mark.asyncio
class TestMappingIntegration:
    async def test_full_mapping_pipeline(self, sample_profile, sample_form_fields):
        engine = MappingEngine(
            matchers=[RuleMatcher(), FuzzyMatcher()],
            scorer=ConfidenceScorer()
        )
        
        mappings = engine.map_form_fields(sample_form_fields, sample_profile)
        
        # "Full Name" should map to personal.full_name with high confidence
        name_mapping = next(m for m in mappings if m.form_field.label == "Full Name")
        assert name_mapping.profile_path == "personal.full_name"
        assert name_mapping.confidence >= 0.90
```

---

## 4. E2E Tests

### 4.1. Full Workflow Test

```python
@pytest.mark.e2e
@pytest.mark.asyncio
async def test_full_workflow_basic_form():
    """Test complete: open → analyze → map → review → fill → verify"""
    
    # Setup
    profile = load_test_profile()
    orchestrator = Orchestrator(...)
    
    # Execute
    result = await orchestrator.fill_form(
        url=f"file://{TEST_FORM_PATH}",
        profile=profile,
        auto_approve_high_confidence=True,
        auto_submit=False  # Never auto-submit in tests
    )
    
    # Verify
    assert result.fields_detected >= 3
    assert result.fields_filled >= 3
    assert result.fill_success_rate >= 0.90
```

### 4.2. Google Forms E2E (Manual trigger only)

```python
@pytest.mark.e2e
@pytest.mark.google_forms
@pytest.mark.manual  # Must be run manually, not in CI
async def test_google_forms_basic():
    """Test against a real Google Form. Requires network."""
    # This test uses a test Google Form created specifically for testing
    # URL: [configured in test config]
    ...
```

---

## 5. Regression Test Dataset

### 5.1. Field Label → Expected Mapping Dataset

```json
{
  "test_cases": [
    {"label": "Full Name", "expected": "personal.full_name", "min_confidence": 0.95},
    {"label": "Your name", "expected": "personal.full_name", "min_confidence": 0.90},
    {"label": "Applicant name", "expected": "personal.full_name", "min_confidence": 0.85},
    {"label": "What is your name?", "expected": "personal.full_name", "min_confidence": 0.80},
    {"label": "Email", "expected": "contact.email", "min_confidence": 0.95},
    {"label": "Email Address", "expected": "contact.email", "min_confidence": 0.95},
    {"label": "Your email address", "expected": "contact.email", "min_confidence": 0.90},
    {"label": "Phone Number", "expected": "contact.phone", "min_confidence": 0.95},
    {"label": "Mobile", "expected": "contact.phone", "min_confidence": 0.85},
    {"label": "Contact number", "expected": "contact.phone", "min_confidence": 0.85},
    {"label": "University", "expected": "education.university", "min_confidence": 0.90},
    {"label": "What university are you currently studying at?", "expected": "education.university", "min_confidence": 0.80},
    {"label": "School", "expected": "education.university", "min_confidence": 0.80},
    {"label": "Gender", "expected": "personal.gender", "min_confidence": 0.95},
    {"label": "Date of Birth", "expected": "personal.date_of_birth", "min_confidence": 0.95},
    {"label": "Favorite color", "expected": null, "min_confidence": 0.0},
    {"label": "Tell us about yourself", "expected": null, "min_confidence": 0.0}
  ]
}
```

### 5.2. Regression Test Runner

```python
def test_mapping_regression():
    """Run all regression test cases and report accuracy."""
    dataset = load_regression_dataset()
    matcher = MappingEngine(...)
    
    correct = 0
    total = len(dataset["test_cases"])
    
    for case in dataset["test_cases"]:
        result = matcher.map_field(
            FormField(label=case["label"], field_type=FieldType.TEXT, ...),
            sample_profile
        )
        
        if case["expected"] is None:
            if result.confidence_level == ConfidenceLevel.NO_MATCH:
                correct += 1
        elif result.profile_path == case["expected"] and result.confidence >= case["min_confidence"]:
            correct += 1
    
    accuracy = correct / total
    assert accuracy >= 0.85, f"Mapping accuracy {accuracy:.0%} below threshold 85%"
```

---

## 6. Test Infrastructure

### 6.1. Tools

| Tool | Purpose |
|---|---|
| **pytest** | Test framework |
| **pytest-asyncio** | Async test support |
| **pytest-playwright** | Playwright fixtures |
| **pytest-cov** | Coverage reporting |
| **pytest-xdist** | Parallel test execution (future) |

### 6.2. pytest Configuration

```toml
# pyproject.toml

[tool.pytest.ini_options]
testpaths = ["tests"]
asyncio_mode = "auto"
markers = [
    "unit: Unit tests (fast, no external dependencies)",
    "integration: Integration tests (may use browser)",
    "e2e: End-to-end tests (full workflow)",
    "google_forms: Tests against Google Forms (requires network)",
    "manual: Tests that must be run manually",
]

[tool.coverage.run]
source = ["src/autoform"]
omit = ["tests/*"]

[tool.coverage.report]
fail_under = 80
```

### 6.3. CI Test Commands

```bash
# Run unit tests only (fast, CI-safe)
pytest -m unit --cov

# Run unit + integration tests
pytest -m "unit or integration" --cov

# Run everything except manual tests
pytest -m "not manual" --cov

# Run with verbose output
pytest -v --tb=short
```

---

## 7. Success Metrics

### 7.1. Accuracy Metrics

| Metric | Target | How to Measure |
|---|---|---|
| **Field Detection Accuracy** | > 95% | Detected fields / actual fields in test forms |
| **Mapping Accuracy** | > 85% | Correct mappings / total mappable fields (regression dataset) |
| **Autofill Success Rate** | > 95% | Successfully filled / attempted fills |
| **False Mapping Rate** | < 5% | Wrong mappings / total mappings |
| **Average Processing Time** | < 10s | Time from URL input to review screen |
| **AI Cost per Form** | < $0.05 | API costs for LLM calls (when enabled) |

### 7.2. How to Track

```python
class MetricsCollector:
    def record_form_session(self, result: FillResult):
        metrics = {
            "timestamp": datetime.now().isoformat(),
            "form_url_hash": hash(result.url),  # Not actual URL for privacy
            "fields_detected": result.fields_detected,
            "fields_mapped": result.fields_mapped,
            "fields_filled": result.fields_filled,
            "fields_failed": result.fields_failed,
            "mapping_accuracy": result.mapping_accuracy,
            "fill_success_rate": result.fill_success_rate,
            "processing_time_ms": result.processing_time_ms,
            "ai_calls": result.ai_calls,
            "ai_cost_usd": result.ai_cost_usd,
        }
        self._append_to_metrics_log(metrics)
```
