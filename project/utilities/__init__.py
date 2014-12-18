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
        if isinstance(variable, bool):
            return "Boolean" 
        elif isinstance(variable, int):
            return 'Number' 
        elif isinstance(variable, float):
            return "Double"
        else:
             return "String"