import pytest
import responses
from src.scheduler import Scheduler

URL = "https://ofc-test-01.tspb.su/test-task/"


@pytest.fixture
def mock_api():
    """
    Mock API response with sample schedule data.
    """
    with responses.RequestsMock() as rsps:
        rsps.add(
            responses.GET,
            URL,
            json={
                "days": [
                    {"id": 1, "date": "2024-10-10", "start": "09:00", "end": "18:00"},
                    {"id": 2, "date": "2024-10-11", "start": "08:00", "end": "17:00"},
                ],
                "timeslots": [
                    {"id": 1, "day_id": 1, "start": "11:00", "end": "12:00"},
                    {"id": 2, "day_id": 2, "start": "09:30", "end": "16:00"},
                ],
            },
            status=200,
        )
        yield rsps


def test_get_busy_slots(mock_api):
    """
    Test retrieving busy slots for a given date.
    """
    scheduler = Scheduler(url=URL)
    assert scheduler.get_busy_slots("2024-10-10") == [("11:00", "12:00")]
    assert scheduler.get_busy_slots("2024-10-11") == [("09:30", "16:00")]
    assert scheduler.get_busy_slots("2024-10-12") == []


def test_get_free_slots(mock_api):
    '''
    Test retrieving free slots for a given date.
    '''
    scheduler = Scheduler(url=URL)
    assert scheduler.get_free_slots('2024-10-10') == [('09:00', '11:00'), ('12:00', '18:00')]
    assert scheduler.get_free_slots('2024-10-11') == [('08:00', '09:30'), ('16:00', '17:00')]
    assert scheduler.get_free_slots('2024-10-12') == []


def test_is_available(mock_api):
    '''
    Test checking availability if a time interval.
    '''
    scheduler = Scheduler(url=URL)
    assert scheduler.is_available('2024-10-10', '10:00', '10:30') is True
    assert scheduler.is_available('2024-10-10', '11:30', '12:30') is False
    assert scheduler.is_available('2024-10-11', '10:00', '10:30') is False


def test_find_slot_for_duration(mock_api):
    '''
    Test finding the first available slot for a given duration.
    '''
    scheduler = Scheduler(url=URL)
    assert scheduler.find_slot_for_duration(60) == ('2024-10-10', '09:00', '10:00')
    assert scheduler.find_slot_for_duration(150) == ('2024-10-10', '12:00', '14:30')
    with pytest.raises(ValueError):
        scheduler.find_slot_for_duration(600)