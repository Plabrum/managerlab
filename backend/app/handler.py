from mangum import Mangum
from app.index import app

# Create Lambda handler by wrapping the Litestar app with Mangum
handler = Mangum(app, lifespan="on")  # type: ignore[arg-type]
