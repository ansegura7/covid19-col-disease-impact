USE [AC_C19_DATA]
GO

-- Validate indicator data
SELECT [event],[capital],[department],[year],[week],[date],[value]
  FROM [dbo].[events_data_by_capital]
 WHERE [event] = 'EDA'
 ORDER BY [year], [week];
GO

-- Validate grouped data
SELECT [year], COUNT(*), SUM([value])
  FROM [dbo].[events_data_by_capital]
 WHERE [event] = 'EDA'
 GROUP BY [year]
 ORDER BY [year];
GO

-- Validate department list
SELECT [department], [capital], COUNT(*) AS [count]
  FROM [dbo].[events_data_by_capital]
 WHERE [event] = 'EDA'
  -- AND [capital] <> [department]
 GROUP BY [department], [capital]
 ORDER BY [department];
GO

-- Update deparments from entities
UPDATE [events_data_by_capital]
   SET [department] = 'ARAUCA'
     , [capital]  = 'ARAUCA CAP'
 WHERE [event] = 'EDA'
   AND [capital] = 'ARAUCA'
   AND [department] = 'ARAUCA';
GO

-- Validate NULLs date
SELECT [year], [week], MIN([date]) AS [date]
		  FROM (
			SELECT c.[year], c.[week], d.date
			  FROM [AC_C19_DATA].[dbo].[events_data] AS c
			 INNER JOIN
				   [DEVOPS].[dbo].[dim_date] AS d
				ON c.year = d.year AND c.week = d.week_of_year
			 WHERE [event] = 'EDA') AS t
		 GROUP BY [year], [week]
		 ORDER BY [year], [week];
GO

-- Update NULLs date
UPDATE a
   SET a.[date] = b.[date]
  FROM [AC_C19_DATA].[dbo].[events_data_by_capital] AS a
 INNER JOIN
	(SELECT [year],[week_of_year],MIN([date]) AS [date]
       FROM [DEVOPS].[dbo].[dim_date]
      GROUP BY [year],[week_of_year]) AS b
  ON a.[week] = b.[week_of_year] AND a.[year] = b.[year]
 WHERE a.[date] IS NULL
   AND [event] = 'EDA';
GO

-- Update Department name
UPDATE [dbo].[department_list]
   SET [zone] = RTRIM(LTRIM(UPPER([zone]))),
	   [capital] = RTRIM(LTRIM(UPPER([capital])));

UPDATE [dbo].[events_data_by_capital]
   SET [department] = RTRIM(LTRIM(UPPER([department]))),
	   [capital] = RTRIM(LTRIM(UPPER([capital]))); 
GO

-- Validate date blocks
SELECT [date], COUNT(*) AS [count]
  FROM [dbo].[events_data_by_capital]
 WHERE [year] >= 2017
 GROUP BY [date]
 ORDER BY [date];

SELECT [event], [date], COUNT(*) AS [count]
  FROM [dbo].[events_data_by_capital] 
 WHERE [date] IN ('20200101', '20190101', '20180101')
 GROUP BY [event], [date]
 ORDER BY [event], [date];

-- Fix min date
UPDATE [dbo].[events_data_by_capital] 
   SET [date] = '20171231'
 WHERE [event] = 'EDA'
   AND [date] = '20180101';
UPDATE [dbo].[events_data_by_capital] 
   SET [date] = '20181230'
 WHERE [event] = 'EDA'
   AND [date] = '20190101';
UPDATE [dbo].[events_data_by_capital] 
   SET [date] = '20191229'
 WHERE [event] = 'EDA'
   AND [date] = '20200101';
GO
