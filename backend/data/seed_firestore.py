"""
Maahir — Firestore Seeder
Reads mock_providers.json and uploads to Firestore providers collection.
Idempotent: safe to run multiple times (uses provider ID as document ID).
"""

import json
import os
import sys
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")
logger = logging.getLogger("seeder")

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from dotenv import load_dotenv
load_dotenv()

from config import FIRESTORE_PROVIDERS_COLLECTION, GCP_PROJECT_ID

MOCK_DATA_PATH = os.path.join(os.path.dirname(__file__), "mock_providers.json")


def seed_firestore():
    """Upload mock providers to Firestore. Idempotent via document ID."""
    try:
        from google.cloud import firestore
        db = firestore.Client(project=GCP_PROJECT_ID)
    except Exception as e:
        logger.error(f"Could not initialize Firestore client: {e}")
        logger.info("Make sure GOOGLE_APPLICATION_CREDENTIALS is set and the service account has Firestore access.")
        return False

    # Load mock data
    try:
        with open(MOCK_DATA_PATH, "r", encoding="utf-8") as f:
            providers = json.load(f)
        logger.info(f"Loaded {len(providers)} providers from {MOCK_DATA_PATH}")
    except Exception as e:
        logger.error(f"Could not load mock data: {e}")
        return False

    # Upload each provider
    collection_ref = db.collection(FIRESTORE_PROVIDERS_COLLECTION)
    success_count = 0
    
    for provider in providers:
        provider_id = provider.get("id", "")
        if not provider_id:
            logger.warning("Skipping provider with no ID")
            continue

        try:
            doc_ref = collection_ref.document(provider_id)
            doc_ref.set(provider)
            logger.info(f"  ✓ {provider_id}: {provider.get('business_name', 'Unknown')} ({provider.get('service_type', '?')})")
            success_count += 1
        except Exception as e:
            logger.error(f"  ✗ Failed to upload {provider_id}: {e}")

    logger.info(f"\nSeeding complete: {success_count}/{len(providers)} providers uploaded to '{FIRESTORE_PROVIDERS_COLLECTION}' collection")
    return success_count == len(providers)


if __name__ == "__main__":
    logger.info(f"Seeding Firestore for project: {GCP_PROJECT_ID}")
    logger.info(f"Collection: {FIRESTORE_PROVIDERS_COLLECTION}")
    logger.info(f"Data file: {MOCK_DATA_PATH}")
    logger.info("---")
    
    success = seed_firestore()
    if success:
        logger.info("✅ All providers seeded successfully!")
    else:
        logger.warning("⚠️ Some providers may not have been seeded. Check logs above.")
