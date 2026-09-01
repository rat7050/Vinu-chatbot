from ocr.validator import IndianPlateValidator


def test_standard_indian_plates():
    for raw in [
        "MH47BP8265", "DL01AB1234", "KA01MN1234", "TN38BC9012", "UP16AB1234", "RJ14AB1234"
    ]:
        is_valid, plate, plate_type = IndianPlateValidator.validate(raw)
        assert is_valid is True
        assert plate == raw
        assert plate_type in {"Standard", "BH-Series"}


def test_bharat_series():
    is_valid, plate, plate_type = IndianPlateValidator.validate("22BH1234AA")
    assert is_valid is True
    assert plate == "22BH1234AA"
    assert plate_type == "BH-Series"


def test_positional_corrections():
    is_valid, plate, _ = IndianPlateValidator.validate("MH47BPO26S")
    assert is_valid is True
    assert plate == "MH47BP0265"

    is_valid, plate, _ = IndianPlateValidator.validate("8R01AB1234")
    assert is_valid is True
    assert plate == "BR01AB1234"


def test_invalid_plates():
    invalid_cases = ["INVALID123", "ZZ99XX9999", "12345", ""]
    for invalid in invalid_cases:
        is_valid, _, _ = IndianPlateValidator.validate(invalid)
        assert is_valid is False
