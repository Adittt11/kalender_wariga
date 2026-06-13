from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile

from app.services.admin_auth_service import require_admin
from app.services.knowledge_service import (
    KNOWLEDGE_CATEGORIES,
    create_knowledge_document,
    list_knowledge_documents,
)


router = APIRouter()


@router.get("/categories")
def knowledge_categories(_admin=Depends(require_admin)):
    return {
        "success": True,
        "data": list(KNOWLEDGE_CATEGORIES),
    }


@router.get("")
def knowledge_list(_admin=Depends(require_admin)):
    try:
        documents = list_knowledge_documents()
    except RuntimeError as error:
        raise HTTPException(status_code=503, detail=str(error)) from error

    return {
        "success": True,
        "data": documents,
    }


@router.post("")
def knowledge_upload(
    _admin=Depends(require_admin),
    category: str = Form(...),
    title: str = Form(""),
    file: UploadFile = File(...),
):
    try:
        file.file.seek(0)
        document = create_knowledge_document(
            category=category,
            title=title,
            filename=file.filename or "knowledge.txt",
            file_bytes=file.file,
        )
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    except RuntimeError as error:
        raise HTTPException(status_code=503, detail=str(error)) from error

    return {
        "success": True,
        "data": document,
    }
