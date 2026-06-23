"""Integration endpoints: list, connect, disconnect."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import (
    CurrentPrincipal,
    get_business_or_404,
    get_current_principal,
    paginate,
)
from app.db import get_db
from app.models.business import Business
from app.models.integration import Integration
from app.schemas.common import Page
from app.schemas.metric import (
    IntegrationConnectRequest,
    IntegrationConnectResponse,
    IntegrationItem,
)
from app.services.activity import log_activity

router = APIRouter()

# Catalog of available providers and their category.
_PROVIDER_CATALOG: dict[str, str] = {
    "github": "dev_product",
    "vercel": "deploy_infra",
    "stripe": "payments",
    "hubspot": "crm_sales",
    "google_ads": "marketing_ads",
    "meta_ads": "marketing_ads",
    "gmail": "email_comms",
    "sendgrid": "email_comms",
    "intercom": "support",
    "google_analytics": "analytics",
}

_AUTH_URLS: dict[str, str] = {
    "google_ads": "https://accounts.google.com/o/oauth2/v2/auth",
    "gmail": "https://accounts.google.com/o/oauth2/v2/auth",
    "google_analytics": "https://accounts.google.com/o/oauth2/v2/auth",
    "github": "https://github.com/login/oauth/authorize",
    "stripe": "https://connect.stripe.com/oauth/authorize",
}


@router.get("/{business_id}/integrations", response_model=Page[IntegrationItem])
def list_integrations(
    business: Business = Depends(get_business_or_404),
    db: Session = Depends(get_db),
    limit: int = 20,
    offset: int = 0,
) -> Page[IntegrationItem]:
    limit, offset = paginate(limit, offset)
    connected = {
        i.provider: i
        for i in db.execute(
            select(Integration).where(Integration.business_id == business.id)
        ).scalars().all()
    }
    items: list[IntegrationItem] = []
    for provider, category in _PROVIDER_CATALOG.items():
        existing = connected.get(provider)
        if existing is not None:
            items.append(
                IntegrationItem(
                    provider=provider,
                    category=existing.category or category,
                    status=existing.status,
                    connected_at=existing.connected_at,
                )
            )
        else:
            items.append(
                IntegrationItem(provider=provider, category=category, status="available")
            )
    return Page[IntegrationItem](
        items=items[offset : offset + limit], total=len(items), limit=limit, offset=offset
    )


@router.post(
    "/{business_id}/integrations/{provider}/connect",
    response_model=IntegrationConnectResponse,
)
def connect_integration(
    provider: str,
    body: IntegrationConnectRequest,
    business: Business = Depends(get_business_or_404),
    principal: CurrentPrincipal = Depends(get_current_principal),
    db: Session = Depends(get_db),
) -> IntegrationConnectResponse:
    state = str(uuid.uuid4())
    category = _PROVIDER_CATALOG.get(provider, "analytics")

    existing = db.execute(
        select(Integration).where(
            Integration.business_id == business.id, Integration.provider == provider
        )
    ).scalar_one_or_none()
    if existing is None:
        integration = Integration(
            tenant_id=business.tenant_id,
            business_id=business.id,
            provider=provider,
            category=category,
            status="connected",
            config={"oauth_state": state, "redirect_uri": body.redirect_uri},
            connected_at=datetime.now(UTC),
        )
        db.add(integration)
    else:
        existing.status = "connected"
        existing.config = {"oauth_state": state, "redirect_uri": body.redirect_uri}
        existing.connected_at = datetime.now(UTC)
    db.flush()

    log_activity(
        db,
        tenant_id=business.tenant_id,
        business_id=business.id,
        actor_type="human",
        actor_id=str(principal.user.id),
        action="integration.connect_started",
        target_type="integration",
        target_id=provider,
        summary=f"Started connect flow for {provider}.",
    )

    base_url = _AUTH_URLS.get(provider, "https://example.com/oauth/authorize")
    auth_url = (
        f"{base_url}?client_id=myuno&response_type=code"
        f"&redirect_uri={body.redirect_uri}&state={state}"
    )
    return IntegrationConnectResponse(
        provider=provider, authorization_url=auth_url, state=state
    )


@router.post(
    "/{business_id}/integrations/{provider}/disconnect",
    status_code=status.HTTP_204_NO_CONTENT,
)
def disconnect_integration(
    provider: str,
    business: Business = Depends(get_business_or_404),
    principal: CurrentPrincipal = Depends(get_current_principal),
    db: Session = Depends(get_db),
) -> Response:
    existing = db.execute(
        select(Integration).where(
            Integration.business_id == business.id, Integration.provider == provider
        )
    ).scalar_one_or_none()
    if existing is not None:
        db.delete(existing)
        log_activity(
            db,
            tenant_id=business.tenant_id,
            business_id=business.id,
            actor_type="human",
            actor_id=str(principal.user.id),
            action="integration.disconnected",
            target_type="integration",
            target_id=provider,
            summary=f"Disconnected {provider}.",
        )
    return Response(status_code=status.HTTP_204_NO_CONTENT)
