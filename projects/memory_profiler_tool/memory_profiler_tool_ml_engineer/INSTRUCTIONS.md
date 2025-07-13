# Memory Profiler Tool - Machine Learning Engineer Diego Instructions

You are tasked with implementing a memory profiler tool specifically designed for Diego, an ML engineer deploying models to production who needs to profile memory usage during inference. He wants to optimize model serving for cost efficiency while maintaining performance.

## Core Requirements

### 1. Model memory footprint analysis by layer type
- Profile memory usage per model layer
- Track activation memory requirements
- Identify memory-intensive layer types
- Measure gradient memory overhead
- Compare different model architectures

### 2. Batch size optimization for memory efficiency
- Calculate optimal batch sizes for memory constraints
- Model memory scaling with batch size
- Identify memory vs throughput trade-offs
- Generate batch size recommendation curves
- Support dynamic batching scenarios

### 3. Model quantization memory impact visualization
- Compare memory usage across quantization levels
- Track accuracy vs memory trade-offs
- Visualize layer-wise quantization impact
- Calculate memory savings potential
- Generate quantization strategy reports

### 4. Multi-model memory sharing opportunities
- Identify shareable model components
- Analyze weight sharing potential
- Track model switching overhead
- Optimize model loading strategies
- Calculate memory pooling benefits

### 5. Edge deployment memory requirement prediction
- Estimate memory needs for edge devices
- Model memory constraints by device type
- Predict runtime memory overhead
- Generate deployment feasibility reports
- Optimize for specific hardware targets

## Implementation Guidelines

- Use Python exclusively for all implementations
- No UI components - focus on programmatic APIs and CLI tools
- All output should be text-based (JSON, CSV, or formatted text)
- Support major ML frameworks (PyTorch, TensorFlow, ONNX)
- Design for production inference environments

## Testing Requirements

All tests must be written using pytest and follow these guidelines:
- Generate detailed test reports using pytest-json-report
- Test with various model architectures
- Validate memory measurement accuracy
- Test quantization impact calculations
- Ensure framework compatibility

## Project Structure

```
memory_profiler_tool_ml_engineer/
├── src/
│   ├── __init__.py
│   ├── layer_profiler.py      # Layer-wise memory analysis
│   ├── batch_optimizer.py     # Batch size optimization
│   ├── quantization_analyzer.py # Quantization impact
│   ├── model_sharer.py        # Multi-model optimization
│   └── edge_predictor.py      # Edge deployment analysis
├── tests/
│   ├── __init__.py
│   ├── test_layer_profiler.py
│   ├── test_batch_optimizer.py
│   ├── test_quantization_analyzer.py
│   ├── test_model_sharer.py
│   └── test_edge_predictor.py
├── requirements.txt
└── README.md
```

Remember: This tool must help ML engineers optimize model deployment for production environments, balancing memory efficiency with inference performance across different deployment targets.