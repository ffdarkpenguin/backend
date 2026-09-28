from datetime import datetime

from portal.lib import dh


def test_agora_devolve_datetime_com_timezone():
    momento = dh.agora()
    assert isinstance(momento, datetime)
    assert momento.tzinfo
