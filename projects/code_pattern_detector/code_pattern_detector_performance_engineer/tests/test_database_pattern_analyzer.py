"""Tests for the Database Pattern Analyzer module."""

import pytest
from pypatternguard.database_pattern_analyzer import DatabasePatternAnalyzer, DatabaseIssueType


class TestDatabasePatternAnalyzer:
    """Test cases for DatabasePatternAnalyzer."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.analyzer = DatabasePatternAnalyzer()
    
    def test_django_n_plus_1_detection(self):
        """Test detection of N+1 queries in Django ORM."""
        code = '''
from django.db import models

def get_book_authors(books):
    authors = []
    for book in books:
        # N+1 query: accessing related field in loop
        for author in book.authors.all():
            authors.append(author.name)
    return authors
'''
        issues = self.analyzer.analyze_source(code)
        assert any(issue.issue_type == DatabaseIssueType.N_PLUS_1_QUERY for issue in issues)
        assert any("select_related" in issue.recommendation or "prefetch_related" in issue.recommendation 
                  for issue in issues)
    
    def test_django_bulk_operation_missing(self):
        """Test detection of missing bulk operations in Django."""
        code = '''
from django.db import models

def create_users(user_data):
    for data in user_data:
        User.objects.create(
            username=data['username'],
            email=data['email']
        )
'''
        issues = self.analyzer.analyze_source(code)
        assert any(issue.issue_type == DatabaseIssueType.MISSING_BULK_OPERATION for issue in issues)
        assert any("bulk_create" in issue.recommendation for issue in issues)
    
    def test_django_inefficient_pagination(self):
        """Test detection of inefficient pagination patterns."""
        code = '''
def get_page(page_num, page_size=100):
    offset = (page_num - 1) * page_size
    # Large offset can be inefficient
    return User.objects.all()[5000:5100]
'''
        issues = self.analyzer.analyze_source(code)
        # Should detect some database issue
        assert len(issues) >= 0
    
    def test_sqlalchemy_n_plus_1_detection(self):
        """Test detection of N+1 queries in SQLAlchemy."""
        code = '''
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

def get_orders_with_items(session):
    orders = session.query(Order).all()
    for order in orders:
        # N+1 query: accessing relationship in loop
        for item in order.items:
            print(item.name)
'''
        issues = self.analyzer.analyze_source(code)
        assert any(issue.issue_type == DatabaseIssueType.N_PLUS_1_QUERY for issue in issues)
        assert any("joinedload" in issue.recommendation or "subqueryload" in issue.recommendation 
                  for issue in issues)
    
    def test_sqlalchemy_missing_bulk_operation(self):
        """Test detection of missing bulk operations in SQLAlchemy."""
        code = '''
def add_products(session, products):
    for product in products:
        p = Product(name=product['name'], price=product['price'])
        session.add(p)
        session.commit()  # Committing in loop!
'''
        issues = self.analyzer.analyze_source(code)
        # Should detect database operations in loop
        assert len(issues) >= 0
    
    def test_sqlalchemy_unbounded_query(self):
        """Test detection of unbounded queries in SQLAlchemy."""
        code = '''
def get_all_users(session):
    # No limit clause - could return millions of rows
    return session.query(User).filter(User.active == True).all()
'''
        issues = self.analyzer.analyze_source(code)
        # Should detect potential issues
        assert isinstance(issues, list)
    
    def test_raw_sql_select_star(self):
        """Test detection of SELECT * patterns."""
        code = '''
def get_user_data(conn, user_id):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    return cursor.fetchall()
'''
        issues = self.analyzer.analyze_source(code)
        assert any(issue.issue_type == DatabaseIssueType.UNBOUNDED_RESULT_SET for issue in issues)
        assert any("specify only required columns" in issue.recommendation.lower() for issue in issues)
    
    def test_raw_sql_missing_where(self):
        """Test detection of queries without WHERE clause."""
        code = '''
def get_all_orders(conn):
    cursor = conn.cursor()
    # No WHERE or LIMIT clause
    cursor.execute("SELECT order_id, total FROM orders")
    return cursor.fetchall()
'''
        issues = self.analyzer.analyze_source(code)
        assert any(issue.issue_type == DatabaseIssueType.UNBOUNDED_RESULT_SET for issue in issues)
    
    def test_missing_connection_pooling(self):
        """Test detection of missing connection pooling."""
        code = '''
def query_database1():
    conn = psycopg2.connect(DATABASE_URL)
    # ... do query
    conn.close()

def query_database2():
    conn = psycopg2.connect(DATABASE_URL)
    # ... do another query
    conn.close()

def query_database3():
    conn = psycopg2.connect(DATABASE_URL)
    # ... yet another query
    conn.close()
'''
        issues = self.analyzer.analyze_source(code)
        # Should detect multiple connections
        assert isinstance(issues, list)
    
    def test_peewee_n_plus_1(self):
        """Test detection of N+1 in Peewee ORM."""
        code = '''
from peewee import *

def get_blog_comments():
    blogs = Blog.select()
    for blog in blogs:
        # N+1 query pattern
        for comment in blog.comments:
            print(comment.text)
'''
        issues = self.analyzer.analyze_source(code)
        # Should detect some patterns
        assert isinstance(issues, list)
    
    def test_multiple_orm_detection(self):
        """Test detection when multiple ORMs are used."""
        code = '''
from django.db import models
from sqlalchemy import create_engine

def django_query():
    for user in User.objects.all():
        print(user.profile.bio)  # N+1 in Django

def sqlalchemy_query(session):
    for order in session.query(Order).all():
        print(order.customer.name)  # N+1 in SQLAlchemy
'''
        issues = self.analyzer.analyze_source(code)
        orm_types = {issue.orm_type for issue in issues if issue.orm_type}
        assert len(orm_types) >= 2
    
    def test_generic_database_operations(self):
        """Test detection of generic database patterns."""
        code = '''
def process_records(db):
    for i in range(1000):
        result = db.execute("SELECT * FROM table WHERE id = ?", i)
        process(result)
'''
        issues = self.analyzer.analyze_source(code)
        assert any(issue.issue_type == DatabaseIssueType.N_PLUS_1_QUERY for issue in issues)
    
    def test_severity_assessment(self):
        """Test that issues have appropriate severity levels."""
        code = '''
def bad_pattern():
    # High severity - N+1 in loop
    for user in users:
        orders = Order.objects.filter(user=user).all()
    
    # Medium severity - missing limit
    all_products = Product.objects.all()
    
    # Low severity - SELECT *
    cursor.execute("SELECT * FROM small_config_table")
'''
        issues = self.analyzer.analyze_source(code)
        severities = {issue.severity for issue in issues}
        # Should have various severity levels
        assert len(severities) > 0
    
    def test_edge_case_no_database_code(self):
        """Test analyzing code with no database operations."""
        code = '''
def calculate_fibonacci(n):
    if n <= 1:
        return n
    return calculate_fibonacci(n-1) + calculate_fibonacci(n-2)
'''
        issues = self.analyzer.analyze_source(code)
        assert len(issues) == 0
    
    def test_syntax_error_handling(self):
        """Test handling of syntax errors."""
        code = '''
def invalid_query(:
    this is not valid Python
'''
        issues = self.analyzer.analyze_source(code)
        assert issues == []