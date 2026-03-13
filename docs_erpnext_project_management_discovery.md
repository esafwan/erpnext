# ERPNext Project Management Module Discovery

## 1. Purpose of This Document
This document is a code-and-metadata-based discovery of ERPNext Project Management, focused on the implementation under `erpnext/projects` and directly related cross-module behavior. It is intended as an engineering handoff reference before any frontend rebuild work.

## 2. Progress Tracker / Todo Board
Investigation order followed: module footprint → DocTypes → metadata → behavior logic → views/reports → backend contract → hidden dependencies → consolidation.

- [x] Identify module footprint
- [x] Identify core DocTypes
- [x] Inspect metadata
- [x] Inspect behavior logic
- [x] Inspect views and reports
- [x] Inspect backend contract
- [x] Inspect hidden dependencies
- [x] Compile final documentation

### Step Log (tracked)
1. **[x] Step 1 — Module footprint**  
   - **Goal:** Enumerate all files under `erpnext/projects`.  
   - **Inspected:** doctype/report/workspace/dashboard/number_card/module_onboarding/web_form trees.  
   - **Findings:** Projects module includes `Project`, `Task`, `Timesheet` families plus template/update/settings masters, dedicated reports, dashboard chart + number cards, workspace, tree/calendar/list JS.  
   - **Open questions:** None.

2. **[x] Step 2 — Core + supporting DocTypes**  
   - **Goal:** Identify central vs supporting models.  
   - **Inspected:** all `erpnext/projects/doctype/*/*.json` + related `.py/.js`.  
   - **Findings:** Core: `Project`, `Task`, `Project Update`, `Timesheet`, `Timesheet Detail`. Supporting: `Project Template`, `Project Template Task`, `Task Depends On`, `Project User`, `Project Type`, `Task Type`, `Activity Type`, `Activity Cost`, `Projects Settings`.  
   - **Open questions:** `Dependent Task` exists but appears minimally used (legacy/auxiliary table).

3. **[x] Step 3 — Metadata extraction**  
   - **Goal:** Capture field-level metadata including `depends_on`/linkage.  
   - **Inspected:** DocType JSON definitions for core/supporting types.  
   - **Findings:** `Project` has 59 fields with progress-collection scheduler fields; `Task` is tree (`is_tree=1`) with dependency table; `Timesheet` is submittable with detail table and billing/currency fields; multiple hidden/read-only computed fields.  
   - **Open questions:** Some status-related UI conditions reference old status strings (not fully aligned with current options).

4. **[x] Step 4 — Python behavior**  
   - **Goal:** Trace server-side lifecycle and calculations.  
   - **Inspected:** `project.py`, `task.py`, `timesheet.py`, `timesheet_detail.py`, `project_template.py`, `project_update.py`, `utils.py`.  
   - **Findings:** Project progress/costing is heavily server-derived; task updates cascade to project; timesheet submission updates task/project; scheduler jobs drive reminders, overdue flags, and sales/billing recalculation.  
   - **Open questions:** `project_update.py.daily_reminder` overlaps conceptually with reminder logic already in `project.py`.

5. **[x] Step 5 — JS/view behavior**  
   - **Goal:** Trace form/list/tree/calendar UX logic.  
   - **Inspected:** doctype JS/list/tree/calendar files + report JS.  
   - **Findings:** Project form adds action buttons (duplicate/update costing/set status/Gantt/Kanban). Task list has bulk status action and Gantt popup. Timesheet form includes timer flow, dynamic currency/rate behavior, and create-invoice action.
   - **Open questions:** None.

6. **[x] Step 6 — Views/reports/workspace/dashboard**  
   - **Goal:** Map user entry points and analytical surfaces.  
   - **Inspected:** `report/*`, `workspace/projects/projects.json`, dashboard chart + number cards + dashboard metadata.  
   - **Findings:** Workspace combines masters + transactional docs + query reports. Project dashboard uses Project Summary report chart. Number cards show open projects, non-completed tasks, timesheet hours.
   - **Open questions:** None.

