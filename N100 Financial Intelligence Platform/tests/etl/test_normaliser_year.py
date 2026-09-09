from src.etl.normaliser import normalize_year

def test_normalize_year_1():
    assert normalize_year('2024') == 2024

def test_normalize_year_2():
    assert normalize_year('FY24') == 2024

def test_normalize_year_3():
    assert normalize_year('FY-24') == 2024

def test_normalize_year_4():
    assert normalize_year('FY 24') == 2024

def test_normalize_year_5():
    assert normalize_year('2023-24') == 2023

def test_normalize_year_6():
    assert normalize_year('2022') == 2022

def test_normalize_year_7():
    assert normalize_year('2019') == 2019

def test_normalize_year_8():
    assert normalize_year('FY19') == 2019

def test_normalize_year_9():
    assert normalize_year('FY 30') == 2030

def test_normalize_year_10():
    assert normalize_year("'24") == None

def test_normalize_year_11():
    assert normalize_year(None) == None

def test_normalize_year_12():
    assert normalize_year('') == None

def test_normalize_year_13():
    assert normalize_year('abc') == None

def test_normalize_year_14():
    assert normalize_year(2024) == 2024

def test_normalize_year_15():
    assert normalize_year(2020.0) == 2020

def test_normalize_year_16():
    assert normalize_year('FY25') == 2025

def test_normalize_year_17():
    assert normalize_year('2018-19') == 2018

def test_normalize_year_18():
    assert normalize_year('2021/22') == 2021

def test_normalize_year_19():
    assert normalize_year('FY 09') == 2009

def test_normalize_year_20():
    assert normalize_year('FY 49') == 2049
