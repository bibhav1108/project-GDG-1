import time
from typing import Dict, Tuple
from urllib.parse import urlparse
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from common.config import settings
from automation.locators import get_profile_or_suggestions, resolve_selector

def _highlight(driver, element, ms=300):
    try:
        driver.execute_script("arguments[0].style.outline='3px solid #00b894';", element)
        time.sleep(ms / 1000.0)
        driver.execute_script("arguments[0].style.outline='';", element)
    except Exception:
        pass

def _set_value(el, value: str):
    tag = el.tag_name.lower()
    if tag == "select":
        try:
            Select(el).select_by_visible_text(str(value))
            return True
        except Exception:
            # fallback: first option
            try:
                Select(el).select_by_index(1)
                return True
            except Exception:
                return False
    elif tag in ("input", "textarea"):
        t = (el.get_attribute("type") or "").lower()
        if t in ("radio", "checkbox"):
            # Try to match label text similarity
            try:
                el.click()
                return True
            except Exception:
                return False
        else:
            el.clear()
            el.send_keys(str(value))
            return True
    return False

def autofill_with_mapping(driver: WebDriver, domain: str, data: Dict[str, str]) -> Tuple[int, int]:
    mapping = get_profile_or_suggestions(driver, domain)
    success, failed = 0, 0
    wait = WebDriverWait(driver, settings.get("automation.explicit_wait", 10))
    for field, selector in mapping.items():
        if field not in data or not data[field]:
            continue
        el = resolve_selector(driver, selector)
        if not el:
            failed += 1
            continue
        try:
            wait.until(EC.element_to_be_clickable((By.XPATH, "//body")))
            _highlight(driver, el, settings.get("automation.highlight_ms", 300))
            ok = _set_value(el, data[field])
            if ok:
                success += 1
            else:
                failed += 1
        except Exception:
            failed += 1
    return success, failed
