
/****** Object:  StoredProcedure [dbo].[Pr_FormBuilderUpdateConf_One_Form]    Script Date: 12/02/2018 12:35:31 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO



ALTER PROCEDURE [dbo].[Pr_FormBuilderUpdateConf_One_Form]
(
		@ObjectType varchar(255),
		@id_frontmodule BIGINT,
		@proto_id int
)
AS
	BEGIN
			/********************************************************/
			-- SUPPRESSION de la configuration

			--DECLARE @ObjectType varchar(255) SET @ObjectType = 'Protocole'
			--DECLARE @id_frontmodule BIGINT SET @id_frontmodule = 1
			--DECLARE @proto_id int SET @proto_id=241
			IF object_id('tempdb..#oldConf') IS NOT NULL
						DROP TABLE #oldConf

			SELECT * 
			INTO #oldConf
			FROM [ModuleForms] f
			WHERE module_id= @id_frontmodule
			AND TypeObj = @proto_id 

			DELETE f 
			FROM [ModuleForms] f
			WHERE module_id= @id_frontmodule
			AND TypeObj = @proto_id  --and (Locked = 0 or Locked is null) 

			/********************************************************/
			-- INSERTION DE LA CONFIGURATION

			IF object_id('tempdb..#inputsINFOS') IS NOT NULL
						DROP TABLE #inputsINFOS

			SELECT  FF.internalID,
					FI.ID as pk_input,
					CASE WHEN (SELECT Count(*) From ObservationDynProp WHERE Name = FI.name) > 0 THEN (SELECT Name From ObservationDynProp WHERE Name = FI.name)
						 ELSE Fi.name
					END	 as name,
					FI.atBeginingOfLine,
					FI.labelFr,
					FI.required,
					FI.fieldSize,
					CASE WHEN FBD.BBEditor is not null THEN FBD.BBEditor ELSE  FI.type END AS type
					, (CASE WHEN FI.editMode <= 1 THEN FI.editMode 
						WHEN FI.editMode&2 = 0 THEN 1
						WHEN FI.editMode&1 = 0 THEN 0 
						ELSE 7 
						END) + 
						(CASE WHEN isgrid.value = 1 AND FI.[order] < CONVERT(int,nbfixCol.value) THEN 8
						 ELSE 0
						 END)
						 AS editMode,
					'form-control' as editorClass,
					FI.[order],
					CASE WHEN fi.Legend != '' THEN fi.Legend ELSE NULL end Legend,
					Fi.fieldClassDisplay,
					FI.fieldClassEdit,
					FI.curStatus,
					FBD.BBEditor,
					FBD.FBInputPropertyValue,
					FBD.FBInputPropertyName,
					FF.ID aS FormID,
					IPdefVal.value as defaultValue

			INTO #inputsINFOS 
			FROM FormBuilderInputInfos FI 
			JOIN FormBuilderFormsInfos FF ON FI.fk_form = FF.ID
			LEFT JOIN FormBuilderFormProperty isgrid ON isgrid.fk_Form = FF.ID AND isgrid.name ='isgrid'
			LEFT JOIN FormBuilderFormProperty nbfixCol ON nbfixCol.fk_Form = FF.ID AND nbfixCol.name ='nbFixedCol'
			LEFT JOIN FormBuilderType_DynPropType FBD ON FBD.[FBType] = FI.type 
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
			LEFT JOIN FormBuilderInputProperty IPdefVal ON FI.ID =IPdefVal.fk_input AND IPdefVal.name = 'defaultValue'
			WHERE FF.internalID =  @proto_id AND 
			FF.ObjectType = @ObjectType

			/* NUMBER */ 
			INSERT INTO [ModuleForms]
					   ([module_id]
					   ,[TypeObj]
					   ,[Name]
					   ,[Label]
					   ,[Required]
					   ,[FieldSizeEdit]
					   ,[FieldSizeDisplay]
					   ,[InputType]
					   ,[editorClass]
					   ,[FormRender]
					   ,[FormOrder]
					   ,[Legend]
					   ,[Options]
					   ,[Validators]
					   ,[displayClass]
					   ,[EditClass]
					   ,[Status]
					   ,Locked
					   ,DefaultValue
					   )
			SELECT		@id_frontmodule,
						@proto_id,
						i.name,
						i.labelFr,
						i.required,
						i.fieldSize,
						i.fieldSize,
						i.type,
						i.editorClass,
						CASE WHEN i.atBeginingOfLine = 1 THEN i.editMode +32 ELSE i.editMode END as formRender,
						I.[order],
						i.Legend,
						NULL as Options,
						Case WHEN minVal.value != '' AND maxVal.Value != '' 
								THEN '[{"type":"min", "value":'+minVal.value+'},{"type":"max", "value":'+ maxVal.Value+'}]'
							WHEN minVal.value = '' AND maxVal.Value != ''
								THEN '[{"type":"max", "value":'+ maxVal.Value+'}]'
							WHEN minVal.value != '' AND maxVal.Value = ''
								THEN '[{"type":"min", "value":'+ minVal.Value+'}]'
							ELSE NULL
						END  AS Validator,
						i.fieldClassDisplay,
						I.fieldClassEdit,
						I.curStatus,
						0 as locked,
						i.defaultValue
			FROM #inputsINFOS i
			LEFT JOIN [FormBuilderInputProperty] minVal ON i.pk_input = minVal.fk_Input AND minVal.name = 'minValue'
			LEFT JOIN [FormBuilderInputProperty] maxVal ON i.pk_input = maxVal.fk_Input AND maxVal.name = 'maxValue'
			LEFT JOIN [FormBuilderInputProperty] prec ON i.pk_input = prec.fk_Input AND prec.name = 'precision'
			WHERE i.type = 'Number'

			/************* Text ***************/ 
			INSERT INTO [ModuleForms]
					   ([module_id]
					   ,[TypeObj]
					   ,[Name]
					   ,[Label]
					   ,[Required]
					   ,[FieldSizeEdit]
					   ,[FieldSizeDisplay]
					   ,[InputType]
					   ,[editorClass]
					   ,[FormRender]
					   ,[FormOrder]
					   ,[Legend]
					   ,[Options]
					   ,[Validators]
					   ,[displayClass]
					   ,[EditClass]
					   ,[Status]
					   ,Locked
					   ,DefaultValue
					   )
			SELECT		@id_frontmodule,
						@proto_id,
						i.name,
						i.labelFr,
						i.required,
						i.fieldSize,
						i.fieldSize,
						i.type,
						i.editorClass,
						CASE WHEN i.atBeginingOfLine = 1 THEN i.editMode +32 ELSE i.editMode END as formRender,
						I.[order],
						i.Legend,
						NULL as Options,
						NULL  AS Validator,
						i.fieldClassDisplay,
						I.fieldClassEdit,
						I.curStatus,
						0 as locked,
						i.defaultValue
			FROM #inputsINFOS i
			WHERE i.type in ('Text', 'TextArea')

			/************* CheckBox ***************/ 
			INSERT INTO [ModuleForms]
					   ([module_id]
					   ,[TypeObj]
					   ,[Name]
					   ,[Label]
					   ,[Required]
					   ,[FieldSizeEdit]
					   ,[FieldSizeDisplay]
					   ,[InputType]
					   ,[editorClass]
					   ,[FormRender]
					   ,[FormOrder]
					   ,[Legend]
					   ,[Options]
					   ,[Validators]
					   ,[displayClass]
					   ,[EditClass]
					   ,[Status]
					   ,Locked
					   ,DefaultValue
					   )
			SELECT		@id_frontmodule,
						@proto_id,
						i.name,
						i.labelFr,
						i.required,
						i.fieldSize,
						i.fieldSize,
						'Checkbox',
						i.editorClass,
						CASE WHEN i.atBeginingOfLine = 1 THEN i.editMode +32 ELSE i.editMode END as formRender,
						I.[order],
						i.Legend,
						NULL as Options,
						NULL  AS Validator,
						i.fieldClassDisplay,
						I.fieldClassEdit,
						I.curStatus,
						0 as locked,
						i.defaultValue
			FROM #inputsINFOS i
			WHERE i.type in ('Checkbox', 'Checkboxes')


			/*************** DatePicker *********************/ 
			INSERT INTO [ModuleForms]
					   ([module_id]
					   ,[TypeObj]
					   ,[Name]
					   ,[Label]
					   ,[Required]
					   ,[FieldSizeEdit]
					   ,[FieldSizeDisplay]
					   ,[InputType]
					   ,[editorClass]
					   ,[FormRender]
					   ,[FormOrder]
					   ,[Legend]
					   ,[Options]
					   ,[Validators]
					   ,[displayClass]
					   ,[EditClass]
					   ,[Status]
					   ,Locked
					   ,DefaultValue
					   )
			SELECT		@id_frontmodule,
						@proto_id,
						i.name,
						i.labelFr,
						i.required,
						i.fieldSize,
						i.fieldSize,
						i.type,
						i.editorClass,
						CASE WHEN i.atBeginingOfLine = 1 THEN i.editMode +32 ELSE i.editMode END as formRender,
						I.[order],
						i.Legend,
						'{"format":"'+format_.value+'"}' as Options,
						NULL  AS Validator,
						i.fieldClassDisplay,
						I.fieldClassEdit,
						I.curStatus,
						0 as locked,
						i.defaultValue
			FROM #inputsINFOS i
			LEFT JOIN [FormBuilderInputProperty] format_ on format_.fk_Input = i.pk_input and format_.name = 'format'
			WHERE i.type = 'DateTimePickerEditor'

			/*************** SELECT *********************/ 
			INSERT INTO [ModuleForms]
					   ([module_id]
					   ,[TypeObj]
					   ,[Name]
					   ,[Label]
					   ,[Required]
					   ,[FieldSizeEdit]
					   ,[FieldSizeDisplay]
					   ,[InputType]
					   ,[editorClass]
					   ,[FormRender]
					   ,[FormOrder]
					   ,[Legend]
					   ,[Options]
					   ,[Validators]
					   ,[displayClass]
					   ,[EditClass]
					   ,[Status]
					   ,Locked
					   ,DefaultValue
					   )
			SELECT		@id_frontmodule,
						@proto_id,
						i.name,
						i.labelFr,
						i.required,
						i.fieldSize,
						i.fieldSize,
						i.type,
						i.editorClass,
						CASE WHEN i.atBeginingOfLine = 1 THEN i.editMode +32 ELSE i.editMode END as formRender,
						I.[order],
						i.Legend,
						Case WHEN choice.value in (NULL,'','[]') THEN sqlquery.value ELSE REPLACE(choice.value, 'fr', 'label') END as Options,
						NULL  AS Validator,
						i.fieldClassDisplay,
						I.fieldClassEdit,
						I.curStatus,
						0 as locked,
						i.defaultValue
			FROM #inputsINFOS i
			LEFT JOIN [FormBuilderInputProperty] choice on choice.fk_Input = i.pk_input and choice.name = 'choices'
			LEFT JOIN [FormBuilderInputProperty] sqlquery on sqlquery.fk_Input = i.pk_input and sqlquery.name = 'sqlQuery'
			WHERE i.type = 'Select'

			/*************** Thesaurus *********************/ 
			INSERT INTO [ModuleForms]
					   ([module_id]
					   ,[TypeObj]
					   ,[Name]
					   ,[Label]
					   ,[Required]
					   ,[FieldSizeEdit]
					   ,[FieldSizeDisplay]
					   ,[InputType]
					   ,[editorClass]
					   ,[FormRender]
					   ,[FormOrder]
					   ,[Legend]
					   ,[Options]
					   ,[Validators]
					   ,[displayClass]
					   ,[EditClass]
					   ,[Status]
					   ,Locked
					   ,DefaultValue
					   )
			SELECT		@id_frontmodule,
						@proto_id,
						i.name,
						i.labelFr,
						i.required,
						i.fieldSize,
						i.fieldSize,
						i.type,
						i.editorClass,
						CASE WHEN i.atBeginingOfLine = 1 THEN i.editMode +32 ELSE i.editMode END as formRender,
						I.[order],
						i.Legend,
						CONVERT(varchar(250),node.value) as Options,
						NULL  AS Validator,
						i.fieldClassDisplay,
						I.fieldClassEdit,
						I.curStatus,
						0 as locked,
						defaultpath.value
			FROM #inputsINFOS i
			LEFT JOIN [FormBuilderInputProperty] node on node.fk_Input = i.pk_input and node.name = 'defaultNode'
			LEFT JOIN [FormBuilderInputProperty] defaultpath on defaultpath.fk_Input = i.pk_input and defaultpath.name = 'defaultPath'
			WHERE i.type = 'AutocompTreeEditor'

			/*************** AutocompleteEditor *********************/ 
			INSERT INTO [ModuleForms]
					   ([module_id]
					   ,[TypeObj]
					   ,[Name]
					   ,[Label]
					   ,[Required]
					   ,[FieldSizeEdit]
					   ,[FieldSizeDisplay]
					   ,[InputType]
					   ,[editorClass]
					   ,[FormRender]
					   ,[FormOrder]
					   ,[Legend]
					   ,[Options]
					   ,[Validators]
					   ,[displayClass]
					   ,[EditClass]
					   ,[Status]
					   ,Locked
					   ,DefaultValue
					   )
			SELECT		@id_frontmodule,
						@proto_id,
						i.name,
						i.labelFr,
						i.required,
						i.fieldSize,
						i.fieldSize,
						i.type,
						i.editorClass,
						CASE WHEN i.atBeginingOfLine = 1 THEN i.editMode +32 ELSE i.editMode END as formRender,
						I.[order],
						i.Legend,
						'{"source":"'+IPurl.value+'","minLength":'+IPlength.value+'}' as Options,
						NULL  AS Validator,
						i.fieldClassDisplay,
						I.fieldClassEdit,
						I.curStatus,
						0 as locked,
						i.defaultValue
			FROM #inputsINFOS i
			LEFT JOIN FormBuilderInputProperty IPurl ON i.pk_input =IPurl.fk_input AND IPurl.name = 'url'
			LEFT JOIN FormBuilderInputProperty IPlength ON  i.pk_input =IPlength.fk_input AND IPlength.name = 'triggerlength'
			WHERE i.type = 'AutocompleteEditor'

			/*************** ObjectPicker *********************/ 
			INSERT INTO [ModuleForms]
					   ([module_id]
					   ,[TypeObj]
					   ,[Name]
					   ,[Label]
					   ,[Required]
					   ,[FieldSizeEdit]
					   ,[FieldSizeDisplay]
					   ,[InputType]
					   ,[editorClass]
					   ,[FormRender]
					   ,[FormOrder]
					   ,[Legend]
					   ,[Options]
					   ,[Validators]
					   ,[displayClass]
					   ,[EditClass]
					   ,[Status]
					   ,Locked
					   ,DefaultValue
					   )
			SELECT		@id_frontmodule,
						@proto_id,
						i.name,
						i.labelFr,
						i.required,
						i.fieldSize,
						i.fieldSize,
						i.type,
						CASE WHEN IPobjT.Name = 'Non Identified Individual' THEN  i.editorClass+ ' unidentified-picker' END,
						CASE WHEN i.atBeginingOfLine = 1 THEN i.editMode +32 ELSE i.editMode END as formRender,
						I.[order],
						i.Legend,
						CASE WHEN IPobjLab.value is not null THEN '{"usedLabel":"'+IPobjLab.value+'"}'
						WHEN IPobjT.Name = 'Non Identified Individual' THEN '{"withToggle":1}' END as Options,
						NULL  AS Validator,
						i.fieldClassDisplay,
						I.fieldClassEdit,
						I.curStatus,
						0 as locked,
						i.defaultValue
			FROM #inputsINFOS i
			LEFT JOIN FormBuilderInputProperty IPobjT ON i.pk_input =IPobjT.fk_input AND IPobjT.name = 'objectType'
			LEFT JOIN FormBuilderInputProperty IPobjLab ON i.pk_input =IPobjLab.fk_input AND IPobjLab.name = 'linkedLabel'
			WHERE i.type = 'ObjectPicker'

			/*************** GridForm *********************/ 
			INSERT INTO [ModuleForms]
					   ([module_id]
					   ,[TypeObj]
					   ,[Name]
					   ,[Label]
					   ,[Required]
					   ,[FieldSizeEdit]
					   ,[FieldSizeDisplay]
					   ,[InputType]
					   ,[editorClass]
					   ,[FormRender]
					   ,[FormOrder]
					   ,[Legend]
					   ,[Options]
					   ,[Validators]
					   ,[displayClass]
					   ,[EditClass]
					   ,[Status]
					   ,Locked
					   ,DefaultValue
					   )
			SELECT		@id_frontmodule,
						@proto_id,
						ptGrid.Name,
						i.labelFr,
						i.required,
						i.fieldSize,
						i.fieldSize,
						i.type,
						i.editorClass,
						CASE WHEN i.atBeginingOfLine = 1 THEN i.editMode +32 ELSE i.editMode END as formRender,
						I.[order],
						i.Legend,
						CONVERT(Varchar(250),'{"showLines":"'+showLines.value+'","protocoleType":'
							+CONVERT(Varchar(250),ptGrid.ID)+',"delFirst":'+delFirst.value+',"nbFixedCol":'+nbFixedCol.value+'}') 
							as Options,
						NULL  AS Validator,
						i.fieldClassDisplay,
						I.fieldClassEdit,
						I.curStatus,
						0 as locked,
						i.defaultValue
			FROM #inputsINFOS i
			LEFT JOIN FormBuilderInputProperty delFirst ON i.pk_input =delFirst.fk_input AND delFirst.name = 'delFirst'
			LEFT JOIN FormBuilderInputProperty nbFixedCol ON i.pk_input =nbFixedCol.fk_input AND nbFixedCol.name = 'nbFixedCol'
			LEFT JOIN FormBuilderInputProperty childForm ON i.pk_input =childForm.fk_input AND childForm.name = 'childForm'
			LEFT JOIN FormBuilderInputProperty showLines ON i.pk_input=showLines.fk_input AND showLines.name = 'showLines'
			LEFT JOIN ProtocoleType ptGrid ON ptGrid.OriginalId='FormBuilder-'+ISNULL(childForm.value, '')
			WHERE i.type = 'GridFormEditor'



			/*************** ListOfNestedModel *********************/ 
			INSERT INTO [ModuleForms]
					   ([module_id]
					   ,[TypeObj]
					   ,[Name]
					   ,[Label]
					   ,[Required]
					   ,[FieldSizeEdit]
					   ,[FieldSizeDisplay]
					   ,[InputType]
					   ,[editorClass]
					   ,[FormRender]
					   ,[FormOrder]
					   ,[Legend]
					   ,[Options]
					   ,[Validators]
					   ,[displayClass]
					   ,[EditClass]
					   ,[Status]
					   ,Locked
					   ,DefaultValue
					   )
			SELECT		@id_frontmodule,
						@proto_id,
						ptGrid.Name,
						NULL,
						i.required,
						6,
						6,
						i.type,
						i.editorClass,
						CASE WHEN i.atBeginingOfLine = 1 THEN i.editMode +32 ELSE i.editMode END as formRender,
						I.[order],
						CASE WHEN i.Legend IS NOT NULL THEN i.Legend ELSE i.labelFr end,
						CONVERT(Varchar(250), ptGrid.ID)
							as Options,
						NULL  AS Validator,
						i.fieldClassDisplay,
						I.fieldClassEdit,
						I.curStatus,
						0 as locked,
						i.defaultValue
			FROM #inputsINFOS i
			LEFT JOIN FormBuilderInputProperty childForm ON i.pk_input =childForm.fk_input AND childForm.name = 'childForm'
			LEFT JOIN ProtocoleType ptGrid ON ptGrid.OriginalId='FormBuilder-'+ISNULL(childForm.value, '')
			WHERE i.type = 'ListOfNestedModel'


			/* Insert FK_ProtocoleType with defaults */ 
			INSERT INTO [ModuleForms]
					   ([module_id]
					   ,[TypeObj]
					   ,[Name]
					   ,[Label]
					   ,[Required]
					   ,[FieldSizeEdit]
					   ,[FieldSizeDisplay]
					   ,[InputType]
					   ,[editorClass]
					   ,[FormRender]
					   ,[FormOrder]
					   ,[Legend]
					   ,[Options]
					   ,[Validators]
					   ,[displayClass]
					   ,[EditClass]
					   ,[Status]
					   ,Locked
					   ,DefaultValue
					   )
			SELECT @id_frontmodule
					   ,@proto_id
					   ,'FK_ProtocoleType'
					   ,'FK_ProtocoleType'
					   ,0
					   ,3
					   ,3
					   ,'Number'
					   ,NULL
					   ,0
					   ,0
					   ,NULL
					   ,NULL
					   ,NULL
					   ,'hide'
					   ,'hide'
					   ,NULL
					   ,0
					   ,@proto_id



			/*** update rules because Formbuilder doesn't manage it yet ***/ 
			UPDATE f SET Rules = o.Rules
			FROM [ModuleForms] f
			JOIN #oldConf o ON f.Name = o.Name AND f.TypeObj = o.TypeObj
			WHERE f.module_id = 1
  
END
