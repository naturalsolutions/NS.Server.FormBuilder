UPDATE IP
SET IP.value = F.pk_Form
FROM Input I, InputProperty IP
  INNER JOIN Form F
    ON F.name = IP.value
  WHERE I.type = 'ChildForm'
    AND ISNUMERIC(IP.value) = 0
    AND IP.name = 'childForm'
    AND IP.fk_Input = Input.pk_Input
GO
