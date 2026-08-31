import pytest
from services.code_execution_service import analyze_python_ast_complexity

def test_ast_constant_time_complexity():
    code = """
def get_first_element(arr):
    if not arr:
        return None
    return arr[0]
"""
    result = analyze_python_ast_complexity(code)
    assert result.time_complexity_static == "O(1)"
    assert result.space_complexity_static == "O(1)"
    assert result.analysis_type == "STATIC_AST"

def test_ast_linear_time_complexity():
    code = """
def linear_sum(arr):
    total = 0
    for num in arr:
        total += num
    return total
"""
    result = analyze_python_ast_complexity(code)
    assert result.time_complexity_static == "O(N)"
    assert result.space_complexity_static == "O(1)"

def test_ast_quadratic_time_complexity():
    code = """
def bubble_sort(arr):
    n = len(arr)
    for i in range(n):
        for j in range(0, n - i - 1):
            if arr[j] > arr[j + 1]:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
    return arr
"""
    result = analyze_python_ast_complexity(code)
    assert result.time_complexity_static == "O(N^2)"
    assert "Nested iteration" in result.reasoning

def test_ast_logarithmic_binary_search():
    code = """
def binary_search(arr, target):
    low = 0
    high = len(arr) - 1
    while low <= high:
        mid = (low + high) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            low = mid + 1
        else:
            high = mid - 1
    return -1
"""
    result = analyze_python_ast_complexity(code)
    assert result.time_complexity_static == "O(log N)"
    assert "binary search" in result.reasoning.lower() or "logarithmic" in result.reasoning.lower()
