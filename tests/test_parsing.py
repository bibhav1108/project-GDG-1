from parsing.validators import validate_email, validate_phone, validate_postal, parse_date
from parsing.normalizers import normalize_phone, title_case_name, split_address

def test_validators():
    assert validate_email("a@b.com")[0]
    assert validate_phone("+91 98765 43210")[0]
    assert validate_postal("110001")[0]
    iso, conf = parse_date("03/05/2001")
    assert iso in ("2001-05-03", "2001-03-05")  # depending on parser heuristic

def test_normalizers():
    assert normalize_phone("9876543210").startswith("+91")
    assert title_case_name("rohan sharma") == "Rohan Sharma"
    sp = split_address("45 MG Road, Delhi")
    assert sp["address_line1"] == "45 MG Road"
