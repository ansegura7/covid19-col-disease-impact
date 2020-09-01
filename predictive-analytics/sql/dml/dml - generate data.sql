USE [AC_C19_DATA]
GO

-- Generate by indicator
SELECT [date], YEAR([date]) AS [year], MONTH([date]) AS [month], DATEPART(WEEK, [date]) AS [week], [value]
  FROM 
	  (SELECT [indicator],[date],SUM([value]) AS [value]
	     FROM [dbo].[indicator_data]
		WHERE [indicator] = 'TB'
		 -- AND [department] = 'CHOCO'
	    GROUP BY [indicator],[date]) AS t
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