7. **[x] Step 7 — Backend contract**  
   - **Goal:** Enumerate whitelisted methods + frontend-callable flows.  
   - **Inspected:** `@frappe.whitelist` methods under projects + JS `frappe.call/xcall` invocations.  
   - **Findings:** Key callable methods include project duplication/status/cost recalculation/kanban setup; task bulk status/tree methods/timesheet mapping; timesheet rate fetch/report-like APIs and sales invoice creation.
   - **Open questions:** None.

8. **[x] Step 8/9/10 — Cross-module dependencies + hidden logic + final consolidation**  
   - **Goal:** Capture non-obvious behavior and external side effects.  
   - **Inspected:** `erpnext/hooks.py`, `stock_entry.py` material cost update, issue/task linkage, assignment utilities.  
   - **Findings:** Project metrics are impacted by stock entry consumption cost and accounting docs; assignment closure/clearing occurs via task status changes; website list contexts exist for Project/Timesheet.
   - **Open questions:** runtime permission constraints may vary with installed apps/roles and website mode.

## 3. Executive Summary
ERPNext Project Management is implemented as a tightly coupled set of transactional DocTypes (`Project`, `Task`, `Timesheet`) with derived analytics and reminder automation. `Project` and `Task` are the behavior core: task lifecycle and dependencies drive project completion, while timesheet + sales/purchase/stock references drive project cost, billing, and margin metrics. `Project Update` supports periodic status collection via email-driven workflows. Most critical logic lives in server controllers (`project.py`, `task.py`, `timesheet.py`) with complementary form/list/tree JS behaviors. The biggest parity risk in a rebuild is missing implicit side effects: project/task auto-sync, dependency enforcement, scheduled status transitions, and computed financial fields sourced from multiple modules.

## 4. Module Footprint

### Core DocTypes
- **Project** — project lifecycle, scheduling, users, financial/progress rollups.  
  Paths: `erpnext/projects/doctype/project/*`
- **Task** — hierarchical work items, status/progress/dependencies.  
  Paths: `erpnext/projects/doctype/task/*`
- **Timesheet** — time logging + billing pipeline.  
  Paths: `erpnext/projects/doctype/timesheet/*`
- **Timesheet Detail** — child rows for time entries linked to project/task/activity.  
  Path: `erpnext/projects/doctype/timesheet_detail/*`
- **Project Update** — status-update communication record (submittable).  
  Path: `erpnext/projects/doctype/project_update/*`

### Supporting DocTypes
- `Project Template`, `Project Template Task`
- `Task Depends On`, `Dependent Task`
- `Project User`
- `Project Type`, `Task Type`
- `Activity Type`, `Activity Cost`
- `Projects Settings`

### Child Tables
- `Project User`
- `Task Depends On`
- `Project Template Task`
- `Timesheet Detail`

### Reports
- `Project Summary`
- `Delayed Tasks Summary`
- `Daily Timesheet Summary`
- `Timesheet Billing Summary`
- `Project wise Stock Tracking`

### Workspaces / Dashboards / Cards
- Workspace: `erpnext/projects/workspace/projects/projects.json`
- Dashboard metadata: `erpnext/projects/projects_dashboard/project/project.json`
- Dashboard charts: `dashboard_chart/project_summary`, `dashboard_chart/completed_projects`
- Number cards: `open_projects`, `non_completed_tasks`, `timesheet_working_hours`

### JS and client files
- Core forms/lists: `project.js`, `project_list.js`, `task.js`, `task_list.js`, `timesheet.js`, `timesheet_list.js`
- Alternate views: `task_tree.js`, `task_calendar.js`, `timesheet_calendar.js`
- Supporting forms: `project_template.js`, `project_update.js`, `activity_type.js`

### Hooks / utilities / other relevant files
- Scheduler + routes + website hooks: `erpnext/hooks.py`
- Search utility: `erpnext/projects/utils.py`
- Cross-module cost side effect: `erpnext/stock/doctype/stock_entry/stock_entry.py` (`update_cost_in_project`)
- Web form: `erpnext/projects/web_form/tasks/*`

## 5. DocType Relationship Map

