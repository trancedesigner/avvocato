import os
import psycopg2
import psycopg2.extras
from datetime import datetime

# Database connection
def get_connection():
    """Create a connection to the PostgreSQL database"""
    conn = psycopg2.connect(
        os.environ["DATABASE_URL"],
        sslmode='require'
    )
    return conn

def initialize_database():
    """Create tables if they don't exist"""
    conn = get_connection()
    cur = conn.cursor()
    
    # Create services table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS services (
        id SERIAL PRIMARY KEY,
        name VARCHAR(255) NOT NULL,
        description TEXT NOT NULL,
        file_content TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)
    
    # Create clients table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS clients (
        id SERIAL PRIMARY KEY,
        nome VARCHAR(255) NOT NULL,
        cognome VARCHAR(255) NOT NULL,
        email VARCHAR(255) NOT NULL,
        telefono VARCHAR(100),
        codice_fiscale VARCHAR(16) NOT NULL,
        indirizzo TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)
    
    # Create quotes table
    cur.execute("""
    CREATE TABLE IF NOT EXISTS quotes (
        id SERIAL PRIMARY KEY,
        client_id INTEGER REFERENCES clients(id),
        valore_bene NUMERIC(15, 2) NOT NULL,
        total_fee NUMERIC(15, 2) NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)
    
    # Create quote_services (junction table)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS quote_services (
        quote_id INTEGER REFERENCES quotes(id),
        service_id INTEGER REFERENCES services(id),
        PRIMARY KEY (quote_id, service_id)
    );
    """)
    
    conn.commit()
    cur.close()
    conn.close()

def load_services_from_db():
    """Load services from the database"""
    conn = get_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    
    cur.execute("SELECT * FROM services ORDER BY name")
    services = [dict(service) for service in cur.fetchall()]
    
    cur.close()
    conn.close()
    
    return services

def save_service_to_db(name, description, file_content=None):
    """Save a service to the database"""
    conn = get_connection()
    cur = conn.cursor()
    
    cur.execute("""
    INSERT INTO services (name, description, file_content) 
    VALUES (%s, %s, %s) RETURNING id
    """, (name, description, file_content))
    
    service_id = cur.fetchone()[0]
    
    conn.commit()
    cur.close()
    conn.close()
    
    return service_id

def delete_service_from_db(service_id):
    """Delete a service from the database"""
    conn = get_connection()
    cur = conn.cursor()
    
    # First delete from junction table if there are any references
    cur.execute("DELETE FROM quote_services WHERE service_id = %s", (service_id,))
    
    # Then delete the service
    cur.execute("DELETE FROM services WHERE id = %s", (service_id,))
    
    conn.commit()
    cur.close()
    conn.close()

def save_quote_to_db(client_data, selected_services, fees):
    """Save quote and client data to the database"""
    conn = get_connection()
    cur = conn.cursor()
    
    # Insert client data
    cur.execute("""
    INSERT INTO clients (nome, cognome, email, telefono, codice_fiscale, indirizzo)
    VALUES (%s, %s, %s, %s, %s, %s) RETURNING id
    """, (
        client_data['nome'], 
        client_data['cognome'], 
        client_data['email'], 
        client_data['telefono'], 
        client_data['codice_fiscale'], 
        client_data['indirizzo']
    ))
    
    client_id = cur.fetchone()[0]
    
    # Insert quote
    cur.execute("""
    INSERT INTO quotes (client_id, valore_bene, total_fee)
    VALUES (%s, %s, %s) RETURNING id
    """, (client_id, client_data['valore_bene'], fees['total']))
    
    quote_id = cur.fetchone()[0]
    
    # Insert quote-service relationships
    for service in selected_services:
        cur.execute("""
        INSERT INTO quote_services (quote_id, service_id)
        VALUES (%s, %s)
        """, (quote_id, service['id']))
    
    conn.commit()
    cur.close()
    conn.close()
    
    return quote_id

