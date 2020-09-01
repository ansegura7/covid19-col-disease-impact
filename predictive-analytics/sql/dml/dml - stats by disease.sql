USE [AC_C19_DATA]
GO
SELECT [year], SUM([value]) AS [value]
  FROM [dbo].[indicator_data]
 WHERE [indicator] = 'TB'
 GROUP BY [year]
 ORDER BY [year];
GO

SELECT [year], [sub_indicator], SUM([value]) AS [value]
  FROM [dbo].[indicator_data]
 WHERE [indicator] = 'TB'
 GROUP BY [year], [sub_indicator]
 ORDER BY [year], [sub_indicator];
GO