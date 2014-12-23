from ..models import Input, session, InputProperty
from ..utilities import Utility

# InputRepository contains some method to lighten controllers
class InputRepository:
    
    def __init__(self, input):
        self.input = input

    # Update an input with new values
    # When an input needs to be updated, we check each properties
    def updateInput(self, **kwargs):

        # Update input, this method use **kwargs and takes only Input common properties like Name, IsRequired
        self.input.update(**kwargs)
        # Update input properties (see InputProperty class)
        self.updateInputProperties(**kwargs)
        return self.input

    # Update input properties
    def updateInputProperties(self, **kwargs):
        # List to update
        inputPropertiesList     = Utility._pickNot(kwargs, Input.getColumnsList())
        # Update each property value
        for each in inputPropertiesList:
            session.query(InputProperty).filter_by(fk_Input = self.input.pk_Input, Name = each).update({"Value" : inputPropertiesList[each]})

    # create a new input
    def createInput(self, **kwargs):
        newInput                 = Input( **Utility._pick(kwargs, Input.getColumnsList()) )
        newInputPropertiesValues = Utility._pickNot(kwargs, Input.getColumnsList())

        for prop in newInputPropertiesValues:
            newInput.addProperty ( InputProperty(prop, str(newInputPropertiesValues[prop]), Utility._getType(newInputPropertiesValues[prop])) )

        return newInput
        


