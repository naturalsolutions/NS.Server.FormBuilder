
/****** Object:  StoredProcedure [dbo].[_Centralisation_UpdateDBFromReferentiel]    Script Date: 20/02/2018 15:13:25 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO


CREATE PROCEDURE [dbo].[_Centralisation_UpdateDBFromReferentiel](
	@ID_Centralisation_SourceTarget INT
)
AS
BEGIN

	DECLARE @mem_error nvarchar(max)
	SET @mem_error = ''
	DECLARE @ErrorMessage NVARCHAR(4000);
	DECLARE @ErrorSeverity INT;
	DECLARE @ErrorState INT;
	DECLARE @ProcessOk BIT;

	BEGIN TRY
		BEGIN TRAN 
			DECLARE 
			@SourceDatabase VARCHAR(250)
			,@TargetDatabase VARCHAR(250)
			,@TargetInstance INT
			,@HasError BIT
			,@DisableConstraint BIT

			--DECLARE @ID_Centralisation_SourceTarget INT; SET @ID_Centralisation_SourceTarget = 1;
			-- TODO Prendre en compte la table TPropagation
			-- TODO Pour éviter les conflits synonym utiliser infostatus, cf. Gestion individuhistory 
	
			SET @HasError = 0

			SELECT @SourceDatabase = [SourceDatabase],@TargetDatabase=TargetDatabase,@TargetInstance=Instance, @DisableConstraint=DisableConstraint
			FROM _Centralisation_SourceTarget
			WHERE ID=@ID_Centralisation_SourceTarget

			print ' instance ' + convert(varchar,@TargetInstance)
	
			--Gestion des contraintes DROP
			IF @DisableConstraint='True'
				BEGIN
					EXEC _Centralisation_ConstraintsManagement @ID_Centralisation_SourceTarget,'Start',@ProcessOk OUTPUT
					IF @ProcessOk = 0
						BEGIN
							SET @HasError  =1
							print 'Error in Constraints management from _Centralisation_UpdateDBFromReferentiel'
							RAISERROR ('Error in Constraints management from _Centralisation_UpdateDBFromReferentiel Starting process, see TLOG_MESSAGES for details' , -- Message text.
										15, -- Severity.
										2 -- State.
										);
						END
				END
			
			DECLARE @cur_SQL NVARCHAR(MAX)
			SET @cur_SQL = 'IF EXISTS (SELECT * FROM sys.synonyms WHERE name = ''SysColonne'')  drop synonym SysColonne ; CREATE SYNONYM SysColonne FOR ' + replace(@SourceDatabase,'dbo.','sys.') + 'columns'
			print @cur_SQL
			exec sp_executesql @cur_SQL

			SET @cur_SQL = 'IF EXISTS (SELECT * FROM sys.synonyms WHERE name = ''SysObject'')  drop synonym SysObject ; CREATE SYNONYM SysObject FOR ' + replace(@SourceDatabase,'dbo.','sys.') + 'objects'
			print @cur_SQL
			exec sp_executesql @cur_SQL

			DECLARE @TableName VARCHAR(250)
			,@TabidName VARCHAR(250)
			,@TypeObject [varchar](50)
			,@IdObject [varchar](50)

			DECLARE c_table CURSOR FOR
				select [Name] ,[IdNamere] ,[TypeObject],idObject
				FROM _Centralisation_TablesToUpdate T JOIN [_Centralisation_SourceTargetTable] S ON t.ID = S.fk_TablesToUpdate
				WHERE S.[fk_SourceTarget] = @ID_Centralisation_SourceTarget
				ORDER by [OrdreExecution]


			OPEN c_table   
			FETCH NEXT FROM c_table INTO @TableName, @TabidName , @TypeObject,@IdObject

			WHILE @@FETCH_STATUS = 0   
			BEGIN   
				-- TODO Gérer les exceptions
				BEGIN TRY

					print 'Traitement de la table '+ @TableName + ' Type: ' + @TypeObject

					IF OBJECT_ID('tempdb..#IdToUpdate') IS NOT NULL
					DROP TABLE #IdToUpdate

					CREATE TABLE #IdToUpdate(ID INT,IDObject INT )

					DECLARE @SQLOld nvarchar(max)
					,@SQLNew nvarchar(max)
					,@SQLFinalUpdate nvarchar(max)
					,@SQLInsert nvarchar(max)
					,@SQLSelectinInsert nvarchar(max)

					SET @SQLOld='SELECT '
					SET @SQLNew='SELECT '
					SET @SQLFinalUpdate='UPDATE OLd SET '
					SET @SQLInsert = 'SET IDENTITY_INSERT ' +  @TargetDatabase + @TableName + ' ON; INSERT INTO  ' + @TargetDatabase + @TableName + '(' + @TabidName 
					SET @SQLSelectinInsert=@TabidName


					SELECT @SQLOld = @SQLOld + c.name + ',' 
					,@SQLNew=@SQLNew+c.name + ',' 
					,@SQLFinalUpdate=CASE WHEN c.name = @TabidName THEN @SQLFinalUpdate ELSE @SQLFinalUpdate + c.name + ' = New.' + c.name + ','    END
					,@SQLInsert = CASE WHEN c.name = @TabidName THEN @SQLInsert ELSE @SQLInsert + ',' + c.name END
					,@SQLSelectinInsert = CASE WHEN c.name = @TabidName THEN @SQLSelectinInsert ELSE @SQLSelectinInsert + ',' + c.name END
					FROM SysColonne c JOIN SysObject o ON c.object_id = o.object_id 
					WHERE o.name = @TableName and o.type='U'
					and c.system_type_id not in (35)


					SET @SQLOld = @SQLOld +'#FROM ' + @TargetDatabase +  @TableName 
					SET @SQLOld = replace(@SQLOld,',#FROM',' FROM')

					SET @SQLNew = @SQLNew +'#FROM ' + @SourceDatabase +  @TableName 
					SET @SQLNew = replace(@SQLNew,',#FROM',' FROM')


					SET @cur_SQL = 'SELECT ' + @TabidName + ',' + @IdObject + '  FROM (' + @SQLNew  + ' EXCEPT ' + @SQLOld + ') E'
					print @cur_SQL

					INSERT INTO #IdToUpdate
					exec sp_executesql @cur_SQL


					--select @TableName
					--select @TypeObject

			

					select * from #IdToUpdate

					-- On supprime les IDs des objets qui ont comme première règle qui match un valeur de propagation à 0
					DELETE from #IdToUpdate 
					where ID in (
								select ID from
								(SELECT row_number() over(partition by I.id order by [Priority]) nb,I.ID, P.propagation 
								from [TPropagation] P LEFT JOIN #IdToUpdate I ON (I.IDObject = [Source_ID] or [Source_ID] =-1)
								where (P.[Instance] = @TargetInstance or P.[Instance] =-1) and (P.[TypeObject] = @TypeObject or P.typeobject IS NULL)
								) P where P.nb =1 and P.propagation=0
					)		
			
			
			
					PRINT 'after delete ID with no rules' 
					select * from #IdToUpdate
			




					SET @SQLFinalUpdate = @SQLFinalUpdate + '#FROM  ' + @TargetDatabase +  @TableName + ' Old  JOIN ' + @SourceDatabase +  @TableName + ' New ON Old.' +  @TabidName + '= New.' +  @TabidName
					SET @SQLFinalUpdate = @SQLFinalUpdate + ' WHERE Old.' + @TabidName + ' IN (SELECT  ID FROM #IdToUpdate) ' 

					SET @SQLFinalUpdate = replace(@SQLFinalUpdate,',#FROM',' FROM')


					-- TODO Gérer les suppressions ???????
					print @SQLFinalUpdate
			
					exec sp_executesql @SQLFinalUpdate


					SET @SQLInsert = @SQLInsert + ') select ' + @SQLSelectinInsert+ ' FROM ' + @SourceDatabase + @TableName + ' New where ' + @TabidName + ' not in (select ' + @TabidName + ' FROM ' + @TargetDatabase + @TableName + ') AND  New.' + @TabidName + ' IN (SELECT  ID FROM #IdToUpdate)  ;SET IDENTITY_INSERT ' +  @TargetDatabase + @TableName + ' OFF '
					print @SQLInsert

					exec sp_executesql @SQLInsert
					INSERT INTO NSLog.dbo.TLOG_MESSAGES
						VALUES (GETDATE(), 1, 'Centralisation', 'SP : _Centralisation_UpdateDBFromReferentiel', 'No user', 2,
						4, CONVERT(varchar,(select count(*) from #IdToUpdate))+ ' rows INSERTED or UPDATED in '+@TargetDatabase +  @TableName
						, 'Concerned ID: ' + CONVERT(varchar,(SELECT STUFF((SELECT ','+ CONVERT(varchar,f.ID)
																FROM #IdToUpdate f
																 FOR XML PATH('')), 1, 1, ''))
												 )
						+ ',  used request: '+@SQLInsert
						)



					/****** delete **/
					PRINT('DELETE Old values ') 

					IF OBJECT_ID('tempdb..#IdToDelete') IS NOT NULL
					DROP TABLE #IdToDelete

					CREATE TABLE #IdToDelete(ID INT,IDObject INT )

						SET @cur_SQL = 'SELECT ' + @TabidName + ',' + @IdObject + '  FROM (' + @SQLOld  + ' EXCEPT ' +  @SQLNew+ ') E'
					print @cur_SQL

					INSERT INTO #IdToDelete
					exec sp_executesql @cur_SQL



					select 'delete '+@TargetDatabase +  @TableName as tt

					select * from #IdToDelete

					IF (SELECT AllowDelete FROM _Centralisation_TablesToUpdate WHERE Name = @TableName) = 1
					BEGIN
					-- On supprime les ID des objets qui ont comme première règle qui match un valeur de propagation à 0
						DELETE from #IdToDelete 
						where ID in (
									select ID from
									(	SELECT row_number() over(partition by i.id order by [Priority]) nb,i.ID,p.propagation 
										from [TPropagation] P 
										LEFT JOIN #IdToDelete I ON (i.IDObject = [Source_ID] or [Source_ID] =-1)
										where (P.[Instance] = @TargetInstance or P.[Instance] =-1) and (p.[TypeObject] = @TypeObject or p.typeobject IS NULL)
									) P where p.nb =1 and p.propagation=0 
						) 
			
						DECLARE @SQLFinalDelete nvarchar(max)
						SET @SQLFinalDelete = 'DELETE Old'
						SET @SQLFinalDelete = @SQLFinalDelete + ' FROM  ' + @TargetDatabase +  @TableName + ' Old '
						SET @SQLFinalDelete = @SQLFinalDelete + ' WHERE Old.' + @TabidName + ' IN (SELECT ID FROM #IdToDelete) ' 

						print @SQLFinalDelete
						exec sp_executesql @SQLFinalDelete

							INSERT INTO NSLog.dbo.TLOG_MESSAGES
							VALUES (GETDATE(), 1, 'Centralisation', 'SP : _Centralisation_UpdateDBFromReferentiel', 'No user', 2,
							3, CONVERT(varchar,(select count(*) from #IdToDelete))+ ' rows DELETED in '+@TargetDatabase +  @TableName
							, 'Concerned ID: ' + CONVERT(varchar,(SELECT STUFF((SELECT ','+ CONVERT(varchar,f.ID)
																	FROM #IdToDelete f
																	 FOR XML PATH('')), 1, 1, ''))
													 )
							+ ', With request: '+@SQLFinalDelete
							)
					END

				END TRY
				BEGIN CATCH

					SET @HasError  =1
					print 'Traitement erreur sur objet : ' + @TypeObject
						
					SELECT 
						@ErrorMessage = ERROR_MESSAGE(),
						@ErrorSeverity = ERROR_SEVERITY(),
						@ErrorState = ERROR_STATE();
					SET @ErrorMessage = REPLACE(@ErrorMessage,'''','''''')
				
					SET @mem_error = @mem_error +'INSERT INTO NSLog.dbo.TLOG_MESSAGES
						VALUES (GETDATE(), 2, ''Centralisation'', ''SP : _Centralisation_UpdateDBFromReferentiel'', ''No user'', 2,
						'+STR(@ErrorState)+', '''+@ErrorMessage+''', ''Severity: '' + CONVERT(varchar,'+STR(@ErrorSeverity)+')+''  Object: '''''+@TypeObject+'''''''); '
				
				END CATCH	

				FETCH NEXT FROM c_table INTO @TableName, @TabidName  ,@TypeObject,@IdObject

			END

			CLOSE c_table   
			DEALLOCATE c_table

		IF (@HasError=1)
			BEGIN 
				RAISERROR ('Error during copy, see TLOG_MESSAGES for details' , -- Message text.
								15, -- Severity.
								2 -- State.
								);
			END
		ELSE
			BEGIN
			--Gestion des contraintes ADD
			IF @DisableConstraint='True'
				BEGIN
					EXEC _Centralisation_ConstraintsManagement @ID_Centralisation_SourceTarget,'End',@ProcessOk OUTPUT
					IF @ProcessOk = 0
						BEGIN
							SET @HasError  =1
							print 'Error in Constraints management from _Centralisation_UpdateDBFromReferentiel'
							RAISERROR ('Error in Constraints management from _Centralisation_UpdateDBFromReferentiel Ending process, see TLOG_MESSAGES for details' , -- Message text.
										15, -- Severity.
										2 -- State.
										);
						END
				END
			COMMIT TRAN 
			END
	END TRY
	BEGIN CATCH
		ROLLBACK TRAN 
		--print 'ERROR-3='+STR(@HasError)
		SET @HasError  =1
		print 'Erreur globale'
			
		SELECT 
			@ErrorMessage = ERROR_MESSAGE(),
			@ErrorSeverity = ERROR_SEVERITY(),
			@ErrorState = ERROR_STATE();
			SET @ErrorMessage = REPLACE(@ErrorMessage,'''','''''')
			SET @mem_error = @mem_error +'INSERT INTO NSLog.dbo.TLOG_MESSAGES
						VALUES (GETDATE(), 4, ''Centralisation'', ''SP : _Centralisation_UpdateDBFromReferentiel'', ''No user'', 2,
						'+STR(@ErrorState)+', '''+@ErrorMessage+''', ''Severity: '' + CONVERT(varchar,'+STR(@ErrorSeverity)+')+''  Localisation: Global error. Rollback Tran in catch.''); '
			--print '=0>'+@mem_error
			EXEC(@mem_error)
			RAISERROR ('Global Error in _Centralisation_UpdateDBFromReferentiel, Ending process, see TLOG_MESSAGES for details' , -- Message text.
									16, -- Severity.
									2 -- State.
									);
	END CATCH


END