USE [AC_C19_DATA]
GO
SELECT [indicator],[entity],[department],[year],[week],[date],[value]
  FROM [dbo].[indicator_by_departament]
 WHERE [indicator] = 'MI'
 ORDER BY [year], [week];
GO

SELECT DISTINCT [department]--, [entity]
  FROM [dbo].[indicator_by_departament]
 --WHERE [entity] <> [department]
 ORDER BY [department];
GO

SELECT [year], COUNT(*)
  FROM [dbo].[indicator_by_departament]
 WHERE [indicator] = 'MI'
 GROUP BY [year]
 ORDER BY [year];
GO

UPDATE a
   SET a.[date] = b.[date]
  FROM [indicator_by_departament] AS a
 INNER JOIN
	   (SELECT [year], [week], MIN([date]) AS [date]
		  FROM (
			SELECT c.[year], c.[week], d.date
			  FROM [AC_C19_DATA].[dbo].[indicator_by_departament] AS c
			 INNER JOIN
				   [OVS_DEVOPS_WFS].[dbo].[dim_date] AS d
				ON c.year = d.year AND c.week = d.week_of_year
			 WHERE [indicator] = 'MM') AS t
		 GROUP BY [year], [week]) AS b
	ON a.year = b.year AND a.week = b.week
 WHERE [indicator] = 'MM'
   AND a.[date] IS NULL;
GO

SELECT [year], [week], MIN([date]) AS [date]
		  FROM (
			SELECT c.[year], c.[week], d.date
			  FROM [AC_C19_DATA].[dbo].[indicator_by_departament] AS c
			 INNER JOIN
				   [OVS_DEVOPS_WFS].[dbo].[dim_date] AS d
				ON c.year = d.year AND c.week = d.week_of_year
			 WHERE [indicator] = 'MI') AS t
		 GROUP BY [year], [week]
		 ORDER BY [year], [week];
GO

UPDATE [indicator_by_departament]
   SET [indicator] = 'IM'
  WHERE [indicator] = 'MI';
GO