def test_hello():
    print("Hello from Python!")
    print("If you see this message, Python is working correctly!")
    
    # Test some basic Python operations
    numbers = [1, 2, 3, 4, 5]
    sum_result = sum(numbers)
    print(f"Sum of numbers 1-5: {sum_result}")
    
    # Test string operations
    message = "Python Extension Test"
    print(f"Uppercase: {message.upper()}")
    print(f"Lowercase: {message.lower()}")
    
    return "Test completed successfully!"

if __name__ == "__main__":
    result = test_hello()
    print(f"\nFinal result: {result}") 