```text
Project (parent)
 ├─ users -> Project User (child table)
 ├─ tasks <- Task.project (1:N)
 │   ├─ depends_on -> Task Depends On (child table referencing Task)
 │   └─ parent_task -> Task (tree hierarchy)
 ├─ timesheets <- Timesheet.parent_project / Timesheet Detail.project
 ├─ updates <- Project Update.project
 │   └─ users -> Project User (status/comment rows in update context)
 ├─ templates <- Project.project_template -> Project Template
 │   └─ tasks -> Project Template Task -> Task (template tasks)
 └─ financial linkage via Sales Order / Sales Invoice / Purchase Invoice / Stock Entry

Timesheet
 └─ time_logs -> Timesheet Detail
      ├─ activity_type -> Activity Type (+ Activity Cost overrides)
      ├─ task -> Task
      └─ project -> Project
```

Dependency chains:
- Task status/progress/date changes → `Task.on_update()` → project recompute.
- Timesheet submit/cancel/update → task + project time/cost rollups.
- Stock Entry consumed material recalculation updates `Project.total_consumed_material_cost`.
- Scheduled jobs set overdue tasks and send project update reminders/summary emails.

## 6. Detailed DocType Documentation

## DocType: `Project`
### Role in Project Management
Top-level planning, ownership, progress model, and financial rollup document.

### File Paths
- `erpnext/projects/doctype/project/project.json`
- `erpnext/projects/doctype/project/project.py`
- `erpnext/projects/doctype/project/project.js`
- `erpnext/projects/doctype/project/project_list.js`
- `erpnext/projects/doctype/project/project_dashboard.py`
- `erpnext/projects/doctype/project/project_dashboard.html`

### Metadata Summary
- `autoname`: `naming_series:` (series default `PROJ-.####`)
- non-submittable; non-tree
- child table: `users` (`Project User`)
- key links: `Project Type`, `Project Template`, `Department`, `Customer`, `Sales Order`, `Company`, `Cost Center`, `Holiday List`
- progress mode: manual/completion/progress/weight
- collect-progress scheduling fields conditionally displayed via `depends_on`

### Fields Table (behavioral)
| fieldname | type | key behavior |
|---|---|---|
| `project_name` | Data (reqd) | Human title; used in UI and reminders. |
| `status` | Select | Open/Completed/Cancelled; auto-updated by completion logic unless cancelled. |
| `percent_complete_method` | Select | Controls percent calculation source. |
| `percent_complete` | Percent (read_only) | Computed unless manual. |
| `project_template` | Link | Triggers task copy when project has no tasks. |
| `expected_start_date` / `expected_end_date` | Date | Validated from/to; drives template task scheduling. |
| `users` | Table(Project User) | Collaboration list + reminder recipients. |
| `actual_start_date` / `actual_end_date` / `actual_time` | Read-only | Derived from submitted timesheet details. |
| `estimated_costing` | Currency | Estimated budget signal (manual input). |
| `total_costing_amount` / `total_billable_amount` / `total_billed_amount` | Currency read-only | Computed from timesheets/invoices. |
| `total_purchase_cost` | Currency read-only | Derived from submitted purchase invoice items. |
| `total_consumed_material_cost` | Currency read-only | Updated by stock entry consumed-material rollup. |
| `gross_margin` / `per_gross_margin` | Read-only | Computed from billed minus costs. |
| `collect_progress` + schedule fields | Check/Time/Select | Governs automated project-update reminder flow. |
| `subject` / `message` | Data/Text | Used as reminder email content when collect-progress enabled. |

### Form Structure
- Main planning fields + status/priority/type/customer/sales order.
- Team table (`users`) for collaboration.
- Notes + accounting/costing section with computed totals.
- Progress collection section appears when `collect_progress` checked, with frequency-specific time fields.
- Custom buttons add operational actions (duplicate, force costing update, set project status, Gantt, Kanban).

### Business Logic
- `validate`: welcome email, costing update, percent completion update, date validation.
- Template copy: if template exists and no tasks, creates project tasks from template task docs and remaps dependencies/parent links.
- Percent complete:
  - Manual: user-driven (or forced 100 on completed).
  - Task Completion: completed+cancelled count / total.
  - Task Progress: avg task progress.
  - Task Weight: weighted sum by `task_weight`.
