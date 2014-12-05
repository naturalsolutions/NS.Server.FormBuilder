--	This script create table for input persistence
--	Each form (see CreateTablesForm.sql file) has many input

-- the current status (curStatus) cans take 3 values : 1 Active, 2 Archived and 4 Deleted

--	Each input has an InputType e.g : a weight field has a float type

CREATE TABLE InputType (

	pk_InputType BIGINT IDENTITY(1,1)	NOT NULL,	--	primary key

	Name		VARCHAR(100)	NOT NULL,
	CurStatus	TINYINT			NOT NULL,

	CONSTRAINT [PK_InputType] PRIMARY KEY CLUSTERED ([PK_InputType] )

)


CREATE TABLE Input (

	pk_Input		BIGINT IDENTITY(1,1) NOT NULL,	--	primary key

	fk_form			BIGINT NOT NULL,	--	foreign key , give parent form id to the input
	fk_TypeInput 	BIGINT NOT NULL,	--	In put type foreign key

	Name			VARCHAR(100) 	NOT NULL,
	LabelFR			VARCHAR(300) 	NOT NULL,
	LabelEN			VARCHAR(300) 	NOT NULL,
	IsRequired		BIT 			NOT NULL,
	IsReadOnly		BIT 			NOT NULL,
	BootStrapSize	VARCHAR(100) 	NOT NULL,
	SizeData		INT 			NOT NULL,
	IsEOL			BIT 			NOT NULL,
	StartDate		DATETIME 		NOT NULL,
	CurStatus		TINYINT			NOT NULL,

	CONSTRAINT pk_Input PRIMARY KEY CLUSTERED (pk_Input ),

	--	constraints
	CONSTRAINT Input_fk_TypeInput 	FOREIGN KEY (fk_TypeInput) 	REFERENCES InputType(pk_InputType),	--	link input to its inputType
	CONSTRAINT Input_fk_form 		FOREIGN KEY (fk_form) 		REFERENCES form(pk_form)			--	link input to its parent

)


--	Properties section
--	Each input has one or many dynamic properties


CREATE TABLE InputDynPropriete (

	pk_InputDynPropriete BIGINT IDENTITY(1,1) NOT NULL,	--	primary key

	Name		VARCHAR(100) NOT NULL,
	TypeProp	VARCHAR(100) NOT NULL,

	CONSTRAINT pk_InputDynPropriete PRIMARY KEY CLUSTERED (pk_InputDynPropriete )

)


CREATE TABLE InputType_DynPropriete (

	pk_InputType_DynPropriete BIGINT IDENTITY(1,1) NOT NULL,	--	primary key

	fk_InputType			BIGINT NOT NULL,
	fk_InputDynPropriete	BIGINT NOT NULL,

	AcceptedValues			VARCHAR(500) 	NULL,
	Recurence				INT 			NOT NULL,	--	-1 no recurence, 0 infinte recurence , positive N : N recurrence allowed
	InfoIHM					VARCHAR(500) 	NULL,

	CONSTRAINT pk_TypeInputDynPropriete PRIMARY KEY CLUSTERED (pk_InputType_DynPropriete),

	--	constraintes
	CONSTRAINT InputTypeDynPropriete_fk_InputType 			FOREIGN KEY (fk_InputType) 			REFERENCES InputType(pk_InputType),
	CONSTRAINT InputTypeDynPropriete_fk_InputDynPropriete 	FOREIGN KEY (fk_InputDynPropriete) 	REFERENCES InputDynPropriete(pk_InputDynPropriete)

)

CREATE UNIQUE INDEX UQ_InputType_DynPropriete ON InputType_DynPropriete(fk_InputType,fk_InputDynPropriete)

CREATE TABLE InputDynValeur (

	pk_InputDynValeur		BIGINT IDENTITY(1,1) NOT NULL,	--	primary key

	fk_InputDynPropriete 	BIGINT NOT NULL,
	fk_Input 				BIGINT NOT NULL,

	DateDebut		DateTime 		NOT NULL,
	ValeurInt		BIGINT  		NULL,
	ValeurFloat		FLOAT  			NULL,
	ValeurDate		DATETIME  		NULL,
	ValeurString	VARCHAR(MAX)  	NULL,
	Parametre		VARCHAR(500) 	NULL,

	CONSTRAINT pk_InputDynValeur PRIMARY KEY CLUSTERED (pk_InputDynValeur),

	--	constraints
	CONSTRAINT InputDynValeur_fk_fk_InputDynPropriete 	FOREIGN KEY (fk_InputDynPropriete) 	REFERENCES InputDynPropriete(pk_InputDynPropriete),
	CONSTRAINT InputDynValeur_fk_Input 					FOREIGN KEY (fk_Input) 				REFERENCES Input(pk_Input)

)