"""
Display Rescuetime productivity summary for today.

Displays the hours and minutes spend in total productive and total distracting
time.

Configuration parameters:
    api_key: Rescutime API key for the desired user (default "")
    request_timeout: time to wait for a response (default 10)
    retry_timeout: time to retry if request failed (default 60)
    refresh_interval: refresh interval for this module (default 600)

Examples:
```
# Basic usage
rescue {
    api_key = my_api_key
}

# Customize refresh interval
rescue {
    api_key = my_api_key
    refresh_interval = 300
}
```

Based on code from the weather_yahoo module.
"""

import datetime

URL = "https://www.rescuetime.com/anapi/data?rk=productivity&rb={date}&format=json&key={api_key}"

def format_seconds(seconds):
    """ Format a time in seconds into a string in hours and minutes """
    mins, _ = divmod(seconds, 60)
    hours, mins = divmod(mins, 60)
    return "{hours}h {mins}m".format(hours=hours, mins=mins)

class Py3status:
    # Configuration Parameters
    api_key = ""
    request_timeout = 10
    retry_timeout = 60
    refresh_interval = 600 

    def _get_rt_data(self):
        """
        Get Rescuetime productivity times for the current date

        Returns:
            Object containing productivity totals or None if the request
            failed.
        """
        try:
            now = datetime.datetime.now()
            cur_date = "%04d-%02d-%02d" % (now.year, now.month, now.day)
            return self.py3.request(URL.format(api_key=self.api_key,
                                               date=cur_date),
                                    timeout=self.request_timeout).json()
        except self.py3.RequestException:
            return None

    def rescue(self):
        """ Create the formatted text string for Py3Status
        """

        # Try to get data from Rescuetime
        cached_until = self.retry_timeout
        out_string = "No data"
        rt_data = self._get_rt_data()

        if rt_data is not None:
            # If valid data is received, cache until the next refresh time
            cached_until = self.py3.time_in(self.refresh_interval)

            # Sum total productive and total distracting time from  table 
            total_productive = 0
            total_distracting = 0

            # Table format: (rank, time spent (seconds), number of people,
            #                productivity)
            for _, seconds, _, productivity in rt_data['rows']:
                if productivity > 0:
                    total_productive += seconds
                elif productivity < 0:
                    total_distracting += seconds

            # Produce formatted productivity totals
            out_string = "P: {productive} D: {distracting}".format(
                          productive=format_seconds(total_productive),
                          distracting=format_seconds(total_distracting))
        return {
                'full_text': out_string,
                'cached_until': cached_until
                }
