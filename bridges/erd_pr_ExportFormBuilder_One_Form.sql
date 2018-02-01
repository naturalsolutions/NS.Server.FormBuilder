USE [EcoReleve_ECWP_FOR_Referentiel]
GO
/****** Object:  StoredProcedure [dbo].[pr_ExportFormBuilder_One_Form]    Script Date: 01/02/2018 15:25:09 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO



ALTER PROCEDURE [dbo].[pr_ExportFormBuilder_One_Form]
    @form_id int

AS
  BEGIN

    DELETE ip
    FROM FormBuilderInputProperty ip
      JOIN FormBuilderInputInfos i ON i.ID = ip.fk_Input and i.fk_form = @form_id

    DELETE FormBuilderInputInfos
    WHERE fk_form = @form_id

    DELETE FormBuilderFormProperty
    where fk_form =  @form_id

    DELETE FormBuilderFormsInfos
    where ID =  @form_id

    /**************** INSERT FormsInfos ***********************/

    --SET IDENTITY_INSERT  [FormBuilderFormsInfos] ON;
    INSERT INTO [FormBuilderFormsInfos]
    (ID
      ,[name]
      ,[tag]
      ,[labelFr]
      ,[labelEn]
      ,[creationDate]
      ,[modificationDate]
      ,[curStatus]
      ,[descriptionFr]
      ,[descriptionEn]
      ,[obsolete]
      ,[propagate]
      ,[isTemplate]
      ,[context]
      ,ObjectType)

      SELECT   [pk_Form]
        ,[name]
        ,[tag]
        ,[labelFr]
        ,[labelEn]
        ,[creationDate]
        ,[modificationDate]
        ,[curStatus]
        ,[descriptionFr]
        ,[descriptionEn]
        ,[obsolete]
        ,[propagate]
        ,[isTemplate]
        ,[context]
        ,'Protocole'
      FROM Formbuilder_DEV.dbo.Form fo
      WHERE context = 'ecoreleve' and pk_Form = @form_id
    ;
    --SET IDENTITY_INSERT  [FormBuilderFormsInfos] OFF;
    -- TODO ajouter le nom de l'application


    --SET IDENTITY_INSERT  [FormBuilderFormProperty] ON;
    INSERT INTO [dbo].[FormBuilderFormProperty]
    (--ID,
     [fk_Form]
      ,[name]
      ,[value]
      ,[creationDate]
      ,[valueType])
      SELECT		--pk_FormProperty,
        fp.[fk_Form]
        ,fp.[name]
        ,fp.[value]
        ,fp.[creationDate]
        ,fp.[valueType]
      FROM Formbuilder_DEV.dbo.FormProperty fp
        JOIN Formbuilder_DEV.dbo.Form f ON f.pk_Form = fp.fk_Form AND f.context = 'ecoreleve'
      WHERE fk_Form = @form_id

    /**************** INSERT InputInfos ***********************/

    --SET IDENTITY_INSERT  [FormBuilderInputInfos] ON;
    INSERT INTO [FormBuilderInputInfos]
    (ID
      ,[fk_form]
      ,[name]
      ,[labelFr]
      ,[labelEn]
      ,[required]
      ,[readonly]
      ,[fieldSize]
      ,atBeginingOfLine
      ,[startDate]
      ,[curStatus]
      ,[type]
      ,[editorClass]
      ,[fieldClassEdit]
      ,[fieldClassDisplay]
      ,[linkedFieldTable]
      ,[linkedField]
      ,[order]
      ,Legend
      ,editMode
    )
      SELECT pk_Input
        ,I.[fk_form]
        ,I.[name]
        ,I.[labelFr]
        ,I.[labelEn]
        , CASE WHEN  I.editMode&4 = 0 THEN 1 else 0 END
        ,0
        ,I.[fieldSize]
        ,I.atBeginingOfLine
        ,I.[startDate]
        ,I.[curStatus]
        ,I.[type]
        ,I.[editorClass]
        ,I.[fieldClassEdit]
        ,I.[fieldClassDisplay]
        ,I.[linkedFieldTable]
        ,I.[linkedField]
        ,I.[order]
        ,I.linkedFieldset
        ,I.editMode

      FROM Formbuilder_DEV.dbo.Input I
      --LEFT JOIN Formbuilder_DEV.dbo.InputProperty ip ON I.pk_Input = ip.fk_Input AND I.type = 'Date' AND ip.name = 'format'
      --LEFT JOIN Formbuilder_DEV.dbo.Fieldset F ON I.linkedFieldset = F.refid --and F.pk_Fieldset in (select * from toto)
      WHERE i.fk_form in (select ID from [FormBuilderFormsInfos]) AND I.[curStatus] = 1
            and i.fk_form = @form_id


    --SET IDENTITY_INSERT  [FormBuilderInputInfos] OFF;



    /**************** INSERT InputProperty ***********************/

    --SET IDENTITY_INSERT  [FormBuilderInputProperty] ON;

    INSERT INTO [FormBuilderInputProperty]
    (ID
      ,[fk_Input]
      ,[name]
      ,[value]
      ,[creationDate]
      ,[valueType])
      SELECT [pk_InputProperty]
        ,[fk_Input]
        ,IP.[name]
        ,IP.[value]
        ,IP.[creationDate]
        ,IP.[valueType]
      FROM Formbuilder_DEV.[dbo].[InputProperty] IP WHERE fk_Input in (select ID FROM [FormBuilderInputInfos])
                                                          and EXISTS (select * FROM Formbuilder_DEV.dbo.Input I where I.pk_Input = IP.fk_Input and I.fk_form = @form_id)


    --SET IDENTITY_INSERT  [FormBuilderInputProperty] OFF;

    ---EXEC dbo.[pr_ImportFormBuilder]
  END