def get_recent_quotes(limit=10):
    """Get recent quotes with client information"""
    conn = get_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    
    cur.execute("""
    SELECT q.id, q.valore_bene, q.total_fee, q.created_at,
           c.nome, c.cognome, c.email
    FROM quotes q
    JOIN clients c ON q.client_id = c.id
    ORDER BY q.created_at DESC
    LIMIT %s
    """, (limit,))
    
    quotes = [dict(quote) for quote in cur.fetchall()]
    
    # For each quote, get the services
    for quote in quotes:
        cur.execute("""
        SELECT s.name
        FROM services s
        JOIN quote_services qs ON s.id = qs.service_id
        WHERE qs.quote_id = %s
        """, (quote['id'],))
        
        quote['services'] = [row[0] for row in cur.fetchall()]
    
    cur.close()
    conn.close()
    
    return quotes

def import_json_services(services):
    """Import services from JSON to database"""
    conn = get_connection()
    cur = conn.cursor()
    
    for service in services:
        cur.execute("""
        INSERT INTO services (id, name, description, file_content) 
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (id) DO UPDATE 
        SET name = EXCLUDED.name, 
            description = EXCLUDED.description, 
            file_content = EXCLUDED.file_content
        """, (service['id'], service['name'], service['description'], service['file_content']))
    
    # Reset the sequence to max id + 1
    cur.execute("""
    SELECT setval('services_id_seq', (SELECT MAX(id) FROM services))
    """)
    
    conn.commit()
    cur.close()
    conn.close()

def get_service_statistics():
    """Get statistics about most requested services"""
    conn = get_connection()
    if conn:
        try:
            # Create cursor
            cur = conn.cursor()
            
            # Get service request counts
            cur.execute("""
                SELECT s.id, s.name, COUNT(qs.service_id) as count
                FROM services s
                LEFT JOIN quote_services qs ON s.id = qs.service_id
                GROUP BY s.id, s.name
                ORDER BY count DESC
            """)
            
            service_counts = [
                {'id': row[0], 'name': row[1], 'count': row[2]} 
                for row in cur.fetchall()
            ]
            
            # Get average quote value by service
            cur.execute("""
                SELECT s.id, s.name, AVG(q.valore_bene) as avg_value, AVG(q.total_fee) as avg_fee
                FROM services s
                JOIN quote_services qs ON s.id = qs.service_id
                JOIN quotes q ON qs.quote_id = q.id
                GROUP BY s.id, s.name
                ORDER BY s.name
            """)
            
            service_values = [
                {'id': row[0], 'name': row[1], 'avg_value': row[2], 'avg_fee': row[3]} 
                for row in cur.fetchall()
            ]
            
            # Get monthly quote counts
            cur.execute("""
                SELECT 
                    EXTRACT(YEAR FROM created_at) as year,
                    EXTRACT(MONTH FROM created_at) as month,
                    COUNT(*) as count
                FROM quotes
                GROUP BY year, month
                ORDER BY year, month
            """)
            
            monthly_counts = [
                {'year': int(row[0]), 'month': int(row[1]), 'count': row[2]} 
                for row in cur.fetchall()
            ]
            
            # Get total statistics
            cur.execute("""
                SELECT 
                    COUNT(*) as total_quotes, 
                    AVG(valore_bene) as avg_value,
                    AVG(total_fee) as avg_fee
                FROM quotes
            """)
            
            total_stats = cur.fetchone()
            if total_stats:
                total_stats = {
                    'total_quotes': total_stats[0],
                    'avg_value': total_stats[1] or 0,
                    'avg_fee': total_stats[2] or 0
                }
            else:
                total_stats = {
                    'total_quotes': 0,
                    'avg_value': 0,
                    'avg_fee': 0
                }
            
            # Close cursor
            cur.close()
            
            return {
                'service_counts': service_counts,
                'service_values': service_values,
                'monthly_counts': monthly_counts,
                'total_stats': total_stats
            }
            
        except psycopg2.Error as e:
            print(f"Database error: {e}")
            if conn:
                conn.rollback()
        finally:
            if conn:
                conn.close()
    
    return {
        'service_counts': [],
        'service_values': [],
        'monthly_counts': [],
        'total_stats': {'total_quotes': 0, 'avg_value': 0, 'avg_fee': 0}
    }