# Scheduler

A Python application to manage worker's schedule by fetching data from an API  
and providing methods to:

- query busy and free timeslots
- check if a timeslot is available
- find slots for a given duration

The application contains tests for the mentioned methods.

## Setup

1. **Clone this repo to your machine:**

```bash
git clone https://github.com/MikhailKlidzhan/scheduler.git
cd scheduler
```

2. **Install Poetry if not yet:**

```bash
curl -sSL https://install.python-poetry.org | python3 -
```

3. **Install dependencies:**

```bash
poetry install
```

4. **Run tests:**

```bash
poetry run pytest tests/
```

## Usage

```python
from src.scheduler import Scheduler

# Initialize with your API endpoint
scheduler = Scheduler(url='https://api.example.com/schedule')

# Get busy slots
busy_slots = scheduler.get_busy_slots('2025-10-11')
print(f'Busy slots: {busy_slots}')

# Get free slots
free_slots = scheduler.get_free_slots('2025-10-11')
print(f'Free slots: {free_slots}')

# Check availability
is_available = scheduler.is_available('2025-10-11', '10:00', '11:30')
print(f'Available? {is_available}')

# Find a 30-min slot
slot = scheduler.find_slot_for_duration(30)
print(f'First available slot: {slot}')

```

## API Response Format

The application expects the following JSON structure from an API:

```json
{
  "days": [
    {
      "id": 1,
      "date": "2024-10-10",
      "start": "09:00",
      "end": "18:00"
    }
  ],
  "timeslots": [
    {
      "id": 1,
      "day_id": 1,
      "start": "11:00",
      "end": "12:00"
    }
  ]
}
```
