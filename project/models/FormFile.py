
from sqlalchemy import *
from .base import Base

# FormFile Class
class FormFile(Base):
    __tablename__   = "FormFile"

    Pk_ID           = Column(BigInteger, primary_key=True, nullable=False)
    fk_form         = Column(ForeignKey('Form.pk_Form'), nullable=False)

    name            = Column(String(300, 'French_CI_AS'), nullable=True)
    filedata        = Column(VARBINARY('max'), nullable=False)

    # Constructor
    def __init__(self, **kwargs):
        self.name                = kwargs['name']
        self.filedata            = kwargs['filedata']

    # Update form values
    def update(self, **kwargs):
        self.name				= kwargs['name']
        self.filedata			= kwargs['filedata']

    def toJSON(self):
        return {
            "Pk_ID"         : self.Pk_ID,
            "fk_form"       : self.fk_form,
            "name"     	    : self.name,
            "filedata"      : self.filedata.decode('utf-8')
        }

    @classmethod
    def getColumnList(cls):
        return [
            'name',
            'filedata'
        ]