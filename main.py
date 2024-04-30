from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routes.AdminRoute import adminRouter
from routes.UserRoute import userRouter
from routes.ProductRoute import productRouter
from routes.ShoppingCartRoute import shoppingCartRouter
from routes.OrderRoute import orderRoute

app = FastAPI(
    title="Ecommerce Shopping App - Backend",
    docs_url="/api",
)

app.include_router(adminRouter)
app.include_router(userRouter)
app.include_router(productRouter)
app.include_router(shoppingCartRouter)
app.include_router(orderRoute)

app.add_middleware(CORSMiddleware, allow_origins = ["http://localhost", "http://localhost:3000"], allow_credentials = True, allow_methods = ["*"], allow_headers = ["http://localhost", "http://localhost:3000"])