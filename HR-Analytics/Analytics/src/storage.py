"""Database storage for model metrics and training history"""

import sqlite3
import json
from datetime import datetime
from typing import Dict, List
import os
import pandas as pd
import streamlit as st


class ModelMetricsDB:
    """SQLite database for storing model training metrics"""
    
    def __init__(self, db_path: str = "model/metrics.db"):
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.init_db()
    
    def init_db(self):
        """Initialize database schema"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS model_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                run_id TEXT UNIQUE NOT NULL,
                timestamp TEXT NOT NULL,
                accuracy REAL,
                precision REAL,
                recall REAL,
                f1_score REAL,
                roc_auc REAL,
                train_accuracy REAL,
                test_accuracy REAL,
                confusion_matrix TEXT,
                feature_importance TEXT,
                notes TEXT,
                dataset_size INTEGER,
                training_params TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        conn.close()
    
    def save_metrics(self, run_id: str, metrics_dict: Dict) -> bool:
        """Save model metrics to database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO model_metrics (
                    run_id, timestamp, accuracy, precision, recall, 
                    f1_score, roc_auc, train_accuracy, test_accuracy,
                    confusion_matrix, feature_importance, notes, dataset_size
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                run_id,
                datetime.now().isoformat(),
                metrics_dict.get("test_accuracy"),
                metrics_dict.get("precision"),
                metrics_dict.get("recall"),
                metrics_dict.get("f1"),
                metrics_dict.get("roc_auc"),
                metrics_dict.get("train_accuracy"),
                metrics_dict.get("test_accuracy"),
                json.dumps(metrics_dict.get("confusion_matrix", []).tolist() 
                          if hasattr(metrics_dict.get("confusion_matrix"), "tolist") 
                          else metrics_dict.get("confusion_matrix", [])),
                json.dumps(metrics_dict.get("feature_importance", {})),
                metrics_dict.get("notes", ""),
                metrics_dict.get("dataset_size", 0)
            ))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            st.error(f"Error saving metrics: {str(e)}")
            return False
    
    def get_metrics_history(self) -> pd.DataFrame:
        """Retrieve all model training metrics from database"""
        try:
            conn = sqlite3.connect(self.db_path)
            df = pd.read_sql_query(
                "SELECT * FROM model_metrics ORDER BY created_at DESC",
                conn
            )
            conn.close()
            return df
        except Exception as e:
            st.error(f"Error retrieving metrics: {str(e)}")
            return pd.DataFrame()
    
    def get_latest_metrics(self) -> Dict:
        """Get the latest model training metrics"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT * FROM model_metrics 
                ORDER BY created_at DESC 
                LIMIT 1
            """)
            
            result = cursor.fetchone()
            conn.close()
            
            if result:
                columns = [description[0] for description in cursor.description]
                return dict(zip(columns, result))
            return {}
        except Exception as e:
            st.error(f"Error retrieving latest metrics: {str(e)}")
            return {}
    
    def delete_metrics(self, run_id: str) -> bool:
        """Delete specific model metrics"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM model_metrics WHERE run_id = ?", (run_id,))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            st.error(f"Error deleting metrics: {str(e)}")
            return False
    
    def clear_all(self) -> bool:
        """Clear all metrics from database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM model_metrics")
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            st.error(f"Error clearing metrics: {str(e)}")
            return False


@st.cache_resource
def get_db() -> ModelMetricsDB:
    """Get cached database instance"""
    return ModelMetricsDB()
