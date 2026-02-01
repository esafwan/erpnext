# Demo data setup in ERPNext (Frappe app)

This document explains how ERPNext wires demo data into the install/setup experience, how the data is produced, and how you can replicate the pattern in another Frappe app.

## Where the demo-data option shows up

ERPNext adds a **“Generate Demo Data for Exploration”** checkbox to the setup wizard. This is defined in the setup wizard front-end slide configuration (`setup_wizard.js`) under the organization slide as the `setup_demo` field. When checked, its value is included in the setup wizard payload. 【F:erpnext/public/js/setup_wizard.js†L30-L74】

## How the setup wizard triggers demo data

ERPNext’s `hooks.py` connects the setup wizard’s completion hook to `erpnext.setup.setup_wizard.setup_wizard.setup_demo`. This is the hook the Frappe setup flow calls when the wizard finishes. 【F:erpnext/hooks.py†L65-L70】

Inside `setup_wizard.py`, the `setup_demo` function checks the incoming args for `setup_demo` and, if present, enqueues demo data creation after the setup transaction commits. This keeps demo creation asynchronous and ensures it only runs after the base setup is persisted. 【F:erpnext/setup/setup_wizard/setup_wizard.py†L67-L70】

## What happens during demo data creation

ERPNext’s demo pipeline is in `erpnext/setup/demo.py`:

1. **`setup_demo_data()`** is the entry point. It creates a demo company, loads demo master data, and then creates demo transactions. It also clears cache keys and publishes a realtime event on success. 【F:erpnext/setup/demo.py†L18-L36】
2. **Company cloning:** `create_demo_company()` takes the first existing Company, creates a “(Demo)” company, sets it as default, and adds a demo bank account. It also records the demo company in *Global Defaults* for later cleanup. 【F:erpnext/setup/demo.py†L59-L83】
3. **Master data:** `process_masters()` iterates `demo_master_doctypes` from hooks and loads JSON fixtures from `erpnext/setup/demo_data/*.json` (via `read_data_file_using_hooks`) before inserting them. 【F:erpnext/setup/demo.py†L85-L101】【F:erpnext/setup/demo.py†L225-L231】
4. **Transactions:** `make_transactions()` iterates `demo_transaction_doctypes` from hooks, loads JSON fixtures, and creates transactions with dates/warehouses adjusted for the demo company. It then converts some orders into invoices and payments. 【F:erpnext/setup/demo.py†L104-L175】
5. **Data source:** `read_data_file_using_hooks()` reads the JSON fixtures from `erpnext/setup/demo_data` based on the doctype key. 【F:erpnext/setup/demo.py†L225-L231】

The doctype lists that drive which JSON files are loaded are defined in `hooks.py` as `demo_master_doctypes` and `demo_transaction_doctypes`. 【F:erpnext/hooks.py†L95-L106】

## How demo data is cleaned up

ERPNext exposes `clear_demo_data()` as a whitelisted method. It uses the demo company recorded in *Global Defaults* to delete demo transactions and masters, then deletes the demo company itself. This is the counterpart to demo setup and is essential for reversible demo installs. 【F:erpnext/setup/demo.py†L37-L83】【F:erpnext/setup/demo.py†L194-L223】

## Implementation checklist for other Frappe apps

Use the ERPNext wiring as a blueprint:

1. **Expose a setup option in the wizard UI**
   - Add a checkbox (e.g., `setup_demo`) to your setup wizard UI so the user can opt in. ERPNext does this in `erpnext/public/js/setup_wizard.js`. 【F:erpnext/public/js/setup_wizard.js†L30-L74】

2. **Wire a completion hook in `hooks.py`**
   - Set `setup_wizard_complete` to your app’s handler (e.g., `my_app.setup.setup_wizard.setup_demo`). ERPNext wires this to `erpnext.setup.setup_wizard.setup_wizard.setup_demo`. 【F:erpnext/hooks.py†L65-L70】

3. **Enqueue demo creation after commit**
   - In your setup handler, check the incoming args and enqueue your demo job with `enqueue_after_commit=True` so base setup is committed before demo data is inserted. This pattern is shown in ERPNext’s `setup_demo()` implementation. 【F:erpnext/setup/setup_wizard/setup_wizard.py†L67-L70】

4. **Define demo doctypes in hooks**
   - Add `demo_master_doctypes` and `demo_transaction_doctypes` in your app’s `hooks.py`. ERPNext uses these lists to decide which JSON fixtures to load. 【F:erpnext/hooks.py†L95-L106】

5. **Store demo fixtures in your app**
   - Place JSON fixtures under a predictable location (ERPNext uses `erpnext/setup/demo_data`) and load them dynamically so you can use hooks to decide which files are used. 【F:erpnext/setup/demo.py†L85-L101】【F:erpnext/setup/demo.py†L225-L231】

6. **Provide cleanup/reset**
   - Implement a `clear_demo_data()` or equivalent to delete the demo company and any demo data. ERPNext uses *Global Defaults* (`demo_company`) to keep a stable reference for cleanup. 【F:erpnext/setup/demo.py†L37-L83】【F:erpnext/setup/demo.py†L194-L223】

## Execution flow summary (ERPNext)

1. User checks **Generate Demo Data** during setup. 【F:erpnext/public/js/setup_wizard.js†L30-L74】
2. Setup wizard completes and `setup_wizard_complete` calls ERPNext’s `setup_demo` hook. 【F:erpnext/hooks.py†L65-L70】
3. `setup_demo` enqueues `setup_demo_data` after commit. 【F:erpnext/setup/setup_wizard/setup_wizard.py†L67-L70】
4. `setup_demo_data` creates the demo company, loads masters, and inserts demo transactions from JSON fixtures. 【F:erpnext/setup/demo.py†L18-L175】
5. Demo data can be cleared later via `clear_demo_data()`. 【F:erpnext/setup/demo.py†L37-L83】【F:erpnext/setup/demo.py†L194-L223】
