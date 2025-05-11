from datetime import datetime
from zoneinfo import ZoneInfo as _ZoneInfo

class timezone(_ZoneInfo):
    """
    A thin subclass of zoneinfo.ZoneInfo that adds a .localize() method
    so that datetime objects can be localized in the pytz style.
    """
    def localize(self, dt):
        # attach this tzinfo to a naive datetime
        return dt.replace(tzinfo=self)

# UTC singleton
utc = timezone("UTC")
