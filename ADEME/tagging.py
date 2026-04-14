import re

import unidecode


# Precompile regexes
REGEX_ETAGE = re.compile(
    r"(?i)(?:"
    # Pattern 1-3: r3, r+3, n3, rn3 style (groups 1, 2, 3)
    r"r[+]?(\d{1,2})|n[+]?(\d{1,2})|rn[+]?(\d{1,2})|"
    # Pattern 4-5: "etage 3", "niveau 3" - word before number (groups 4, 5)
    r"(etage|etg|niveau)\s*(\d{1,2})(?:er|ere|re|eme|ieme|ième|e)?|"
    # Pattern 6: "3eme etage", "1er niveau" - ordinal before word (group 6)
    r"(\d{1,2})(?:er|ere|re|eme|ieme|ième|e)\s*(?:etage|etg|niveau)|"
    # Pattern 7: standalone ordinals "3eme", "1er" - use lookbehind to avoid street numbers (group 7)
    r"(?<![0-9])(\d{1,2})(?:er|ere|eme|ieme|ième)(?![0-9])|"
    # Pattern 8-9: apartment/lot numbers "apt 301" -> floor 3 (groups 8, 9)
    r"(?:apt|appt|appartement|app|lot)\s*(\d)(\d{2})\b|"
    # Pattern 10: ground floor variants (group 10)
    r"(rdc|rc|rdv|rezdechaussee|rezchausse)|"
    # Pattern 11: garden level (group 11)
    r"(rdj|rj|rezdejardin)|"
    # Pattern 12: basement (group 12)
    r"(ss|soussol|ssol|niveauinferieur)|"
    # Pattern 13: mezzanine/entresol (group 13)
    r"(entresol|mezzanine)|"
    # Pattern 14: intermediate level (group 14)
    r"(niveauintermediaire)|"
    # Pattern 15: top floor variants (group 15)
    r"(dernier(?:etage|niveau|niveauetage)?|hautetage|combles|mansarde))"
)

REGEX_LOCALISATION = re.compile(
    r"(?:porte\s*(gauche|droite)|porte[^\w]?(g|d)|\b(pg|pd)\b|cotegauche|cotedroite|enface|fond|milieu)?",
    re.IGNORECASE,
)

REGEX_DIRECTION = re.compile(
    r"(gauche|droite|àgauche|àdroite|cotegauche|cotedroite)", re.IGNORECASE
)


def normalize_text(text):
    if not text:
        return ""
    return re.sub(
        r"\W+", "", unidecode.unidecode(text.lower().replace(" ", "").replace("-", ""))
    )


def categorize_dpe_method(input_text):
    if not input_text:
        return None

    input_text = normalize_text(input_text).replace("-", "").replace("_", "")

    invoice_patterns = ["facture", "invoice"]
    cl3_patterns = ["3cl", "dpe"]
    th_bce_patterns = ["thbce", "thce"]

    if any(pattern in input_text for pattern in invoice_patterns):
        return "INVOICE"
    elif any(pattern in input_text for pattern in cl3_patterns):
        return "3CL"
    elif any(pattern in input_text for pattern in th_bce_patterns):
        return "Th-BCE"
    return None


def fast_extract_info(text):
    text = normalize_text(str(text))

    etage_match = REGEX_ETAGE.search(text)
    loc_match = REGEX_LOCALISATION.search(text)
    dir_match = REGEX_DIRECTION.search(text)

    # Floor parsing
    floor = None
    if etage_match:
        groups = etage_match.groups()
        # etage_val = etage_match.group(0).lower()

        # Group 10: ground floor (rdc, rc, rdv, rezdechaussee, rezchausse)
        # Group 11: garden level (rdj, rj, rezdejardin)
        if groups[9] or groups[10]:
            floor = 0
        # Group 12: basement (ss, soussol, ssol, niveauinferieur)
        elif groups[11]:
            floor = -1
        # Group 13: mezzanine/entresol
        # Group 14: intermediate level
        elif groups[12] or groups[13]:
            floor = None
        # Group 15: top floor (dernier, hautetage, combles, mansarde)
        elif groups[14]:
            floor = "top"
        # Groups 1-3: r3, n3, rn3 style
        elif groups[0] and groups[0].isdigit():
            floor = int(groups[0])
        elif groups[1] and groups[1].isdigit():
            floor = int(groups[1])
        elif groups[2] and groups[2].isdigit():
            floor = int(groups[2])
        # Group 5: "etage 3" style (number after word)
        elif groups[4] and groups[4].isdigit():
            floor = int(groups[4])
        # Group 6: "3eme etage" style (ordinal before word)
        elif groups[5] and groups[5].isdigit():
            floor = int(groups[5])
        # Group 7: standalone ordinal "3eme", "1er"
        elif groups[6] and groups[6].isdigit():
            floor = int(groups[6])
        # Groups 8-9: apartment number "apt 301" -> floor is first digit
        elif groups[7] and groups[7].isdigit():
            floor = int(groups[7])

    # Localisation parsing
    loc = None
    if loc_match:
        g1, g2, g3 = loc_match.group(1), loc_match.group(2), loc_match.group(3)
        val = loc_match.group(0).lower()
        if g1:
            loc = g1
        elif g2 == "g":
            loc = "gauche"
        elif g2 == "d":
            loc = "droite"
        elif g3 == "pg":
            loc = "gauche"
        elif g3 == "pd":
            loc = "droite"
        elif "cotegauche" in val:
            loc = "gauche"
        elif "cotedroite" in val:
            loc = "droite"
        elif "fond" in val:
            loc = "fond"
        elif "milieu" in val:
            loc = "milieu"
        elif "enface" in val:
            loc = "enface"

    # Direction parsing
    direction = dir_match.group(0).lower() if dir_match else None

    return floor, loc, direction
