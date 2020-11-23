USE [AC_C19_DATA]
GO

SELECT SUM([value]) AS [total]
  FROM [dbo].[events_data]
 WHERE [event] = 'EDA'
   AND [year] = 2018
 ORDER BY [total];
GO

DECLARE @DPTO_ALFA FLOAT = 0.5007;
DECLARE @CAPT_ALFA FLOAT = 0.4900;

WITH cte_data AS (
	SELECT 'EDA' AS [event], p.[department], p.[entity], t.[year], [week], [perc], [value_2018], 
			FLOOR([perc] * [value_2018]) AS [value], ([perc] * [value_2018] % 1) AS [float_part],
			CASE WHEN ([perc] * [value_2018] % 1) >= @DPTO_ALFA THEN FLOOR([perc] * [value_2018]) + 1 ELSE FLOOR([perc] * [value_2018]) END AS [result]
	  FROM (
			SELECT t1.[department], t1.[entity], [week], [value], [total], (1.0 * [value] / [total]) AS [perc]
				FROM (
					SELECT [department], [entity], [week], SUM([value]) AS [value]
					  FROM [dbo].[events_data]
					 WHERE [event] = 'EDA'
					   AND [year] IN ('2017', '2019')
					 GROUP BY [department], [entity], [week]) AS t1
				INNER JOIN
					(SELECT [department], [entity], SUM([value]) AS [total]
					   FROM [dbo].[events_data]
					  WHERE [event] = 'EDA'
						AND [year] IN ('2017', '2019')
					  GROUP BY [department], [entity]) AS t2
				ON t1.[entity] = t2.[entity]) AS p
		INNER JOIN
			(SELECT [department], [entity], [year], SUM([value]) AS [value_2018]
			   FROM [dbo].[events_data]
			  WHERE [event] = 'EDA'
				AND [year] = 2018
			  GROUP BY [department], [entity], [year]) AS t
		ON p.[entity] = t.[entity] AND p.[department] = t.[department])

--SELECT *
--  FROM cte_data;

UPDATE tgt
   SET tgt.[value] = src.[result]
  FROM [events_data] AS tgt
 INNER JOIN
	   [cte_data] AS src
	ON tgt.[event] = src.[event]
   AND tgt.[department] = src.[department]
   AND tgt.[entity] = src.[entity]
   AND tgt.[year] = src.[year]
   AND tgt.[week] = src.[week]
 WHERE tgt.[event] = 'EDA'
   AND src.[year] = 2018;
GO

SELECT * --DELETE
  FROM [dbo].[events_data]
 WHERE [event] = 'EDA'
   AND [year] = 2018;
GO
