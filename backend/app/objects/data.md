# Time Series Data Endpoint

## Overview

The `/o/{object_type}/data` endpoint allows you to query any field from any object type as a time series with flexible aggregation and filtering options.

## Endpoint

```
POST /o/{object_type}/data
```

## Request Schema

```typescript
{
  field: string;                    // Column name to aggregate (e.g., "created_at", "amount", "status")
  time_range?: TimeRange;           // Relative time range (optional)
  start_date?: datetime;            // Absolute start date (overrides time_range)
  end_date?: datetime;              // Absolute end date (overrides time_range)
  granularity?: Granularity;        // Time bucket size (default: "automatic")
  aggregation?: AggregationType;    // Aggregation type (auto-determined if null)
  filters?: FilterDefinition[];     // Same filters as list endpoint
  fill_missing?: boolean;           // Fill gaps with null/0 (default: true)
}
```

## Time Ranges

### Relative Time Ranges
- `last_7_days`
- `last_30_days`
- `last_90_days`
- `last_6_months`
- `last_year`
- `year_to_date`
- `month_to_date`
- `all_time`

### Absolute Time Ranges
Specify `start_date` and/or `end_date` as ISO datetime strings. These override `time_range`.

**Default**: If no time range is specified, defaults to last 30 days.

## Granularity

### Automatic (Recommended)
Set `granularity: "automatic"` and the system will choose based on the time range:
- ≤ 1 day → hourly buckets
- ≤ 7 days → daily buckets
- ≤ 90 days → weekly buckets
- ≤ 365 days → monthly buckets
- ≤ 2 years → quarterly buckets
- > 2 years → yearly buckets

### Manual Options
- `hour`
- `day`
- `week`
- `month`
- `quarter`
- `year`

## Aggregation Types

Aggregation is automatically determined based on field type, but can be overridden:

### Numerical Fields (Int, Float, USD)
- `sum` - Sum of values (default for numerical)
- `avg` - Average of values
- `max` - Maximum value
- `min` - Minimum value
- `count` - Count of records

### Categorical Fields (String, Enum, Bool)
- `count` - Count of records (default for categorical)
- `mode` - Most frequent value with breakdown by category

## Response Schema

The response uses a discriminated union based on whether the data is numerical or categorical:

### Numerical Response
```typescript
{
  data: {
    type: "numerical";
    data_points: Array<{
      timestamp: datetime;
      value: number | null;
      count: number;
    }>;
  };
  field_name: string;
  field_type: FieldType;
  aggregation_type: AggregationType;
  granularity_used: Granularity;
  start_date: datetime;
  end_date: datetime;
  total_records: number;
}
```

### Categorical Response
```typescript
{
  data: {
    type: "categorical";
    data_points: Array<{
      timestamp: datetime;
      breakdowns: Record<string, number>;  // category -> count
      total_count: number;
    }>;
  };
  field_name: string;
  field_type: FieldType;
  aggregation_type: AggregationType;
  granularity_used: Granularity;
  start_date: datetime;
  end_date: datetime;
  total_records: number;
}
```

## Examples

### Example 1: Brand Creation Over Time

Query how many brands were created each day in the last 30 days:

```json
POST /o/brands/data
{
  "field": "created_at",
  "time_range": "last_30_days",
  "granularity": "day",
  "aggregation": "count"
}
```

Response:
```json
{
  "data": {
    "type": "numerical",
    "data_points": [
      {"timestamp": "2025-09-17T00:00:00Z", "value": 0, "count": 0},
      {"timestamp": "2025-09-18T00:00:00Z", "value": 3, "count": 3},
      {"timestamp": "2025-09-19T00:00:00Z", "value": 5, "count": 5},
      ...
    ]
  },
  "field_name": "created_at",
  "field_type": "datetime",
  "aggregation_type": "count",
  "granularity_used": "day",
  "start_date": "2025-09-17T00:00:00Z",
  "end_date": "2025-10-17T00:00:00Z",
  "total_records": 42
}
```

### Example 2: Campaign Status Breakdown

