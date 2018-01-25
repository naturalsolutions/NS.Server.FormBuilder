import pprint

class Utility:

    @classmethod
    def _pick(self,array, keys):
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