- Status autopivot to Completed/Open from percent (except Cancelled state preserved).
- Costing update aggregates submitted `Timesheet Detail`, purchase cost, sales amount, billed amount; computes margins.
- Scheduler helpers send reminder/update-summary emails and auto-create `Project Update` drafts.
- Whitelisted actions: duplicate project (with tasks), set global status for project+tasks, create Kanban board, force update costing/billing.

### UI/Behavior Significance
Project is the integration hub: operational planning + derived cost/profit metrics + team communication workflow.

### Related Code Paths
- `Project.update_percent_complete`, `update_costing`, `calculate_gross_margin`
- `copy_from_template`, `dependency_mapping`
- `send_project_update_email_to_users`, `collect_project_status`, `send_project_status_email_to_users`
- `set_project_status`, `create_duplicate_project`, `update_costing_and_billing`

### Notes / Risks
- Completion metric depends on task states including Cancelled.
- Multiple external document types influence project financial fields.
- Reminder flow depends on scheduler timing and configured holiday list/users.

---

## DocType: `Task`
### Role in Project Management
Granular executable unit with hierarchy, dependency graph, progress/status, and time-cost accumulation.

### File Paths
- `erpnext/projects/doctype/task/task.json`
- `erpnext/projects/doctype/task/task.py`
- `erpnext/projects/doctype/task/task.js`
- `erpnext/projects/doctype/task/task_list.js`
- `erpnext/projects/doctype/task/task_tree.js`
- `erpnext/projects/doctype/task/task_calendar.js`
- `erpnext/projects/doctype/task/task_dashboard.py`

### Metadata Summary
- `autoname`: `TASK-.YYYY.-.#####`
- `is_tree=1`, nested set (`parent_task`, `lft`, `rgt`)
- dependency child table: `depends_on` (`Task Depends On`)
- key links: `Project`, `Issue`, `Task Type`, `Task` parent, `Department`, `Company`, `User`
- template fields: `is_template`, `start`, `duration`, `template_task`

### Fields Table (behavioral)
| fieldname | type | key behavior |
|---|---|---|
| `subject` | Data (reqd) | Task title. |
| `project` | Link(Project) | Governs project rollup and filtering. |
| `status` | Select | Open/Working/Pending Review/Overdue/Template/Completed/Cancelled. |
| `priority` | Select | Low/Medium/High/Urgent. |
| `is_group` | Check | Required for parenting child tasks. |
| `parent_task` | Link(Task) | Tree hierarchy; parent must be group. |
| `depends_on` | Table(Task Depends On) | Dependency prerequisites for completion/rescheduling. |
| `exp_start_date` / `exp_end_date` | Datetime | Date constraints + overdue logic. |
| `expected_time` | Float | If set and end date missing, auto-computes end date. |
| `progress` | Percent | Max 100; forced 100 when completed. |
| `task_weight` | Float | Used in project weighted completion model. |
| `act_start_date` / `act_end_date` / `actual_time` | Read-only | Derived from submitted timesheets. |
| `total_costing_amount` / `total_billing_amount` | Read-only | Derived from timesheets. |
| `completed_by` / `completed_on` | conditional | completion metadata. |
| `is_template`, `start`, `duration`, `template_task` | template controls | used in project template copy/scheduling. |

### Form Structure
- Core fields for project/status/priority/type/parent.
- Schedule/progress fields.
- Dependency child table.
- Actual time/cost summary read-only section.
- Template-specific fields conditionally shown.

### Business Logic
- Validation stack: date order, progress cap, status consistency, dependency string update, template dependency correctness, completion date validity, parent-is-group enforcement.
- Completion guard: cannot mark completed if dependent tasks not completed/cancelled.
- On update: updates nested set, recursion check, reschedules dependent tasks, triggers project refresh, handles assignment cleanup, auto-populates parent dependency row.
- Rescheduling: if a dependency task pushes later, open dependent tasks are shifted forward preserving duration.
- Overdue scheduler: `set_tasks_as_overdue` updates non-completed tasks based on expected end/review dates.
- Deletion guard: blocks delete when child tasks exist.
- Whitelisted APIs: child existence check, project query, bulk status set, make timesheet, tree load/add node/add multiple.