Query campaign status distribution over time with weekly buckets:

```json
POST /o/campaigns/data
{
  "field": "state",
  "time_range": "last_90_days",
  "granularity": "week",
  "aggregation": "count"
}
```

Response:
```json
{
  "data": {
    "type": "categorical",
    "data_points": [
      {
        "timestamp": "2025-07-21T00:00:00Z",
        "breakdowns": {
          "draft": 5,
          "active": 12,
          "completed": 3
        },
        "total_count": 20
      },
      {
        "timestamp": "2025-07-28T00:00:00Z",
        "breakdowns": {
          "draft": 3,
          "active": 15,
          "completed": 5
        },
        "total_count": 23
      },
      ...
    ]
  },
  "field_name": "state",
  "field_type": "enum",
  "aggregation_type": "count",
  "granularity_used": "week",
  "start_date": "2025-07-19T00:00:00Z",
  "end_date": "2025-10-17T00:00:00Z",
  "total_records": 156
}
```

### Example 3: Revenue Over Time with Filters

Query total invoice amounts per month, filtering for paid invoices only:

```json
POST /o/invoices/data
{
  "field": "amount",
  "time_range": "year_to_date",
  "granularity": "month",
  "aggregation": "sum",
  "filters": [
    {
      "type": "enum_filter",
      "column": "status",
      "values": ["paid"]
    }
  ]
}
```

Response:
```json
{
  "data": {
    "type": "numerical",
    "data_points": [
      {"timestamp": "2025-01-01T00:00:00Z", "value": 15420.50, "count": 23},
      {"timestamp": "2025-02-01T00:00:00Z", "value": 18950.00, "count": 31},
      {"timestamp": "2025-03-01T00:00:00Z", "value": 22100.75, "count": 28},
      ...
    ]
  },
  "field_name": "amount",
  "field_type": "usd",
  "aggregation_type": "sum",
  "granularity_used": "month",
  "start_date": "2025-01-01T00:00:00Z",
  "end_date": "2025-10-17T00:00:00Z",
  "total_records": 245
}
```

### Example 4: Absolute Date Range with Hourly Granularity

Query post creation for a specific day with hourly breakdown:

```json
POST /o/posts/data
{
  "field": "created_at",
  "start_date": "2025-10-15T00:00:00Z",
  "end_date": "2025-10-15T23:59:59Z",
  "granularity": "hour",
  "aggregation": "count",
  "fill_missing": true
}
```

## Filtering

The endpoint supports the same filtering system as the list endpoints:

### Available Filter Types

**Text Filter** (for String, Email, URL, Text fields):
```json
{
  "type": "text_filter",
  "column": "name",
  "operation": "contains",  // "contains" | "starts_with" | "ends_with" | "equals"
  "value": "acme"
}
```

**Range Filter** (for Int, Float, USD fields):
```json
{
  "type": "range_filter",
  "column": "amount",
  "start": 100,
  "finish": 1000
}
```

**Date Filter** (for Date, Datetime fields):
```json
{
  "type": "date_filter",
  "column": "created_at",
  "start": "2025-01-01T00:00:00Z",
  "finish": "2025-12-31T23:59:59Z"
}
```

**Boolean Filter**:
```json
{
  "type": "boolean_filter",
  "column": "is_active",
  "value": true
}
```

**Enum Filter**:
```json
{
  "type": "enum_filter",
  "column": "status",
  "values": ["active", "pending"]
}
```

## Fill Missing Data

When `fill_missing: true` (default), the endpoint generates a complete time series with no gaps:
- Missing numerical buckets are filled with `value: 0, count: 0`
- Categorical data is returned sparse (no filling)

Set `fill_missing: false` to return only buckets with actual data (sparse time series).

## Notes

- All timestamps are returned in UTC
- The `timestamp` in each data point represents the **start** of the time bucket
- The endpoint validates that the requested field exists in the object's column definitions
- Uses PostgreSQL's `date_trunc()` for efficient time bucketing
- Filters are applied **before** aggregation
- The TypeScript client provides full type safety with discriminated unions
