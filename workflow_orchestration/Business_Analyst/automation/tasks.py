"""
Example tasks for data extraction, processing, and report generation.
"""

def data_extraction(context):
    # Simulate data extraction
    return [1, 2, 3, 4, 5]

def data_processing(context):
    # Process the extracted data
    data = context.get('data_extraction', [])
    return [x * 10 for x in data]

def report_generation(context):
    # Generate a simple textual report
    processed = context.get('data_processing', [])
    return f"Report generated with {len(processed)} entries: {processed}"
