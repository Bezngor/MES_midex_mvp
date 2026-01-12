# Power BI Integration

This document describes how to integrate the MES platform with Power BI.

## Data Source

- Use backend analytics export endpoints, for example:
  - `GET /api/v1/export/analytics?format=csv&date_from=...&date_to=...`

- The export should include fields such as:
  - `date`
  - `work_center_id`
  - `work_center_name`
  - `task_id`
  - `order_id`
  - `planned_time_minutes`
  - `actual_time_minutes`
  - `quality_passed` (boolean)
  - `status`

## Example DAX Measures

- OEE:
  ```text
  OEE = [Availability] * [Performance] * [Quality]
Availability:

text
Availability = 1 - (DIVIDE([DowntimeMinutes], [PlannedTimeMinutes]))
Performance:

text
Performance = DIVIDE([ActualTimeMinutes], [PlannedTimeMinutes])
Quality:

text
Quality = DIVIDE([PassedUnits], [TotalUnits])
(Implement actual measures according to your data model in Power BI.)

Reports
Example dashboards:

OEE by work center.

Task timeline (Gantt-style).

Order completion status over time.

Quality pass rate by product or work center.

Keep this document updated as analytics endpoints and Power BI models evolve.