from fastapi import APIRouter, HTTPException, Query, status

from app.dependencies.types import CurrentUserDep, DbSessionDep, NotificationRepoDep
from app.schemas.notification import (
    NotificationListResponse,
    NotificationResponse,
    UnreadCountResponse,
)

router = APIRouter(prefix="/api/v1/notifications", tags=["Notifications"])


@router.get(
    "",
    summary="Get user notifications",
    description="Retrieve notifications for the current user with pagination support.",
    response_model=NotificationListResponse,
    status_code=status.HTTP_200_OK,
)
async def get_notifications(
    user: CurrentUserDep,
    notification_repo: NotificationRepoDep,
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    unread_only: bool = Query(default=False, alias="unread-only"),
):
    notifications = await notification_repo.get_by_user_id(
        user_id=user.user_id,
        limit=limit,
        offset=offset,
        unread_only=unread_only,
    )
    unread_count = await notification_repo.get_unread_count(user.user_id)

    return NotificationListResponse(
        notifications=[
            NotificationResponse(
                id=n.id,
                notification_type=n.notification_type,
                message=n.message,
                details=n.details,
                is_read=n.is_read,
                created_at=n.created_at,
            )
            for n in notifications
        ],
        unread_count=unread_count,
    )


@router.get(
    "/unread-count",
    summary="Get unread notification count",
    description="Get the count of unread notifications for the current user.",
    response_model=UnreadCountResponse,
    status_code=status.HTTP_200_OK,
)
async def get_unread_count(
    user: CurrentUserDep,
    notification_repo: NotificationRepoDep,
):
    count = await notification_repo.get_unread_count(user.user_id)
    return UnreadCountResponse(unread_count=count)


@router.patch(
    "/{notification_id}/read",
    summary="Mark notification as read",
    description="Mark a specific notification as read.",
    response_model=NotificationResponse,
    status_code=status.HTTP_200_OK,
)
async def mark_as_read(
    notification_id: int,
    user: CurrentUserDep,
    notification_repo: NotificationRepoDep,
    session: DbSessionDep,
):
    notification = await notification_repo.get_by_id(notification_id)

    if notification is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found",
        )

    if notification.user_id != user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot access notification belonging to another user",
        )

    updated = await notification_repo.mark_as_read(notification_id)
    await session.commit()

    return NotificationResponse(
        id=updated.id,
        notification_type=updated.notification_type,
        message=updated.message,
        details=updated.details,
        is_read=updated.is_read,
        created_at=updated.created_at,
    )


@router.post(
    "/read-all",
    summary="Mark all notifications as read",
    description="Mark all notifications as read for the current user.",
    response_model=UnreadCountResponse,
    status_code=status.HTTP_200_OK,
)
async def mark_all_as_read(
    user: CurrentUserDep,
    notification_repo: NotificationRepoDep,
    session: DbSessionDep,
):
    await notification_repo.mark_all_as_read(user.user_id)
    await session.commit()
    return UnreadCountResponse(unread_count=0)
