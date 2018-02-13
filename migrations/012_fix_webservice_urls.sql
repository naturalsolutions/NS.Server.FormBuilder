UPDATE InputProperty
SET value = REPLACE(value, '127.0.0.1', 'track')
WHERE name = 'webServiceURL'
GO

UPDATE InputProperty
SET value = REPLACE(value, '/Thesaurus/api/', '/ThesaurusCore/api/')
WHERE name = 'webServiceURL'
GO
