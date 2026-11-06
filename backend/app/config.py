"""Settings of the running service, read from the environment at start.

Every variable of compose is required (``${VAR:?}``); here only the build's
two and the edition must be non-empty -- the seams are measured, not
refused: ``/health`` reports what came (``seams``, ``checks.config``).
``PROFILE_DIR`` is the product's profile the machine mounts (form D); a
product without data gives none.
"""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """The environment of the app container."""

    model_config = SettingsConfigDict(populate_by_name=True, extra="ignore")

    edition: str = Field(validation_alias="EDITION", min_length=1)
    release: str = Field(validation_alias="PRIMER_RELEASE", min_length=1)
    commit: str = Field(validation_alias="PRIMER_COMMIT", min_length=1)
    api_url: str = Field(validation_alias="SERVICE_API_URL", default="")
    token: str = Field(validation_alias="SERVICE_TOKEN", default="")
    key: str = Field(validation_alias="SERVICE_KEY", default="")
    webhook: str = Field(validation_alias="PRODUCT_WEBHOOK_URL", default="")
    profile_dir: str = Field(validation_alias="PROFILE_DIR", default="")
