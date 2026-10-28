from fastapi import FastAPI, APIRouter

app = FastAPI()

router = APIRouter()

@router.get("/")
def test ():
    return {"Hello from: " : "FASTAPI"}

app.include_router(router)