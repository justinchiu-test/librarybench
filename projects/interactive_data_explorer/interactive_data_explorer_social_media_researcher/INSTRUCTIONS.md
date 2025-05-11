# Social Media Data Explorer

## Overview
A specialized terminal-based data exploration framework designed for social media researchers who study interaction patterns across digital platforms. This tool enables analysis of conversation networks, content trends, community structures, and influence patterns in large-scale social data without requiring external visualization libraries or graphical interfaces.

## Persona Description
Dr. Rivera studies social interaction patterns across digital platforms. She needs to explore conversation networks and content trends while identifying community structures and influence patterns in large-scale social data.

## Key Requirements
1. **Network graph visualization** - Generate terminal-friendly visualizations of social connections with community detection algorithms to identify cohesive groups within larger networks. This capability is essential for researchers to understand the structure of social communities and how information flows between different groups.

2. **Sentiment analysis overlays** - Apply and visualize emotional tone measurements across different user groups and conversations, allowing researchers to identify emotional patterns in social interactions. Understanding the emotional content of communications helps researchers interpret interaction dynamics and community formation.

3. **Topic modeling tools** - Implement natural language processing techniques to identify conversation themes and their evolution over time, enabling researchers to track discourse trends and content shifts. This feature helps researchers understand what communities are discussing and how subjects of interest change over time.

4. **Influence flow visualization** - Create representations showing how ideas propagate through social networks to identify key influencers and amplification pathways. This capability is critical for understanding information diffusion and analyzing how specific content spreads in social environments.

5. **Demographic clustering** - Apply advanced clustering techniques to identify distinct user groups based on behavior patterns, content preferences, and interaction styles. This helps researchers segment populations for more nuanced analysis of different social groups' characteristics.

## Technical Requirements
- **Testability Requirements**:
  - Graph algorithms must be verified against established network analysis libraries
  - Sentiment analysis must be validated against human-labeled test datasets
  - Topic models must produce consistent results on benchmark text corpora
  - Influence metrics must correlate with established social influence measures
  - Clustering algorithms must be evaluated using standard cohesion and separation metrics

- **Performance Expectations**:
  - Must handle networks with up to 100,000 nodes and 1 million edges
  - Graph visualization generation within 10 seconds for networks up to 10,000 nodes
  - Sentiment analysis processing 100,000 text items within 2 minutes
  - Topic modeling for 50,000 documents within 5 minutes
  - Memory usage must remain below 4GB even with large datasets

- **Integration Points**:
  - Support for common social media data formats (JSON, CSV, GraphML)
  - Import capability for pre-processed text corpora and embeddings
  - Export functionality for analysis results in standard formats
  - Compatibility with external NLP models and resources
  - Support for incremental data processing and analysis

- **Key Constraints**:
  - All visualizations must be terminal-compatible without external dependencies
  - Privacy protection for sensitive user data in compliance with research ethics
  - Handling of multilingual content and cultural context
  - Must operate without sending data to external services
  - Reproducible analysis with proper random seed management

IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality
The Social Media Data Explorer must provide a comprehensive framework for social media research:

1. **Network Analysis and Community Detection**:
   - Load and process social network data from various sources
   - Calculate network metrics (centrality, density, clustering coefficients)
   - Implement community detection algorithms (Louvain, Label Propagation, etc.)
   - Generate network visualizations optimized for terminal display
   - Identify key nodes and relationships in social graphs

2. **Text Analysis and Sentiment Processing**:
   - Process and normalize social media text content
   - Implement sentiment analysis using lexicon-based and machine learning approaches
   - Calculate sentiment scores and emotional dimensions
   - Detect sarcasm, irony, and other complex emotional expressions
   - Visualize sentiment distribution across different communities

3. **Topic Discovery and Tracking**:
   - Implement topic modeling techniques (LDA, NMF, BERTopic)
   - Track topic evolution and shifts over time
   - Identify emerging and declining conversation themes
   - Link topics to specific communities and user groups
   - Visualize topic distributions and relationships

4. **Influence and Information Diffusion**:
   - Model information propagation through social networks
   - Identify key influencers and opinion leaders
   - Calculate cascade sizes and velocities for content spread
   - Detect amplification patterns and coordinated behavior
   - Visualize information flow and influence pathways

5. **User Behavior and Demographic Analysis**:
   - Extract behavioral features from user activity patterns
   - Implement clustering algorithms for user segmentation
   - Identify distinct user groups based on behavior
   - Characterize user segments by common attributes
   - Generate profiles for different user communities

## Testing Requirements
- **Key Functionalities to Verify**:
  - Network visualization correctly represents community structures
  - Sentiment analysis accurately captures emotional tone in text
  - Topic modeling identifies coherent and meaningful themes
  - Influence flow analysis correctly traces information propagation
  - Demographic clustering produces meaningful user segments

- **Critical User Scenarios**:
  - Analyzing community structure in a political discussion network
  - Mapping sentiment distribution across different social groups
  - Tracking topic evolution in a year-long conversation dataset
  - Tracing the spread of specific information through a network
  - Identifying distinct user types based on behavior patterns

- **Performance Benchmarks**:
  - Process network with 100,000 nodes within 30 seconds
  - Generate community visualization for 10,000 node network within 10 seconds
  - Complete sentiment analysis for 100,000 tweets within 2 minutes
  - Process topic modeling for 50,000 documents within 5 minutes
  - Memory usage below 4GB during all operations

- **Edge Cases and Error Conditions**:
  - Handling disconnected graph components
  - Processing extremely short or non-standard text content
  - Managing multilingual content in topic modeling
  - Dealing with sparse or incomplete network data
  - Handling temporal gaps in longitudinal data

- **Required Test Coverage Metrics**:
  - 90% code coverage for all core functionality
  - 100% coverage for data transformation and processing functions
  - All algorithms validated against benchmark datasets
  - Complete integration tests for all public APIs
  - Performance tests for all computationally intensive operations

IMPORTANT:
- ALL functionality must be testable via pytest without any manual intervention
- Tests should verify behavior against requirements, not implementation details
- Tests should be designed to validate the WHAT (requirements) not the HOW (implementation)
- Tests should be comprehensive enough to verify all aspects of the requirements
- Tests should not assume or dictate specific implementation approaches
- REQUIRED: Tests must be run with pytest-json-report to generate a pytest_results.json file:
  ```
  pip install pytest-json-report
  pytest --json-report --json-report-file=pytest_results.json
  ```
- The pytest_results.json file must be included as proof that all tests pass

## Success Criteria
A successful implementation of the Social Media Data Explorer will demonstrate:

1. Effective visualization of social network structures with accurate community detection
2. Reliable sentiment analysis that captures emotional content in social media text
3. Topic modeling that identifies coherent and meaningful conversation themes
4. Clear visualization of influence flows and information propagation
5. Meaningful clustering of users into distinct behavioral and demographic groups

REQUIRED FOR SUCCESS:
- All tests must pass when run with pytest
- A valid pytest_results.json file must be generated showing all tests passing
- The implementation must satisfy all key requirements specified for this persona

To set up the development environment, use:
```
uv venv
source .venv/bin/activate
uv pip install -e .
```

CRITICAL: Running tests with pytest-json-report and providing the pytest_results.json file is MANDATORY:
```
pip install pytest-json-report
pytest --json-report --json-report-file=pytest_results.json
```