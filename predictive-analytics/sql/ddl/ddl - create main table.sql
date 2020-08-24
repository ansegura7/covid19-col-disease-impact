USE [AC_C19_DATA]
GO

/****** Object:  Table [dbo].[indicator_by_departament]    Script Date: 8/10/2020 3:46:08 PM ******/
SET ANSI_NULLS ON
GO

SET QUOTED_IDENTIFIER ON
GO

CREATE TABLE [dbo].[indicator_by_departament](
	[indicator] [nvarchar](50) NULL,
	[sub_indicator] [nvarchar](250) NULL,
	[entity] [nvarchar](50) NULL,
	[department] [nvarchar](50) NULL,
	[year] [int] NULL,
	[week] [int] NULL,
	[date] [date] NULL,
	[value] [int] NULL
) ON [PRIMARY]
GO


