

from datetime import datetime, tzinfo, timedelta
import time
import pytz

def convertScrapySettingToDict(settings):
    """
    internal datastructure conversion
    :param settings:
    :return:
    """
    dict_settting = {}
    for key in settings.attributes:
        dict_settting[key] = settings.attributes[key].value
    return dict_settting

class TimeService(object):
    """
    Etc/GMT-8 is GMT+8
    can't use Asia/ShangHai since minutes offset in pytz
    """
    tz = pytz.timezone('Etc/GMT-8')
    utc = pytz.timezone('UTC')

    def __init__(self, epochTime):
        self.now = datetime.fromtimestamp(epochTime, self.utc)

    def get_local_time(self):
        return self.now.astimezone(self.tz)

    def get_utc_time(self):
        return self.now.astimezone(self.utc)

    def get_epoch_time(self):
        return time.mktime(self.now.astimezone(self.utc).timetuple())


class TimeHelper(object):

    tz = pytz.timezone('Etc/GMT-8')
    utc = pytz.timezone('UTC')

    @classmethod
    def get_today_epoch_time(cls):
        dt = datetime.now(tz=cls.tz)
        md_today = datetime(dt.year, dt.month, dt.day, hour=0, minute=0, second=0, microsecond=0, tzinfo=cls.tz)
        return time.mktime(md_today.astimezone(cls.utc).timetuple())


class TickerConversion(object):

    @classmethod
    def get_symbol(cls, ticker, source='xueqiu'):
        """
        convert ticker to internal symbol
        :param ticker:
        :param source:
        :return:
        """
        if ticker.startwith('SH'):
            return ticker[2:]
        return ticker

    @classmethod
    def get_ticker(cls, sym, source='xueqiu'):
        """
        convert internal symbol to source ticker
        :param sym:
        :param source:
        :return:
        """
        if sym.endswith('.SH'):
            return 'SH' + sym[:sym.find('.SH')]
        else:
            return None

if __name__ == '__main__':
    sym = TickerConversion.get_ticker('600000.SH')
    if sym != 'SH600000':
        raise AssertionError()