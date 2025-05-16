"""Core interpreter for the legal discovery query language."""

import uuid
import time
import logging
from typing import Dict, List, Optional, Any, Union, Set, Callable
from datetime import datetime

from common.core.interpreter import BaseInterpreter
from common.core.query import BaseQuery, ExecutionContext
from common.core.result import QueryResult as CommonQueryResult

from .query import (
    LegalDiscoveryQuery,
    LegalQueryResult,
    QueryClause,
    FullTextQuery,
    MetadataQuery,
    ProximityQuery,
    CommunicationQuery,
    TemporalQuery,
    PrivilegeQuery,
    CompositeQuery,
)
from .document import DocumentCollection, Document


class QueryExecutionContext(ExecutionContext):
    """Context for legal query execution."""

    def __init__(
        self,
        document_collection: DocumentCollection,
        user_id: str = None,
        expand_terms_func: Optional[Callable] = None,
        calculate_proximity_func: Optional[Callable] = None,
        analyze_communication_func: Optional[Callable] = None,
        resolve_timeframe_func: Optional[Callable] = None,
        detect_privilege_func: Optional[Callable] = None,
    ):
        """Initialize the query execution context.

        Args:
            document_collection: Collection of documents to search
            user_id: ID of the user executing the query
            expand_terms_func: Function for expanding terms using legal ontology
            calculate_proximity_func: Function for calculating proximity between terms
            analyze_communication_func: Function for analyzing communication patterns
            resolve_timeframe_func: Function for resolving legal timeframes
            detect_privilege_func: Function for detecting privileged content
        """
        super().__init__(user_id=user_id)

        self.document_collection = document_collection
        self.expand_terms_func = expand_terms_func
        self.calculate_proximity_func = calculate_proximity_func
        self.analyze_communication_func = analyze_communication_func
        self.resolve_timeframe_func = resolve_timeframe_func
        self.detect_privilege_func = detect_privilege_func

        # Runtime state
        self.matched_documents: Set[str] = set()
        self.relevance_scores: Dict[str, float] = {}
        self.privilege_status: Dict[str, str] = {}
        self.highlighting: Dict[str, List[Dict[str, Any]]] = {}


