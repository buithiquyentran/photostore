from fastapi import APIRouter, Depends, HTTPException, UploadFile, File,Request
from sqlmodel import Session, select, func
from PIL import Image
import io, os
from uuid import uuid4
from datetime import datetime, timedelta
from fastapi.security import OAuth2PasswordBearer
from fastapi.responses import JSONResponse
from db.supabase_client import supabase
from db.session import get_session
from models import  Projects, Folders, Assets , Users
from core.security import get_current_user
from db.crud_item import save_asset_to_db
router = APIRouter(prefix="/assets",  tags=["Assets"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


# @router.get("/all")
# def get_assets(session: Session = Depends(get_session)):
    
#     try:
#         statement = select(Assets)
#         results = session.exec(statement).all()
#         return {"status": "success", "data": results}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Lỗi khi truy vấn dữ liệu: {e}")
    
# @router.get("/images")
# def get_images(session: Session = Depends(get_session)):
    
#     try:
#         statement = select(Assets).where(Assets.is_image == True)
#         results = session.exec(statement).all()
#         return {"status": "success", "data": results}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Lỗi khi truy vấn dữ liệu: {e}")

# @router.get("/videos")
# def get_videos(session: Session = Depends(get_session)):
   
#     try:
#         statement = select(Assets).where(Assets.is_image == False)
#         results = session.exec(statement).all()
#         return {"status": "success", "data": results}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Lỗi khi truy vấn dữ liệu: {e}")
   
 
@router.get("/count")
def count(session: Session = Depends(get_session)):
    try:
        statement = select(func.count()).select_from(Assets)
        total = session.exec(statement).one()
        return {"status": "success", "data": total}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi khi đếm: {e}")
    
    
# @router.get("/get-image/{file_name}")
# async def get_private_image(file_name: str):
#     try:
#         # Tạo signed URL hết hạn sau 60 giây
#         signed_url = supabase.storage.from_(BUCKET_NAME).create_signed_url(f"sys_folder/{file_name}", 60)
#         return {"signed_url": signed_url}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))


# @router.get("/all")
# def list_assets(id=Depends(get_current_user), session: Session = Depends(get_session)):
#     try:
#         statement = (
#             select(Assets).where(Assets.access_control == True)
#             .join(Folders, Assets.folder_id == Folders.id)
#             .join(Projects, Folders.project_id == Projects.id)
#             .where(Projects.user_id == id)
#         )
#         results = session.exec(statement).all()
#         return {"status": "success", "data": results}

#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Lỗi truy vấn ORM: {str(e)}")
BUCKET_NAME = "photostore"
@router.get("/all")
def list_private_assets(
    id=Depends(get_current_user),
    session: Session = Depends(get_session)
):
    try:
        statement = (
            select(Assets)
            .join(Folders, Assets.folder_id == Folders.id)
            .join(Projects, Folders.project_id == Projects.id)
            .where(Projects.user_id == id)
        )
        results = session.exec(statement).all()
        # return results
        data_with_signed = []
        for asset in results:
            signed = supabase.storage \
                .from_(BUCKET_NAME) \
                .create_signed_url(asset.url, expires_in=60*10)  # 10 phút
                
            data_with_signed.append({
                "id": asset.id,
                "name": asset.name,
                "format": asset.format,
                "width": asset.width,
                "height": asset.height,
                "file_size": asset.file_size,
                "created": asset.created,
                "url": signed.get("signedURL"),
            })

        return {"status": "success", "data": data_with_signed}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi ORM hoặc Supabase: {str(e)}")



@router.get("/public_asssets")
def list_public_assets(session: Session = Depends(get_session)):
    try:
        statement = (
            select(Assets).where(Assets.access_control == True)
            .join(Folders, Assets.folder_id == Folders.id)
            .join(Projects, Folders.project_id == Projects.id)
            .join(Users, Projects.user_id == Users.id)
            .where(Users.is_superuser == True)
        )
        results = session.exec(statement).all()
        return {"status": "success", "data": results}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi truy vấn ORM: {str(e)}")



# @router.post("/upload-image")
# async def upload_image(file: UploadFile = File(...)):
#     try:
#         # Đọc nội dung file
#         file_path = f"sys_folder/{file.filename}"
#         # Xác định content-type từ UploadFile
#         content_type = file.content_type or "application/octet-stream"
#         file_bytes = await file.read()
        
#         # Upload lên bucket 
#         supabase.storage.from_(BUCKET_NAME).upload(file_path,file_bytes,
#         {
#             "content-type": content_type,

#         })

#         # Nếu bucket public → có thể generate URL public
#         public_url = supabase.storage.from_(BUCKET_NAME).get_public_url(file_path)

#         return JSONResponse({
#             "status": "success",
#             "public_url": public_url
#         })

#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))


@router.post("/upload-image")
async def upload_asset(request: Request, file: UploadFile = File(...), id=Depends(get_current_user),session: Session = Depends(get_session)):
    print(request.headers)  # debug
    try:
        # Tìm folder mặc định của user
        folder = session.exec(
            select(Folders).join(Projects, Folders.project_id == Projects.id and Folders.is_default == True)
            .where(Projects.user_id == id, Projects.is_default == True)
        ).first()
        if not folder:
            raise HTTPException(404, "Không tìm thấy folder mặc định cho user")

        folder_id = folder.id

        # validate mime
        if not file.content_type or not file.content_type.startswith(("image/", "video/")):
            raise HTTPException(400, "Only image/video allowed")

        # đọc bytes
        file_bytes = await file.read()
        size = len(file_bytes)

        # lấy dimension nếu là ảnh
        width = height = None
        if file.content_type.startswith("image/"):
            try:
                with Image.open(io.BytesIO(file_bytes)) as im:
                    width, height = im.size
            except Exception:
                raise HTTPException(400, "Invalid image")

        # path trong bucket (mỗi user 1 folder)
        ext = os.path.splitext(file.filename or "")[1].lower() or ".bin"
        object_path = f"{id}/{uuid4().hex}{ext}"

        # upload (bucket đang private)
        supabase.storage.from_(BUCKET_NAME).upload(
            object_path,
            file_bytes,
            {"content-type": file.content_type, "x-upsert": "false"},
        )
        try:
            asset_id = save_asset_to_db(  
            db=session,
            user_id=id,
            folder_id =folder_id,
            url=object_path,
            name=file.filename or object_path,
            format=file.content_type,
            width=width, height=height,
            file_size=size,
        )
        except Exception as e:
            # rollback supabase nếu DB fail
            supabase.storage.from_(BUCKET_NAME).remove([object_path])
            raise HTTPException(status_code=500, detail=f"DB insert failed: {e}")
        # tạo signed url ngắn hạn để preview (tuỳ chọn)
        signed = supabase.storage.from_(BUCKET_NAME).create_signed_url(object_path, 120)  # 60s
        return {
            "status":1,
            "id": asset_id,
            "path": object_path,
            "preview_url": signed.get("signedURL"),
            "width": width, "height": height, "file_size": size,
            "mime_type": file.content_type,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))