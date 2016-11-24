from ansible.module_utils.six import string_types


def in_loop_list(
        val, loop_var, path=[], module='stat', param='exists', param_val=True):
    """Verifies if any of the loop results have the desired value"""

    ret = False

    for result in loop_var['results']:
        item = result['item']

        for field in path:
            if (
                    (
                        isinstance(field, string_types) and
                        isinstance(item, dict) and
                        field in item
                    ) or (
                        isinstance(field, int) and
                        isinstance(item, list) and
                        len(item) > field
                    )):
                item = item[field]
            else:
                # Incorrect path
                break

        if (
                item == val and
                module in result and
                param in result[module] and
                result[module][param] == param_val):
            ret = True
            break

    return ret


class FilterModule(object):
    """Custom Jinja2 filters"""

    def filters(self):
        return {
            'in_loop_list': in_loop_list,
        }
