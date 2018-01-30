SET ANSI_NULLS ON
GO

SET QUOTED_IDENTIFIER ON
GO

/****** Object:  Table [dbo].[Language]    Script Date: 24/10/2017 15:30:08 ******/
CREATE TABLE [dbo].[Language](
	[PK_Name] [nvarchar](2) NOT NULL,
	[Label] [nvarchar](100) NOT NULL,
	[Description] [nvarchar](900) DEFAULT '',
 CONSTRAINT [PK_TLanguage] PRIMARY KEY CLUSTERED
(
	[PK_Name] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO

/****** Object:  Table [dbo].[FormTrad]    Script Date: 24/10/2017 15:30:00 ******/
CREATE TABLE [dbo].[FormTrad](
	[PK_formtrad] [bigint] IDENTITY(1,1) NOT FOR REPLICATION NOT NULL,
	[Name] [nvarchar](200) DEFAULT '',
	[Description] [nvarchar](255) DEFAULT '',
	[Keywords] [nvarchar] (255) DEFAULT '',
	[FK_Form] [bigint] NOT NULL,
	[FK_Language] [nvarchar](2) NOT NULL,
 CONSTRAINT [PK_FormLibelle] PRIMARY KEY CLUSTERED
(
	[PK_formtrad] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO

ALTER TABLE [dbo].[FormTrad]  WITH CHECK ADD  CONSTRAINT [FK_FormLibelle_Form] FOREIGN KEY([FK_Form])
REFERENCES [dbo].[Form] ([pk_Form])
GO

ALTER TABLE [dbo].[FormTrad] CHECK CONSTRAINT [FK_FormLibelle_Form]
GO

ALTER TABLE [dbo].[FormTrad]  WITH CHECK ADD  CONSTRAINT [FK_FormLibelle_Language] FOREIGN KEY([FK_Language])
REFERENCES [dbo].[Language] ([PK_Name])
GO

ALTER TABLE [dbo].[FormTrad] CHECK CONSTRAINT [FK_FormLibelle_Language]
GO


insert into Language (PK_Name, Label, Description) VALUES ('fr', 'Français', 'Langue française'), ('en', 'English', 'English language'), ('ar', 'Arabe', '')
insert into FormTrad (FK_Form, FK_Language, Name, Description) select pk_Form, 'fr', LabelFr, descriptionFr FROM Form
insert into FormTrad (FK_Form, FK_Language, Name, Description) select pk_Form, 'en', LabelEn, descriptionEn FROM Form

Alter Table Form Drop column LabelFr
Alter Table Form Drop column LabelEn
Alter Table Form Drop column DescriptionFr
Alter Table Form Drop column DescriptionEn

/****** Object:  Table [dbo].[InputTrad]    Script Date: 26/10/2017 16:31:15 ******/
CREATE TABLE [dbo].[InputTrad](
	[PK_inputtrad] [bigint] IDENTITY(1,1) NOT FOR REPLICATION NOT NULL,
	[Name] [nvarchar](200) DEFAULT '',
	[Help] [nvarchar](200) DEFAULT '',
	[FK_Input] [bigint] NOT NULL,
	[FK_Language] [nvarchar](2) NOT NULL,
	CONSTRAINT [PK_inputtrad] PRIMARY KEY CLUSTERED
		(
			[PK_inputtrad] ASC
		)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]
GO

ALTER TABLE [dbo].[InputTrad]  WITH CHECK ADD  CONSTRAINT [FK_InputLibelle_Input] FOREIGN KEY([FK_Input])
REFERENCES [dbo].[Input] ([pk_Input])
GO

ALTER TABLE [dbo].[InputTrad] CHECK CONSTRAINT [FK_InputLibelle_Input]
GO

ALTER TABLE [dbo].[InputTrad]  WITH CHECK ADD  CONSTRAINT [FK_InputLibelle_Language] FOREIGN KEY([FK_Language])
REFERENCES [dbo].[Language] ([PK_Name])
GO

ALTER TABLE [dbo].[InputTrad] CHECK CONSTRAINT [FK_InputLibelle_Language]
GO

insert into InputTrad ([FK_Input], FK_Language, Name) select pk_Input, 'fr', LabelFr FROM Input
insert into InputTrad ([FK_Input], FK_Language, Name) select pk_Input, 'en', LabelEn FROM Input

Alter Table [Input] Drop column LabelFr
Alter Table [Input] Drop column LabelEn
GO