### UI/Behavior Significance
Task is both list/tree/calendar/gantt primitive and the main driver of project completion state.

### Notes / Risks
- Dependency semantics are non-trivial (completion prerequisites + date shifts + recursion checks).
- Parent group rules and nested-set behavior are critical for tree parity.

---

## DocType: `Timesheet` / `Timesheet Detail`
### Role in Project Management
Captures work logs and converts them into billing/costing amounts that feed task and project analytics.

### File Paths
- `erpnext/projects/doctype/timesheet/timesheet.json`, `.py`, `.js`, `_list.js`, `_calendar.js`, `_dashboard.py`
- `erpnext/projects/doctype/timesheet_detail/timesheet_detail.json`, `.py`

### Metadata Summary
- `Timesheet`: submittable, naming series, `time_logs` child table (`Timesheet Detail`), employee/user/customer/project/currency context fields, aggregate totals and billed percentage.
- `Timesheet Detail`: project/task/activity row with from/to/hours, billable toggles, rates, amounts, base-currency mirrors.

### Key Fields
- Parent-level: `employee`, `parent_project`, `customer`, `currency`, `exchange_rate`, totals (`total_hours`, `total_billable_amount`, etc.).
- Row-level: `activity_type`, `task`, `project`, `hours`, `billing_hours`, `is_billable`, `billing_rate`, `costing_rate`, derived amounts.

### Business Logic
- Parent validate/on_submit/on_cancel recalculates totals/status/dates and updates linked Task/Project rollups.
- Overlap validation for workstation/user/employee is controlled by `Projects Settings` flags.
- `Timesheet Detail` ensures task-project coherence, date validity, billing-hour warnings, and auto-derivations (`to_time`, `project`, rates, amounts).
- JS adds timer UX, dynamic currency labels, rate fetches (`get_activity_cost`), and invoice creation (`make_sales_invoice`).

### UI/Behavior Significance
Timesheet directly powers project/task actual effort/cost and downstream billing operations.

---

## DocType: `Project Update`
### Role
Captures project-status updates from collaborators; supports reminder and summary email workflow.

### Metadata
- Submittable; link to `Project`; child table `users` (`Project User`) storing status entries.
- Date/time/sent are read-only and auto-filled by JS/server flows.

### Logic
- Project reminder jobs create updates and collect email replies into update rows.
- `collect_project_status()` parses inbound communication replies and appends HTML statuses per user.

---

## Supporting Master/Structure DocTypes
- **Project Template / Project Template Task:** defines reusable task sets; validates dependencies are present in template list.
- **Task Depends On:** per-row link + fetched subject; drives dependency graph.
- **Project User:** shared child table for project team and project-update status rows.
- **Project Type / Task Type:** classification masters; task type exposes `weight` used by task defaulting and weighted progress.
- **Activity Type / Activity Cost:** default and employee-specific costing/billing rates.
- **Projects Settings:** singleton flags that toggle overlap validations and sales-invoice timesheet behavior.
- **Dependent Task:** single link child table; limited active behavior observed in current core flows.

## 7. Child Tables and Nested Structures
- **Project User**
  - Parents: `Project`, `Project Update`.
  - Key fields: user identity, email/full_name/image fetch, `welcome_email_sent`, attachment visibility flags, `project_status` text (shown in Project Update context).
  - Impact: recipient determination, collaboration onboarding, update summaries.

- **Task Depends On**
  - Parent: `Task`.
  - Fields: dependency task link + fetched subject + project text.
  - Impact: completion lock, recursive dependency validation, dependent task rescheduling.

- **Project Template Task**
  - Parent: `Project Template`.
  - Fields: template task link + fetched subject.
  - Impact: controls generated project task set and template dependency validation.

