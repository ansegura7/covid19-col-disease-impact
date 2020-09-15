USE [AC_C19_DATA]
GO

/****** Object:  Table [dbo].[indicator_data]    Script Date: 9/1/2020 9:29:53 AM ******/
SET ANSI_NULLS ON
GO

SET QUOTED_IDENTIFIER ON
GO

CREATE TABLE [dbo].[indicator_data](
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


