USE [AC_C19_DATA]
GO

-- Generate by indicator
SELECT [date], [year], MONTH([date]) AS [month], [week], SUM([value]) AS [value]
  FROM [dbo].[indicator_data]
 WHERE [indicator] = 'TB'
   AND [year] >= 2016
   AND [department] = 'BOGOTA'
 GROUP BY [date],[year], MONTH([date]), [week]
 ORDER BY [date];
GO

-- Generate for all indicators
SELECT [date],[MM],[IM],[TB]
   FROM 
	  (SELECT [indicator],[date],SUM([value]) AS [value]
	     FROM [dbo].[indicator_data]
	    GROUP BY [indicator],[date]) AS t
 PIVOT (SUM([value]) FOR [indicator] IN ([MM],[IM],[TB])) AS p
 ORDER BY [date];
GO