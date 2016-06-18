import re


def is_valid_phone(phone):
    rule = re.compile('^(?:\+?254)?(0|7|07)\d{8}$')
    return False if rule.match(phone) is None else True


def sanitize_phone(phone):
    if phone[0] == "0":
        return phone
    elif phone[0] == "+":
        return "0" + phone[4:]
    elif phone.startswith("254"):
    	return "0" + phone[3:]
    elif len(phone) == 9:
        return "0" + phone
    else:
        return phone