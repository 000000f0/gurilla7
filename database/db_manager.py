import os
import json
import sqlite3
from datetime import datetime
from typing import Dict, Any, Optional, List

class DatabaseManager:
    def __init__(self, client_id: str):
        """Initialize database manager for a specific client."""
        self.client_id = client_id
        self.db_path = self._get_db_path()
        self._init_database()

    def _get_db_path(self) -> str:
        """Get the database path for the client."""
        db_dir = os.path.join(os.path.dirname(__file__), "client_dbs")
        os.makedirs(db_dir, exist_ok=True)
        return os.path.join(db_dir, f"{self.client_id}.db")

    def _json_array_contains(self, json_array: str, value: str) -> bool:
        """SQLite function to check if a JSON array contains a value."""
        if not json_array:
            return False
        try:
            array = json.loads(json_array)
            return value in array if isinstance(array, list) else False
        except json.JSONDecodeError:
            return False

    def _init_database(self):
        """Initialize the database with all required tables."""
        with sqlite3.connect(self.db_path) as conn:
            # Register JSON array contains function
            conn.create_function("json_array_contains", 2, self._json_array_contains)

            # Create clients table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS clients (
                    telegram_handle TEXT PRIMARY KEY,
                    email TEXT,
                    industry TEXT,
                    location TEXT,
                    campaign_parameters TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Create industry_data table with new fields for title, tags, and crawl timestamp
            conn.execute("""
                CREATE TABLE IF NOT EXISTS industry_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    source TEXT,
                    title TEXT,
                    content TEXT,
                    pain_points TEXT,
                    tags TEXT,  -- JSON array of tags
                    crawled_at TEXT,  -- ISO format timestamp
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Create lead_bucket table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS lead_bucket (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    company_name TEXT,
                    website TEXT,
                    contact_info TEXT,
                    details TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Create tailored_solutions table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS tailored_solutions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    lead_id INTEGER,
                    solution_text TEXT,
                    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    status TEXT DEFAULT 'pending',
                    FOREIGN KEY (lead_id) REFERENCES lead_bucket (id)
                )
            """)

            # Create outreach_log table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS outreach_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    lead_id INTEGER,
                    message_sent TEXT,
                    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    response TEXT,
                    updated_at TIMESTAMP,
                    FOREIGN KEY (lead_id) REFERENCES lead_bucket (id)
                )
            """)

    def create_client(self, telegram_handle: str, email: str, industry: str, 
                     location: str, campaign_parameters: Dict[str, Any]) -> bool:
        """Create a new client record."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT INTO clients 
                    (telegram_handle, email, industry, location, campaign_parameters)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    telegram_handle,
                    email,
                    industry,
                    location,
                    json.dumps(campaign_parameters)
                ))
                return True
        except sqlite3.IntegrityError:
            return False

    def get_client(self, telegram_handle: str) -> Optional[Dict[str, Any]]:
        """Retrieve client information."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                "SELECT * FROM clients WHERE telegram_handle = ?", 
                (telegram_handle,)
            )
            row = cursor.fetchone()
            if row:
                client_data = dict(row)
                client_data['campaign_parameters'] = json.loads(
                    client_data['campaign_parameters']
                )
                return client_data
            return None

    def add_industry_data(self, source: str, content: str, pain_points: str,
                         title: Optional[str] = None, tags: Optional[List[str]] = None,
                         crawled_at: Optional[str] = None) -> int:
        """
        Add new industry data entry.
        
        Args:
            source: URL or source of the data
            content: The actual content in markdown format
            pain_points: Extracted pain points
            title: Optional title of the content
            tags: Optional list of tags for categorization
            crawled_at: Optional ISO format timestamp of when the data was crawled
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                INSERT INTO industry_data 
                (source, title, content, pain_points, tags, crawled_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                source,
                title,
                content,
                pain_points,
                json.dumps(tags) if tags else None,
                crawled_at
            ))
            return cursor.lastrowid

    def get_industry_data(self, limit: int = 10, tags: Optional[List[str]] = None) -> list:
        """
        Retrieve recent industry data entries.
        
        Args:
            limit: Maximum number of entries to return
            tags: Optional list of tags to filter by
        """
        with sqlite3.connect(self.db_path) as conn:
            # Register JSON array contains function
            conn.create_function("json_array_contains", 2, self._json_array_contains)
            conn.row_factory = sqlite3.Row
            
            if tags:
                # Build query to match any of the provided tags
                tag_conditions = ' OR '.join(
                    f"json_array_contains(tags, ?)" for _ in tags
                )
                cursor = conn.execute(f"""
                    SELECT * FROM industry_data 
                    WHERE {tag_conditions}
                    ORDER BY created_at DESC LIMIT ?
                """, [*tags, limit])
            else:
                cursor = conn.execute(
                    "SELECT * FROM industry_data ORDER BY created_at DESC LIMIT ?",
                    (limit,)
                )
            
            results = []
            for row in cursor.fetchall():
                data = dict(row)
                if data['tags']:
                    try:
                        data['tags'] = json.loads(data['tags'])
                    except json.JSONDecodeError:
                        data['tags'] = None
                results.append(data)
            return results

    def search_industry_data(self, keyword: str, tags: Optional[List[str]] = None) -> list:
        """
        Search industry data by keyword and optionally filter by tags.
        
        Args:
            keyword: Search term
            tags: Optional list of tags to filter by
        """
        with sqlite3.connect(self.db_path) as conn:
            # Register JSON array contains function
            conn.create_function("json_array_contains", 2, self._json_array_contains)
            conn.row_factory = sqlite3.Row
            
            if tags:
                # Build query to match any of the provided tags
                tag_conditions = ' OR '.join(
                    f"json_array_contains(tags, ?)" for _ in tags
                )
                cursor = conn.execute(f"""
                    SELECT * FROM industry_data 
                    WHERE ({tag_conditions})
                    AND (content LIKE ? OR title LIKE ?)
                    ORDER BY created_at DESC
                """, [*tags, f"%{keyword}%", f"%{keyword}%"])
            else:
                cursor = conn.execute("""
                    SELECT * FROM industry_data 
                    WHERE content LIKE ? OR title LIKE ?
                    ORDER BY created_at DESC
                """, (f"%{keyword}%", f"%{keyword}%"))
            
            results = []
            for row in cursor.fetchall():
                data = dict(row)
                if data['tags']:
                    try:
                        data['tags'] = json.loads(data['tags'])
                    except json.JSONDecodeError:
                        data['tags'] = None
                results.append(data)
            return results

    def add_lead(self, company_name: str, website: str, 
                contact_info: str, details: str) -> int:
        """Add new lead to the bucket."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                INSERT INTO lead_bucket 
                (company_name, website, contact_info, details)
                VALUES (?, ?, ?, ?)
            """, (company_name, website, contact_info, details))
            return cursor.lastrowid

    def add_solution(self, lead_id: int, solution_text: str) -> int:
        """Add new tailored solution."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                INSERT INTO tailored_solutions (lead_id, solution_text)
                VALUES (?, ?)
            """, (lead_id, solution_text))
            return cursor.lastrowid

    def log_outreach(self, lead_id: int, message_sent: str) -> int:
        """Log new outreach attempt."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                INSERT INTO outreach_log (lead_id, message_sent)
                VALUES (?, ?)
            """, (lead_id, message_sent))
            return cursor.lastrowid

    def update_outreach_response(self, outreach_id: int, response: str) -> bool:
        """Update outreach log with response."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    UPDATE outreach_log 
                    SET response = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (response, outreach_id))
                return True
        except sqlite3.Error:
            return False

    # Industry Data Methods
    def get_industry_data(self, limit: int = 10, tags: Optional[List[str]] = None) -> list:
        """
        Retrieve recent industry data entries.
        
        Args:
            limit: Maximum number of entries to return
            tags: Optional list of tags to filter by
        """
        with sqlite3.connect(self.db_path) as conn:
            # Register JSON array contains function
            conn.create_function("json_array_contains", 2, self._json_array_contains)
            conn.row_factory = sqlite3.Row
            
            if tags:
                # Build query to match any of the provided tags
                tag_conditions = ' OR '.join(
                    f"json_array_contains(tags, ?)" for _ in tags
                )
                cursor = conn.execute(f"""
                    SELECT * FROM industry_data 
                    WHERE {tag_conditions}
                    ORDER BY created_at DESC LIMIT ?
                """, [*tags, limit])
            else:
                cursor = conn.execute(
                    "SELECT * FROM industry_data ORDER BY created_at DESC LIMIT ?",
                    (limit,)
                )
            
            results = []
            for row in cursor.fetchall():
                data = dict(row)
                if data['tags']:
                    try:
                        data['tags'] = json.loads(data['tags'])
                    except json.JSONDecodeError:
                        data['tags'] = None
                results.append(data)
            return results

    def search_industry_data(self, keyword: str, tags: Optional[List[str]] = None) -> list:
        """
        Search industry data by keyword and optionally filter by tags.
        
        Args:
            keyword: Search term
            tags: Optional list of tags to filter by
        """
        with sqlite3.connect(self.db_path) as conn:
            # Register JSON array contains function
            conn.create_function("json_array_contains", 2, self._json_array_contains)
            conn.row_factory = sqlite3.Row
            
            if tags:
                # Build query to match any of the provided tags
                tag_conditions = ' OR '.join(
                    f"json_array_contains(tags, ?)" for _ in tags
                )
                cursor = conn.execute(f"""
                    SELECT * FROM industry_data 
                    WHERE ({tag_conditions})
                    AND (content LIKE ? OR title LIKE ?)
                    ORDER BY created_at DESC
                """, [*tags, f"%{keyword}%", f"%{keyword}%"])
            else:
                cursor = conn.execute("""
                    SELECT * FROM industry_data 
                    WHERE content LIKE ? OR title LIKE ?
                    ORDER BY created_at DESC
                """, (f"%{keyword}%", f"%{keyword}%"))
            
            results = []
            for row in cursor.fetchall():
                data = dict(row)
                if data['tags']:
                    try:
                        data['tags'] = json.loads(data['tags'])
                    except json.JSONDecodeError:
                        data['tags'] = None
                results.append(data)
            return results

    # Lead Management Methods
    def get_leads(self, status: Optional[str] = None, limit: int = 50) -> list:
        """Retrieve leads with optional status filter."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            query = """
                SELECT lb.*, ts.status 
                FROM lead_bucket lb
                LEFT JOIN tailored_solutions ts ON lb.id = ts.lead_id
            """
            params = []
            if status:
                query += " WHERE ts.status = ?"
                params.append(status)
            query += " ORDER BY lb.created_at DESC LIMIT ?"
            params.append(limit)
            
            cursor = conn.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]

    def update_lead(self, lead_id: int, updates: Dict[str, Any]) -> bool:
        """Update lead information."""
        valid_fields = {'company_name', 'website', 'contact_info', 'details'}
        update_fields = {k: v for k, v in updates.items() if k in valid_fields}
        
        if not update_fields:
            return False
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                set_clause = ", ".join(f"{k} = ?" for k in update_fields)
                query = f"UPDATE lead_bucket SET {set_clause} WHERE id = ?"
                params = list(update_fields.values()) + [lead_id]
                conn.execute(query, params)
                return True
        except sqlite3.Error:
            return False

    # Solution Management Methods
    def get_solutions(self, lead_id: Optional[int] = None, 
                     status: Optional[str] = None) -> list:
        """Retrieve solutions with optional filters."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            query = "SELECT * FROM tailored_solutions WHERE 1=1"
            params = []
            
            if lead_id is not None:
                query += " AND lead_id = ?"
                params.append(lead_id)
            if status:
                query += " AND status = ?"
                params.append(status)
            
            query += " ORDER BY generated_at DESC"
            cursor = conn.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]

    def update_solution_status(self, solution_id: int, status: str) -> bool:
        """Update solution status."""
        valid_statuses = {'pending', 'sent', 'reviewed', 'approved', 'rejected'}
        if status not in valid_statuses:
            return False
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    UPDATE tailored_solutions 
                    SET status = ? 
                    WHERE id = ?
                """, (status, solution_id))
                return True
        except sqlite3.Error:
            return False

    # Outreach Management Methods
    def get_outreach_history(self, lead_id: Optional[int] = None, 
                           limit: int = 50) -> list:
        """Retrieve outreach history."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            query = """
                SELECT ol.*, lb.company_name 
                FROM outreach_log ol
                JOIN lead_bucket lb ON ol.lead_id = lb.id
            """
            params = []
            
            if lead_id is not None:
                query += " WHERE ol.lead_id = ?"
                params.append(lead_id)
            
            query += " ORDER BY ol.sent_at DESC LIMIT ?"
            params.append(limit)
            
            cursor = conn.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]

    def get_pending_responses(self) -> list:
        """Get outreach entries without responses."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT ol.*, lb.company_name 
                FROM outreach_log ol
                JOIN lead_bucket lb ON ol.lead_id = lb.id
                WHERE ol.response IS NULL
                ORDER BY ol.sent_at DESC
            """)
            return [dict(row) for row in cursor.fetchall()]

    # Analytics Methods
    def get_campaign_stats(self) -> Dict[str, Any]:
        """Get campaign statistics."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            
            # Get lead counts
            cursor = conn.execute("SELECT COUNT(*) as total FROM lead_bucket")
            lead_count = cursor.fetchone()['total']
            
            # Get solution stats
            cursor = conn.execute("""
                SELECT status, COUNT(*) as count 
                FROM tailored_solutions 
                GROUP BY status
            """)
            solution_stats = {row['status']: row['count'] 
                            for row in cursor.fetchall()}
            
            # Get outreach stats
            cursor = conn.execute("""
                SELECT 
                    COUNT(*) as total_outreach,
                    SUM(CASE WHEN response IS NOT NULL THEN 1 ELSE 0 END) as responses
                FROM outreach_log
            """)
            outreach_stats = dict(cursor.fetchone())
            
            return {
                'total_leads': lead_count,
                'solution_stats': solution_stats,
                'outreach_stats': outreach_stats
            }

    def export_campaign_data(self) -> Dict[str, Any]:
        """Export all campaign data for reporting."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            
            # Get client info
            cursor = conn.execute("SELECT * FROM clients LIMIT 1")
            client_info = dict(cursor.fetchone())
            
            # Get all data
            data = {
                'client_info': client_info,
                'industry_data': self.get_industry_data(limit=1000),
                'leads': self.get_leads(limit=1000),
                'solutions': self.get_solutions(),
                'outreach_history': self.get_outreach_history(limit=1000),
                'campaign_stats': self.get_campaign_stats()
            }
            
            return data
