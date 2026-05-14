from fastapi import APIRouter

router = APIRouter(
    prefix="/posts"
)

@router.get("/")
async def get_posts():
    pass
