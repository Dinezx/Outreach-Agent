from leadminerai.main import app
from fastapi.openapi.utils import get_openapi

try:
    schema = get_openapi(
        title=app.title,
        version=app.version,
        openapi_version=app.openapi_version,
        description=app.description,
        routes=app.routes,
    )
    print("OpenAPI schema generated successfully!")
except Exception as e:
    print("Failed to generate OpenAPI schema:")
    import traceback
    traceback.print_exc()
