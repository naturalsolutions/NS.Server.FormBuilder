ALTER TABLE [dbo].[Form]
  ADD state INT NOT NULL DEFAULT(0),
      initialID INT NOT NULL DEFAULT(0)
GO

UPDATE [dbo].[Form]
  SET state = 1,
      initialID = pk_Form
GO
