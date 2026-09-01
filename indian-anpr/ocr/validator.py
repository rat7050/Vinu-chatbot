import re
from typing import Optional, Tuple


class IndianPlateValidator:
    INDIAN_STATE_CODES = {
        "AP", "AR", "AS", "BR", "CG", "GA", "GJ", "HR", "HP", "JH",
        "KA", "KL", "MP", "MH", "MN", "ML", "MZ", "NL", "OD", "PB",
        "RJ", "SK", "TN", "TS", "TR", "UP", "UK", "WB", "DL", "JK",
        "LA", "CH", "PY", "AN", "DN", "LD",
    }

    STANDARD_REGEX = re.compile(r"^([A-Z]{2})([0-9]{1,2})([A-Z]{0,3})([0-9]{4})$")
    BH_REGEX = re.compile(r"^([0-9]{2})BH([0-9]{4})([A-Z]{1,2})$")

    NUM_TO_CHAR = {"0": "O", "1": "I", "2": "Z", "5": "S", "8": "B"}
    CHAR_TO_NUM = {"O": "0", "I": "1", "Z": "2", "S": "5", "B": "8", "Q": "0", "D": "0", "G": "6"}

    @classmethod
    def clean_text(cls, raw_text: str) -> str:
        if not raw_text:
            return ""
        cleaned = re.sub(r"[^A-Za-z0-9]", "", raw_text).upper()
        if cleaned.startswith("IND") and len(cleaned) > 8:
            cleaned = cleaned[3:]
        return cleaned

    @classmethod
    def correct_positional(cls, text: str) -> str:
        text = cls.clean_text(text)
        if len(text) < 8 or len(text) > 11:
            return text

        chars = list(text)

        if len(text) >= 9 and text[2:4].upper() in {"BH", "8H"}:
            if len(chars) >= 10:
                for i in range(0, 2):
                    if chars[i] in cls.CHAR_TO_NUM:
                        chars[i] = cls.CHAR_TO_NUM[chars[i]]
                for i in [2, 3]:
                    if chars[i] in cls.NUM_TO_CHAR:
                        chars[i] = cls.NUM_TO_CHAR[chars[i]]
                if chars[2] == "8":
                    chars[2] = "B"
                if chars[3] == "H":
                    pass
                for i in range(4, len(chars)):
                    if chars[i] in cls.CHAR_TO_NUM and i >= 4:
                        chars[i] = cls.CHAR_TO_NUM[chars[i]]
                return "".join(chars)

        for i in [0, 1]:
            if chars[i] in cls.NUM_TO_CHAR:
                chars[i] = cls.NUM_TO_CHAR[chars[i]]

        for i in [2, 3]:
            if i < len(chars) and chars[i] in cls.CHAR_TO_NUM:
                chars[i] = cls.CHAR_TO_NUM[chars[i]]

        if len(chars) >= 4:
            for i in range(4, len(chars) - 4):
                if chars[i] in cls.NUM_TO_CHAR:
                    chars[i] = cls.NUM_TO_CHAR[chars[i]]

        for i in range(len(chars) - 4, len(chars)):
            if i >= 4 and chars[i] in cls.CHAR_TO_NUM:
                chars[i] = cls.CHAR_TO_NUM[chars[i]]

        return "".join(chars)

    @classmethod
    def validate(cls, raw_text: str) -> Tuple[bool, str, Optional[str]]:
        cleaned = cls.correct_positional(raw_text)

        bh_match = cls.BH_REGEX.match(cleaned)
        if bh_match:
            return True, cleaned, "BH-Series"

        std_match = cls.STANDARD_REGEX.match(cleaned)
        if std_match:
            state_code = std_match.group(1)
            if state_code in cls.INDIAN_STATE_CODES:
                return True, cleaned, "Standard"
            return False, cleaned, f"Invalid State Code: {state_code}"

        return False, cleaned, "Invalid Format"
