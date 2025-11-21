import os
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional, Any, Dict

from schemas import Intention, Affirmation, Session
from database import create_document, get_documents, db

app = FastAPI(title="Consciousness Work API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _serialize(doc: Dict[str, Any]) -> Dict[str, Any]:
    """Convert MongoDB document to JSON serializable dict"""
    if not doc:
        return doc
    d = dict(doc)
    if "_id" in d:
        d["id"] = str(d.pop("_id"))
    # Convert datetime to isoformat if present
    for k, v in list(d.items()):
        try:
            from datetime import datetime
            if isinstance(v, datetime):
                d[k] = v.isoformat()
        except Exception:
            pass
    return d


@app.get("/")
def read_root():
    return {"message": "Consciousness Work Backend Running"}


@app.get("/api/hello")
def hello():
    return {"message": "Hello from the backend API!"}


@app.get("/test")
def test_database():
    """Test endpoint to check if database is available and accessible"""
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }

    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Configured"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"

            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"

    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    # Check environment variables
    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"

    return response


# -------- Intentions --------
@app.post("/api/intentions")
def create_intention(payload: Intention):
    try:
        inserted_id = create_document("intention", payload)
        return {"id": inserted_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/intentions")
def list_intentions(active: Optional[bool] = None, limit: int = Query(100, ge=1, le=500)):
    try:
        filter_dict: Dict[str, Any] = {}
        if active is not None:
            filter_dict["is_active"] = active
        docs = get_documents("intention", filter_dict, limit)
        return [_serialize(d) for d in docs]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# -------- Affirmations --------
@app.post("/api/affirmations")
def create_affirmation(payload: Affirmation):
    try:
        inserted_id = create_document("affirmation", payload)
        return {"id": inserted_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/affirmations")
def list_affirmations(tag: Optional[str] = None, limit: int = Query(200, ge=1, le=1000)):
    try:
        filter_dict: Dict[str, Any] = {}
        if tag:
            filter_dict["tags"] = {"$in": [tag]}
        docs = get_documents("affirmation", filter_dict, limit)
        return [_serialize(d) for d in docs]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# -------- Sessions --------
@app.post("/api/sessions")
def create_session(payload: Session):
    try:
        inserted_id = create_document("session", payload)
        return {"id": inserted_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/sessions")
def list_sessions(limit: int = Query(50, ge=1, le=500)):
    try:
        docs = get_documents("session", {}, limit)
        return [_serialize(d) for d in docs]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/summary")
def summary():
    try:
        counts = {
            "intentions": db["intention"].count_documents({}) if db else 0,
            "affirmations": db["affirmation"].count_documents({}) if db else 0,
            "sessions": db["session"].count_documents({}) if db else 0,
        }
        recent_sessions = get_documents("session", {}, 10) if db else []
        return {
            "counts": counts,
            "recent_sessions": [_serialize(d) for d in recent_sessions],
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/schema")
def get_schema():
    """Expose model schemas for tooling/viewers."""
    try:
        return {
            "intention": Intention.model_json_schema(),
            "affirmation": Affirmation.model_json_schema(),
            "session": Session.model_json_schema(),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