- **Timesheet Detail**
  - Parent: `Timesheet`.
  - Fields: activity/time/task/project/rate/amount vectors.
  - Impact: source of all task/project time and costing rollups.

## 8. Feature Inventory
### Project lifecycle features
- Project creation with naming series and optional template-based task generation.
- Status controls including forced mass transition for project + all tasks.
- Costing/billing manual refresh action.

### Task lifecycle features
- Tree hierarchy and group tasks.
- Status + progress management with completion constraints.
- Bulk list status update and overdue scheduler updates.

### Task dependency features
- Child table dependencies.
- Circular reference prevention and auto-rescheduling of downstream tasks.

### Progress tracking features
- Project percent completion by manual/task completion/task progress/task weight.
- Task progress capped at 100 and forced to 100 on completion.

### Assignment / timeline / communication
- Task completion/cancel closes or clears ToDo assignments.
- Project updates gather communication replies into user status rows.
- Project onload provides activity summary for dashboard context.

### Reporting + dashboards
- Query reports for project summary, delayed tasks, timesheet summaries, stock tracking.
- Workspace cards/charts/number cards for operational navigation.

### Linked document features
- Sales/Purchase/Stock integrations update project totals and margins.
- Issue link on task.
- Timesheet-to-sales-invoice creation flow.

## 9. Hooks, Controllers, and Behavioral Entry Points
### Python controllers
- `Project.validate/onload/update_project/...` — progress, costs, template copy, reminders.
- `Task.validate/on_update/...` — dependencies, tree model, project sync, assignment cleanup.
- `Timesheet.validate/on_submit/on_cancel/...` — totals, overlap checks, downstream updates.
- `TimesheetDetail` methods — row-level derivations/validations.

### JS form logic
- `project.js`: custom actions and filtered link queries.
- `task.js`: dependency/parent queries, group conversion warning behavior.
- `timesheet.js`: timer UX, dynamic rates/currency, invoice creation.

### List/tree/calendar logic
- `project_list.js`: indicator based on status/completion.
- `task_list.js`: indicator, bulk status actions, gantt popup customization.
- `task_tree.js`: server-backed tree nodes and bulk add dialog.
- `task_calendar.js` + `timesheet_calendar.js`: alternate calendar/gantt configs.

### Hook-based logic
In `erpnext/hooks.py` scheduler events include:
- project reminder collection + status mail sending + sales/billing updates.
- periodic task overdue updater.
Also includes route redirects and website permissions context involving Project.

### Helpers/utilities
- `erpnext/projects/utils.py::query_task` (search API)
- project/task/ timesheet whitelisted methods (documented below)

## 10. Conditions, Dependencies, and Hidden Logic
- `Project.collect_progress` controls visibility/usage of frequency/time/message/subject fields.
- Frequency-specific fields shown via `depends_on` expressions.
- `Task.completed_on`, `completed_by`, template offsets, review/closing dates are conditionally displayed.
- `Task.validate_status` blocks completion until dependencies are completed/cancelled.
- `Task.on_update` can reschedule dependent tasks automatically.
- `Task.update_project` silently triggers project recompute unless flagged `from_project`.
- `Project.update_percent_complete` can auto-flip project status.
- `Project.send_welcome_email` mutates child rows (`welcome_email_sent`) during validation.
- `Timesheet` overlap checks depend on singleton settings flags.
- `Timesheet Detail.task` auto-sets project in client and server flows.
- `Stock Entry.update_cost_in_project` updates project consumed material cost outside projects module.
- Assignment side effects occur via `close_all_assignments` / `clear` in task updates.

## 11. Endpoints and Backend Contract
### Standard document access patterns
As standard Frappe DocTypes, Project/Task/Timesheet support list/get/insert/save/submit/cancel via framework APIs (`frappe.get_list`, `frappe.get_doc`, desk form saves, etc.).

