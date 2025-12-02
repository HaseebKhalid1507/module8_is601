# main.py

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field, field_validator  # Use @validator for Pydantic 1.x
from fastapi.exceptions import RequestValidationError
from app.operations import add, subtract, multiply, divide  # Ensure correct import path
from app.routes.users import router as users_router  # Import user routes
from app.routes.calculations import router as calculations_router  # Import calculation routes
from app.database import create_tables  # Import table creation function
import uvicorn
import logging
import logging.config
import os
import time

# Setup logging configuration (console + file)
def setup_logging() -> None:
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)
    
    # Check if we can write to the logs directory
    log_file = os.path.join(log_dir, "app.log")
    can_write_file = True
    try:
        with open(log_file, 'a'):
            pass
    except (IOError, PermissionError):
        can_write_file = False
    
    handlers_config = {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "standard",
            "level": "INFO",
            "stream": "ext://sys.stdout",
        },
    }
    
    # Only add file handler if we can write to the log file
    if can_write_file:
        handlers_config["file"] = {
            "class": "logging.handlers.RotatingFileHandler",
            "formatter": "standard",
            "level": "INFO",
            "filename": log_file,
            "maxBytes": 2 * 1024 * 1024,  # 2MB
            "backupCount": 3,
            "encoding": "utf-8",
        }
    
    handler_list = ["console", "file"] if can_write_file else ["console"]
    
    logging.config.dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "standard": {
                    "format": "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
                    "datefmt": "%Y-%m-%d %H:%M:%S",
                }
            },
            "handlers": handlers_config,
            "loggers": {
                "uvicorn": {"level": "INFO", "handlers": handler_list, "propagate": False},
                "uvicorn.access": {"level": "INFO", "handlers": handler_list, "propagate": False},
                "app": {"level": "INFO", "handlers": handler_list, "propagate": False},
                # Detailed function-level logs for operations
                "app.operations": {"level": "DEBUG", "handlers": handler_list, "propagate": False},
            },
            "root": {"level": "INFO", "handlers": handler_list},
        }
    )


setup_logging()
logger = logging.getLogger("app.main")

app = FastAPI()

# Include user routes
app.include_router(users_router)

# Include calculation routes
app.include_router(calculations_router)

# Setup templates directory
templates = Jinja2Templates(directory="templates")

# Pydantic model for request data
class OperationRequest(BaseModel):
    a: float = Field(..., description="The first number")
    b: float = Field(..., description="The second number")

    @field_validator('a', 'b')  # Correct decorator for Pydantic 1.x
    def validate_numbers(cls, value):
        if not isinstance(value, (int, float)):
            raise ValueError('Both a and b must be numbers.')
        return value

# Pydantic model for successful response
class OperationResponse(BaseModel):
    result: float = Field(..., description="The result of the operation")

# Pydantic model for error response
class ErrorResponse(BaseModel):
    error: str = Field(..., description="Error message")

# Custom Exception Handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    logger.error(f"HTTPException on {request.url.path}: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail},
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    # Extracting error messages
    error_messages = "; ".join([f"{err['loc'][-1]}: {err['msg']}" for err in exc.errors()])
    logger.error(f"ValidationError on {request.url.path}: {error_messages}")
    return JSONResponse(
        status_code=400,
        content={"error": error_messages},
    )

@app.get("/")
async def read_root(request: Request):
    """
    Serve the index.html template.
    """
    logger.debug("Rendering index template for %s", request.client.host if request.client else "unknown")
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/login")
async def login_page(request: Request):
    """
    Serve the login.html template.
    """
    logger.debug("Rendering login template for %s", request.client.host if request.client else "unknown")
    return templates.TemplateResponse("login.html", {"request": request})


@app.get("/register")
async def register_page(request: Request):
    """
    Serve the register.html template.
    """
    logger.debug("Rendering register template for %s", request.client.host if request.client else "unknown")
    return templates.TemplateResponse("register.html", {"request": request})


@app.post("/add", response_model=OperationResponse, responses={400: {"model": ErrorResponse}})
async def add_route(operation: OperationRequest):
    """
    Add two numbers.
    """
    try:
        logger.info("Add requested: a=%s b=%s", operation.a, operation.b)
        result = add(operation.a, operation.b)
        logger.info("Add result: %s", result)
        return OperationResponse(result=result)
    except Exception as e:
        logger.error(f"Add Operation Error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/subtract", response_model=OperationResponse, responses={400: {"model": ErrorResponse}})
async def subtract_route(operation: OperationRequest):
    """
    Subtract two numbers.
    """
    try:
        logger.info("Subtract requested: a=%s b=%s", operation.a, operation.b)
        result = subtract(operation.a, operation.b)
        logger.info("Subtract result: %s", result)
        return OperationResponse(result=result)
    except Exception as e:
        logger.error(f"Subtract Operation Error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/multiply", response_model=OperationResponse, responses={400: {"model": ErrorResponse}})
async def multiply_route(operation: OperationRequest):
    """
    Multiply two numbers.
    """
    try:
        logger.info("Multiply requested: a=%s b=%s", operation.a, operation.b)
        result = multiply(operation.a, operation.b)
        logger.info("Multiply result: %s", result)
        return OperationResponse(result=result)
    except Exception as e:
        logger.error(f"Multiply Operation Error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/divide", response_model=OperationResponse, responses={400: {"model": ErrorResponse}})
async def divide_route(operation: OperationRequest):
    """
    Divide two numbers.
    """
    try:
        logger.info("Divide requested: a=%s b=%s", operation.a, operation.b)
        result = divide(operation.a, operation.b)
        logger.info("Divide result: %s", result)
        return OperationResponse(result=result)
    except ValueError as e:
        logger.error(f"Divide Operation Error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Divide Operation Internal Error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error")


# Request/response logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = time.monotonic()
    client_host = request.client.host if request.client else "unknown"
    path = request.url.path
    method = request.method
    try:
        response = await call_next(request)
        return response
    finally:
        duration_ms = (time.monotonic() - start) * 1000
        status = getattr(locals().get('response', None), 'status_code', 'N/A')
        logger.info("%s %s %s -> %s in %.2fms", client_host, method, path, status, duration_ms)


@app.on_event("startup")
async def on_startup():
    # Create database tables on startup
    create_tables()
    logger.info("Database tables created")
    logger.info("Application startup complete")


@app.on_event("shutdown")
async def on_shutdown():
    logger.info("Application shutdown initiated")

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
