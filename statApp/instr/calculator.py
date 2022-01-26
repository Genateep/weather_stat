from django.db.models import Avg, Count, Max, Min


class Calculator:
    """creates a dictionary with calculated parameters to the context
    """
    def __init__(self, raw_data, city, start_date, end_date):
        self.raw_data = raw_data
        self.city = city
        self.start_date = start_date
        self.end_date = end_date

    def stat(self) -> dict:
        stat = {
            'city': self.city,
            'start_date': self.raw_data.first().date,
            'end_date': self.raw_data.last().date,
            'day_count': self.raw_data.aggregate(Count('date')),
            'abs_min_temp': self.abs_min_temp(self.raw_data),
            'avg_temp': self.avg_temp(self.raw_data),
            'abs_max_temp': self.abs_max_temp(self.raw_data),
            'year_min': self.year_min(self.raw_data),
            'year_max': self.year_max(self.raw_data),
            'precip_days': self.precip_days(self.raw_data),
            'most_frequent_prec': self.most_frequent_prec(self.raw_data),
            'avg_wind_speed': self.avg_wind_speed(self.raw_data),
            'avg_wind_dir': self.avg_wind_dir(self.raw_data)
        }
        return stat

    @staticmethod
    def abs_min_temp(raw_data) -> int:
        """calculates average min temp from query
        """
        return raw_data.aggregate(Min('minTemp'))['minTemp__min']

    @staticmethod
    def avg_temp(raw_data) -> float:
        """calculates average temp from query
        """
        return round(raw_data.aggregate(Avg('avgTemp'))['avgTemp__avg'], 1)

    @staticmethod
    def abs_max_temp(raw_data) -> int:
        """calculates average max temp from query
        """
        return raw_data.aggregate(Max('maxTemp'))['maxTemp__max']

    def year_min(self, raw_data) -> list:
        """calculates min temp averages of full years if period > 2 years
        """
        if int(self.start_date[:4]) < int(self.end_date[:4]) - 2:
            year_min_avg = list(raw_data.values('date__year').annotate(
                Avg('minTemp')
            ).order_by("date__year"))[1:-1]
            for x in year_min_avg:
                x['minTemp__avg'] = round(x['minTemp__avg'], 1)
            return year_min_avg

    def year_max(self, raw_data) -> list:
        """calculates max temp averages of full years if period > 2 years
        """
        if int(self.start_date[:4]) < int(self.end_date[:4]) - 2:
            year_max_avg = list(raw_data.values('date__year').annotate(
                Avg('maxTemp')
            ).order_by("date__year"))[1:-1]
            for x in year_max_avg:
                x['maxTemp__avg'] = round(x['maxTemp__avg'], 1)
            return year_max_avg

    @staticmethod
    def precip_days(raw_data) -> int:
        """calculates percentage of days with precipitation
        """
        days_zero_prec = raw_data.annotate(
            Count('precipitation')
        ).filter(precipitation=0).count()
        return round(
            days_zero_prec / raw_data.annotate(
                Count('precipitation')
            ).count() * 100
        )

    @staticmethod
    def most_frequent_prec(raw_data) -> str:
        """calculates 2 most frequent precipitation descriptions
        """
        pr_count = raw_data.values('desc').annotate(
            count=Count('desc')
        ).filter(
            precipitation__gt=0
        ).order_by(
            '-count'
        )[:2]
        return ', '.join(x['desc'] for x in pr_count)

    @staticmethod
    def avg_wind_speed(raw_data) -> float:
        """calculates average wind speed from query
        """
        return round(
            raw_data.aggregate(Avg('windSpeed'))['windSpeed__avg'], 1
        )

    @staticmethod
    def avg_wind_dir(raw_data) -> str:
        """shows the most frequent wind direction
        """
        return raw_data.values('windDir').annotate(
            count=Count('windDir')
        ).order_by(
            '-count'
        )[0]['windDir']
