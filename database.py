import psycopg2
from psycopg2.extras import RealDictCursor
import streamlit as st
from config import DB_CONFIG

def get_connection():
    return psycopg2.connect(**DB_CONFIG)

def run_query(query, params=None, fetch=True):
    conn = get_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    try:
        cur.execute(query, params)
        if fetch:
            result = cur.fetchall()
            conn.commit()
            return result
        else:
            conn.commit()
            return cur.rowcount
    except Exception as e:
        conn.rollback()
        st.error(f"Database error: {e}")
        return None
    finally:
        cur.close()
        conn.close()