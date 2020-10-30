USE [AC_C19_DATA]
GO

-- Generate for the country
SELECT [date], [year], MONTH([date]) AS [month], [week], SUM((CASE WHEN [value] = -1 THEN 0 ELSE [value] END)) AS [value]
  FROM [dbo].[events_data]
 WHERE [event] = 'DM'
   AND [year] >= 2017
 GROUP BY [date], [year], MONTH([date]), [week]
 ORDER BY [date];
GO

-- Generate by departments
SELECT [date], [department], [year], MONTH([date]) AS [month], [week], SUM((CASE WHEN [value] = -1 THEN 0 ELSE [value] END)) AS [value]
  FROM [dbo].[events_data]
 WHERE [event] = 'DM'
   AND [year] >= 2017
   AND [department] NOT IN ('EXTERIOR', 'PROCEDENCIA DESCONOCIDA', 'BOGOTA')
 GROUP BY [date], [department], [year], MONTH([date]), [week]
 ORDER BY [department], [date];
GO

-- Generate by capitals
SELECT [date], [capital], [year], MONTH([date]) AS [month], [week], SUM((CASE WHEN [value] = -1 THEN 0 ELSE [value] END)) AS [value]
  FROM [dbo].[events_data_by_capital]
 WHERE [event] = 'DM'
   AND [year] >= 2017
   AND [capital] NOT IN ('EXTERIOR', 'PROCEDENCIA DESCONOCIDA')
 GROUP BY [date], [capital], [year], MONTH([date]), [week]
 ORDER BY [capital], [date];
GO
