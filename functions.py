def search_key_with_value(v, tab):
    for k, j in tab.items():
        if j == v:
            return k

    return None


def array_to_string(tab):
    result = "["

    for i in range(len(tab) - 1):
        result += str(tab[i]) + ", "

    result += str(tab[len(tab) - 1]) + "]"

    return result
