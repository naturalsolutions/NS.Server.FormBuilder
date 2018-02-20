
/****** Object:  StoredProcedure [dbo].[_Centralisation_ConstraintsManagement]    Script Date: 20/02/2018 15:13:23 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO


CREATE PROCEDURE [dbo].[_Centralisation_ConstraintsManagement](
	@ID_Centralisation_SourceTarget INT,
	@ProcessusStage VARCHAR(5),  --Possible values =Start or End
	@ProcessusOk BIT OUTPUT 
)
AS
BEGIN
	DECLARE @SQL NVARCHAR(MAX)
	DECLARE @SourceDatabase VARCHAR(250)
	DECLARE @TargetDatabase VARCHAR(250)
	DECLARE @Instance INT
	DECLARE @DisableConstraint BIT

	DECLARE @ErrorMessage NVARCHAR(4000)
	DECLARE @ErrorSeverity INT
	DECLARE @ErrorState INT
	DECLARE @cur_SQL NVARCHAR(MAX)

	SET @SQL=''
	SET @ProcessusOk = 'False'
	BEGIN TRY				
			SELECT @SourceDatabase=[SourceDatabase]
				  ,@TargetDatabase=[TargetDatabase]
				  ,@Instance=[Instance]
				  ,@DisableConstraint=[DisableConstraint]
			FROM [dbo].[_Centralisation_SourceTarget]
			WHERE [ID] = @ID_Centralisation_SourceTarget

			IF @ProcessusStage = 'Start'
				BEGIN
					SET @cur_SQL = 'IF EXISTS (SELECT * FROM sys.synonyms WHERE name = ''current_sysobjects'')  drop synonym current_sysobjects ; 
					CREATE SYNONYM current_sysobjects FOR ' + @TargetDatabase + 'sysobjects'
					print @cur_SQL
					exec sp_executesql @cur_SQL
					SET @cur_SQL = 'IF EXISTS (SELECT * FROM sys.synonyms WHERE name = ''current_sysdefault_constraints'')  drop synonym current_sysdefault_constraints ; 
					CREATE SYNONYM current_sysdefault_constraints FOR ' +replace(@TargetDatabase,'dbo.','sys.') + 'default_constraints'
					print @cur_SQL
					exec sp_executesql @cur_SQL
					SET @cur_SQL = 'IF EXISTS (SELECT * FROM sys.synonyms WHERE name = ''current_sysconstraints'')  drop synonym current_sysconstraints ; 
					CREATE SYNONYM current_sysconstraints FOR ' + @TargetDatabase + 'sysconstraints'
					print @cur_SQL
					exec sp_executesql @cur_SQL
					SET @cur_SQL = 'IF EXISTS (SELECT * FROM sys.synonyms WHERE name = ''current_syscolumns'')  drop synonym current_syscolumns ; 
					CREATE SYNONYM current_syscolumns FOR ' + @TargetDatabase + 'syscolumns'
					print @cur_SQL
					exec sp_executesql @cur_SQL
					SET @cur_SQL = 'IF EXISTS (SELECT * FROM sys.synonyms WHERE name = ''current_sysforeignkeys'')  drop synonym current_sysforeignkeys ; 
					CREATE SYNONYM current_sysforeignkeys FOR ' + @TargetDatabase + 'sysforeignkeys'
					print @cur_SQL
					exec sp_executesql @cur_SQL
					SET @cur_SQL = 'IF EXISTS (SELECT * FROM sys.synonyms WHERE name = ''current_referential_constraints'')  drop synonym current_referential_constraints ; 
					CREATE SYNONYM current_referential_constraints FOR ' + replace(@TargetDatabase,'dbo.','INFORMATION_SCHEMA.') + 'REFERENTIAL_CONSTRAINTS'
					print @cur_SQL
					exec sp_executesql @cur_SQL

					SELECT @SQL=@SQL+'ALTER TABLE '+ @TargetDatabase+OBJECT_NAME(SO.parent_obj,DB_ID(REPLACE(@TargetDatabase,'.dbo.','')))+' DROP CONSTRAINT ['+SO.name+']; '
						FROM current_sysobjects SO 
						LEFT OUTER JOIN current_sysdefault_constraints SDC ON SO.name = SDC.name 
						LEFT OUTER JOIN current_sysconstraints SC ON SO.id = SC.constid 
						INNER JOIN current_syscolumns SM ON SC.colid = SM.colid AND SO.parent_obj = SM.id
						LEFT OUTER JOIN current_sysforeignkeys SFK ON SFK.constid = so.id 
						LEFT OUTER JOIN current_syscolumns SM2 ON SFK.rkey = SM2.colid AND SFK.rkeyid = SM2.id
						LEFT OUTER JOIN current_referential_constraints RC ON RC.CONSTRAINT_NAME = SO.name
					WHERE SO.xtype IN ('F','D') 
					AND OBJECT_NAME(SO.PARENT_OBJ,DB_ID(REPLACE(@TargetDatabase,'.dbo.',''))) IN (SELECT DISTINCT [Name] 
															FROM [dbo].[_Centralisation_TablesToUpdate] TAC 
															INNER JOIN [dbo].[_Centralisation_SourceTargetTable] STT ON TAC.ID = STT.[fk_TablesToUpdate]
														WHERE [fk_SourceTarget] = @ID_Centralisation_SourceTarget)
					print 'SQLSTART='+COALESCE(@SQL,'NULL')
					EXEC(@SQL)
					SET @cur_SQL = 'IF EXISTS (SELECT * FROM sys.synonyms WHERE name = ''current_sysobjects'')  drop synonym current_sysobjects ; 
					IF EXISTS (SELECT * FROM sys.synonyms WHERE name = ''current_sysdefault_constraints'')  drop synonym current_sysdefault_constraints ;
					IF EXISTS (SELECT * FROM sys.synonyms WHERE name = ''current_sysconstraints'')  drop synonym current_sysconstraints ;  
					IF EXISTS (SELECT * FROM sys.synonyms WHERE name = ''current_syscolumns'')  drop synonym current_syscolumns ;
					IF EXISTS (SELECT * FROM sys.synonyms WHERE name = ''current_sysforeignkeys'')  drop synonym current_sysforeignkeys ;
					IF EXISTS (SELECT * FROM sys.synonyms WHERE name = ''current_referential_constraints'')  drop synonym current_referential_constraints ;'
					print @cur_SQL
					exec sp_executesql @cur_SQL
				END
			ELSE IF @ProcessusStage = 'End'
				BEGIN
					SET @cur_SQL = 'IF EXISTS (SELECT * FROM sys.synonyms WHERE name = ''current_sysobjects'')  drop synonym current_sysobjects ; 
					CREATE SYNONYM current_sysobjects FOR ' + @SourceDatabase + 'sysobjects'
					print @cur_SQL
					exec sp_executesql @cur_SQL
					SET @cur_SQL = 'IF EXISTS (SELECT * FROM sys.synonyms WHERE name = ''current_sysdefault_constraints'')  drop synonym current_sysdefault_constraints ; 
					CREATE SYNONYM current_sysdefault_constraints FOR ' +replace(@SourceDatabase,'dbo.','sys.') + 'default_constraints'
					print @cur_SQL
					exec sp_executesql @cur_SQL
					SET @cur_SQL = 'IF EXISTS (SELECT * FROM sys.synonyms WHERE name = ''current_sysconstraints'')  drop synonym current_sysconstraints ; 
					CREATE SYNONYM current_sysconstraints FOR ' + @SourceDatabase + 'sysconstraints'
					print @cur_SQL
					exec sp_executesql @cur_SQL
					SET @cur_SQL = 'IF EXISTS (SELECT * FROM sys.synonyms WHERE name = ''current_syscolumns'')  drop synonym current_syscolumns ; 
					CREATE SYNONYM current_syscolumns FOR ' + @SourceDatabase + 'syscolumns'
					print @cur_SQL
					exec sp_executesql @cur_SQL
					SET @cur_SQL = 'IF EXISTS (SELECT * FROM sys.synonyms WHERE name = ''current_sysforeignkeys'')  drop synonym current_sysforeignkeys ; 
					CREATE SYNONYM current_sysforeignkeys FOR ' + @SourceDatabase + 'sysforeignkeys'
					print @cur_SQL
					exec sp_executesql @cur_SQL
					SET @cur_SQL = 'IF EXISTS (SELECT * FROM sys.synonyms WHERE name = ''current_referential_constraints'')  drop synonym current_referential_constraints ; 
					CREATE SYNONYM current_referential_constraints FOR ' + replace(@SourceDatabase,'dbo.','INFORMATION_SCHEMA.') + 'REFERENTIAL_CONSTRAINTS'
					print @cur_SQL
					exec sp_executesql @cur_SQL

					SELECT @SQL=@SQL+STUFF(CASE 
								WHEN SO.xtype='D' THEN 
									'ALTER TABLE '+ @TargetDatabase+OBJECT_NAME(SO.parent_obj)+' ADD CONSTRAINT ['+SO.name+'] DEFAULT '+SDC.definition+' FOR ['+SM.name+']; '--,*,OBJECT_NAME(PARENT_OBJECT_ID)
								WHEN SO.xtype = 'F' THEN 
									'ALTER TABLE '+ @TargetDatabase+OBJECT_NAME(SO.parent_obj)+' WITH CHECK ADD CONSTRAINT ['+SO.name+'] FOREIGN KEY (['+SM.name+']) REFERENCES '+@TargetDatabase+'['+OBJECT_NAME(SFK.rkeyid)+'] (['+SM2.name+'])'
									+CASE WHEN DELETE_RULE = 'CASCADE' THEN ' ON DELETE CASCADE'
										ELSE ''
										END+'
									; '
							END,1,0,'')
						FROM current_sysobjects SO 
						LEFT OUTER JOIN current_sysdefault_constraints SDC ON SO.name = SDC.name 
						LEFT OUTER JOIN current_sysconstraints SC ON SO.id = SC.constid 
						INNER JOIN current_syscolumns SM ON SC.colid = SM.colid AND SO.parent_obj = SM.id
						LEFT OUTER JOIN current_sysforeignkeys SFK ON SFK.constid = so.id 
						LEFT OUTER JOIN current_syscolumns SM2 ON SFK.rkey = SM2.colid AND SFK.rkeyid = SM2.id
						LEFT OUTER JOIN current_referential_constraints RC ON RC.CONSTRAINT_NAME = SO.name
					WHERE SO.xtype IN ('F','D') 
					AND OBJECT_NAME(SO.PARENT_OBJ) IN (SELECT DISTINCT [Name] 
															FROM [dbo].[_Centralisation_TablesToUpdate] TAC 
															INNER JOIN [dbo].[_Centralisation_SourceTargetTable] STT ON TAC.ID = STT.[fk_TablesToUpdate]
														WHERE [fk_SourceTarget] = @ID_Centralisation_SourceTarget)
					print 'SQLEND='+COALESCE(@SQL,'NULL')
					EXEC(@SQL)
					SET @cur_SQL = 'IF EXISTS (SELECT * FROM sys.synonyms WHERE name = ''current_sysobjects'')  drop synonym current_sysobjects ; 
					IF EXISTS (SELECT * FROM sys.synonyms WHERE name = ''current_sysdefault_constraints'')  drop synonym current_sysdefault_constraints ;
					IF EXISTS (SELECT * FROM sys.synonyms WHERE name = ''current_sysconstraints'')  drop synonym current_sysconstraints ;  
					IF EXISTS (SELECT * FROM sys.synonyms WHERE name = ''current_syscolumns'')  drop synonym current_syscolumns ;
					IF EXISTS (SELECT * FROM sys.synonyms WHERE name = ''current_sysforeignkeys'')  drop synonym current_sysforeignkeys ;
					IF EXISTS (SELECT * FROM sys.synonyms WHERE name = ''current_referential_constraints'')  drop synonym current_referential_constraints ;'
					print @cur_SQL
					exec sp_executesql @cur_SQL
				END
			ELSE
				BEGIN
					RAISERROR ('Error during constraints management, wrong @ProcessuStage parameters see TLOG_MESSAGES for details' , -- Message text.
										15, -- Severity.
										2 -- State.
										);
				END	
			SET @ProcessusOk = 'True'	
	END TRY
	BEGIN CATCH		
		print 'Erreur Gestion contraintes'			
		SELECT 
			@ErrorMessage = ERROR_MESSAGE(),
			@ErrorSeverity = ERROR_SEVERITY(),
			@ErrorState = ERROR_STATE();
			SET @ErrorMessage = REPLACE(@ErrorMessage,'''','''''')
			SET @SQL = 'INSERT INTO NSLog.dbo.TLOG_MESSAGES
						VALUES (GETDATE(), 2, ''Centralisation'', ''SP : GestionContrainteReferentiel'', ''No user'', 0,
						'+STR(@ErrorState)+', '''+@ErrorMessage+''', ''Severity: '' + CONVERT(varchar,'+STR(@ErrorSeverity)+')+''  Localisation: Constraints management error for '+@ProcessusStage+'ing process. Rollback Tran in catch.''); '
			print '=Error>'+@SQL
			EXEC(@SQL)
	END CATCH
	SELECT @ProcessusOk
END