### Confirmed whitelisted methods
- `erpnext.projects.doctype.project.project.get_users_for_project`
- `...project.get_cost_center_name`
- `...project.create_duplicate_project`
- `...project.create_kanban_board_if_not_exists`
- `...project.set_project_status`
- `...project.update_costing_and_billing`
- `erpnext.projects.doctype.task.task.check_if_child_exists`
- `...task.get_project`
- `...task.set_multiple_status`
- `...task.make_timesheet`
- `...task.get_children`
- `...task.add_node`
- `...task.add_multiple_tasks`
- `erpnext.projects.doctype.timesheet.timesheet.get_projectwise_timesheet_data`
- `...timesheet.get_timesheet_detail_rate`
- `...timesheet.get_timesheet`
- `...timesheet.get_timesheet_data`
- `...timesheet.make_sales_invoice`
- `...timesheet.get_activity_cost`
- `...timesheet.get_events`
- `erpnext.projects.utils.query_task`
- `erpnext.projects.doctype.project_update.project_update.daily_reminder`

### Report/data methods
Each report exposes `execute(filters)` in corresponding `report/<report>/<report>.py`, returning columns + data (+ chart/summary in some reports).

### Frontend server-call patterns
- Project form invokes duplicate/status/costing/Kanban server methods.
- Task list invokes bulk status setter; tree view calls child-node APIs.
- Timesheet form calls activity cost fetch and sales invoice generation.

## 12. Views, Reports, Workspace, Dashboard, and Navigation
### Form views
- Rich action-enabled forms for Project/Task/Timesheet.

### List views
- Project list default filter `status=Open`; percent indicator.
- Task list default `status=Open`; status indicator + bulk actions.
- Timesheet list custom indicators by status.

### Alternate views
- Task tree view (project/task filters).
- Task calendar with gantt enabled.
- Timesheet calendar with gantt enabled.

### Reports
- Project Summary: per-project totals with chart + report summary.
- Delayed Tasks Summary: delay computations and percentage chart.
- Daily Timesheet Summary: row-level time log extract.
- Timesheet Billing Summary: optionally grouped tree-style output.
- Project wise Stock Tracking: purchased/issued/delivered cost rollup.

### Workspace/dashboard
- Workspace “Projects” links masters, transactions, settings, and query reports.
- Includes “Completed Projects” chart and three number cards.
- Document dashboard for Project includes chart reference to “Project Summary”.

## 13. Permissions and Access Behavior Relevant to Module Understanding
- DocType permission matrices are declared in each DocType JSON; core docs include role-specific read/write/create/submit controls.
- Project website list behavior is permission-aware (customer/contact context via website controller hooks).
- Task webform permission includes project membership check (`Project User` child table) in `has_webform_permission`.
- Certain query methods use match conditions (`get_users_for_project`, `get_project`, report match conditions).
- Mass project status update explicitly checks doc permission before applying task changes.

## 14. Risks, Ambiguities, and Open Questions
### Confirmed
- Core lifecycle/cost/progress logic is server-driven in project/task/timesheet controllers.
- Task dependency and tree logic materially affect UX and data integrity.
- Workspace/report/dashboard artifacts are first-class navigation surfaces.

### Inferred (high confidence)
- Some behavior depends on framework-standard timeline/comments/tags/files for all non-single DocTypes (not custom-coded here but enabled by Frappe document framework).
- API contract for CRUD mostly follows standard Frappe DocType routes in addition to whitelisted methods.

### Not fully resolved
- Legacy or overlapping reminder logic in `project_update.py` vs `project.py` may lead to deployment-specific usage.
- Installed-app combinations and custom scripts/property setters can alter statuses/fields at runtime.
- `Dependent Task` table has low visibility in current execution paths; likely compatibility artifact.

## 15. Final Consolidated Understanding
ERPNext Project Management is a backend-heavy module where `Project` orchestrates planning, progress, communication, and finance; `Task` encodes execution hierarchy/dependencies; and `Timesheet` converts work logs into cost/billing signals. Significant behavior is distributed across DocType metadata (`depends_on`/links), server controller side effects, scheduled jobs, and targeted JS workflows for forms and alternate list/tree/gantt views. Any future frontend parity effort must preserve: dependency enforcement and rescheduling, project percent-complete modes, timesheet-to-task/project rollups, periodic reminder/update flows, and cross-module financial rollups (sales/purchase/stock).
