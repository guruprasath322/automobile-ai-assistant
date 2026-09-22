# Phase 4: Version 3 & 4 - SQLite Database Integration

## What We Built

**Version 3 & 4** adds permanent data storage using **SQLite**, a lightweight database that stores information in a single file.

1. **Database Schema**: Created `database/database.py` to manage two tables:
   - `vehicles`: Stores registration number, manufacturer, model, year, fuel, transmission, mileage, and service date.
   - `diagnosis_history`: Stores timestamp, vehicle registration, symptoms, predicted fault, confidence, severity, and recommendations.

2. **Persistence**:
   - Data no longer disappears when you refresh the page or restart the application.
   - The app automatically loads the last active vehicle on startup.

3. **Multi-Vehicle Support**:
   - Added a **Vehicle Selector** in the sidebar.
   - You can now register multiple vehicles and switch between them.
   - The Dashboard and History pages automatically filter data based on the selected vehicle.

## Why This Matters

A real-world application must remember user data. By moving from **Session State** (temporary memory) to **SQLite** (permanent storage), our app becomes a real tool:
- **History Tracking**: You can see how a vehicle's health changes over months.
- **Reliability**: Even if the server crashes, no data is lost.
- **Scalability**: We can easily add more tables (like maintenance schedules or user profiles) in the future.

## File Structure for Phase 4

```
automobile-ai-assistant/
├── app.py
├── database/
│   ├── database.py           # Database helper script
│   └── automobile_assistant.db # The actual database file (created automatically)
├── docs/
│   ├── phase1_architecture.md
│   ├── phase2_version1.md
│   ├── phase3_version2.md
│   └── phase4_version3_4.md  # This file
```

## How to Run Version 3 & 4

### Step 1: Run the App
```bash
streamlit run app.py
```

## Testing Version 3 & 4

### Test Case 1: Permanent Registration
1. Register a vehicle (e.g., `MH-12-XY-5678`, Honda City).
2. Refresh the browser page (or stop and start the app).
3. Expected Result: The vehicle details should still be visible on the Dashboard.

### Test Case 2: Multi-Vehicle Switch
1. Register a **second** vehicle (e.g., `KA-05-ZZ-9999`, Tata Nexon).
2. Look at the sidebar under **"🚗 Switch Vehicle"**.
3. Select the first vehicle (`MH-12-XY-5678`).
4. Expected Result: The Dashboard should update to show the Honda City's details.

### Test Case 3: History Persistence
1. Perform a diagnosis for the active vehicle.
2. Go to **"📋 Diagnosis History"**.
3. Verify the diagnosis is listed.
4. Refresh the page.
5. Expected Result: The diagnosis record should still be there.

## Key Database Concepts Explained

### 1. SQLite
Unlike MySQL or PostgreSQL, SQLite doesn't need a separate server. It stores everything in a simple `.db` file. This is perfect for beginners and mobile/desktop apps.

### 2. SQL (Structured Query Language)
The language used to talk to the database.
- `CREATE TABLE`: Setup the storage structure.
- `INSERT`: Save new data.
- `SELECT`: Retrieve saved data.

### 3. Primary Key
A unique identifier for each record. For our vehicles, the `registration_number` is the primary key because no two cars have the same number.

### 4. Foreign Key
A link between two tables. In `diagnosis_history`, the `vehicle_reg` column is a foreign key that points to the `vehicles` table, ensuring every diagnosis belongs to a registered car.

## Next Steps

Proceed to Phase 5 to implement the **OBD-II Simulation Module** and **DTC Lookup System**!
