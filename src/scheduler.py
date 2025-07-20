import requests
from datetime import datetime, timedelta

class Scheduler:
    '''
    A class to manage worker's schedule and timeslots from API.

    Attributes:
        url (str): API endpoint to fetch schedule data.
        days (list): List of working day dictionaries.
        timeslots (list): List of busy timeslots dictionaries.
    '''

    def __init__(self, url: str) -> None:
        '''
        Initialize the Scheduler with API URL and fetch schedule data.

        Args:
            url (str): API endpoint to fetch schedule data.

        Raises:
            requests.RequestException: If API request fails.
        '''
        self.url = url
        self.days = []
        self.timeslots = []
        self._fetch_schedule()

    def _fetch_schedule(self) -> None:
        '''
        Fetch schedule data from API and populate days and timeslots.

        Raises:
            requests.RequestException: If API request fails.
        '''
        response = requests.get(self.url)
        response.raise_for_status()
        data = response.json()
        self.days = data.get('days', [])
        self.timeslots = data.get('timeslots', [])


    def _parse_datetime(self, date_str: str, time_str: str) -> datetime:
        '''
        Parse date and time strings into a datetime object.
        Args:
            date_str (str): Date in "YYYY-MM-DD" format.
            time_str (str): Time in "HH-MM" format.

        Returns:
            A datetime object with date and time.
        '''
        return datetime.strptime(f'{date_str} {time_str}', '%Y-%m-%d %H:%M')
        
    
    def _validate_date(self, date: str) -> None:
        '''
        Raise ValueError if a date is not in the schedule.
        '''
        if not any(d['date'] == date for d in self.days):
            raise ValueError(f'Date {date} not found in the schedule')


    def get_busy_slots(self, date: str) -> list[tuple[str, str]]:
        '''
        Get all busy timeslots for specified date.

        Args:
            date (str): Date in "YYYY-MM-DD" format.

        Returns:
            List of tuples with start and end times of busy slots.
        '''
        busy_slots = []
        for timeslot in self.timeslots:
            day = next((d for d in self.days if d['id'] == timeslot['day_id']), None)
            if day and day['date'] == date:
                busy_slots.append((timeslot['start'], timeslot['end']))
        return busy_slots
        

    def get_free_slots(self, date: str) -> list[tuple[str, str]]:
        '''
        Get all free timeslots for the specified date.

        Args:
            date (str): Date in "YYYY-MM-DD" format.

        Returns:
            List of tuples with start and end times of free slots.
        '''
        self._validate_date(date)

        day = next((d for d in self.days if d['date'] == date), None)
        if not day:
            return []
            
        start = self._parse_datetime(date, day['start'])
        end = self._parse_datetime(date, day['end'])
        busy_slots = [
            (
                self._parse_datetime(date, slot['start']),
                self._parse_datetime(date, slot['end'])
            )
            for slot in self.timeslots
            if (day := next((d for d in self.days if d['id'] == slot['day_id']), None)) is not None and day['date'] == date
        ]

        free_slots = []
        current = start
        for busy_start, busy_end in sorted(busy_slots):
            if current < busy_start:
                free_slots.append((current.strftime('%H:%M'), busy_start.strftime('%H:%M')))
            current = max(current, busy_end)

        if current < end:
            free_slots.append((current.strftime('%H:%M'), end.strftime('%H:%M')))

        return free_slots
        

    def is_available(self, date: str, start: str, end: str) -> bool:
        '''
        Check if the specified time interval is available.

        Args:
            date (str): Date in "YYYY-MM-DD" format.
            start (str): Start time in "HH:MM" format.
            end (str): End time in "HH:MM" format.

        Returns:
            True if the interval is available, otherwise False.
        '''
        self._validate_date(date)

        interval_start = self._parse_datetime(date, start)
        interval_end = self._parse_datetime(date, end)
        busy_slots = [
            (
                self._parse_datetime(date, slot['start']),
                self._parse_datetime(date, slot['end'])
            )
            for slot in self.timeslots
            if (day := next((d for d in self.days if d['id'] == slot['day_id']), None)) is not None and day['date'] == date
        ]

        for busy_start, busy_end in busy_slots:
            if not (interval_end <= busy_start or interval_start >= busy_end):
                return False
                
        return True
        

    def find_slot_for_duration(self, duration_minutes: int) -> tuple[str, str, str]:
        '''
        Find the first available slot for the specified duration.

        Args:
            duration_minutes (int): Duration of the slot in minutes.

        Returns:
            Tuple of (date, start time, end time) for the first available slot.

        Raises:
            ValueError: If no slot is found.
        '''
        if not self.days:
            raise ValueError('No dates in the schedule')

        duration = timedelta(minutes=duration_minutes)
        for day in sorted(self.days, key=lambda x: x['date']):
            date = day['date']
            free_slots = self.get_free_slots(date)
            for start, end in free_slots:
                slot_start = self._parse_datetime(date, start)
                slot_end = self._parse_datetime(date, end)
                if slot_end - slot_start >= duration:
                    return (date, start, (slot_start + duration).strftime('%H:%M'))
            
        raise ValueError('No available slot found for the specified duration')



