from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

from routes.AdminRoute import adminRouter
from routes.UserRoute import userRouter
from routes.ProductRoute import productRouter
from routes.ShoppingCartRoute import shoppingCartRouter
from routes.OrderRoute import orderRoute

from HTMLContent import html_content

app = FastAPI(
    title="Ecommerce Shopping App - Backend",
    docs_url="/api",
)
@app.get("/", response_class=HTMLResponse)
async def home():
    return HTMLResponse(content=html_content)

app.include_router(adminRouter)
app.include_router(userRouter)
app.include_router(productRouter)
app.include_router(shoppingCartRouter)
app.include_router(orderRoute)

app.add_middleware(CORSMiddleware, allow_origins = ["http://localhost", "http://localhost:3000"], allow_credentials = True, allow_methods = ["*"], allow_headers = ["http://localhost", "http://localhost:3000"])