--	This script create all tables for inputs functionnalities
--	Each form (see CreateTablesForm.sql file) has many input

-- the current status (curStatus) cans take 3 values : 1 Active, 2 Archived and 4 Deleted

--	This script is samplier than CreateTableInputDynProp
--	Currently it is script implemented in the Python code

CREATE TABLE Input (

	pk_Input		BIGINT IDENTITY(1,1) NOT NULL,	--	primary key

	fk_form			BIGINT NOT NULL,	--	foreign key , give parent form id to the input

	Name			VARCHAR(100) 	NOT NULL,
	LabelFR			VARCHAR(300) 	NOT NULL,
	LabelEN			VARCHAR(300) 	NOT NULL,
	IsRequired		BIT 			NOT NULL,
	IsReadOnly		BIT 			NOT NULL,
	BootStrapSize	VARCHAR(100) 	NOT NULL,
	--	is End Of Line
	IsEOL			BIT 			NOT NULL,
	StartDate		DATETIME 		NOT NULL,
	CurStatus		TINYINT			NOT NULL,
	EditorClass		VARCHAR(255)	NULL,
	FieldClass		VARCHAR(255)	NULL,
	InputType		VARCHAR(255)	NOT NULL,

	CONSTRAINT pk_Input PRIMARY KEY CLUSTERED (pk_Input ),

	--	link input to its parent
	CONSTRAINT Input_fk_form FOREIGN KEY (fk_form) REFERENCES form(pk_form) 
)

--	Properties section
--	Each Input has many properties : see formbuilder font end model schema
--	E.G : TextField has a defaultValue, if it is multiline etc ...

CREATE TABLE InputProperty (

	pk_InputProperty BIGINT IDENTITY(1,1) NOT NULL,	--	primary key

	fk_Input 		BIGINT NOT NULL,

	Name			VARCHAR(255)	NOT NULL,
	Value			VARCHAR(255)	NOT NULL,
	CreationDate	DateTime		NOT NULL,
	ValueType		VARCHAR(10)		NOT NULL CHECK (ValueType IN('Boolean', 'Number', 'Double', 'String'))

	CONSTRAINT pk_InputProperty PRIMARY KEY CLUSTERED (pk_InputProperty )

	-- Link a Property to its Input parent
	CONSTRAINT InputProperty_fk_Input FOREIGN KEY (fk_Input) REFERENCES Input(pk_Input)
)