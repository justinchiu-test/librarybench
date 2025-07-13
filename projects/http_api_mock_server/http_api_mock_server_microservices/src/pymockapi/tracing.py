"""Distributed tracing implementation with W3C Trace Context support."""

import asyncio
import secrets
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Set, Tuple

from .models import TraceContext, Span


class TracingSystem:
    """Manages distributed tracing across services."""
    
    def __init__(self):
        self._traces: Dict[str, List[Span]] = {}
        self._active_spans: Dict[str, Span] = {}
        self._lock = asyncio.Lock()
    
    def generate_trace_id(self) -> str:
        """Generate a new 32-character hex trace ID."""
        return secrets.token_hex(16)
    
    def generate_span_id(self) -> str:
        """Generate a new 16-character hex span ID."""
        return secrets.token_hex(8)
    
    async def create_trace_context(
        self,
        trace_id: Optional[str] = None,
        parent_span_id: Optional[str] = None
    ) -> TraceContext:
        """Create a new trace context."""
        if not trace_id:
            trace_id = self.generate_trace_id()
        
        span_id = self.generate_span_id()
        
        return TraceContext(
            trace_id=trace_id,
            parent_id=parent_span_id,
            span_id=span_id
        )
    
    async def start_span(
        self,
        service_name: str,
        operation_name: str,
        trace_context: TraceContext,
        tags: Optional[Dict[str, Any]] = None
    ) -> Span:
        """Start a new span."""
        span = Span(
            trace_id=trace_context.trace_id,
            span_id=trace_context.span_id,
            parent_span_id=trace_context.parent_id,
            service_name=service_name,
            operation_name=operation_name,
            tags=tags or {}
        )
        
        async with self._lock:
            # Store active span
            self._active_spans[span.span_id] = span
            
            # Add to trace
            if span.trace_id not in self._traces:
                self._traces[span.trace_id] = []
            self._traces[span.trace_id].append(span)
        
        return span
    
    async def end_span(
        self,
        span_id: str,
        status_code: int = 200,
        error: Optional[str] = None
    ):
        """End an active span."""
        async with self._lock:
            if span_id in self._active_spans:
                span = self._active_spans[span_id]
                span.end_time = datetime.now(timezone.utc)
                span.status_code = status_code
                span.error = error
                del self._active_spans[span_id]
    
    async def get_trace(self, trace_id: str) -> List[Span]:
        """Get all spans for a trace."""
        async with self._lock:
            return list(self._traces.get(trace_id, []))
    
    async def get_active_spans(self) -> List[Span]:
        """Get all currently active spans."""
        async with self._lock:
            return list(self._active_spans.values())
    
    async def propagate_context(
        self,
        current_context: TraceContext,
        service_name: str
    ) -> TraceContext:
        """Create a new context for propagation to another service."""
        return TraceContext(
            trace_id=current_context.trace_id,
            parent_id=current_context.span_id,
            span_id=self.generate_span_id(),
            trace_flags=current_context.trace_flags,
            trace_state=current_context.trace_state
        )
    
    def parse_traceparent_header(self, header: str) -> Optional[TraceContext]:
        """Parse W3C traceparent header."""
        parts = header.split('-')
        if len(parts) != 4:
            return None
        
        version, trace_id, parent_id, trace_flags = parts
        
        if version != "00":  # Only support version 00
            return None
        
        try:
            return TraceContext(
                trace_id=trace_id,
                parent_id=parent_id,
                span_id=self.generate_span_id(),
                trace_flags=trace_flags
            )
        except ValueError:
            return None
    
    def format_traceparent_header(self, context: TraceContext) -> str:
        """Format trace context as W3C traceparent header."""
        return f"00-{context.trace_id}-{context.span_id}-{context.trace_flags}"
    
    async def get_trace_graph(self, trace_id: str) -> Dict[str, Any]:
        """Get trace as a graph structure."""
        spans = await self.get_trace(trace_id)
        
        nodes = []
        edges = []
        
        for span in spans:
            nodes.append({
                "id": span.span_id,
                "service": span.service_name,
                "operation": span.operation_name,
                "duration": (
                    (span.end_time - span.start_time).total_seconds() * 1000
                    if span.end_time else None
                ),
                "status": span.status_code,
                "error": span.error
            })
            
            if span.parent_span_id:
                edges.append({
                    "from": span.parent_span_id,
                    "to": span.span_id
                })
        
        return {
            "trace_id": trace_id,
            "nodes": nodes,
            "edges": edges
        }
    
    async def get_service_dependencies_from_traces(self) -> Dict[str, Set[str]]:
        """Extract service dependencies from trace data."""
        dependencies: Dict[str, Set[str]] = {}
        
        async with self._lock:
            for trace_spans in self._traces.values():
                span_map = {span.span_id: span for span in trace_spans}
                
                for span in trace_spans:
                    if span.parent_span_id and span.parent_span_id in span_map:
                        parent_span = span_map[span.parent_span_id]
                        if parent_span.service_name != span.service_name:
                            if parent_span.service_name not in dependencies:
                                dependencies[parent_span.service_name] = set()
                            dependencies[parent_span.service_name].add(span.service_name)
        
        return dependencies
    
    async def get_trace_statistics(self) -> Dict[str, Any]:
        """Get statistics about traces."""
        async with self._lock:
            total_traces = len(self._traces)
            total_spans = sum(len(spans) for spans in self._traces.values())
            active_spans = len(self._active_spans)
            
            service_counts: Dict[str, int] = {}
            error_counts: Dict[str, int] = {}
            
            for spans in self._traces.values():
                for span in spans:
                    service_counts[span.service_name] = service_counts.get(span.service_name, 0) + 1
                    if span.error:
                        error_counts[span.service_name] = error_counts.get(span.service_name, 0) + 1
            
            return {
                "total_traces": total_traces,
                "total_spans": total_spans,
                "active_spans": active_spans,
                "service_span_counts": service_counts,
                "service_error_counts": error_counts
            }
    
    async def cleanup_old_traces(self, max_age_seconds: int = 3600):
        """Remove traces older than specified age."""
        cutoff_time = datetime.now(timezone.utc).timestamp() - max_age_seconds
        
        async with self._lock:
            traces_to_remove = []
            
            for trace_id, spans in self._traces.items():
                if spans and spans[0].start_time.timestamp() < cutoff_time:
                    traces_to_remove.append(trace_id)
            
            for trace_id in traces_to_remove:
                del self._traces[trace_id]
            
            return len(traces_to_remove)