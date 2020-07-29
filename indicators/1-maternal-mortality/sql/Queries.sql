USE [AC_C19_DATA]
GO
SELECT [zone], [date], [year], MONTH([date]) AS [month], [week], [value]
  FROM (
	SELECT b.zone, a.date, a.year, a.week, SUM(a.value) AS [value]
		FROM [dbo].[indicator_by_departament] AS a
		INNER JOIN
			[dbo].[department_list] AS b
		ON a.department = b.department
		GROUP BY b.zone, a.date, a.year, a.week) AS a;
GO
SELECT [zone], COUNT(*)
  FROM [dbo].[department_list]
 GROUP BY [zone];
GO
UPDATE [dbo].[department_list]
   SET [zone] = RTRIM(LTRIM(UPPER([zone]))),
	   [capital] = RTRIM(LTRIM(UPPER([capital])));
GO