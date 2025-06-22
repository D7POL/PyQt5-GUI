from PyQt5.QtCore import QDate

CALENDAR_TODAY_OVERRIDE = QDate(2025, 6, 13)

def get_weekday(date_obj):
    """Get weekday name from a date object"""
    weekdays = ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag", "Sonntag"]
    return weekdays[date_obj.weekday()] 