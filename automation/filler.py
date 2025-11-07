# file: automation/filler.py
import json
import time
import os
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException
from loguru import logger
from automation.locators import resolve_selector, suggest_mapping_for_page
from datastore.storage import load_profile, save_profile


def highlight(driver, element, duration=0.3):
    """Temporarily highlight an input element for visual feedback."""
    try:
        original = element.get_attribute("style")
        driver.execute_script(
            "arguments[0].setAttribute('style', arguments[1]);",
            element,
            "border: 2px solid #1a73e8; background: #eaf1fe;"
        )
        time.sleep(duration)
        driver.execute_script("arguments[0].setAttribute('style', arguments[1]);", element, original)
    except Exception:
        pass


def _load_mapping(domain: str) -> dict:
    """
    Try to load mapping profile from datastore; fallback to suggestion generation.
    Supports both `mapping` and `field_mapping` keys for compatibility.
    """
    prof = load_profile(domain)
    if prof:
        if "mapping" in prof:
            logger.info(f"✅ Loaded 'mapping' profile for domain: {domain}")
            return prof["mapping"]
        elif "field_mapping" in prof:
            logger.info(f"✅ Loaded 'field_mapping' profile for domain: {domain}")
            return prof["field_mapping"]
    logger.warning(f"⚠️ No saved mapping found for {domain}. Generating suggestions...")
    return {}


def fill_form_fields(driver, url: str, domain: str, data: dict, wait_seconds: float = 0.4):
    """
    Fill all form fields using Selenium based on mapping profile.
    Keeps browser open for manual verification.
    """
    try:
        mapping = _load_mapping(domain)

        # Generate mapping dynamically if not found
        if not mapping:
            logger.info("🧠 Generating field mapping suggestions from the form page...")
            mapping = suggest_mapping_for_page(driver)
            save_profile(domain, {"mapping": mapping})
            logger.info("💾 New mapping profile saved for future use.")

        logger.info("Loaded mapping:\n{}", json.dumps(mapping, indent=2))
        logger.info("🚀 Starting autofill process...")
        filled_count = 0
        skipped_fields = []

        for field, selector in mapping.items():
            value = data.get(field)
            if not value:
                logger.warning(f"⚠️ Field '{field}' has no extracted value in data.")
                skipped_fields.append(field)
                continue

            element = resolve_selector(driver, selector)
            if not element:
                logger.warning(f"❌ Could not locate element for '{field}' → {selector}")
                skipped_fields.append(field)
                continue

            try:
                highlight(driver, element)
                tag = element.tag_name.lower()
                input_type = (element.get_attribute("type") or "text").lower()

                if tag in ["input", "textarea"]:
                    element.clear()
                    element.send_keys(str(value))
                elif tag == "select":
                    try:
                        Select(element).select_by_visible_text(str(value))
                    except Exception:
                        element.send_keys(str(value))
                elif input_type in ["checkbox", "radio"]:
                    val = str(value).lower()
                    if val in ["yes", "true", "1", "checked"]:
                        if not element.is_selected():
                            element.click()
                else:
                    element.send_keys(str(value))

                logger.info(f"✅ Filled '{field}' → {selector} with '{value}'")
                filled_count += 1
                time.sleep(wait_seconds)

            except Exception as e:
                logger.warning(f"⚠️ Could not fill '{field}' ({selector}): {e}")
                skipped_fields.append(field)

        # --- Summary ---
        logger.info(f"✅ Autofill complete. {filled_count}/{len(mapping)} fields filled.")
        if skipped_fields:
            logger.warning(f"⚠️ Skipped {len(skipped_fields)} fields: {', '.join(skipped_fields)}")

        print("\n✅ Form filled successfully.")
        print("👉 Please review the filled details in the browser.")
        print("👉 Click the Submit button manually when ready.\n")
        input("Press ENTER to close the browser after reviewing the autofill...")

    except Exception as e:
        logger.error(f"❌ Autofill crashed: {e}")
        input("⚠️ Press ENTER to close the browser after inspecting the issue...")

# Backward compatibility alias for UI import
autofill_with_mapping = fill_form_fields
