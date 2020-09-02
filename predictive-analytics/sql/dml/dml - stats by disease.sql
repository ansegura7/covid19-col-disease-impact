USE [AC_C19_DATA]
GO
SELECT [year], SUM([value]) AS [cases]
  FROM [dbo].[indicator_data]
 WHERE [indicator] = 'TB'
 GROUP BY [year]
 ORDER BY [year];
GO

SELECT [sub_indicator], SUM([value]) AS [cases]
  FROM [dbo].[indicator_data]
 WHERE [indicator] = 'TB'
 GROUP BY [sub_indicator]
 ORDER BY [sub_indicator];
GO

SELECT [year], [sub_indicator], SUM([value]) AS [cases]
  FROM [dbo].[indicator_data]
 WHERE [indicator] = 'TB'
 GROUP BY [year], [sub_indicator]
 ORDER BY [year], [sub_indicator];
GO
