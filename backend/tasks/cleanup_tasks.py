from datetime import datetime, timedelta
from celery_app import celery_app
from db.session import engine
from sqlmodel import Session, select
from models import Assets
import os

from core.config import settings


@celery_app.task(name="tasks.cleanup_tasks.permanent_delete_assets")
def permanent_delete_assets():
    """Xóa hoàn toàn các asset đã bị đánh dấu xóa > 7 ngày"""
    try:
        with Session(engine) as db:
            threshold_date = int((datetime.utcnow() - timedelta(days=settings.PERMANENT_DELETE_AFTER_DAYS)).timestamp())
            assets_to_delete = db.exec(
                select(Assets).where(
                    Assets.is_deleted == True,
                    Assets.updated_at <= threshold_date
                )
            ).all()

            for asset in assets_to_delete:
                # Xóa file vật lý (nếu có)
                if asset.path and os.path.exists(asset.path):
                    os.remove(asset.path)

                # Xóa bản ghi khỏi DB
                db.delete(asset)

            db.commit()
            print(f"🧹 Đã xóa {len(assets_to_delete)} asset cũ")

    except Exception as e:
        print(f"❌ Lỗi khi xóa asset: {e}")
