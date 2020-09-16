USE [AC_C19_DATA]
GO

-- Generate for the country
SELECT [date], [year], MONTH([date]) AS [month], [week], SUM([value]) AS [value]
  FROM [dbo].[indicator_data]
 WHERE [indicator] = 'EMM'
   AND [year] >= 2017
 GROUP BY [date], [year], MONTH([date]), [week]
 ORDER BY [date];
GO

-- Generate by departments
SELECT [date], [department], [year], MONTH([date]) AS [month], [week], SUM([value]) AS [value]
  FROM [dbo].[indicator_data]
 WHERE [indicator] = 'EMM'
   AND [year] >= 2017
   AND [department] NOT IN ('EXTERIOR', 'PROCEDENCIA DESCONOCIDA')
 GROUP BY [date], [department], [year], MONTH([date]), [week]
 ORDER BY [department], [date];
GO
