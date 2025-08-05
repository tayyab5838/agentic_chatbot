# backend/services/tools.py
from agents import function_tool
import random
import time

@function_tool
def add(a: int, b: int) -> int:
    """Addition function that takes two integers and returns their sum."""
    print("add tool called")
    return a + b

@function_tool
def get_weather(city: str) -> str:
    """Return weather based on city name provided."""
    print("weather tool called")
    return f"The weather in {city} is sunny"

@function_tool
def get_stock_price(stock_name: str)-> str:
    """Take stock name and return the price of the stock
    Args:
    stock_name: The name of the stock to fetch the price
    
    """
    prices = [25, 50, 80, 100]
    stock_price = random.choice(prices)
    time.sleep(3)
    return f"The stock price of {stock_name} is {stock_price}"
