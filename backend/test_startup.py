import sys
print("Starting main module import...")
try:
    import main
    print("Main module loaded successfully!")
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)
print("Startup test complete.")
