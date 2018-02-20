
/****** Object:  StoredProcedure [dbo].[SendDataToReferential]    Script Date: 12/02/2018 11:24:00 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO


ALTER PROCEDURE [dbo].[SendDataToReferential]
	@form_id int
AS
BEGIN
		
		--DECLARE @form_id int SET @form_id = XX ;

		EXEC [pr_ExportFormBuilder_One_Form] @form_id;

		SET @form_id = (SELECT initialID FROM Formbuilder_DEV.dbo.Form WHERE pk_Form = @form_id)

		/********************************************************/
		------- INSERTION DES NOUVEAU PROTOCOLETYPE -------

		INSERT INTO dbo.ProtocoleType  (Name,OriginalId,Status,obsolete)

		SELECT	FI.Name,
				'FormBuilder-' + convert(varchar,FI.ID),
				CASE WHEN fp_grid.Value = '1' then 10 
					WHEN fp_hidden.Value = '1' THEN 6
					ELSE 4 
				END,
				FI.obsolete
		FROM FormBuilderFormsInfos FI
		LEFT JOIN FormbuilderFormProperty fp_grid on FI.ID = fp_grid.fk_form AND fp_grid.name = 'isgrid'
		LEFT JOIN FormbuilderFormProperty fp_hidden on FI.ID = fp_hidden.fk_form AND fp_hidden.name = 'ishiddenprotocol'
		WHERE NOT EXISTS (SELECT * FROM ProtocoleType PT 
					WHERE CONVERT(varchar(250),FI.ID )= REPLACE(PT.OriginalId,'FormBuilder-',''))
			  AND FI.ID = @form_id
 
		-- Gestion de mise à jour des Noms des protocoles existants
		UPDATE PT  SET	Name= FI.Name,
						obsolete = FI.obsolete,
						Status = CASE WHEN fp_grid.Value = 1 then 10 
									WHEN fp_hidden.Value = 1 THEN 6
									ELSE 4
								END
		FROM ProtocoleType PT 
		JOIN FormBuilderFormsInfos FI ON REPLACE(PT.OriginalId,'FormBuilder-','') = FI.ID
		LEFT JOIN FormbuilderFormProperty fp_grid on FI.ID = fp_grid.fk_form AND fp_grid.name = 'isgrid'
		LEFT JOIN FormbuilderFormProperty fp_hidden on FI.ID = fp_hidden.fk_form AND fp_hidden.name = 'ishiddenprotocol'
		AND FI.ID = @form_id


		--- Gestion de la propagation
		DELETE TPropagation WHERE TypeObject =  'Protocole_ERD' and FB_ID = @form_id
		INSERT INTO TPropagation (FB_ID,Source_ID,Instance,TypeObject,Priority,Propagation,Date_Modif,Comment)
		SELECT  FI.ID  , pt.ID, -1 ,'Protocole_ERD',0, Fi.propagate, GETDate(),'From Forbuilder'
		FROM ProtocoleType PT 
		JOIN FormBuilderFormsInfos FI ON REPLACE(PT.OriginalId,'FormBuilder-','') = FI.ID
		AND FI.ID = @form_id


		DELETE TPropagation WHERE TypeObject =  'Forms_ERD' and FB_ID = @form_id
		INSERT INTO TPropagation(FB_ID,Source_ID,Instance,TypeObject,Priority,Propagation,Date_Modif,Comment)
		SELECT  FI.ID  , FI.ID, -1 ,'Forms_ERD',0, Fi.propagate, GETDate(),'From Forbuilder'
		FROM ProtocoleType PT 
		JOIN FormBuilderFormsInfos FI ON REPLACE(PT.OriginalId,'FormBuilder-','') = FI.ID
		AND FI.ID = @form_id


		/********************************************************/
		------ Suppression des liens dynprop _ protocole -----
		DELETE l 
		FROM [ProtocoleType_ObservationDynProp] l
		JOIN ProtocoleType PT ON l.FK_ProtocoleType = PT.ID
		JOIN FormBuilderFormsInfos FI ON REPLACE(PT.OriginalId,'FormBuilder-','') = FI.ID
		AND FI.ID = @form_id


		/********************************************************/
		------ INSERTION DES NOUVELLES DYN PROP --------
		--DECLARE @form_id int SET @form_id = 72;

		INSERT INTO dbo.ObservationDynProp  (Name,TypeProp)
		--OUTPUT INSERTED.ID,INSERTED.NAME,INSERTED.TypeProp INTO @NewDynProp 
		SELECT DISTINCT FI.Name, CASE WHEN FBD.[DynPropType] IS NULL THEN 'String' ELSE FBD.[DynPropType] END--, fipp.*
		FROM FormBuilderInputInfos FI 
		LEFT JOIN [FormBuilderType_DynPropType] FBD ON FBD.[FBType] = FI.type 
				AND (
					[FBInputPropertyName] IS NULL 
					OR (FBD.IsEXISTS =1 AND EXISTS (	SELECT * FROM FormBuilderInputProperty FIP
							Where FIP.fk_input = Fi.ID 
							AND FIP.value = FBD.[FBInputPropertyValue] 
							AND FIP.name = FBD.[FBInputPropertyName]  
							)
						)
					OR (FBD.IsEXISTS =0 AND NOT EXISTS (	SELECT * FROM FormBuilderInputProperty FIP
							Where FIP.fk_input = Fi.ID 
							AND FIP.value = FBD.[FBInputPropertyValue] 
							AND FIP.name = FBD.[FBInputPropertyName]  
							)
						)
					)
		--LEFT JOIN FormBuilderInputProperty fipp ON fipp.fk_input = fi.ID and fipp.name = 'format'
		WHERE EXISTS (SELECT * FROM ProtocoleType PT WHERE REPLACE(PT.OriginalId,'FormBuilder-','') = FI.fk_form)  
		AND NOT EXISTS (SELECT * FROM ObservationDynProp ODP WHERE ODP.Name = FI.name)
		AND FI.name NOT IN  (SELECT name FROM  sys.columns WHERE object_id = OBJECT_ID('dbo.Observation') )
		AND (FBD.BBEditor NOT IN ('ListOfNestedModel', 'GridFormEditor') OR  FBD.BBEditor is null )
		AND FI.type NOT IN ('ListOfNestedModel', 'GridFormEditor', 'SubFormGrid', 'childForm')
		AND FI.fk_form = @form_id

		select * 
		FROM FormBuilderInputProperty fip
		JOIN [FormBuilderType_DynPropType] fb on fip.name = fb.FBInputPropertyName and fip.value = fb.FBInputPropertyValue
		WHERE fip.fk_Input = 1248
		/********************************************************/
		---------- INSERTION DES NOUVELLES DYNPROP/TYPE --------
		--DECLARE @form_id int SET @form_id = 72 ;

		DECLARE @id_curProto int
		INSERT INTO [ProtocoleType_ObservationDynProp]
				([Required]
				,[FK_ProtocoleType]
				,[FK_ObservationDynProp]
				,Locked
				,LinkedTable
				,LinkedField
				,LinkedID
				,LinkSourceID)
		SELECT FI.required, PT.ID,OD.ID,0
		,CASE WHEN Fi.linkedFieldTable != '' AND fi.linkedFieldTable IS NOT NULL THEN FI.linkedFieldTable ELSE NULL END 
		,CASE WHEN Fi.linkedField != '' THEN FI.linkedField ELSE NULL END 
		--,CASE WHEN Fi.linkedFieldIdentifyingColumn != '' THEN FI.linkedFieldIdentifyingColumn ELSE NULL END 
		, 'ID'
		,CASE WHEN FI.linkedFieldTable IS NOT NULL AND Fi.linkedFieldTable != '' THEN 'FK_'+FI.linkedFieldTable
		ELSE NULL END --,fi.name

		FROM FormBuilderInputInfos FI 
		JOIN FormBuilderFormsInfos FF ON FI.fk_form = FF.ID AND FF.ID = @form_id
		JOIN ObservationDynProp OD ON OD.Name = FI.Name
		JOIN ProtocoleType PT ON REPLACE(PT.OriginalId,'FormBuilder-','') = FF.ID 
		WHERE NOT EXISTS (select * from [ProtocoleType_ObservationDynProp] ODN 
					where ODN.FK_ProtocoleType = PT.ID 
					AND ODN.FK_ObservationDynProp = OD.ID) 

		UPDATE FF
		SET internalID = PT.ID
		FROM FormBuilderFormsInfos FF 
		JOIN ProtocoleType PT ON REPLACE(PT.OriginalId,'FormBuilder-','') = FF.ID
		WHERE FF.ID = @form_id


		SELECT @id_curProto = PT.ID FROM FormBuilderFormsInfos FF 
		JOIN ProtocoleType PT ON REPLACE(PT.OriginalId,'FormBuilder-','') = FF.ID
		WHERE FF.ID = @form_id

		EXEC [Pr_FormBuilderUpdateConf_One_Form] @ObjectType = 'Protocole',@id_frontmodule=1,@proto_id = @id_curProto
 
END
