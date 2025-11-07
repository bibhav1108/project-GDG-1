# file: automation/locators.py
from typing import Dict, List, Optional, Tuple
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.common.exceptions import NoSuchElementException
from rapidfuzz import fuzz
from bs4 import BeautifulSoup
from datastore.storage import load_profile

CANDIDATE_ATTRS = ["name", "id", "aria-label", "placeholder"]

# Canonical cues: hints used for automatic field matching
CANONICAL_CUES = {
    "full_name": ["name", "full name", "applicant name", "student name"],
    "father_name": ["father name", "guardian name"],
    "mother_name": ["mother name"],
    "date_of_birth": ["dob", "date of birth", "birth"],
    "gender": ["gender", "sex"],
    "email": ["email", "mail id", "e-mail"],
    "phone": ["phone", "mobile", "contact number"],
    "alternate_contact": ["alternate phone", "alt contact"],
    "address_line1": ["address", "street", "line 1"],
    "address_line2": ["address 2", "line 2", "alternate address"],
    "city": ["city", "town"],
    "state": ["state", "province"],
    "postal_code": ["pin", "pincode", "zip", "postal"],
    "country": ["country"],
    "university_id": ["university id", "roll number"],
    "previous_school": ["previous school", "last school"],
    "course_applying_for": ["course", "program"],
    "academic_year": ["academic year", "session"],
    "fees": ["fees", "amount", "tuition"],
    "nationality": ["nationality"],
    "religion": ["religion"],
    "category": ["category", "caste"],
    "blood_group": ["blood group"],
    "emergency_contact": ["emergency contact", "guardian contact"]
}


def _css_or_xpath(selector: str) -> Tuple[str, str]:
    sel = selector.strip()
    if sel.startswith("/") or sel.startswith("("):
        return (By.XPATH, sel)
    return (By.CSS_SELECTOR, sel)


def _score_label(text: str, cues: List[str]) -> int:
    """Compute fuzzy similarity between field label and canonical cues."""
    text = (text or "").lower().strip()
    return max(fuzz.QRatio(text, cue) for cue in cues) if text else 0


def _collect_inputs_soup(html: str) -> List[Dict]:
    """Parse HTML and collect all input-like elements with visible labels."""
    soup = BeautifulSoup(html, "lxml")
    inputs = []

    for el in soup.select("input, textarea, select"):
        label_text = ""
        if el.has_attr("id"):
            lbl = soup.select_one(f"label[for='{el['id']}']")
            if lbl:
                label_text = lbl.get_text(" ", strip=True)

        if not label_text:
            label_text = el.get("aria-label") or el.get("placeholder") or ""

        inputs.append({
            "tag": el.name,
            "attrs": dict(el.attrs),
            "label": label_text
        })

    return inputs


def suggest_mapping_for_page(driver: WebDriver) -> Dict[str, str]:
    """
    Suggests mappings for form fields dynamically using fuzzy label matching.
    Returns: {canonical_field: CSS selector}
    """
    html = driver.page_source
    inputs = _collect_inputs_soup(html)
    mapping = {}

    for field, cues in CANONICAL_CUES.items():
        best = None
        best_score = 0

        for el in inputs:
            label = el["label"] or " ".join([el["attrs"].get(a, "") for a in CANDIDATE_ATTRS])
            score = _score_label(label, cues)
            if score > best_score:
                best = el
                best_score = score

        if best and best_score >= 70:
            attrs = best["attrs"]
            if "id" in attrs:
                mapping[field] = f"#{attrs['id']}"
            elif "name" in attrs:
                mapping[field] = f"[name='{attrs['name']}']"
            elif "aria-label" in attrs:
                mapping[field] = f"[aria-label='{attrs['aria-label']}']"
            elif "placeholder" in attrs:
                mapping[field] = f"[placeholder='{attrs['placeholder']}']"

    return mapping


def resolve_selector(driver: WebDriver, selector: str) -> Optional[WebElement]:
    """Try resolving selector to an element; return None if not found."""
    by, expr = _css_or_xpath(selector)
    try:
        return driver.find_element(by, expr)
    except NoSuchElementException:
        return None


def get_profile_or_suggestions(driver: WebDriver, domain: str) -> Dict[str, str]:
    """
    Loads stored profile mapping from local datastore, or auto-generates if not found.
    """
    prof = load_profile(domain)
    if prof and prof.get("mapping"):
        return prof["mapping"]
    return suggest_mapping_for_page(driver)
