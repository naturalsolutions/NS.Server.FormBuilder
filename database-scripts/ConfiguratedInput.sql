
-- A ConfiguratedInput is a Input not attached on a Form
-- This script looks like the CreateTableInput.sql file

CREATE TABLE ConfiguratedInput (

	pk_ConfiguratedInput		BIGINT IDENTITY(1,1) NOT NULL,

	Name			VARCHAR(100) 	NOT NULL,
	LabelFR			VARCHAR(300) 	NOT NULL,
	LabelEN			VARCHAR(300) 	NOT NULL,
	IsRequired		BIT 			NOT NULL,
	IsReadOnly		BIT 			NOT NULL,
	BootStrapSize	VARCHAR(100) 	NOT NULL,
	IsEOL			BIT 			NOT NULL,
	StartDate		DATETIME 		NOT NULL,
	CurStatus		TINYINT			NOT NULL,
	EditorClass		VARCHAR(255)	NULL,
	FieldClass		VARCHAR(255)	NULL,
	InputType		VARCHAR(255)	NOT NULL,

	CONSTRAINT pk_ConfiguratedInput PRIMARY KEY CLUSTERED (pk_ConfiguratedInput ),
)

CREATE TABLE ConfiguratedInputProperty (

	pk_ConfiguratedInputProperty BIGINT IDENTITY(1,1) NOT NULL,	--	primary key

	fk_ConfiguratedInput 		BIGINT NOT NULL,

	Name			VARCHAR(255)	NOT NULL,
	Value			VARCHAR(255)	NOT NULL,
	CreationDate	DateTime		NOT NULL,
	ValueType		VARCHAR(10)		NOT NULL CHECK (ValueType IN('Boolean', 'Number', 'Double', 'String'))

	CONSTRAINT pk_ConfiguratedInputProperty PRIMARY KEY CLUSTERED (pk_ConfiguratedInputProperty )

	CONSTRAINT ConfiguratedInputProperty_fk_Input 		FOREIGN KEY (fk_ConfiguratedInput) 		REFERENCES ConfiguratedInput(pk_ConfiguratedInput)
)