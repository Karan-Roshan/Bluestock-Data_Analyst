from src.etl.normaliser import normalize_ticker

def test_normalize_ticker_1():
    assert normalize_ticker('tcs') == 'TCS'

def test_normalize_ticker_2():
    assert normalize_ticker(' TCS ') == 'TCS'

def test_normalize_ticker_3():
    assert normalize_ticker('nse:tcs') == 'TCS'

def test_normalize_ticker_4():
    assert normalize_ticker('NSE:INFY') == 'INFY'

def test_normalize_ticker_5():
    assert normalize_ticker('bse:500325') == '500325'

def test_normalize_ticker_6():
    assert normalize_ticker('BSE:500112') == '500112'

def test_normalize_ticker_7():
    assert normalize_ticker('reliance') == 'RELIANCE'

def test_normalize_ticker_8():
    assert normalize_ticker(' adani-enterprises ') == 'ADANI-ENTERPRISES'

def test_normalize_ticker_9():
    assert normalize_ticker('') == None

def test_normalize_ticker_10():
    assert normalize_ticker(None) == None

def test_normalize_ticker_11():
    assert normalize_ticker('INFY ') == 'INFY'

def test_normalize_ticker_12():
    assert normalize_ticker('  hdfcbank  ') == 'HDFCBANK'

def test_normalize_ticker_13():
    assert normalize_ticker('BSE:500000') == '500000'

def test_normalize_ticker_14():
    assert normalize_ticker('nse:ITC') == 'ITC'

def test_normalize_ticker_15():
    assert normalize_ticker('lt') == 'LT'
