
/****** Object:  Table [dbo].[Language]    Script Date: 24/10/2017 15:30:08 ******/
SET ANSI_NULLS ON
GO

SET QUOTED_IDENTIFIER ON
GO

CREATE TABLE [dbo].[Language](
	[PK_Name] [nvarchar](2) NOT NULL,
	[Label] [nvarchar](100) NOT NULL,
	[Description] [nvarchar](900) NULL,
 CONSTRAINT [PK_TLanguage] PRIMARY KEY CLUSTERED 
(
	[PK_Name] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]

GO

/****** Object:  Table [dbo].[FormTrad]    Script Date: 24/10/2017 15:30:00 ******/
SET ANSI_NULLS ON
GO

SET QUOTED_IDENTIFIER ON
GO

CREATE TABLE [dbo].[FormTrad](
	[PK_formtrad] [bigint] IDENTITY(1,1) NOT FOR REPLICATION NOT NULL,
	[Name] [nvarchar](200) NOT NULL,
	[Description] [nvarchar](255) NOT NULL,
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


insert into Language (PK_Name, Label, Description) VALUES ('fr', 'Français', 'Langue française'),('en', 'English', 'English language')
insert into FormTrad (FK_Form, FK_Language, Name, Description) select pk_Form, 'fr', LabelFr, descriptionFr FROM Form
insert into FormTrad (FK_Form, FK_Language, Name, Description) select pk_Form, 'en', LabelEn, descriptionEn FROM Form

Alter Table Form Drop column LabelFr
Alter Table Form Drop column LabelEn
Alter Table Form Drop column DescriptionFr
Alter Table Form Drop column DescriptionEn