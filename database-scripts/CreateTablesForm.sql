--	This script create table for the formbuilder persistence
--	The main table is the Form table

--	A form has many keywords and a keyword cans belong to many forms

-- the current status (curStatus) cans take 3 values : 1 Active, 2 Archived and 4 Deleted

CREATE TABLE Form (

	pk_Form			BIGINT IDENTITY(1,1) NOT NULL,	--	primary key

	Name			VARCHAR(100) 	NOT NULL,
	LabelFR			VARCHAR(300) 	NOT NULL,
	LabelEN			VARCHAR(300) 	NOT NULL,
	CreationDate	DATETIME 		NOT NULL,
	ModifDate		DATETIME 		NULL,
	CurStatus		TINYINT			NOT NULL,
	Comment			VARCHAR(MAX) 	NOT NULL

	CONSTRAINT pk_Form PRIMARY KEY CLUSTERED (pk_Form )
)


CREATE TABLE KeyWord (

	pk_KeyWord			BIGINT IDENTITY(1,1) NOT NULL,	-- primary key

	Name				VARCHAR(100) 	NOT NULL UNIQUE,
	CreationDate		DATETIME 		NOT NULL,
	ModifDate			DATETIME 		NULL,
	CurStatus			TINYINT			NOT NULL,

	CONSTRAINT pk_KeyWord PRIMARY KEY CLUSTERED (pk_KeyWord )
)


CREATE TABLE KeyWord_Form (

	pk_KeyWord_Form		BIGINT IDENTITY(1,1) NOT NULL,	-- primary key

	fk_KeyWord			BIGINT 		NOT NULL,
	fk_Form				BIGINT 		NOT NULL,
	CreationDate		DATETIME 	NOT NULL,
	CurStatus			TINYINT		NOT NULL,

	CONSTRAINT pk_KeyWord_Form PRIMARY KEY CLUSTERED (pk_KeyWord_Form),

	--	Link forms and keywords
	CONSTRAINT KeyWord_Form_fk_KeyWord	FOREIGN KEY (fk_KeyWord)	REFERENCES KeyWord(pk_KeyWord),	
	CONSTRAINT KeyWord_Form_fk_Form		FOREIGN KEY (fk_Form)		REFERENCES Form(pk_Form)
)


CREATE TABLE Unity (

	pk_Unity	BIGINT IDENTITY(1,1) NOT NULL,	-- primary key

	Name		VARCHAR(300) NOT NULL,
	LabelFR		VARCHAR(300)  NULL,
	LabelEN		VARCHAR(300)  NULL,

	CONSTRAINT pk_Unity PRIMARY KEY CLUSTERED (pk_Unity)
)