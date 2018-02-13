Declare @Cons_Name NVARCHAR(100)
Declare @Str NVARCHAR(500)

SELECT @Cons_Name=name
FROM sys.objects
WHERE type='UQ' AND OBJECT_NAME(parent_object_id) = N'Form';

---- Delete the unique constraint.
SET @Str='ALTER TABLE Form DROP CONSTRAINT ' + @Cons_Name;
Exec (@Str)
GO
