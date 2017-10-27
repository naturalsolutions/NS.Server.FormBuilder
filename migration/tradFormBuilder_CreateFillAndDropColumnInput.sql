USE [Formbuilder_Renecore]
GO

/****** Object:  Table [dbo].[FormTrad]    Script Date: 26/10/2017 16:31:15 ******/
SET ANSI_NULLS ON
GO

SET QUOTED_IDENTIFIER ON
GO

CREATE TABLE [dbo].[InputTrad](
	[PK_inputtrad] [bigint] IDENTITY(1,1) NOT FOR REPLICATION NOT NULL,
	[Name] [nvarchar](200) NOT NULL,	
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
