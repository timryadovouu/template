from fastapi import APIRouter, Depends, HTTPException, status, Query  # type: ignore
from sqlalchemy.orm import Session  # type: ignore
from typing import Optional, Literal, Annotated
from datetime import datetime
from sqlalchemy import or_, and_  # type: ignore

from auth.auth import get_current_user
from db.database import get_db
from db.models import User, Post
from db.schemas import PostsResponse, PostResponse, PostCreate, PostUpdate


router = APIRouter(tags=["Posts"])


@router.get("/api/posts", response_model=PostsResponse)
def get_all_posts(
    page: int = Query(1, ge=1),
    pageSize: int = Query(10, ge=1, le=100),
    # filters
    user_id: Optional[int] = Query(None),
    title: Optional[str] = Query(None),
    content: Optional[str] = Query(None),
    likes_min: Optional[int] = Query(None, ge=0),
    likes_max: Optional[int] = Query(None, ge=0),
    created_before: Optional[datetime] = Query(None, description="format  (YYYY-MM-DD)"),
    created_after: Optional[datetime] = Query(None, description="format (YYYY-MM-DD)"),
    # search 
    search: Optional[str] = Query(None),
    search_field: Literal["all", "title", "content"] = Query("all"),
    # sorting
    sort_by: str = Query("created_at", regex="^(created_at|updated_at|title|likes_count)$"),
    sort_order: str = Query("asc", regex="^(asc|desc)$"),
    db: Session = Depends(get_db)
):
    query = db.query(Post)
    
    # ======== filters ========
    filters = []
    if user_id:
        filters.append(Post.user_id == user_id)
    
    if title:
        filters.append(Post.title.ilike(f"%{title}%"))
    
    if content:
        filters.append(Post.content.ilike(f"%{content}%"))
    
    if likes_min is not None:
        filters.append(Post.likes_count >= likes_min)
    
    if likes_max is not None:
        filters.append(Post.likes_count <= likes_max)

    if created_after:
        filters.append(Post.created_at >= created_after)

    if created_before:
        filters.append(Post.created_at <= created_before)
        
    if search:
        search_term = f"%{search}%"
        
        if search_field == "all":
            search_filter = or_(
                Post.title.ilike(search_term),
                Post.content.ilike(search_term)
            )
            filters.append(search_filter)
            
        elif search_field == "title":
            filters.append(Post.title.ilike(search_term))
            
        elif search_field == "content":
            filters.append(Post.content.ilike(search_term))
    
    if filters:
        query = query.filter(and_(*filters))
    
    # ======== sort  ========
    sort_column = getattr(Post, sort_by, Post.created_at)
    if sort_order == "desc":
        query = query.order_by(sort_column.desc())
    else:
        query = query.order_by(sort_column.asc())
    
    # ====== pagination ======
    total_count = query.count()
    offset = (page - 1) * pageSize
    posts = query.offset(offset).limit(pageSize).all()
    total_pages = (total_count + pageSize - 1) // pageSize

    return PostsResponse(
        totalCount=total_count,
        page=page,
        pageSize=pageSize,
        totalPages=total_pages,
        posts=posts
    )


@router.post("/api/posts", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
def create_post(
    post_data: PostCreate, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    new_post = Post(
        user_id=current_user.user_id,
        title=post_data.title,
        content=post_data.content,
        likes_count=0
    )

    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post


@router.get("/api/posts/{post_id}", response_model=PostResponse)
def get_post(
    post_id: int, 
    db: Session = Depends(get_db)
):
    post_obj = db.query(Post).filter(Post.post_id == post_id).first()
    if not post_obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    return post_obj

@router.patch("/api/posts/{post_id}", response_model=PostResponse)
def update_post(
    post_id: int,
    post_data: PostUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    post_obj = db.query(Post).filter(Post.post_id == post_id).first()
    if not post_obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

    if post_obj.user_id != current_user.user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied. Only the author can update the post.")
    
    update_data = post_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(post_obj, field, value)

    db.commit()
    db.refresh(post_obj)
    return post_obj

@router.delete("/api/posts/{post_id}", status_code=status.HTTP_200_OK)
def delete_post(
    post_id: int, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    post_obj = db.query(Post).filter(Post.post_id == post_id).first()
    if not post_obj:
        raise HTTPException(status_code=404, detail="Post not found")

    if post_obj.user_id != current_user.user_id:
        raise HTTPException(status_code=403, detail="Access denied. Only the author can delete the post.")
    
    post_title = post_obj.title

    db.delete(post_obj)
    db.commit()
    return {"message": f"Post '{post_title}' deleted successfully", "id": post_id}

@router.post("/api/posts/{post_id}/like", status_code=status.HTTP_200_OK)
def like_post(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    post_obj = db.query(Post).filter(Post.post_id == post_id).first()
    if not post_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )
    
    post_obj.likes_count += 1
    likes = post_obj.likes_count

    db.commit()
    db.refresh(post_obj)
    
    return {
        "message": "Post liked successfully",
        "post_id": post_id,
        "likes_count": likes
    }

@router.post("/api/posts/{post_id}/unlike", status_code=status.HTTP_200_OK)
def unlike_post(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    post_obj = db.query(Post).filter(Post.post_id == post_id).first()
    if not post_obj:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )
    if post_obj.likes_count <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot unlike: post has no likes"
        )
    
    post_obj.likes_count -= 1
    likes = post_obj.likes_count

    db.commit()
    db.refresh(post_obj)
    
    return {
        "message": "Post unliked successfully",
        "post_id": post_id,
        "likes_count": likes
    }