class LegalQueryInterpreter(BaseInterpreter):
    """Core interpreter for the legal discovery query language."""

    def __init__(
        self,
        document_collection: DocumentCollection,
        ontology_service=None,
        document_analyzer=None,
        communication_analyzer=None,
        temporal_manager=None,
        privilege_detector=None,
        logger=None,
    ):
        """Initialize the query interpreter.

        Args:
            document_collection: Collection of documents to search
            ontology_service: Service for legal term ontology integration
            document_analyzer: Service for document analysis
            communication_analyzer: Service for communication pattern analysis
            temporal_manager: Service for temporal management
            privilege_detector: Service for privilege detection
            logger: Logger instance
        """
        # Initialize the base interpreter
        config = {
            "document_collection": document_collection,
        }
        super().__init__(config=config)

        # Store domain-specific services
        self.document_collection = document_collection
        self.ontology_service = ontology_service
        self.document_analyzer = document_analyzer
        self.communication_analyzer = communication_analyzer
        self.temporal_manager = temporal_manager
        self.privilege_detector = privilege_detector
        self.logger = logger or logging.getLogger(__name__)

        # Register services
        if ontology_service:
            self.register_service("ontology", ontology_service)
        if document_analyzer:
            self.register_service("document_analyzer", document_analyzer)
        if communication_analyzer:
            self.register_service("communication_analyzer", communication_analyzer)
        if temporal_manager:
            self.register_service("temporal_manager", temporal_manager)
        if privilege_detector:
            self.register_service("privilege_detector", privilege_detector)

    def parse(self, query_string: str) -> LegalDiscoveryQuery:
        """Parse a query string into a structured query.

        Args:
            query_string: Query string in the legal discovery query language

        Returns:
            Structured query object

        Raises:
            ValueError: If the query string is invalid
        """
        # This is a placeholder for the actual parsing logic
        # In a real implementation, this would parse the SQL-like query language

        self.logger.info(f"Parsing query: {query_string}")

        # For simplicity, we'll create a basic query
        query_id = str(uuid.uuid4())

        # This is just an example and would be replaced with actual parsing logic
        if "CONTAINS" in query_string.upper():
            # Extract terms from a CONTAINS expression
            start_idx = query_string.upper().find("CONTAINS") + 9
            end_idx = query_string.find(")", start_idx)
            if end_idx == -1:
                end_idx = len(query_string)

            contents = query_string[start_idx:end_idx].strip()
            if contents.startswith("("):
                contents = contents[1:]

            parts = contents.split(",")
            field = parts[0].strip() if len(parts) > 1 else "content"
            terms = [term.strip().strip("'\"") for term in parts[1:]]

            clauses = [FullTextQuery(terms=terms, field=field, expand_terms=True)]
        elif "NEAR" in query_string.upper():
            # Extract terms from a NEAR expression
            start_idx = query_string.upper().find("NEAR") + 5
            end_idx = query_string.find(")", start_idx)
            if end_idx == -1:
                end_idx = len(query_string)

            contents = query_string[start_idx:end_idx].strip()
            if contents.startswith("("):
                contents = contents[1:]

            parts = contents.split(",")
            terms = [term.strip().strip("'\"") for term in parts[0:2]]
            distance = int(parts[2].strip()) if len(parts) > 2 else 10
            unit = parts[3].strip().strip("'\"") if len(parts) > 3 else "WORDS"

            clauses = [
                ProximityQuery(
                    terms=terms, distance=distance, unit=unit, expand_terms=True
                )
            ]
        else:
            # Default to a simple full text query
            clauses = [FullTextQuery(terms=[query_string.strip()], expand_terms=True)]

        return LegalDiscoveryQuery(
            query_id=query_id, clauses=clauses, expand_terms=True
        )

    def execute(self, query: Union[BaseQuery, str]) -> LegalQueryResult:
        """Execute a structured query and return results.

        Args:
            query: The query to execute or a query string

        Returns:
            Query execution result
        """
        # Handle string queries for backward compatibility
        if isinstance(query, str):
            return self.parse_and_execute(query)

        if not isinstance(query, LegalDiscoveryQuery):
            raise ValueError(f"Expected LegalDiscoveryQuery, got {type(query)}")

        start_time = time.time()

        self.logger.info(f"Executing query: {query.query_id}")

        # Create the execution context
        context = QueryExecutionContext(
            document_collection=self.document_collection,
            user_id=query.get_execution_context().user_id
            if query.get_execution_context()
            else None,
            expand_terms_func=self.ontology_service.expand_terms
            if self.ontology_service
            else None,
            calculate_proximity_func=self.document_analyzer.calculate_proximity
            if self.document_analyzer
            else None,
            analyze_communication_func=self.communication_analyzer.analyze_communication
            if self.communication_analyzer
            else None,
            resolve_timeframe_func=self.temporal_manager.resolve_timeframe
            if self.temporal_manager
            else None,
            detect_privilege_func=self.privilege_detector.detect_privilege
            if self.privilege_detector
            else None,
        )

        # Execute each clause
        for clause in query.clauses:
            self._execute_clause(clause, context)

        # Calculate execution time
        execution_time = time.time() - start_time

        # Create data for the result
        matching_docs = []
        for doc_id in context.matched_documents:
            doc = self.document_collection.get_document(doc_id)
            if doc:
                matching_docs.append(
                    {
                        "document_id": doc_id,
                        "title": doc.metadata.title
                        if hasattr(doc.metadata, "title")
                        else "",
                        "relevance_score": context.relevance_scores.get(doc_id, 0),
                        "privilege_status": context.privilege_status.get(
                            doc_id, "UNKNOWN"
                        ),
                    }
                )

        # Set up metadata for backward compatibility
        metadata = {
            "document_ids": list(context.matched_documents),
            "total_hits": len(context.matched_documents),
            "relevance_scores": context.relevance_scores,
            "privilege_status": context.privilege_status,
            "execution_time": execution_time,
            "executed_at": datetime.now(),
        }

        # Create and return the result that fits the common QueryResult format
        result = LegalQueryResult(
            query=query, data=matching_docs, success=True, metadata=metadata
        )

        self.logger.info(
            f"Query {query.query_id} executed in {execution_time:.2f}s with {len(matching_docs)} hits"
        )

        return result

    def parse_and_execute(
        self, query_string: str, user_id: str = None
    ) -> LegalQueryResult:
        """Parse and execute a query string.

        This method overrides the base implementation to use the legal discovery specific types.

        Args:
            query_string: Query string to parse and execute
            user_id: ID of the user executing the query

        Returns:
            QueryResult: Query execution result
        """
        # Parse the query
        query = self.parse(query_string)

        # Create execution context
        context = ExecutionContext(user_id=user_id)
        query.set_execution_context(context)

        # Validate the query
        if not self.validate(query):
            context.fail("Query validation failed")
            return LegalQueryResult(
                query=query,
                success=False,
                error="Query validation failed",
                data=[],
                metadata={
                    "document_ids": [],
                    "total_hits": 0,
                    "execution_time": 0,
                    "executed_at": datetime.now(),
                },
            )

        # Execute the query
        try:
            context.start()
            result = self.execute(query)
            context.complete()
            return result
        except Exception as e:
            context.fail(str(e))
            return LegalQueryResult(
                query=query,
                success=False,
                error=str(e),
                data=[],
                metadata={
                    "document_ids": [],
                    "total_hits": 0,
                    "execution_time": 0,
                    "executed_at": datetime.now(),
                },
            )

    def _execute_clause(
        self, clause: QueryClause, context: QueryExecutionContext
    ) -> None:
        """Execute a single query clause.

        Args:
            clause: Query clause to execute
            context: Query execution context
        """
        if isinstance(clause, FullTextQuery):
            self._execute_full_text_query(clause, context)
        elif isinstance(clause, MetadataQuery):
            self._execute_metadata_query(clause, context)
        elif isinstance(clause, ProximityQuery):
            self._execute_proximity_query(clause, context)
        elif isinstance(clause, CommunicationQuery):
            self._execute_communication_query(clause, context)
        elif isinstance(clause, TemporalQuery):
            self._execute_temporal_query(clause, context)
        elif isinstance(clause, PrivilegeQuery):
            self._execute_privilege_query(clause, context)
        elif isinstance(clause, CompositeQuery):
            self._execute_composite_query(clause, context)
        else:
            self.logger.warning(f"Unknown query clause type: {type(clause)}")

    def _execute_full_text_query(
        self, clause: FullTextQuery, context: QueryExecutionContext
    ) -> None:
        """Execute a full text query clause.

        Args:
            clause: Full text query clause
            context: Query execution context
        """
        self.logger.debug(f"Executing full text query: {clause}")

        # Expand terms if requested and available
        terms = clause.terms
        if clause.expand_terms and context.expand_terms_func:
            expanded_terms = []
            for term in terms:
                expanded = context.expand_terms_func(term)
                expanded_terms.extend(expanded)
            terms = expanded_terms

        # Search for documents containing the terms
        matched_docs = set()
        for doc_id, document in context.document_collection.documents.items():
            # Check if the document contains all/any terms
            content = document.content.lower()

            if clause.operator.value == "AND":
                if all(term.lower() in content for term in terms):
                    matched_docs.add(doc_id)
            elif clause.operator.value == "OR":
                if any(term.lower() in content for term in terms):
                    matched_docs.add(doc_id)
            elif clause.operator.value == "NOT":
                if not any(term.lower() in content for term in terms):
                    matched_docs.add(doc_id)

        # Update the matched documents in the context
        context.matched_documents.update(matched_docs)

        # Calculate relevance scores (simplified)
        for doc_id in matched_docs:
            document = context.document_collection.documents[doc_id]
            content = document.content.lower()

            # Simple TF scoring
            score = sum(content.count(term.lower()) for term in terms)
            # Apply the boost
            score *= clause.boost

            # Update or set the relevance score
            if doc_id in context.relevance_scores:
                context.relevance_scores[doc_id] += score
            else:
                context.relevance_scores[doc_id] = score

    def _execute_metadata_query(
        self, clause: MetadataQuery, context: QueryExecutionContext
    ) -> None:
        """Execute a metadata query clause.

        Args:
            clause: Metadata query clause
            context: Query execution context
        """
        self.logger.debug(f"Executing metadata query: {clause}")

        # Search for documents with matching metadata
        matched_docs = set()
        for doc_id, document in context.document_collection.documents.items():
            # Get the metadata value, defaulting to None if not present
            metadata_value = getattr(document.metadata, clause.field, None)
            if metadata_value is None:
                continue

            # Compare the value based on the operator
            if clause.operator.value == "EQUALS" and metadata_value == clause.value:
                matched_docs.add(doc_id)
            elif (
                clause.operator.value == "CONTAINS"
                and isinstance(metadata_value, str)
                and clause.value in metadata_value
            ):
                matched_docs.add(doc_id)
            elif (
                clause.operator.value == "GREATER_THAN"
                and metadata_value > clause.value
            ):
                matched_docs.add(doc_id)
            elif clause.operator.value == "LESS_THAN" and metadata_value < clause.value:
                matched_docs.add(doc_id)
            elif (
                clause.operator.value == "GREATER_THAN_EQUALS"
                and metadata_value >= clause.value
            ):
                matched_docs.add(doc_id)
            elif (
                clause.operator.value == "LESS_THAN_EQUALS"
                and metadata_value <= clause.value
            ):
                matched_docs.add(doc_id)
            elif clause.operator.value == "IN" and metadata_value in clause.value:
                matched_docs.add(doc_id)

        # Update the matched documents in the context
        context.matched_documents.update(matched_docs)

    def _execute_proximity_query(
        self, clause: ProximityQuery, context: QueryExecutionContext
    ) -> None:
        """Execute a proximity query clause.

        Args:
            clause: Proximity query clause
            context: Query execution context
        """
        self.logger.debug(f"Executing proximity query: {clause}")

        # If a proximity calculation function is available, use it
        if context.calculate_proximity_func:
            matched_docs = set()
            for doc_id, document in context.document_collection.documents.items():
                # Check if terms are within the specified distance
                if context.calculate_proximity_func(
                    document.content,
                    clause.terms,
                    clause.distance,
                    clause.unit.value,
                    clause.ordered,
                ):
                    matched_docs.add(doc_id)

            # Update the matched documents in the context
            context.matched_documents.update(matched_docs)
        else:
            # Fallback to a simplified implementation
            self._execute_full_text_query(
                FullTextQuery(terms=clause.terms, expand_terms=clause.expand_terms),
                context,
            )

    def _execute_communication_query(
        self, clause: CommunicationQuery, context: QueryExecutionContext
    ) -> None:
        """Execute a communication query clause.

        Args:
            clause: Communication query clause
            context: Query execution context
        """
        self.logger.debug(f"Executing communication query: {clause}")

        # If a communication analysis function is available, use it
        if context.analyze_communication_func and hasattr(
            self.communication_analyzer, "find_communications"
        ):
            matched_docs = set(
                self.communication_analyzer.find_communications(
                    clause.participants,
                    direction=clause.direction,
                    date_range=clause.date_range,
                    analyze_threads=clause.thread_analysis,
                    include_cc=clause.include_cc,
                    include_bcc=clause.include_bcc,
                )
            )

            # Update the matched documents in the context
            context.matched_documents.update(matched_docs)
        else:
            # Fallback to a simplified implementation
            matched_docs = set()
            for doc_id, document in context.document_collection.documents.items():
                # Only consider email documents
                if not hasattr(document, "sender") or not hasattr(
                    document, "recipients"
                ):
                    continue

                # Check if any participant is in the sender or recipients
                participants = set(clause.participants)
                doc_participants = {document.sender}
                doc_participants.update(document.recipients)

                if clause.include_cc and hasattr(document, "cc") and document.cc:
                    doc_participants.update(document.cc)

                if clause.include_bcc and hasattr(document, "bcc") and document.bcc:
                    doc_participants.update(document.bcc)

                # Check if there's any overlap between participants
                if participants.intersection(doc_participants):
                    matched_docs.add(doc_id)

            # Update the matched documents in the context
            context.matched_documents.update(matched_docs)

    def _execute_temporal_query(
        self, clause: TemporalQuery, context: QueryExecutionContext
    ) -> None:
        """Execute a temporal query clause.

        Args:
            clause: Temporal query clause
            context: Query execution context
        """
        self.logger.debug(f"Executing temporal query: {clause}")

        # If a timeframe resolution function is available and the value is a timeframe, use it
        if isinstance(clause.value, dict) and context.resolve_timeframe_func:
            timeframe_date = context.resolve_timeframe_func(
                clause.timeframe_type, jurisdiction=clause.jurisdiction
            )
            value = timeframe_date
        else:
            value = clause.value

        # Search for documents with matching date
        matched_docs = set()
        for doc_id, document in context.document_collection.documents.items():
            # Get the date value from the document
            date_value = None
            if clause.date_field == "date_created" and hasattr(
                document.metadata, "date_created"
            ):
                date_value = document.metadata.date_created
            elif clause.date_field == "date_modified" and hasattr(
                document.metadata, "date_modified"
            ):
                date_value = document.metadata.date_modified
            elif hasattr(document.metadata, clause.date_field):
                date_value = getattr(document.metadata, clause.date_field)

            if date_value is None:
                continue

            # Compare the date based on the operator
            if clause.operator.value == "EQUALS" and date_value == value:
                matched_docs.add(doc_id)
            elif clause.operator.value == "GREATER_THAN" and date_value > value:
                matched_docs.add(doc_id)
            elif clause.operator.value == "LESS_THAN" and date_value < value:
                matched_docs.add(doc_id)
            elif clause.operator.value == "GREATER_THAN_EQUALS" and date_value >= value:
                matched_docs.add(doc_id)
            elif clause.operator.value == "LESS_THAN_EQUALS" and date_value <= value:
                matched_docs.add(doc_id)
            elif (
                clause.operator.value == "BETWEEN"
                and isinstance(value, dict)
                and "start" in value
                and "end" in value
            ):
                if value["start"] <= date_value <= value["end"]:
                    matched_docs.add(doc_id)

        # Update the matched documents in the context
        context.matched_documents.update(matched_docs)

    def _execute_privilege_query(
        self, clause: PrivilegeQuery, context: QueryExecutionContext
    ) -> None:
        """Execute a privilege query clause.

        Args:
            clause: Privilege query clause
            context: Query execution context
        """
        self.logger.debug(f"Executing privilege query: {clause}")

        # If a privilege detection function is available, use it
        if context.detect_privilege_func:
            # Get the privilege status for each document
            for doc_id, document in context.document_collection.documents.items():
                privilege_info = context.detect_privilege_func(
                    document,
                    privilege_type=clause.privilege_type,
                    attorneys=clause.attorneys,
                )

                # Update the privilege status in the context
                context.privilege_status[doc_id] = privilege_info["status"]

                # Add to matched documents if the confidence is above the threshold
                if privilege_info["confidence"] >= clause.threshold:
                    if clause.include_potentially_privileged:
                        context.matched_documents.add(doc_id)
                    elif privilege_info["status"] == "PRIVILEGED":
                        context.matched_documents.add(doc_id)
        else:
            # Fallback to a simplified implementation
            matched_docs = set()
            for doc_id, document in context.document_collection.documents.items():
                # Check for privilege indicators in the content
                content = document.content.lower()
                privilege_indicators = [
                    "privileged",
                    "attorney-client",
                    "attorney client",
                    "work product",
                    "legal advice",
                    "confidential",
                ]

                # Check if any indicator is in the content
                if any(indicator in content for indicator in privilege_indicators):
                    matched_docs.add(doc_id)
                    context.privilege_status[doc_id] = "POTENTIALLY_PRIVILEGED"
                else:
                    context.privilege_status[doc_id] = "NOT_PRIVILEGED"

            # Update the matched documents in the context
            if clause.include_potentially_privileged:
                context.matched_documents.update(matched_docs)

    def _execute_composite_query(
        self, clause: CompositeQuery, context: QueryExecutionContext
    ) -> None:
        """Execute a composite query clause.

        Args:
            clause: Composite query clause
            context: Query execution context
        """
        self.logger.debug(f"Executing composite query: {clause}")

        # Create a new context for each subclause
        subcontexts = []
        for subclause in clause.clauses:
            subcontext = QueryExecutionContext(
                document_collection=context.document_collection,
                user_id=context.user_id,
                expand_terms_func=context.expand_terms_func,
                calculate_proximity_func=context.calculate_proximity_func,
                analyze_communication_func=context.analyze_communication_func,
                resolve_timeframe_func=context.resolve_timeframe_func,
                detect_privilege_func=context.detect_privilege_func,
            )

            # Execute the subclause
            self._execute_clause(subclause, subcontext)

            # Add the subcontext to the list
            subcontexts.append(subcontext)

        # Combine the results based on the operator
        if clause.operator.value == "AND":
            # Intersection of all matched documents
            if subcontexts:
                matched_docs = subcontexts[0].matched_documents
                for subcontext in subcontexts[1:]:
                    matched_docs.intersection_update(subcontext.matched_documents)

                # Update the matched documents in the context
                context.matched_documents.update(matched_docs)
        elif clause.operator.value == "OR":
            # Union of all matched documents
            for subcontext in subcontexts:
                context.matched_documents.update(subcontext.matched_documents)
        elif clause.operator.value == "NOT":
            # Documents in the first subcontext but not in any other subcontext
            if subcontexts:
                matched_docs = subcontexts[0].matched_documents
                for subcontext in subcontexts[1:]:
                    matched_docs.difference_update(subcontext.matched_documents)

                # Update the matched documents in the context
                context.matched_documents.update(matched_docs)

        # Combine relevance scores and privilege status
        for subcontext in subcontexts:
            # Merge relevance scores (summing them)
            for doc_id, score in subcontext.relevance_scores.items():
                if doc_id in context.relevance_scores:
                    context.relevance_scores[doc_id] += score
                else:
                    context.relevance_scores[doc_id] = score

            # Merge privilege status (prioritizing privileged status)
            for doc_id, status in subcontext.privilege_status.items():
                if doc_id not in context.privilege_status or status == "PRIVILEGED":
                    context.privilege_status[doc_id] = status


# Add aliases for backward compatibility with tests
QueryInterpreter = LegalQueryInterpreter

# Add method aliases for backward compatibility with tests
LegalQueryInterpreter.parse_query = LegalQueryInterpreter.parse
LegalQueryInterpreter.execute_query = LegalQueryInterpreter.execute
