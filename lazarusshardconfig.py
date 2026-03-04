"""
Configuration management for Lazarus Shard
Centralizes all environment variables and settings with validation
"""
import os
import sys
from dataclasses import dataclass
from typing import Optional
from pathlib import Path

import firebase_admin
from firebase_admin import credentials, firestore
from dotenv import load_dotenv
from pydantic import BaseSettings, Field

# Load environment variables
load_dotenv()

class Settings(BaseSettings):
    """Validated application settings"""
    
    # Firebase Configuration
    firebase_credentials_path: str = Field(
        default="credentials/firebase-service-account.json",
        description="Path to Firebase service account JSON"
    )
    firestore_collection: str = Field(
        default="lazarus_shard_processing",
        description="Firestore collection for processed results"
    )
    
    # AI Processing Configuration
    max_retry_attempts: int = Field(default=3, ge=1, le=5)
    request_timeout_seconds: int = Field(default=30, ge=10, le=120)
    fallback_model_enabled: bool = Field(default=True)
    
    # Data Processing
    batch_size: int = Field(default=100, ge=1, le=1000)
    enable_validation: bool = Field(default=True)
    
    class Config:
        env_file = ".env"
        env_prefix = "LAZARUS_"

@dataclass
class FirebaseClient:
    """Firebase client wrapper with error handling"""
    db: firestore.Client
    collection_name: str
    
    @classmethod
    def initialize(cls, settings: Settings) -> "FirebaseClient":
        """Initialize Firebase with proper error handling"""
        try:
            cred_path = Path(settings.firebase_credentials_path)
            if not cred_path.exists():
                raise FileNotFoundError(
                    f"Firebase credentials not found at {cred_path}. "
                    "Please ensure the service account JSON file exists."
                )
            
            cred = credentials.Certificate(str(cred_path))
            firebase_admin.initialize_app(cred)
            db = firestore.client()
            
            print(f"✅ Firebase initialized successfully")
            print(f"📁 Collection: {settings.firestore_collection}")
            
            return cls(db=db, collection_name=settings.firestore_collection)
            
        except Exception as e:
            print(f"❌ Firebase initialization failed: {e}")
            print("Attempting to continue without Firebase (results will be logged only)")
            # Return a mock client that logs instead of writing to Firebase
            return cls(db=None, collection_name=settings.firestore_collection)