# math_server.py
from mcp.server.fastmcp import FastMCP
import math

import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

mcp = FastMCP("Math")

@mcp.tool()
def add(a: float, b: float) -> float:
    """Add two numbers"""
    logger.info(f"Called add with args: a={a}, b={b}")
    return a + b

@mcp.tool()
def multiply(a: float, b: float) -> float:
    """Multiply two numbers"""
    logger.info(f"Called multiply with args: a={a}, b={b}")
    return a * b

@mcp.tool()
def subtract(a: float, b: float) -> float:
    """Subtract two numbers"""
    logger.info(f"Called subtract with args: a={a}, b={b}")
    return a - b

@mcp.tool()
def divide(a: float, b: float) -> float:
    """Divide two numbers"""
    logger.info(f"Called divide with args: a={a}, b={b}")
    if b == 0:
        raise ValueError("Division by zero")
    return a / b

@mcp.tool()
def sin(angle: float) -> float:
    """計算角度的正弦值（輸入為弧度）"""
    logger.info(f"Called sin with args: angle={angle}")
    return math.sin(angle)

@mcp.tool()
def cos(angle: float) -> float:
    """計算角度的餘弦值（輸入為弧度）"""
    logger.info(f"Called cos with args: angle={angle}")
    return math.cos(angle)

@mcp.tool()
def tan(angle: float) -> float:
    """計算角度的正切值（輸入為弧度）"""
    logger.info(f"Called tan with args: angle={angle}")
    return math.tan(angle)

@mcp.tool()
def degrees_to_radians(degrees: float) -> float:
    """將角度從度數轉換為弧度"""
    logger.info(f"Called degrees_to_radians with args: degrees={degrees}")
    return math.radians(degrees)

@mcp.tool()
def radians_to_degrees(radians: float) -> float:
    """將角度從弧度轉換為度數"""
    logger.info(f"Called radians_to_degrees with args: radians={radians}")
    return math.degrees(radians)

@mcp.tool()
def sqrt(x: float) -> float:
    """計算平方根"""
    logger.info(f"Called sqrt with args: x={x}")
    if x < 0:
        raise ValueError("不能對負數取平方根")
    return math.sqrt(x)

@mcp.tool()
def log(x: float, base: float = math.e) -> float:
    """計算對數，預設為自然對數(ln)"""
    logger.info(f"Called log with args: x={x}, base={base}")
    if x <= 0 or base <= 0 or base == 1:
        raise ValueError("對數的參數必須為正數，且base不能為1")
    return math.log(x, base)

@mcp.tool()
def power(x: float, y: float) -> float:
    """計算x的y次方"""
    logger.info(f"Called power with args: x={x}, y={y}")
    return math.pow(x, y)

@mcp.tool()
def factorial(n: int) -> int:
    """計算階乘"""
    logger.info(f"Called factorial with args: n={n}")
    if n < 0:
        raise ValueError("不能計算負數的階乘")
    if n > 100:
        raise ValueError("輸入值過大，可能導致計算過慢")
    return math.factorial(n)

if __name__ == "__main__":
    mcp.run(transport="stdio")