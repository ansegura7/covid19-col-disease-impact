USE [AC_C19_DATA]
GO
SELECT [indicator],[date],[value]
  FROM 
	  (SELECT [indicator],[date],SUM([value]) AS [value]
	     FROM [dbo].[indicator_by_departament]
		WHERE [indicator] = 'TB'
	    GROUP BY [indicator],[date]) AS t
 ORDER BY [date];
GO

SELECT [date],[MM],[IM],[TB]
   FROM 
	  (SELECT [indicator],[date],SUM([value]) AS [value]
	     FROM [dbo].[indicator_by_departament]
	    GROUP BY [indicator],[date]) AS t
 PIVOT (SUM([value]) FOR [indicator] IN ([MM],[IM],[TB])) AS p
 ORDER BY [date];
GO