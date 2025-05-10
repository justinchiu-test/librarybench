# Smart City Infrastructure Microservices Framework

## Overview
A comprehensive event-driven microservices framework designed for smart city initiatives that connects diverse municipal services across transportation, utilities, and public safety domains. This framework enables geospatial event routing, interdepartmental data sharing, emergency prioritization, selective data persistence, and citizen privacy protection while maintaining operational independence for different city departments.

## Persona Description
Raj develops systems connecting various municipal services for a smart city initiative spanning transportation, utilities, and public safety. His primary goal is to implement a microservices architecture that enables different city departments to share critical information while maintaining independent operation and specialized functionality.

## Key Requirements

1. **Geospatial Event Routing Based on City Zones and Jurisdictions**
   - Implement location-aware event distribution with geofencing capabilities
   - Create routing rules based on municipal jurisdictional boundaries
   - This feature is critical for Raj as it ensures events are automatically directed to the appropriate city departments based on geographic relevance, preventing information overload while ensuring all relevant stakeholders receive notifications for their areas of responsibility

2. **Cross-department Event Subscription with Authorization Policies**
   - Develop fine-grained subscription mechanisms with departmental access controls
   - Create policy enforcement for sensitive information sharing between departments
   - This capability allows Raj to facilitate appropriate information sharing between city departments (e.g., police, fire, transportation) while respecting organizational boundaries and legal requirements, enabling coordination without compromising departmental autonomy

3. **Emergency Broadcast Patterns with Priority Message Handling**
   - Implement emergency notification with guaranteed delivery and acknowledgment
   - Create priority-based message processing that elevates critical communications
   - This feature enables Raj's system to deliver high-priority alerts during emergencies with maximum reliability, ensuring critical information reaches all relevant city services promptly during incidents that require coordinated response

4. **Long-term Data Archiving with Selective Event Persistence**
   - Develop tiered data retention policies based on event type and importance
   - Create configurable persistence strategies for different data categories
   - This capability provides Raj with efficient historical data management that balances storage costs with data availability, ensuring critical city data is preserved appropriately while routine operational data is managed according to retention requirements

5. **Public/Private Information Barriers with Citizen Privacy Controls**
   - Implement separation between internal operational data and public-facing information
   - Create privacy-preserving mechanisms for handling citizen-related data
   - This feature ensures Raj's system maintains appropriate separation between internal city operations and public information sharing, protecting citizen privacy while enabling transparent communication of non-sensitive municipal information

## Technical Requirements

### Testability Requirements
- All geospatial routing must be testable with simulated location data
- Cross-department authorization must be verifiable through policy testing
- Emergency broadcasting must be testable under various priority scenarios
- Data archiving strategies must be testable with accelerated time simulation
- Privacy controls must be comprehensively verifiable through data flow testing

### Performance Expectations
- Geospatial event routing must resolve destinations within 100ms
- Cross-department authorization decisions must complete within 50ms
- Emergency broadcasts must be delivered to all recipients within 1 second
- Archiving policies must handle at least 10,000 events per second at peak times
- Privacy filtering must add no more than 20ms overhead to public information flows

### Integration Points
- Integration with city GIS and mapping systems
- Interfaces for department-specific operational systems
- Connections to emergency management platforms
- Integration with data warehouse and analytics systems
- Interfaces for public information portals and apps

### Key Constraints
- Must comply with municipal data privacy regulations
- Should operate across varied department technology environments
- Must function reliably during emergencies and infrastructure disruptions
- Should accommodate both modern and legacy municipal systems
- Must support incremental adoption by different departments

IMPORTANT: The implementation should have NO UI/UX components. All functionality must be implemented as testable Python modules and classes that can be thoroughly tested using pytest. Focus on creating well-defined APIs and interfaces rather than user interfaces.

## Core Functionality

The framework must provide the following core functionality:

1. **Geospatial Event System**
   - Location-aware event publishing and routing
   - Spatial filtering and boundary-based distribution
   - Dynamic jurisdiction mapping and updates

2. **Inter-departmental Data Exchange**
   - Policy-based access control for cross-department sharing
   - Information classification and handling rules
   - Departmental subscription management

3. **Emergency Communication Framework**
   - Priority-based message delivery
   - Acknowledgment tracking and escalation
   - Alert broadcasting with guaranteed delivery

4. **Municipal Data Management**
   - Tiered data persistence with configurable retention
   - Historical data access and archiving
   - Storage optimization for municipal scale

5. **Privacy Protection System**
   - Citizen data anonymization and protection
   - Public/private information segregation
   - Consent-based information sharing

6. **City Service Coordination**
   - Service dependency management
   - Cross-departmental workflow orchestration
   - Resource allocation during coordinated response

## Testing Requirements

### Key Functionalities That Must Be Verified
- Events route correctly based on geographic relevance and jurisdictions
- Interdepartmental data sharing respects authorization policies
- Emergency messages receive priority handling and guaranteed delivery
- Data persistence follows defined retention policies for different information types
- Citizen privacy is maintained throughout all public-facing operations

### Critical User Scenarios
- Traffic incident triggers coordinated response from multiple departments
- Department accesses relevant data from another department with proper authorization
- Emergency alert is propagated to all relevant services with appropriate priority
- Historical data is retrievable according to retention policies
- Public information is shared while protecting citizen privacy

### Performance Benchmarks
- System handles peak event volumes during high-activity periods
- Authorization and routing decisions complete within specified timeframes
- Emergency communications meet strict delivery time requirements
- Archiving system manages data volume without performance degradation
- All operations scale to support city-wide deployment

### Edge Cases and Error Conditions
- Multiple simultaneous emergencies across different city zones
- Communication infrastructure disruption during critical incidents
- Conflicting jurisdictional boundaries requiring special handling
- Extremely long-term data retrieval requirements (e.g., legal proceedings)
- Complex privacy scenarios involving multiple data sources

### Required Test Coverage Metrics
- 100% coverage of geospatial routing logic
- Complete testing of authorization policy enforcement
- Full verification of emergency message priority handling
- Comprehensive testing of data retention implementation
- End-to-end validation of privacy protection mechanisms

IMPORTANT: 
- ALL functionality must be testable via pytest without any manual intervention
- Tests should verify behavior against requirements, not implementation details
- Tests should be designed to validate the WHAT (requirements) not the HOW (implementation)
- Tests should be comprehensive enough to verify all aspects of the requirements
- Tests should not assume or dictate specific implementation approaches

## Success Criteria
- Events reach all relevant departments based on geographical relevance
- Departments can access appropriate shared information while respecting boundaries
- Emergency alerts are delivered to all stakeholders within required timeframes
- Historical data is available according to retention policies while managing storage costs
- Citizen privacy is verifiably protected in all public-facing operations
- System integrates successfully with varied departmental technologies
- Framework can be adopted incrementally by different city departments
- System scales to support entire municipal operations

## Getting Started

To set up the development environment for this project:

1. Initialize the project using `uv`:
   ```
   uv init --lib
   ```

2. Install dependencies using `uv sync`

3. Run tests using `uv run pytest`

4. To execute specific Python scripts:
   ```
   uv run python your_script.py
   ```

5. For running linters and type checking:
   ```
   uv run ruff check .
   uv run pyright
   ```

Remember to design the framework as a library with well-documented APIs, not as an application with user interfaces. All functionality should be exposed through programmatic interfaces that can be easily tested and integrated into larger systems.