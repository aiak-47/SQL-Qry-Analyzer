from cx_Freeze import setup, Executable

setup(
    name="SQAnalyzer",
    version="1.0",
    description="Compare and analyze two SQl query results side by side.",
    executables=[Executable("SQAnalyzer.py")],
)
