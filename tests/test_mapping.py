from automation.locators import _css_or_xpath

def test_selector_detection():
    by, expr = _css_or_xpath("#email")
    assert expr == "#email"
    by, expr = _css_or_xpath("//input[@name='email']")
    assert expr.startswith("//input")
