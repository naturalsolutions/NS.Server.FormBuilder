UPDATE IP
SET IP.name = 'defaultPath'
FROM Input I
  INNER JOIN InputProperty IP
    ON IP.fk_Input = I.pk_Input
  WHERE I.type = 'Thesaurus'
    AND IP.name = 'defaultValue'
GO
