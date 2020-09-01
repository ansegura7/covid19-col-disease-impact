USE [AC_C19_DATA]
GO
SELECT [indicator],[entity],[department],[year],[week],[date],[value]
  FROM [dbo].[indicator_data]
 WHERE [indicator] = 'MI'
 ORDER BY [year], [week];
GO

SELECT DISTINCT [department]--, [entity]
  FROM [dbo].[indicator_data]
 --WHERE [entity] <> [department]
 ORDER BY [department];
GO

SELECT [year], COUNT(*)
  FROM [dbo].[indicator_data]
 WHERE [indicator] = 'MI'
 GROUP BY [year]
 ORDER BY [year];
GO

UPDATE a
   SET a.[date] = b.[date]
  FROM [indicator_data] AS a
 INNER JOIN
	   (SELECT [year], [week], MIN([date]) AS [date]
		  FROM (
			SELECT c.[year], c.[week], d.date
			  FROM [AC_C19_DATA].[dbo].[indicator_data] AS c
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
			  FROM [AC_C19_DATA].[dbo].[indicator_data] AS c
			 INNER JOIN
				   [OVS_DEVOPS_WFS].[dbo].[dim_date] AS d
				ON c.year = d.year AND c.week = d.week_of_year
			 WHERE [indicator] = 'MI') AS t
		 GROUP BY [year], [week]
		 ORDER BY [year], [week];
GO

UPDATE [indicator_data]
   SET [indicator] = 'IM'
  WHERE [indicator] = 'MI';
GO

UPDATE [dbo].[department_list]
   SET [zone] = RTRIM(LTRIM(UPPER([zone]))),
	   [capital] = RTRIM(LTRIM(UPPER([capital])));
GO

UPDATE a
   SET a.[date] = b.[date]
  FROM [AC_C19_DATA].[dbo].[indicator_data] AS a
 INNER JOIN
	(SELECT [year],[week_of_year],MIN([date]) AS [date]
       FROM [OVS_DEVOPS_WFS].[dbo].[dim_date]
      GROUP BY [year],[week_of_year]) AS b
  ON a.[week] = b.[week_of_year] AND a.[year] = b.[year]
 WHERE a.[date] IS NULL
   AND [indicator] = 'TB';