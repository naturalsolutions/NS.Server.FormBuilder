USE [Referentiel_Track_DEV]
GO
/****** Object:  StoredProcedure [dbo].[SendDataToReferential]    Script Date: 30/01/2018 15:23:40 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO

ALTER PROCEDURE [dbo].[SendDataToReferential]
    @formToUpdate int
AS
  BEGIN

    DECLARE @inputsExceptionTable TABLE (inputName varchar(255))
    DECLARE @dopropagate bit = 1

    INSERT INTO @inputsExceptionTable VALUES ('Egg'),
      ('Individual'),
      ('UserReadonly'),
      ('eventDate'),
      ('TSai_PK_ID')

    DECLARE @comparaisonTable TABLE (TrackType varchar(100), FBType varchar(100))

    INSERT INTO @comparaisonTable VALUES ('Entier', 'Number'),
      ('Réel', 'Decimal'),
      ('Base de donnée', 'Autocomplete'),
      ('Compteur', 'NumericRange'),
      ('Texte', 'Text'),
      ('Note', 'TextArea'),
      ('Arbre', 'Position'),
      ('Date', 'Date'),
      ('Heure', 'Select'),
      ('Sous Formulaire', 'ChildForm'),
      ('Thésaurus', 'Thesaurus')

    DECLARE @comparaisonChampLier TABLE (TIndProp varchar(100), ChampLierName varchar(100))

    INSERT INTO @comparaisonChampLier VALUES ('TInd_BagueID', 'Bague d''adulte')
      ,('TInd_BagueJuvenile', 'Bague de juvénile')
      ,('TInd_OeufID', 'Numéro d''oeuf')
      ,('TInd_DateNaissance', 'Date de naissance')
      ,('TInd_Status', 'Statut')
      ,('TInd_Sexe', 'Sexe')
      ,('TInd_Mere', 'Mère')
      ,('TInd_Pere', 'Père')
      ,('TInd_StatusSortie', 'Statut de sortie')
      ,('TInd_DateSortie', 'Date de sortie')
      ,('TInd_Poids', 'Poids')
      ,('TInd_BagueIDRelacher', 'Bague de relâcher')
      ,('TInd_Position', 'Position')
      ,('TInd_Origine', 'Origine')
      ,('TInd_StatusElevage', 'Statut d''élevage')
      ,('TInd_Espece', 'Espèce')
      ,('TInd_Puce', 'Puce')
      ,('TInd_GroupeGenetique', 'Groupe génétique')
      ,('TInd_Sentinelle', 'Sentinelle')

    DECLARE @formStaticProps TABLE (
      [pk_Form] [bigint] NOT NULL,
      [name] [varchar](100) NOT NULL,
      [tag] [varchar](300) NULL,
      [creationDate] [datetime] NOT NULL,
      [modificationDate] [datetime] NULL,
      [curStatus] [int] NOT NULL,
      [obsolete] [bit] NULL,
      [isTemplate] [bit] NOT NULL,
      [context] [varchar](50) NOT NULL,
      [originalID] [bigint] NULL,
      [propagate] [bit] NULL,
      [state] [int] NOT NULL,
      [initialID] [int] NOT NULL
    )
    INSERT INTO @formStaticProps SELECT * FROM Formbuilder.dbo.Form WHERE pk_Form = @formToUpdate

    DECLARE @formTradFr TABLE (
      [Name] [varchar](200) NULL,
      [Description] [varchar](255) NULL
    )
    INSERT INTO @formTradFr SELECT [Name], [Description] FROM Formbuilder.dbo.FormTrad WHERE FK_Form = @formToUpdate AND FK_Language = 'fr'

    DECLARE @formTradEn TABLE (
      [Name] [varchar](200) NULL,
      [Description] [varchar](255) NULL
    )
    INSERT INTO @formTradEn SELECT [Name], [Description] FROM Formbuilder.dbo.FormTrad WHERE FK_Form = @formToUpdate AND FK_Language = 'en'

    DECLARE @originalTrackFormID int
    SELECT @originalTrackFormID = originalID, @dopropagate = [propagate] FROM @formStaticProps

    IF (@originalTrackFormID IS NOT NULL)
      BEGIN
        UPDATE TProtocole SET
          TPro_Titre = f.[name],
          TPro_Titre_LabelFr = fr.Name, TPro_DescriptionFr = fr.Description,
          TPro_Titre_LabelEn = en.Name, TPro_DescriptionEn = en.Description
          FROM @formStaticProps f, @formTradFr fr, @formTradEn en WHERE TProtocole.TPro_PK_ID = @originalTrackFormID
      END
    ELSE
      BEGIN
        INSERT INTO TProtocole SELECT f.[name], fr.Name, en.Name, fr.Description,
                                 '', '', 0, '', '', 0, 0, fr.Description, en.Description
                               FROM @formStaticProps f, @formTradFr fr, @formTradEn en

        SELECT @originalTrackFormID = MAX(TPro_PK_ID) FROM TProtocole
        UPDATE Formbuilder.dbo.Form SET [originalID] = @originalTrackFormID WHERE [pk_Form] = @formToUpdate
        UPDATE @formStaticProps SET [originalID] = @originalTrackFormID
      END

    DECLARE @formDynamicProps TABLE (
      [pk_FormProperty] [bigint] NOT NULL,
      [fk_Form] [bigint] NOT NULL,
      [name] [varchar](255) NOT NULL,
      [value] [varchar](255) NOT NULL,
      [creationDate] [datetime] NOT NULL,
      [valueType] [varchar](10) NOT NULL
    )

    INSERT INTO @formDynamicProps SELECT * FROM Formbuilder.dbo.FormProperty WHERE fk_Form = @formToUpdate

    WHILE EXISTS (SELECT * FROM @formDynamicProps)
      BEGIN
        DECLARE @rowFormDynamicProps TABLE(
          [pk_FormProperty] [bigint] NOT NULL,
          [fk_Form] [bigint] NOT NULL,
          [name] [varchar](255) NOT NULL,
          [value] [varchar](255) NOT NULL,
          [creationDate] [datetime] NOT NULL,
          [valueType] [varchar](10) NOT NULL
        )

        DECLARE @topjumped bit = 0

        INSERT INTO @rowFormDynamicProps SELECT TOP 1 * FROM @formDynamicProps

        DECLARE @propName varchar(255)
        SELECT @propName = [name] FROM @rowFormDynamicProps

        IF (@propName = 'actif')
          BEGIN
            UPDATE TProtocole SET TPro_Actif = [value]
            FROM @rowFormDynamicProps WHERE TProtocole.TPro_PK_ID = @originalTrackFormID
          END
        IF (@propName = 'activite')
          BEGIN
            UPDATE TProtocole SET TPro_Activite = [value]
            FROM @rowFormDynamicProps WHERE TProtocole.TPro_PK_ID = @originalTrackFormID
          END
        IF (@propName = 'frequence')
          BEGIN
            UPDATE TProtocole SET TPro_Frequence = [value]
            FROM @rowFormDynamicProps WHERE TProtocole.TPro_PK_ID = @originalTrackFormID
          END
        IF (@propName = 'groupe')
          BEGIN
            DECLARE @groupvalue VARCHAR(500)
            SELECT @groupvalue = [value] FROM @rowFormDynamicProps

            IF @groupvalue = 'null'
              BEGIN
                SET @groupvalue = NULL
              END

            UPDATE TProtocole SET TPro_Groupe = @groupvalue
            FROM @rowFormDynamicProps WHERE TProtocole.TPro_PK_ID = @originalTrackFormID
          END
        IF (@propName = 'importance')
          BEGIN
            UPDATE TProtocole SET TPro_Importance = [value]
            FROM @rowFormDynamicProps WHERE TProtocole.TPro_PK_ID = @originalTrackFormID
          END
        IF (@propName = 'importapressortie')
          BEGIN
            UPDATE TProtocole SET TPro_ImportApresSortie = [value]
            FROM @rowFormDynamicProps WHERE TProtocole.TPro_PK_ID = @originalTrackFormID
          END
        IF (@propName = 'typeIndividus')
          BEGIN
            UPDATE TProtocole SET TPro_TypeIndividus = [value]
            FROM @rowFormDynamicProps WHERE TProtocole.TPro_PK_ID = @originalTrackFormID
          END

        DELETE FROM @formDynamicProps
        WHERE [pk_FormProperty] = (SELECT [pk_FormProperty] FROM @rowFormDynamicProps)

        DELETE FROM @rowFormDynamicProps
      END

    DECLARE @inputsStaticProps TABLE (
      [pk_Input] [bigint] NOT NULL,
      [fk_form] [bigint] NOT NULL,
      [name] [varchar](100) NOT NULL,
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
      [linkedFieldset] [varchar](100) NULL
    )

    DELETE FROM @inputsStaticProps

    INSERT INTO @inputsStaticProps SELECT * FROM Formbuilder.dbo.Input WHERE fk_Form = @formToUpdate

    WHILE EXISTS (SELECT * FROM @inputsStaticProps)
      BEGIN
        DECLARE @rowInputsStaticProps TABLE(
          [pk_Input] [bigint] NOT NULL,
          [fk_form] [bigint] NOT NULL,
          [name] [varchar](100) NOT NULL,
          [labelFr] [varchar](300) NULL,
          [labelEn] [varchar](300) NULL,
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
          [linkedFieldset] [varchar](100) NULL
        )

        DECLARE @rowInputName varchar(100) = null
        DECLARE @rowInputID bigint = null
        SELECT TOP 1 @rowInputName = name, @rowInputID = pk_Input FROM @inputsStaticProps

        DECLARE @rowInputLabelFr varchar(200) = (
          SELECT [Name] FROM Formbuilder.dbo.InputTrad WHERE FK_Input = @rowInputID AND FK_Language = 'fr'
        )
        DECLARE @rowInputLabelEn varchar(200) = (
          SELECT [Name] FROM Formbuilder.dbo.InputTrad WHERE FK_Input = @rowInputID AND FK_Language = 'en'
        )


        INSERT INTO @rowInputsStaticProps
        ([pk_Input], [fk_form], [name], [editMode], [fieldSize], [atBeginingOfLine], [startDate],
         [curStatus], [order], [type], [editorClass], [fieldClassEdit], [fieldClassDisplay], [originalID],
         [linkedFieldTable], [linkedField],[linkedFieldset])
          SELECT TOP 1 * FROM @inputsStaticProps
        UPDATE @rowInputsStaticProps SET [labelFr] = @rowInputLabelFr, [labelEn] = @rowInputLabelEn

        DECLARE @track_ttypebase_id int
        SELECT @track_ttypebase_id = TTBse_PK_ID
        FROM TTTypeBase
        WHERE TTBse_Nom = (
          SELECT TrackType
          FROM @comparaisonTable
          WHERE FBType = (
            SELECT [type]
            FROM @rowInputsStaticProps
          )
        )

        DECLARE @checkInputException varchar(100) = NULL

        SELECT @checkInputException = IET.inputName FROM @inputsExceptionTable IET
          JOIN @rowInputsStaticProps RISP ON IET.inputName = RISP.name

        IF @checkInputException IS NULL
          BEGIN

            DECLARE @originalTrackInputID int
            DECLARE @inputType varchar(100)

            SELECT @originalTrackInputID = originalID, @inputType = [type] FROM @rowInputsStaticProps

            DECLARE @isNullOk int
            DECLARE @isConst int
            SELECT @isNullOk = [editMode], @isConst = [editMode] FROM @rowInputsStaticProps
            IF (@isNullOk > 3 AND @isNullOk < 8) OR (@isNullOk - 8) > 3
              BEGIN
                SET @isNullOk = 1
              END
            ELSE
              BEGIN
                SET @isNullOk = 0
              END

            IF (@isConst = 2 OR @isConst = 3 OR @isConst = 6 OR @isConst = 7 OR @isConst = 10 OR
                @isConst = 11 OR @isConst = 14 OR @isConst = 15)
              BEGIN
                SET @isConst = 0
              END
            ELSE
              BEGIN
                SET @isConst = 1
              END

            DECLARE @typeTogive TABLE(
              [TTyp_PK_ID] [int] NOT NULL,
              [TTyp_Nom] [nvarchar](50) NOT NULL,
              [TTyp_Nom_LabelFr] [nvarchar](50) NULL,
              [TTyp_Nom_LabelEn] [nvarchar](50) NULL,
              [TTyp_FK_TTBse_ID] [int] NOT NULL,
              [TTyp_SQL] [nvarchar](500) NULL,
              [TTyp_Masque] [nvarchar](50) NULL,
              [TTyp_ValeurMin] [nvarchar](255) NULL,
              [TTyp_ValeurMax] [nvarchar](255) NULL,
              [TTyp_NbCaractereMax] [int] NULL,
              [TTyp_FK_TPro_ID] [int] NULL,
              [TTyp_FK_TTop_ID] [int] NULL
            )

            DELETE FROM @typeTogive

            IF (@originalTrackInputID IS NOT NULL)
              BEGIN
                ---- UPDATE EXISTING INPUT

                INSERT INTO @typeTogive SELECT * FROM TType WHERE TTyp_PK_ID = (SELECT TObs_FK_TTypID FROM TObservation WHERE TObservation.TObs_PK_ID = @originalTrackInputID)

                ---- UPDATE BaseType in case we're coming from a CONVERT
                UPDATE @typeTogive SET TTyp_FK_TTBse_ID = @track_ttypebase_id

                --------------------------------------------

                UPDATE TObservation SET TObs_Titre = [name], TObs_Titre_LabelFr = [labelFr], TObs_Titre_LabelEn = [labelEn],
                  TObs_ChampLier = (SELECT ChampLierName FROM @comparaisonChampLier WHERE TIndProp = [linkedField]), TObs_NullOK = @isNullOk,
                  TObs_Ordre = [order], TObs_FK_TProID = @originalTrackFormID, TObs_EstConstante = @isConst
                FROM @rowInputsStaticProps WHERE TObservation.TObs_PK_ID = @originalTrackInputID

              END
            ELSE
              BEGIN
                ---- CREATE NEW INPUT

                INSERT INTO @typeTogive VALUES (0, 'FB_GEN_ShouldNotAppear','FB_GEN_FR_ShouldNotAppear', 'FB_GEN_EN_ShouldNotAppear',
                                                   @track_ttypebase_id, '', '', '', '', 0, NULL, NULL)

                DECLARE @tmpTypID INT
                SELECT TOP 1 @tmpTypID = [TTyp_PK_ID] FROM TType

                INSERT INTO TObservation SELECT [name], [labelFr], [labelEn], '', [linkedField], NULL, @isNullOk, [order],
                                           @originalTrackFormID, @tmpTypID, @isConst, NULL, NULL
                                         FROM @rowInputsStaticProps

                SELECT @originalTrackInputID = MAX(TObs_PK_ID) FROM TObservation

                UPDATE Formbuilder.dbo.Input SET [originalID] = @originalTrackInputID WHERE [pk_Input] = (SELECT [pk_Input] FROM @rowInputsStaticProps)
                UPDATE @rowInputsStaticProps SET [originalID] = @originalTrackInputID
              END

            DECLARE @inputsDynamicProps TABLE (
              [pk_InputProperty] [bigint] NOT NULL,
              [fk_Input] [bigint] NOT NULL,
              [name] [varchar](255) NOT NULL,
              [value] [varchar](5000) NOT NULL,
              [creationDate] [datetime] NOT NULL,
              [valueType] [varchar](10) NOT NULL
            )

            INSERT INTO @inputsDynamicProps SELECT * FROM Formbuilder.dbo.InputProperty WHERE [fk_Input] = (SELECT [pk_Input] FROM @rowInputsStaticProps)

            DECLARE @isSql bit = 0

            WHILE EXISTS (SELECT * FROM @inputsDynamicProps)
              BEGIN
                DECLARE @rowInputsDynamicProps TABLE(
                  [pk_InputProperty] [bigint] NOT NULL,
                  [fk_Input] [bigint] NOT NULL,
                  [name] [varchar](255) NOT NULL,
                  [value] [varchar](5000) NOT NULL,
                  [creationDate] [datetime] NOT NULL,
                  [valueType] [varchar](10) NOT NULL
                )

                DECLARE @jumped bit = 0

                INSERT INTO @rowInputsDynamicProps SELECT TOP 1 * FROM @inputsDynamicProps

                DECLARE @inputName varchar(255)
                SELECT @inputName = name FROM @rowInputsDynamicProps

                IF @inputName = 'trackType' AND 1 = 0
                  BEGIN
                    DECLARE @trackTypeValue VARCHAR(250)
                    SELECT @trackTypeValue = value FROM @rowInputsDynamicProps

                    IF (@trackTypeValue = 'normal')
                      BEGIN
                        UPDATE TObservation SET TObs_FK_TTypID = (
                          SELECT TTyp_PK_ID
                          FROM [TType]
                          WHERE TTyp_Nom = [value]
                                AND TTyp_FK_TTBse_ID = @track_ttypebase_id
                        )
                        FROM @rowInputsDynamicProps WHERE TObservation.TObs_PK_ID = @originalTrackInputID
                      END
                    ELSE
                      BEGIN
                        UPDATE TObservation SET TObs_FK_TTypID = (SELECT TOP 1 TTyp_PK_ID FROM [TType] WHERE TTyp_Nom = [value])
                        FROM @rowInputsDynamicProps WHERE TObservation.TObs_PK_ID = @originalTrackInputID
                      END
                  END

                IF @inputType = 'Autocomplete'
                  BEGIN
                    IF @inputName = 'defaultValue'
                      BEGIN
                        UPDATE @typeTogive SET TTyp_SQL = [value]
                        FROM @rowInputsDynamicProps
                      END
                    IF @inputName = 'help'
                      BEGIN
                        ---- Might need the TType management implemented in Formbuilder to be set
                        SET @jumped = 1
                      END
                    IF @inputName = 'isSQL'
                      BEGIN
                        SELECT @isSql = [value]
                        FROM @rowInputsDynamicProps
                      END
                    IF @inputName = 'triggerlength'
                      BEGIN
                        ---- Might need the TType management implemented in Formbuilder to be set
                        SET @jumped = 1
                      END
                    IF @inputName = 'url'
                      BEGIN
                        IF @isSql = 1
                          BEGIN
                            UPDATE @typeTogive SET TTyp_SQL = [value]
                            FROM @rowInputsDynamicProps
                          END
                      END
                  END

                IF @inputType = 'ChildForm'
                  BEGIN
                    IF @inputName = 'childForm'
                      BEGIN
                        ---- Might need the TType management implemented in Formbuilder to be set
                        SET @jumped = 1
                      END
                    IF @inputName = 'childFormName'
                      BEGIN
                        UPDATE @typeTogive SET TTyp_FK_TPro_ID = (
                          SELECT TPro_PK_ID
                          FROM TProtocole
                          WHERE TPro_Titre = [value]
                        )
                        FROM @rowInputsDynamicProps
                      END
                    IF @inputName = 'help'
                      BEGIN
                        ---- Might need the TType management implemented in Formbuilder to be set
                        SET @jumped = 1
                      END
                    IF @inputName = 'minimumAppearance'
                      BEGIN
                        ---- Might need the TType management implemented in Formbuilder to be set
                        SET @jumped = 1
                      END
                  END

                IF @inputType = 'Date'
                  BEGIN
                    IF @inputName = 'defaultValue'
                      BEGIN
                        UPDATE @typeTogive SET TTyp_SQL = [value]
                        FROM @rowInputsDynamicProps
                      END
                    IF @inputName = 'format'
                      BEGIN
                        ---- Might need the TType management implemented in Formbuilder to be set
                        SET @jumped = 1
                      END
                    IF @inputName = 'help'
                      BEGIN
                        ---- Might need the TType management implemented in Formbuilder to be set
                        SET @jumped = 1
                      END
                    IF @inputName = 'isDefaultSQL'
                      BEGIN
                        SELECT @isSql = [value]
                        FROM @rowInputsDynamicProps

                        ---- Dynamically call the result and set the TObs_ValeurDefault with the result ?

                        -- UPDATE TObservation SET TObs_ValeurDefault = [value]
                        -- FROM @rowInputsDynamicProps WHERE TObservation.TObs_PK_ID = @originalTrackInputID
                      END
                  END

                IF @inputType = 'Decimal' OR @inputType = 'Number'
                  BEGIN
                    IF @inputName = 'decimal'
                      BEGIN
                        ---- Might need the TType management implemented in Formbuilder to be set
                        SET @jumped = 1
                      END
                    IF @inputName = 'defaultValue'
                      BEGIN
                        UPDATE TObservation SET TObs_ValeurDefault = [value]
                        FROM @rowInputsDynamicProps
                        WHERE TObservation.TObs_PK_ID = @originalTrackInputID
                              AND [value] <> ''
                      END
                    IF @inputName = 'help'
                      BEGIN
                        ---- Might need the TType management implemented in Formbuilder to be set
                        SET @jumped = 1
                      END
                    IF @inputName = 'maxValue'
                      BEGIN
                        UPDATE @typeTogive SET TTyp_ValeurMax = [value]
                        FROM @rowInputsDynamicProps
                      END
                    IF @inputName = 'minValue'
                      BEGIN
                        UPDATE @typeTogive SET TTyp_ValeurMin = [value]
                        FROM @rowInputsDynamicProps
                      END
                    IF @inputName = 'precision'
                      BEGIN
                        ---- Might need the TType management implemented in Formbuilder to be set
                        SET @jumped = 1
                      END
                    IF @inputName = 'unity'
                      BEGIN
                        UPDATE TObservation SET TObs_Unite = [value]
                        FROM @rowInputsDynamicProps WHERE TObservation.TObs_PK_ID = @originalTrackInputID
                      END
                  END

                IF @inputType = 'Position'
                  BEGIN
                    IF @inputName = 'defaultNode'
                      BEGIN
                        ---- TODO ---- NOT SURE ABOUT THAT ?!
                        UPDATE @typeTogive SET TTyp_FK_TTop_ID = [value]
                        FROM @rowInputsDynamicProps
                      END
                    IF @inputName = 'defaultPath'
                      BEGIN
                        UPDATE TObservation SET TObs_ValeurDefault = [value]
                        FROM @rowInputsDynamicProps
                        WHERE TObservation.TObs_PK_ID = @originalTrackInputID
                              AND [value] <> ''
                      END
                    IF @inputName = 'positionPath'
                      BEGIN
                        ---- Might need the TType management implemented in Formbuilder to be set
                        SET @jumped = 1
                      END
                    IF @inputName = 'webServiceURL'
                      BEGIN
                        ---- Might need the TType management implemented in Formbuilder to be set
                        SET @jumped = 1
                      END
                  END

                IF @inputType = 'Select'
                  BEGIN
                    IF @inputName = 'choices'
                      BEGIN
                        ---- Might need the TType management implemented in Formbuilder to be set
                        SET @jumped = 1
                      END
                    IF @inputName = 'defaultValue'
                      BEGIN
                        UPDATE @typeTogive SET TTyp_SQL = [value]
                        FROM @rowInputsDynamicProps
                      END
                    IF @inputName = 'isDefaultSQL'
                      BEGIN
                        SELECT @isSql = [value]
                        FROM @rowInputsDynamicProps

                        ---- Might need the TType management implemented in Formbuilder to be set
                      END
                  END

                IF @inputType = 'Text' OR @inputType = 'TextArea'
                  BEGIN
                    IF @inputName = 'defaultValue'
                      BEGIN
                        UPDATE @typeTogive SET TTyp_SQL = [value]
                        FROM @rowInputsDynamicProps
                      END
                    IF @inputName = 'help'
                      BEGIN
                        ---- Might need the TType management implemented in Formbuilder to be set
                        SET @jumped = 1
                      END
                    IF @inputName = 'isDefaultSQL'
                      BEGIN
                        SELECT @isSql = [value]
                        FROM @rowInputsDynamicProps

                        If @isSql = 0
                          begin
                            UPDATE TObservation SET TObs_ValeurDefault = (select TOP(1)TTyp_SQL from @typeTogive) where TObservation.TObs_PK_ID = @originalTrackInputID
                            UPDATE @typeTogive SET TTyp_SQL = NULL
                          end
                        ---- Dynamically call the result and set the TObs_ValeurDefault with the result ?

                        -- UPDATE TObservation SET TObs_ValeurDefault = [value]
                        -- FROM @rowInputsDynamicProps WHERE TObservation.TObs_PK_ID = @originalTrackInputID
                      END
                    IF @inputName = 'valuesize'
                      BEGIN

                        SET @jumped = 1
                      END
                    IF @inputName = 'minLength'
                      BEGIN
                        SET @jumped = 1
                      END
                    IF @inputName = 'maxLength'
                      BEGIN
                        UPDATE @typeTogive SET TTyp_NbCaractereMax = [value]
                        FROM @rowInputsDynamicProps
                      END
                  END

                IF @inputType = 'Thesaurus'
                  BEGIN
                    IF @inputName = 'defaultNode'
                      BEGIN
                        UPDATE @typeTogive SET TTyp_FK_TTop_ID = [value]
                        FROM @rowInputsDynamicProps
                      END
                    IF @inputName = 'defaultPath'
                      BEGIN
                        UPDATE TObservation SET TObs_ValeurDefault = [value]
                        FROM @rowInputsDynamicProps
                        WHERE TObservation.TObs_PK_ID = @originalTrackInputID
                              AND [value] <> ''
                      END
                    IF @inputName = 'fullpath'
                      BEGIN
                        ---- Might need the TType management implemented in Formbuilder to be set
                        SET @jumped = 1
                      END
                    IF @inputName = 'iscollapsed'
                      BEGIN
                        ---- Might need the TType management implemented in Formbuilder to be set
                        SET @jumped = 1
                      END
                    IF @inputName = 'webServiceURL'
                      BEGIN
                        ---- Might need the TType management implemented in Formbuilder to be set
                        SET @jumped = 1
                      END
                  END

                DELETE FROM @inputsDynamicProps
                WHERE [pk_InputProperty] = (SELECT [pk_InputProperty] FROM @rowInputsDynamicProps)

                DELETE FROM @rowInputsDynamicProps
              END

            DECLARE @finalTypeID int = null

            SELECT TOP 1 @finalTypeID = t1.TTyp_PK_ID
            FROM TType t1, @typeTogive t2
            WHERE 1 = 1 -- t1.[TTyp_PK_ID] = t2.[TTyp_PK_ID]
                  AND t1.[TTyp_FK_TTBse_ID] = t2.[TTyp_FK_TTBse_ID]
                  AND (t1.[TTyp_SQL] = t2.[TTyp_SQL] OR (t1.[TTyp_SQL] IS NULL AND t2.[TTyp_SQL] IS NULL))
                  AND (t1.[TTyp_Masque] = t2.[TTyp_Masque] OR (t1.[TTyp_Masque] IS NULL AND t2.[TTyp_Masque] IS NULL))
                  AND (t1.[TTyp_ValeurMin] = t2.[TTyp_ValeurMin] OR (t1.[TTyp_ValeurMin] IS NULL AND t2.[TTyp_ValeurMin] IS NULL))
                  AND (t1.[TTyp_ValeurMax] = t2.[TTyp_ValeurMax] OR (t1.[TTyp_ValeurMax] IS NULL AND t2.[TTyp_ValeurMax] IS NULL))
                  AND (t1.[TTyp_NbCaractereMax] = t2.[TTyp_NbCaractereMax] OR (t1.[TTyp_NbCaractereMax] IS NULL AND t2.[TTyp_NbCaractereMax] IS NULL))
                  AND (t1.[TTyp_FK_TPro_ID] = t2.[TTyp_FK_TPro_ID] OR (t1.[TTyp_FK_TPro_ID] IS NULL AND t2.[TTyp_FK_TPro_ID] IS NULL))
                  AND (t1.[TTyp_FK_TTop_ID] = t2.[TTyp_FK_TTop_ID] OR (t1.[TTyp_FK_TTop_ID] IS NULL AND t2.[TTyp_FK_TTop_ID] IS NULL))


            IF @finalTypeID IS NOT NULL
              BEGIN
                print('updating type with ' + str(@finalTypeID))

                UPDATE TObservation SET TObs_FK_TTypID = @finalTypeID
                WHERE TObservation.TObs_PK_ID = @originalTrackInputID
              END
            ELSE
              BEGIN
                DECLARE @originalID int
                SELECT @originalID = TTyp_pk_id FROM @typeTogive

                DECLARE @OutputID TABLE (ID INT)
                DELETE FROM @OutputID

                print('inserting new type !!')

                DECLARE @currTimestamp VARCHAR(50) = DATEDIFF(SECOND, '19891130', CURRENT_TIMESTAMP)

                INSERT INTO TType
                OUTPUT INSERTED.TTyp_PK_ID INTO @OutputID(ID)
                  SELECT
                    LEFT('FBGen_'+@currTimestamp+'_For_'+@rowInputName, 49),
                    LEFT('FBFR_For_'+@rowInputName, 49),
                    LEFT('FBEN_For_'+@rowInputName, 49),
                    [TTyp_FK_TTBse_ID],
                    [TTyp_SQL],
                    [TTyp_Masque],
                    [TTyp_ValeurMin],
                    [TTyp_ValeurMax],
                    [TTyp_NbCaractereMax],
                    [TTyp_FK_TPro_ID],
                    [TTyp_FK_TTop_ID] FROM @typeTogive

                declare @toshoid int
                SELECT @toshoid = ID FROM @OutputID

                print('associating new type with ' + str(@toshoid))

                UPDATE TObservation SET TObs_FK_TTypID = (SELECT ID FROM @OutputID)
                WHERE TObservation.TObs_PK_ID = @originalTrackInputID

                IF @originalID IS NOT NULL
                  BEGIN
                    print('deleting orphan types !!')

                    DELETE FROM TType WHERE TTyp_PK_ID not in (
                      SELECT TTyp_PK_ID FROM TType t WHERE t.TTyp_PK_ID IN (SELECT o.TObs_FK_TTypID FROM TObservation o))
                  END
              END
          END



        DELETE FROM @inputsStaticProps
        WHERE [pk_Input] = (SELECT [pk_Input] FROM @rowInputsStaticProps)

        DELETE FROM @rowInputsStaticProps
      END

    ---- Remove deleted inputs
    DECLARE @existingInputs TABLE (
      [TObs_PK_ID] [bigint] NULL,
      TObs_Titre varchar(500) NULL
    )
    INSERT INTO @existingInputs SELECT [TObs_PK_ID], TObs_Titre FROM TObservation WHERE TObs_FK_TProID = @originalTrackFormID

    WHILE EXISTS (SELECT * FROM @existingInputs)
      BEGIN
        DECLARE @existingInputID BIGINT
        SELECT TOP 1 @existingInputID = [TObs_PK_ID] FROM @existingInputs

        DECLARE @existsInFB BIGINT
        -- filter out inactive forms (state != 1)
        SELECT @existsInFB = i.pk_Input FROM Formbuilder.dbo.Input i, Formbuilder.dbo.Form f
        WHERE i.[originalID] = @existingInputID
        AND   i.[fk_form] = f.[pk_Form]
        AND   f.[state] = 1

        IF @existsInFB IS NULL
          BEGIN
            DELETE FROM TObservation WHERE [TObs_PK_ID] = @existingInputID
          END

        SET @existsInFB = NULL

        DELETE FROM @existingInputs
        WHERE [TObs_PK_ID] = @existingInputID
      END

    IF @dopropagate = 0
      BEGIN
        DECLARE @propagationUnpropagateDefaultExists INT

        SELECT @propagationUnpropagateDefaultExists = Pk_ID FROM TPropagation
        WHERE FB_ID = @formToUpdate
              AND Source_ID = @originalTrackFormID
              AND Propagation = '0'
              AND [Priority] = '-1'
              AND TypeObject = 'ProtocoleTrack'

        IF (@propagationUnpropagateDefaultExists IS NULL)
          BEGIN
            INSERT INTO TPropagation VALUES (@formToUpdate, @originalTrackFormID, '-1', 'ProtocoleTrack', '-1', '0', GETDATE(), 'Default Track Propagation Setup OFF')
          END
      END
    ELSE
      BEGIN
        DELETE FROM TPropagation WHERE FB_ID = @formToUpdate AND Source_ID = @originalTrackFormID AND Propagation = 0
      END

  END
