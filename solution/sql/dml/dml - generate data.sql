USE [AC_C19_DATA]
GO

-- Generate for the country
SELECT [date], [year], MONTH([date]) AS [month], [week], SUM([value]) AS [value]
  FROM [dbo].[events_data]
 WHERE [event] = 'EMM'
   AND [year] >= 2017
 GROUP BY [date], [year], MONTH([date]), [week]
 ORDER BY [date];
GO

-- Generate by departments
SELECT [date], [department], [year], MONTH([date]) AS [month], [week], SUM([value]) AS [value]
  FROM [dbo].[events_data]
 WHERE [event] = 'EMM'
   AND [year] >= 2017
   AND [department] NOT IN ('EXTERIOR', 'PROCEDENCIA DESCONOCIDA')
 GROUP BY [date], [department], [year], MONTH([date]), [week]
 ORDER BY [department], [date];
GO

-- Generate by capitals
SELECT [date], [capital], [year], MONTH([date]) AS [month], [week], SUM([value]) AS [value]
  FROM [dbo].[events_data_by_capital]
 WHERE [event] = 'SA'
   AND [year] >= 2017
   AND [capital] NOT IN ('EXTERIOR', 'PROCEDENCIA DESCONOCIDA')
 GROUP BY [date], [capital], [year], MONTH([date]), [week]
 ORDER BY [capital], [date];
GO
