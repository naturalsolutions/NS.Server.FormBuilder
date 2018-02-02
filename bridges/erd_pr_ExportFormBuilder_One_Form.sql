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

    DECLARE @initialID int = (SELECT initialID FROM Formbuilder_DEV.dbo.Form WHERE pk_Form = @form_id)

    DELETE ip
    FROM FormBuilderInputProperty ip
      JOIN FormBuilderInputInfos i ON i.ID = ip.fk_Input and i.fk_form = @initialID

    DELETE FormBuilderInputInfos
    WHERE fk_form = @initialID

    DELETE FormBuilderFormProperty
    where fk_form =  @initialID

    DELETE FormBuilderFormsInfos
    where ID =  @initialID

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

      SELECT   @initialID
        ,fo.[name]
        ,[tag]
        ,TradFR.[Name]
        ,TradEN.[Name]
        ,[creationDate]
        ,[modificationDate]
        ,[curStatus]
        ,TradFR.[Description]
        ,TradEN.[Description]
        ,[obsolete]
        ,[propagate]
        ,[isTemplate]
        ,[context]
        ,'Protocole'
      FROM Formbuilder_DEV.dbo.Form fo
        LEFT JOIN Formbuilder_DEV.dbo.FormTrad TradFR ON fo.pk_Form = TradFR.FK_Form AND TradFR.FK_Language = 'fr'
        LEFT JOIN Formbuilder_DEV.dbo.FormTrad TradEN ON fo.pk_Form = TradEN.FK_Form AND TradEN.FK_Language = 'en'
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
        @initialID
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
        ,@initialID
        ,I.[name]
        ,TradFR.[Name]
        ,TradEN.[Name]
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
        LEFT JOIN Formbuilder_DEV.dbo.InputTrad TradFR ON I.pk_Input = TradFR.FK_Input AND TradFR.FK_Language = 'fr'
        LEFT JOIN Formbuilder_DEV.dbo.InputTrad TradEN ON I.pk_Input = TradEN.FK_Input AND TradEN.FK_Language = 'en'
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
      FROM Formbuilder_DEV.[dbo].[InputProperty] IP
      WHERE fk_Input IN (select ID FROM [FormBuilderInputInfos])
            AND EXISTS (SELECT * FROM Formbuilder_DEV.dbo.Input I WHERE I.pk_Input = IP.fk_Input AND I.fk_form = @form_id)

    --SET IDENTITY_INSERT  [FormBuilderInputProperty] OFF;
    --EXEC dbo.[pr_ImportFormBuilder]
  END
