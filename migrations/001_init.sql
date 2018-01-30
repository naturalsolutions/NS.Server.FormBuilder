-- Scripted from original Formbuilder database on renecore


-- USE [Formbuilder]
-- GO

/****** Object:  Table [dbo].[ConfiguratedInput]    Script Date: 15/01/2018 15:01:57 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
SET ANSI_PADDING ON
GO
CREATE TABLE [dbo].[ConfiguratedInput](
	[pk_ConfiguratedInput] [bigint] IDENTITY(1,1) NOT NULL,
	[name] [varchar](100) NOT NULL,
	[labelFr] [varchar](300) NOT NULL,
	[labelEn] [varchar](300) NOT NULL,
	[editMode] [int] NOT NULL,
	[fieldSize] [varchar](100) NOT NULL,
	[atBeginingOfLine] [bit] NOT NULL,
	[startDate] [datetime] NOT NULL,
	[curStatus] [int] NOT NULL,
	[type] [varchar](100) NOT NULL,
	[editorClass] [varchar](100) NULL,
	[fieldClassEdit] [varchar](100) NULL,
	[fieldClassDisplay] [varchar](100) NULL,
	[originalID] [bigint] NULL,
	[linkedFieldTable] [varchar](100) NULL,
	[linkedField] [varchar](100) NULL,
	[linkedFieldset] [varchar](100) NULL,
PRIMARY KEY CLUSTERED 
(
	[pk_ConfiguratedInput] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]

GO
SET ANSI_PADDING OFF
GO
/****** Object:  Table [dbo].[ConfiguratedInputProperty]    Script Date: 15/01/2018 15:01:57 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
SET ANSI_PADDING ON
GO
CREATE TABLE [dbo].[ConfiguratedInputProperty](
	[pk_ConfiguratedInputProperty] [bigint] IDENTITY(1,1) NOT NULL,
	[fk_ConfiguratedInput] [bigint] NOT NULL,
	[name] [varchar](255) NOT NULL,
	[value] [varchar](5000) NOT NULL,
	[creationDate] [datetime] NOT NULL,
	[valueType] [varchar](10) NOT NULL,
PRIMARY KEY CLUSTERED 
(
	[pk_ConfiguratedInputProperty] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]

GO
SET ANSI_PADDING OFF
GO
/****** Object:  Table [dbo].[Fieldset]    Script Date: 15/01/2018 15:01:57 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
SET ANSI_PADDING ON
GO
CREATE TABLE [dbo].[Fieldset](
	[pk_Fieldset] [bigint] IDENTITY(1,1) NOT NULL,
	[fk_form] [bigint] NOT NULL,
	[legend] [varchar](255) NOT NULL,
	[fields] [varchar](255) NOT NULL,
	[multiple] [bit] NULL,
	[curStatus] [int] NOT NULL,
	[refid] [varchar](255) NOT NULL,
	[order] [smallint] NOT NULL,
PRIMARY KEY CLUSTERED 
(
	[pk_Fieldset] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]

GO
SET ANSI_PADDING OFF
GO
/****** Object:  Table [dbo].[Form]    Script Date: 15/01/2018 15:01:57 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
SET ANSI_PADDING ON
GO
CREATE TABLE [dbo].[Form](
	[pk_Form] [bigint] IDENTITY(1,1) NOT NULL,
	[name] [varchar](100) NOT NULL,
	[tag] [varchar](300) NULL,
	[labelFr] [varchar](300) NOT NULL,
	[labelEn] [varchar](300) NOT NULL,
	[creationDate] [datetime] NOT NULL,
	[modificationDate] [datetime] NULL,
	[curStatus] [int] NOT NULL,
	[descriptionFr] [varchar](300) NOT NULL,
	[descriptionEn] [varchar](300) NOT NULL,
	[obsolete] [bit] NOT NULL,
	[isTemplate] [bit] NOT NULL,
	[context] [varchar](50) NOT NULL,
	[originalID] [bigint] NULL,
	[propagate] [bit] NOT NULL,
PRIMARY KEY CLUSTERED 
(
	[pk_Form] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY],
UNIQUE NONCLUSTERED 
(
	[name] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]

GO
SET ANSI_PADDING OFF
GO
/****** Object:  Table [dbo].[FormFile]    Script Date: 15/01/2018 15:01:57 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
SET ANSI_PADDING ON
GO
CREATE TABLE [dbo].[FormFile](
	[Pk_ID] [bigint] IDENTITY(1,1) NOT NULL,
	[fk_form] [bigint] NOT NULL,
	[name] [varchar](300) NULL,
	[filedata] [varbinary](max) NOT NULL,
PRIMARY KEY CLUSTERED 
(
	[Pk_ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY] TEXTIMAGE_ON [PRIMARY]

GO
SET ANSI_PADDING OFF
GO
/****** Object:  Table [dbo].[FormProperty]    Script Date: 15/01/2018 15:01:57 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
SET ANSI_PADDING ON
GO
CREATE TABLE [dbo].[FormProperty](
	[pk_FormProperty] [bigint] IDENTITY(1,1) NOT NULL,
	[fk_Form] [bigint] NOT NULL,
	[name] [varchar](255) NOT NULL,
	[value] [varchar](255) NOT NULL,
	[creationDate] [datetime] NOT NULL,
	[valueType] [varchar](10) NOT NULL,
PRIMARY KEY CLUSTERED 
(
	[pk_FormProperty] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]

GO
SET ANSI_PADDING OFF
GO
/****** Object:  Table [dbo].[Input]    Script Date: 15/01/2018 15:01:57 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
SET ANSI_PADDING ON
GO
CREATE TABLE [dbo].[Input](
	[pk_Input] [bigint] IDENTITY(1,1) NOT NULL,
	[fk_form] [bigint] NOT NULL,
	[name] [varchar](100) NOT NULL,
	[labelFr] [varchar](300) NOT NULL,
	[labelEn] [varchar](300) NOT NULL,
	[editMode] [int] NOT NULL,
	[fieldSize] [varchar](100) NOT NULL,
	[atBeginingOfLine] [bit] NOT NULL,
	[startDate] [datetime] NOT NULL,
	[curStatus] [int] NOT NULL,
	[order] [smallint] NULL,
	[type] [varchar](100) NOT NULL,
	[editorClass] [varchar](100) NULL,
	[fieldClassEdit] [varchar](100) NULL,
	[fieldClassDisplay] [varchar](100) NULL,
	[originalID] [bigint] NULL,
	[linkedFieldTable] [varchar](100) NULL,
	[linkedField] [varchar](100) NULL,
	[linkedFieldset] [varchar](100) NULL,
PRIMARY KEY CLUSTERED 
(
	[pk_Input] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]

GO
SET ANSI_PADDING OFF
GO
/****** Object:  Table [dbo].[InputProperty]    Script Date: 15/01/2018 15:01:57 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
SET ANSI_PADDING ON
GO
CREATE TABLE [dbo].[InputProperty](
	[pk_InputProperty] [bigint] IDENTITY(1,1) NOT NULL,
	[fk_Input] [bigint] NOT NULL,
	[name] [varchar](255) NOT NULL,
	[value] [varchar](5000) NOT NULL,
	[creationDate] [datetime] NOT NULL,
	[valueType] [varchar](10) NOT NULL,
PRIMARY KEY CLUSTERED 
(
	[pk_InputProperty] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]

GO
SET ANSI_PADDING OFF
GO
/****** Object:  Table [dbo].[KeyWord]    Script Date: 15/01/2018 15:01:57 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
SET ANSI_PADDING ON
GO
CREATE TABLE [dbo].[KeyWord](
	[pk_KeyWord] [bigint] IDENTITY(1,1) NOT NULL,
	[name] [varchar](100) NOT NULL,
	[creationDate] [datetime] NOT NULL,
	[modificationDate] [datetime] NULL,
	[curStatus] [int] NOT NULL,
	[lng] [varchar](2) NOT NULL,
PRIMARY KEY CLUSTERED 
(
	[pk_KeyWord] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]

GO
SET ANSI_PADDING OFF
GO
/****** Object:  Table [dbo].[KeyWord_Form]    Script Date: 15/01/2018 15:01:57 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
CREATE TABLE [dbo].[KeyWord_Form](
	[pk_KeyWord_Form] [bigint] IDENTITY(1,1) NOT NULL,
	[fk_KeyWord] [bigint] NOT NULL,
	[fk_Form] [bigint] NOT NULL,
	[creationDate] [datetime] NOT NULL,
	[curStatus] [int] NOT NULL,
PRIMARY KEY CLUSTERED 
(
	[pk_KeyWord_Form] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]

GO
/****** Object:  Table [dbo].[Propagation]    Script Date: 15/01/2018 15:01:57 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
SET ANSI_PADDING ON
GO
CREATE TABLE [dbo].[Propagation](
	[Pk_ID] [bigint] IDENTITY(1,1) NOT NULL,
	[FB_ID] [bigint] NULL,
	[Source_ID] [bigint] NOT NULL,
	[Instance] [varchar](100) NOT NULL,
	[TypeObject] [varchar](100) NOT NULL,
	[Priority] [int] NOT NULL,
	[Propagation] [int] NOT NULL,
	[Date_Modif] [datetime] NULL,
	[Comment] [varchar](500) NULL,
PRIMARY KEY CLUSTERED 
(
	[Pk_ID] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]

GO
SET ANSI_PADDING OFF
GO
/****** Object:  Table [dbo].[Unity]    Script Date: 15/01/2018 15:01:57 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO
SET ANSI_PADDING ON
GO
CREATE TABLE [dbo].[Unity](
	[pk_Unity] [bigint] IDENTITY(1,1) NOT NULL,
	[name] [varchar](100) NOT NULL,
	[labelFr] [varchar](300) NULL,
	[labelEn] [varchar](300) NULL,
	[context] [varchar](50) NOT NULL,
	[ordre] [int] NOT NULL,
PRIMARY KEY CLUSTERED 
(
	[pk_Unity] ASC
)WITH (PAD_INDEX = OFF, STATISTICS_NORECOMPUTE = OFF, IGNORE_DUP_KEY = OFF, ALLOW_ROW_LOCKS = ON, ALLOW_PAGE_LOCKS = ON) ON [PRIMARY]
) ON [PRIMARY]

GO
SET ANSI_PADDING OFF
GO
ALTER TABLE [dbo].[ConfiguratedInputProperty]  WITH CHECK ADD FOREIGN KEY([fk_ConfiguratedInput])
REFERENCES [dbo].[ConfiguratedInput] ([pk_ConfiguratedInput])
GO
ALTER TABLE [dbo].[Fieldset]  WITH CHECK ADD FOREIGN KEY([fk_form])
REFERENCES [dbo].[Form] ([pk_Form])
GO
ALTER TABLE [dbo].[FormFile]  WITH CHECK ADD FOREIGN KEY([fk_form])
REFERENCES [dbo].[Form] ([pk_Form])
GO
ALTER TABLE [dbo].[FormProperty]  WITH CHECK ADD FOREIGN KEY([fk_Form])
REFERENCES [dbo].[Form] ([pk_Form])
GO
ALTER TABLE [dbo].[Input]  WITH CHECK ADD FOREIGN KEY([fk_form])
REFERENCES [dbo].[Form] ([pk_Form])
GO
ALTER TABLE [dbo].[InputProperty]  WITH CHECK ADD FOREIGN KEY([fk_Input])
REFERENCES [dbo].[Input] ([pk_Input])
GO
ALTER TABLE [dbo].[KeyWord_Form]  WITH CHECK ADD FOREIGN KEY([fk_Form])
REFERENCES [dbo].[Form] ([pk_Form])
GO
ALTER TABLE [dbo].[KeyWord_Form]  WITH CHECK ADD FOREIGN KEY([fk_KeyWord])
REFERENCES [dbo].[KeyWord] ([pk_KeyWord])
GO
ALTER TABLE [dbo].[ConfiguratedInput]  WITH CHECK ADD CHECK  (([atBeginingOfLine]=(1) OR [atBeginingOfLine]=(0)))
GO
ALTER TABLE [dbo].[Fieldset]  WITH CHECK ADD CHECK  (([multiple]=(1) OR [multiple]=(0)))
GO
ALTER TABLE [dbo].[Form]  WITH CHECK ADD CHECK  (([isTemplate]=(1) OR [isTemplate]=(0)))
GO
ALTER TABLE [dbo].[Form]  WITH CHECK ADD CHECK  (([obsolete]=(1) OR [obsolete]=(0)))
GO
ALTER TABLE [dbo].[Form]  WITH CHECK ADD CHECK  (([propagate]=(1) OR [propagate]=(0)))
GO
ALTER TABLE [dbo].[Input]  WITH CHECK ADD CHECK  (([atBeginingOfLine]=(1) OR [atBeginingOfLine]=(0)))
GO
