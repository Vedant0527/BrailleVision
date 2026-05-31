from braille_dict import (
    BRAILLE_DICT,
    number_map,
    NUMBER_SIGN,
    CAPITAL_SIGN
)

def translate_cells(patterns):

    result = ""
    number_mode = False
    capitalize_next = False

    for pattern in patterns:

        if pattern == NUMBER_SIGN:
            number_mode = True
            continue

        if pattern == CAPITAL_SIGN:
            capitalize_next = True
            continue

        # Number mode
        if number_mode:
            if pattern in number_map:
                result += number_map[pattern]
                continue
            else:
                number_mode = False

        char = BRAILLE_DICT.get(pattern, "?")

        if capitalize_next:
            char = char.upper()
            capitalize_next = False

        result += char

    return result