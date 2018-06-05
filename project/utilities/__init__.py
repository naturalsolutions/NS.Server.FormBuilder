import pprint

class EditMode(object):
    nullmean = False
    nullable = False
    editable = False
    visible = False
    def __init__(self, val = 0):
        self.nullmean = (val >= 8)
        val %= 8
        self.nullable = (val >= 4)
        val %= 4
        self.editable = (val >= 2)
        val %= 2
        self.visible = (val >= 1)

    def toValue(self):
        i = 0
        i += 1 if self.visible else 0
        i += 2 if self.editable else 0
        i += 4 if self.nullable else 0
        i += 8 if self.nullmean else 0
        return i


class Utility:

    @classmethod
    def _pick(self,array, keys):
        # be flexible, set empty if unavailable..
        for key in keys:
            if key not in array:
                array[key] = ''

        return { your_key: array[your_key] for your_key in keys }

    @classmethod
    def _pickNot(self, array, keys):
        arr = {}
        for prop in array:
            if prop not in keys:
                arr[prop] = array[prop]
        return arr

    @classmethod
    def _getType(self, variable):
        if variable is None:
            return 'String'
        if isinstance(variable, bool):
            return "Boolean" 
        elif isinstance(variable, int):
            return 'Number' 
        elif isinstance(variable, float):
            return "Double"
        else:
             return "String"

    @classmethod
    def _print_r(self, variable):
        pp = pprint.PrettyPrinter(indent=4)
        pp.pprint(variable)

    @classmethod
    def datetimeToStr(cls, date, format="%d/%m/%Y - %H:%M:%S"):
        if not date or date == 'NULL':
            return ""

        return date.strftime(format)
